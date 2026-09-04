"""工具错误分类重试指引中间件（loop 改造 C：Typed Error-Feedback）。

前因（见 文档/loop/Agent循环工程详解与本项目改造分析.md 第 3.4/4.3 节）：
    评估方向 A 的指标表累计了真实错误分布（2026-09-03 拉取）：
    - write_file 56/208 失败（26.9%）：几乎全是 "File already exists"
    - order_search_details 42/65（64.6%）：ERP 查询失败
    - generate_visualization 16/16（100%）：图表服务不可用
    - 少量 MCP 连接超时（TimeoutError）
    此前这些错误以裸字符串/裸 traceback 返回给模型——模型面对
    "File already exists" 分不清该重试还是该换路径，要么盲目重试烧 token，
    要么过早放弃。错误消息的质量直接决定循环的自我修正效率。

协议（按真实错误分布设计的分类规则）：
    error_type = transient（可重试：超时/连接/服务暂时不可用）
               | permanent（不可重试：文件已存在/参数不支持/目标不存在——
                           给出修正线索，重试同样的调用没有意义）
    hint       = 下一步该怎么做（模型可执行）
    retry_budget = 剩余重试额度（按 thread+工具统计连续失败，2 次后耗尽——
                   防止同一错误无限重试的护栏，六要素④的工具级实例）

挂载位置：ToolErrorMiddleware 之前（列表更靠前 = 外层）。langchain 工具链
first=outermost：请求从外流向内，结果从内流回外——工具抛出的异常由内层
ToolError 转换成 status="error" 的 ToolMessage 后，回流到本层才能追加指引。
（实测：若挂在 ToolError 之内，异常直接穿过本层被外层捕获，指引永不触发。）
注意：ReportQuality 等会产生自身 error ToolMessage 的中间件必须挂在本层
之外，否则其批评会被本层误加指引。ImageGuard 在本层之内（最内层）。
"""
from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable

from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

logger = logging.getLogger(__name__)

# 连续失败预算：同一 (thread, tool) 连续失败 2 次后，指引转为"换路径"
_MAX_CONSECUTIVE_FAILS = 2

# (thread_id, tool_name) -> 连续失败计数（进程内内存态；重启清零可接受——
# 预算是防当轮死循环的护栏，不是持久状态）
_fail_counter: dict[tuple[str, str], int] = {}

# 分类规则：按真实错误分布排序（先命中先归类），全部大小写不敏感
_RULES: list[tuple[str, str, str]] = [
    # ---- transient：可重试 ----
    ("transient", r"timed? ?out|超时",
     "超时：可原样重试一次；仍超时则缩小查询范围或减少数据量"),
    ("transient", r"connection|connect|remoteprotocol|disconnected|reset by peer|连接",
     "连接类瞬时错误：等待 2 秒后原样重试一次"),
    ("transient", r"\b50[23]\b|service unavailable|bad gateway|temporarily|不可用",
     "服务暂时不可用：可重试一次；仍失败则跳过该能力并向用户如实说明"),
    # ---- permanent：不可重试，给修正线索 ----
    ("permanent", "already exists",
     "文件已存在：先 read_file 查看现有内容；要修改用 edit_file，要覆盖先确认后删除"),
    ("permanent", "not found|no such file|404",
     "目标不存在：检查路径/ID 等参数拼写后换正确参数重试，原样重试无效"),
    ("permanent", "does not support|unsupported|invalid parameter|参数错误|validation",
     "参数不被支持：对照工具说明检查参数名/取值后修正重试"),
    ("permanent", "permission|forbidden|403|unauthorized|401",
     "权限不足：该操作不被允许，不要重试；向用户说明或换允许的操作"),
    ("permanent", "400|bad request|parse|format",
     "请求格式/参数问题：检查输入格式后修正重试"),
]


def _classify(error_text: str) -> tuple[str, str] | None:
    """错误文本 → (error_type, hint)。无命中返回 None（未知错误不强加分类）。"""
    low = error_text.lower()
    for etype, pattern, hint in _RULES:
        if re.search(pattern, low):
            return etype, hint
    return None


class RetryGuidanceMiddleware(AgentMiddleware):
    """给所有工具错误返回追加结构化重试指引（分类 + hint + 预算）。"""

    state_schema = AgentState

    @staticmethod
    def _budget_key(request: ToolCallRequest) -> tuple[str, str]:
        try:
            tid = request.runtime.config["configurable"]["thread_id"]
        except Exception:
            tid = "unknown"
        tc = request.tool_call
        name = tc.get("name", "?") if isinstance(tc, dict) else getattr(tc, "name", "?")
        return (tid, str(name))

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        result = await handler(request)
        if not (isinstance(result, ToolMessage) and result.status == "error"
                and isinstance(result.content, str)):
            # 成功（或非字符串 content）→ 清零连续失败计数
            _fail_counter.pop(self._budget_key(request), None)
            return result

        # 失败 → 计数 +1，构造指引块
        key = self._budget_key(request)
        fails = _fail_counter.get(key, 0) + 1
        _fail_counter[key] = fails

        matched = _classify(result.content)
        if matched is None and fails < _MAX_CONSECUTIVE_FAILS:
            return result  # 未知错误且预算未耗尽：不画蛇添足

        etype, hint = matched or ("unknown", "未知错误类型")
        budget = max(0, _MAX_CONSECUTIVE_FAILS - fails)
        if budget == 0:
            guidance = (
                f"\n\n[错误处理指引] {{\"error_type\": \"{etype}\", "
                f"\"retry_budget\": 0, \"consecutive_fails\": {fails}}}\n"
                f"该工具在本会话已连续失败 {fails} 次，重试预算已耗尽——"
                f"**不要再原样重试**。请更换路径（换工具/换参数/缩小范围），"
                f"或向用户如实报告当前障碍与已尝试的内容。"
            )
        else:
            guidance = (
                f"\n\n[错误处理指引] {{\"error_type\": \"{etype}\", "
                f"\"retry_budget\": {budget}}}\n"
                f"{'可重试：' if etype == 'transient' else '不建议原样重试：'}{hint}。"
            )

        logger.info("RETRY_GUIDANCE tool=%s type=%s budget=%d fails=%d",
                    key[1], etype, budget, fails)
        return result.model_copy(
            update={"content": result.content + guidance})
