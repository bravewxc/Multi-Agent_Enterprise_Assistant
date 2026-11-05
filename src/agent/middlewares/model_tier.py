"""按任务复杂度分级使用模型（成本优化）。

背景：主 Agent 的每一次模型调用都携带完整的工具 schema，并走同一个主模型。
可实际上有一类轮次根本不需要工具，也不需要复杂推理：打招呼、说谢谢、
问"你能做什么"、确认"好的/收到"。让它们也背上几十个工具的 schema，
既费输入 token，又占主模型的并发额度。

做法：在模型调用这一层（`wrap_model_call` / `awrap_model_call`）做分流，
命中"简单轮次"时做两件事：
1. 把模型换成 `FAST_MODEL`（低成本模型）；
2. 把 `tools` 置空，去掉本轮不需要的工具 schema。

判定只用确定性规则（正则 + 长度上限 + 业务关键词黑名单），不额外调用
一次分类模型——否则省下来的钱又被分类调用吃掉。

保守原则（宁可不省，不能降质）：
- 只识别寒暄/致谢/元问题，凡出现业务关键词（订单、采购、补货、供应商…）
  一律走主模型；
- 只在一轮的**第一次**模型调用生效：一旦本轮已经出现工具调用或工具结果，
  说明任务不简单，后续调用立刻回主模型（并恢复工具 schema）；
- 任何异常或无法判定，都退回主模型，不影响正常对话。

边界：只作用于主 Agent 图。同步订单子图、异步分析与补货图处理的本来就是
业务任务，固定使用主模型，不在本中间件的范围内。
"""
from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

logger = logging.getLogger(__name__)

# 简单轮次的长度上限：再长的句子一律按复杂任务处理
_SIMPLE_MAX_CHARS = 24

# 业务关键词黑名单：命中任何一个都不降级
_BUSINESS_KEYWORDS = (
    "订单", "采购", "补货", "供应商", "比价", "报价", "库存", "物料", "审批",
    "下单", "改单", "合同", "交期", "价格", "成本", "预算", "分析", "报告",
    "图表", "查询", "创建", "修改", "删除", "退货", "发票", "付款", "对账",
    "风险", "预警", "安全库存", "再订货点", "寻源", "招标", "sku", "erp",
)

# 简单轮次模式：问候 / 致谢 / 确认 / 身份与能力咨询 / 告别
_SIMPLE_PATTERNS = (
    re.compile(r"^(你好|您好|嗨|哈喽|在吗|在不在|早上好|中午好|下午好|晚上好|"
               r"hi|hello|hey)[！!。,.，、~\s]*$", re.IGNORECASE),
    re.compile(r"^(谢谢|多谢|感谢|辛苦了|thanks|thank you|thx)[！!。,.，、~\s]*$",
               re.IGNORECASE),
    re.compile(r"^(好的|收到|明白了?|知道了|了解了?|ok|okay|嗯+|行|可以)"
               r"[！!。,.，、~\s]*$", re.IGNORECASE),
    re.compile(r"(你是谁|你叫什么|你的名字|你能做什么|你可以做什么|你会做什么|"
               r"你有什么功能|你能帮我做什么|who are you|what can you do)",
               re.IGNORECASE),
    re.compile(r"^(再见|拜拜|bye|goodbye)[！!。,.，、~\s]*$", re.IGNORECASE),
)


def _message_text(message: Any) -> str:
    """取消息的纯文本内容；兼容 content 为 str 或 content blocks 列表。"""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return str(content or "")


def is_simple_turn(text: str) -> bool:
    """判断一条用户消息是否属于"不需要工具和复杂推理"的简单轮次。"""
    normalized = (text or "").strip()
    if not normalized or len(normalized) > _SIMPLE_MAX_CHARS:
        return False
    lowered = normalized.lower()
    if any(keyword in lowered for keyword in _BUSINESS_KEYWORDS):
        return False
    return any(pattern.search(normalized) for pattern in _SIMPLE_PATTERNS)


def should_use_fast_model(messages: Sequence[Any]) -> bool:
    """判断本次模型调用能否降级。

    条件：最后一条用户消息是简单轮次，且该消息之后还没有出现工具调用或
    工具结果（即仍处于本轮第一次模型调用）。
    """
    last_human_index = -1
    for index, message in enumerate(messages):
        if isinstance(message, HumanMessage):
            last_human_index = index
    if last_human_index < 0:
        return False

    for message in messages[last_human_index + 1:]:
        if isinstance(message, ToolMessage):
            return False
        if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
            return False

    return is_simple_turn(_message_text(messages[last_human_index]))


class ModelTierMiddleware(AgentMiddleware):
    """简单轮次降级到低成本模型，并去掉本轮用不到的工具 schema。"""

    def __init__(self, *, fast_model: Any) -> None:
        self.fast_model = fast_model

    def _override(self, request: Any) -> Any:
        try:
            if should_use_fast_model(request.messages):
                logger.info("MODEL_TIER downgrade=fast tools=0")
                return request.override(model=self.fast_model, tools=[])
        except Exception:
            # 判定失败不能影响正常模型调用：退回主模型
            logger.debug("model_tier: 降级判定失败，使用主模型", exc_info=True)
        return request

    def wrap_model_call(self, request: Any, handler: Callable[[Any], Any]) -> Any:
        return handler(self._override(request))

    async def awrap_model_call(
        self,
        request: Any,
        handler: Callable[[Any], Awaitable[Any]],
    ) -> Any:
        return await handler(self._override(request))
