"""补货清单运行时质量评审中间件（loop 改造 A1 评审记录 + A2 Reflexion 重写循环）。

前因（见 文档/loop/Agent循环工程详解与本项目改造分析.md 第 3.2/4.3 节）：
    评估方向 D 的 Judge（judge_report.py）此前只存在于离线脚本——补货清单
    审批通过、存档之后，人才能手动跑一次评审。运行时没有任何"这份清单
    合不合格"的自动判断，质量全押在提示词整改的静态效果上。
    A1 把已校准的评审器（锚点 rubric + 异构模型）搬进运行时：清单生成后、
    展示给用户之前自动跑一遍评审，分数落库 + 打日志。
    A2 在 A1 之上加 Reflexion 重写循环：评审不达标 → 批评意见作为
    status="error" 的 ToolMessage 回流给模型 → 模型修改清单重新提交
    （重新过门禁，通过后才进入审批，用户对合格版再拍板）。最多重写 2 轮，
    第 3 次提交无条件放行（附质量备注）——"带着批评意见放行，不阻断交付"。

工作位置（关键时序，已改为"生成后、展示前"）：
    模型调 replenish_submit
    → 本中间件的 aafter_model 先跑（评审 + A1 记录 + A2 决策）
    → 不达标：批评以 error ToolMessage 回流、jump_to="model"，模型重写
    → 达标：放行到 HITL，中断等审批（用户看到的是已过质量门的清单）
    → 用户 approve → 工具直接执行并落盘（不再二次评审）
    → 用户 reject  → 不落盘

    实现要点：LangGraph 的 after_model 链按中间件列表**反向**执行，
    所以本中间件必须排在 HumanInTheLoopMiddleware **之后**（列表更靠后），
    才能先于审批中断运行；HITL 因此改为在异步图显式挂载，
    不再通过 create_deep_agent(interrupt_on=...) 由框架追加到末尾。

循环护栏（对应 Loop Engineering 六要素④）：
    - 最多重写 2 轮（_MAX_REWRITES），轮次从 state.messages 里的
      批评标记计数——无状态设计，天然幂等，进程重启不丢轮次；
    - 评审基础设施失败（Judge API 挂/Mongo 不可写/解析失败）一律旁路
      放行，只有"确定性检查失败"或"语义分明确低于及格线"才拦截——
      无法判定 ≠ 不合格（基础设施故障不是清单的错）。

与离线 Judge 的关系（Reward Hacking 防线，见改造文档 4.4 节）：
    防线①事实锚定：确定性算术检查 + rubric 只认量化数字，塞空话无效；
    防线②异构分离：glm-5.2 判 DeepSeek，共享上下文最小（只看清单本身）；
    防线③双入口复评：本中间件与 judge_report.py 物理 import 同一段评审
        代码（build_judge_prompt/parse_judge_output/deterministic_checks），
        离线复评分数与运行时分数的偏差 = "循环学会糊弄检查"的警报器；
    防线④禁改验证器：批评意见明示"评审标准固定，糊弄无效"；评审输入
        直接取 tool_call args（模型改不了），不是可篡改的文件。

旁路纪律（与 MemoryUpdate/ToolMetrics 一致）：
    评审自身失败只打日志绝不阻断清单存档——评审是增值能力，不是交付依赖。
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

logger = logging.getLogger(__name__)

# 评审结果落库集合（与 tool_call_metrics 同库，lazy 初始化）
_MONGO_COL = None

# A2：重写循环护栏
_CRITIQUE_MARKER = "【清单质量评审未通过】"   # 批评 ToolMessage 的固定前缀（轮次计数依据）
_MAX_REWRITES = 2                            # 最多重写 2 轮，第 3 次提交无条件放行

# 进程内最近一次评审结果：键 (thread_id, plan 指纹)。
# 只为「审批通过后落盘时补一条质量备注」服务——审批与工具执行之间
# 若进程重启导致缓存缺失，仅少一条备注，不影响落盘主流程。
_VERDICT_CACHE: dict[tuple[str, str], dict] = {}
_VERDICT_CACHE_MAX = 64


def _plan_fingerprint(plan: list) -> str:
    raw = json.dumps(plan, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_verdict(thread_id: str, plan: list, verdict: dict) -> None:
    _VERDICT_CACHE[(thread_id, _plan_fingerprint(plan))] = verdict
    while len(_VERDICT_CACHE) > _VERDICT_CACHE_MAX:
        _VERDICT_CACHE.pop(next(iter(_VERDICT_CACHE)))


def _cached_verdict(thread_id: str, plan: list) -> dict | None:
    return _VERDICT_CACHE.get((thread_id, _plan_fingerprint(plan)))


def _get_collection():
    """MongoDB 集合 lazy 获取（连不上返回 None，调用方旁路）。

    状态约定：None=未初始化 / False=初始化失败（不再重试）/ Collection=可用。
    注意 pymongo 的 Collection 不支持布尔判断，必须显式 is 判断。
    """
    global _MONGO_COL
    if _MONGO_COL is None:
        try:
            from pymongo import MongoClient
            from agent.env_utils import MONGODB_URI
            _MONGO_COL = MongoClient(
                MONGODB_URI, serverSelectionTimeoutMS=3000,
            )["langchain_db"]["report_quality_scores"]
        except Exception:
            logger.warning("report_quality: MongoDB 初始化失败，分数只打日志不落库",
                           exc_info=True)
            _MONGO_COL = False
    if _MONGO_COL is None or _MONGO_COL is False:
        return None
    return _MONGO_COL


class ReportQualityMiddleware(AgentMiddleware):
    """replenish_submit 执行前自动评审清单：A1 记录分数 + A2 低分拦截重写。"""

    state_schema = AgentState

    def __init__(self, judge_model_factory=None, pass_line: float | None = None) -> None:
        super().__init__()
        # 工厂延迟导入：模型实例在 2024 进程内创建（避免模块导入期连 API）
        self._judge_model_factory = judge_model_factory
        # 及格线：默认 6.0（与离线 judge_report 的 LLM_PASS_LINE 一致）。
        # 支持环境变量覆盖——用于故障注入验证（如临时调到 9.5 触发重写循环）。
        if pass_line is None:
            pass_line = float(os.environ.get("REPORT_QUALITY_PASS_LINE", "6"))
        self.pass_line = pass_line

    # ------------------------------------------------------------
    # 评审核心
    # ------------------------------------------------------------
    async def _evaluate(self, plan: list) -> dict:
        """确定性检查 + 异构 LLM 语义评审，返回综合结论。

        返回: {det_checks, det_pass, llm_results, llm_avg, llm_available}
        任何一层失败都不抛出（旁路），llm_available=False 表示语义分缺失。
        """
        from eval.judge_report import (
            build_judge_prompt, parse_judge_output, deterministic_checks,
            build_judge_model, RUBRICS,
        )

        # 1. 确定性检查（本地代码，零成本，绝对可信）
        report = {"plan": plan}
        det_checks = deterministic_checks(report)
        det_pass = all(c["pass"] for c in det_checks)

        # 2. 语义评审（glm-5.2，与被评的 DeepSeek 异构）
        llm_results: list[dict] = []
        llm_available = True
        try:
            if self._judge_model_factory is not None:
                model = self._judge_model_factory()
            else:
                model = build_judge_model()
            for criterion in RUBRICS:
                prompt = build_judge_prompt(criterion, "", plan)
                parsed = None
                for _attempt in range(2):
                    resp = await model.ainvoke(prompt)
                    try:
                        parsed = parse_judge_output(
                            resp.content, criterion, model.model_name)
                        break
                    except Exception:
                        continue
                if parsed is None:
                    # 解析两次失败：视为"本次无法判定"，不记 0 分
                    # （0 分会把清单误判为不合格——基础设施故障≠清单差）
                    llm_available = False
                    llm_results.append({
                        "criterion": criterion, "type": "llm",
                        "pass": None, "score": None,
                        "rationale": "Judge 输出解析失败（运行时旁路）",
                        "judge_model": model.model_name})
                else:
                    llm_results.append(parsed)
        except Exception as e:
            # Judge API 层失败（额度/网络）：语义分缺失，只用确定性结论
            llm_available = False
            logger.warning("report_quality: Judge API 不可用，本次只记录确定性检查"
                           "（%s: %s）", type(e).__name__, str(e)[:120])

        scores = [r["score"] for r in llm_results if r.get("score") is not None]
        llm_avg = round(sum(scores) / len(scores), 1) if scores else None

        return {"det_checks": det_checks, "det_pass": det_pass,
                "llm_results": llm_results, "llm_avg": llm_avg,
                "llm_available": llm_available}

    # ------------------------------------------------------------
    # 记录
    # ------------------------------------------------------------
    def _record(self, verdict: dict, tool_call: dict, thread_id: str,
                action: str, round_no: int) -> None:
        doc = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "thread_id": thread_id,
            "item_count": len(tool_call.get("args", {}).get(
                "replenishment_plan") or []),
            "det_pass": verdict["det_pass"],
            "det_fails": [c["criterion"] for c in verdict["det_checks"]
                          if not c["pass"]],
            "llm_avg": verdict["llm_avg"],
            "llm_available": verdict["llm_available"],
            "llm_detail": {r["criterion"]: {"score": r["score"],
                                            "rationale": r["rationale"]}
                           for r in verdict["llm_results"]},
            "pass_line": self.pass_line,
            # A2 动作: recorded=达标放行到审批 / passed_with_note=轮次耗尽带备注放行 /
            #          blocked_before_approval=展示前拦截重写
            "action": action,
            "round": round_no,
        }
        try:
            col = _get_collection()
            if col is not None:
                col.insert_one(doc)
        except Exception:
            logger.debug("report_quality: 分数落库失败（不影响流程）", exc_info=True)

        logger.info(
            "REPORT_QUALITY thread=%s items=%s det=%s llm_avg=%s%s action=%s round=%s",
            thread_id, doc["item_count"],
            "PASS" if doc["det_pass"] else f"FAIL{doc['det_fails']}",
            verdict["llm_avg"] if verdict["llm_avg"] is not None else "N/A",
            "" if verdict["llm_available"] else "（语义评审不可用）",
            action, round_no,
        )

    # ------------------------------------------------------------
    # A2：拦截决策与批评构造
    # ------------------------------------------------------------
    @staticmethod
    def _count_rewrite_rounds(state) -> int:
        """数 state.messages 里已有的批评标记 → 当前是第几轮。

        无状态设计：轮次不存图 state（避免侵入 state schema），直接从
        消息历史数——进程重启/图重放都不会丢轮次，天然幂等。
        """
        msgs = (state or {}).get("messages", []) if isinstance(state, dict) else []
        n = 0
        for m in msgs:
            try:
                if getattr(m, "type", "") == "tool" and \
                        str(getattr(m, "content", "")).startswith(_CRITIQUE_MARKER):
                    n += 1
            except Exception:
                continue
        return n

    def _should_block(self, verdict: dict) -> bool:
        """拦截条件：确定性失败（客观错）或语义分明确低于及格线。

        Judge 不可用（llm_available=False）时只看确定性结论——
        无法判定 ≠ 不合格，基础设施故障不是清单的错。
        """
        if not verdict["det_pass"]:
            return True
        if verdict["llm_available"] and verdict["llm_avg"] is not None:
            return verdict["llm_avg"] < self.pass_line
        return False

    def _build_critique(self, verdict: dict, round_no: int) -> str:
        """构造批评 ToolMessage 内容（Reflexion 的"反思"部分）。

        内容结构：分数总览 → 具体扣分点（确定性失败项 + 语义低分理由）
        → 修改指令 → 防糊弄声明（Reward Hacking 防线④）。
        """
        lines = [
            f"{_CRITIQUE_MARKER}（第 {round_no}/{_MAX_REWRITES} 轮重写机会）",
            "",
            f"评审结论：确定性检查{'未通过' if not verdict['det_pass'] else '通过'}",
        ]
        if verdict["llm_avg"] is not None:
            lines.append(f"语义均分 {verdict['llm_avg']}/10（及格线 {self.pass_line}）")
        det_fails = [c for c in verdict["det_checks"] if not c["pass"]]
        if det_fails:
            lines.append("")
            lines.append("【确定性失败项（必须修正，这是客观错误）】")
            for c in det_fails:
                lines.append(f"- {c['criterion']}: {c['detail']}")
        low_llm = [r for r in verdict["llm_results"]
                   if r.get("score") is not None and r["score"] < self.pass_line]
        if low_llm:
            lines.append("")
            lines.append("【语义低分理由（按此针对性补强）】")
            for r in low_llm:
                lines.append(f"- {r['criterion']} {r['score']}/10: {r['rationale']}")
        lines.append("")
        lines.append("修改要求：")
        lines.append("1. 只修改 replenishment_plan 的内容本身（量化 reason / urgency 分级 /")
        lines.append("   算术一致性 / 缺失字段），保持任务目标不变；")
        lines.append("2. reason 必须含真实数字（当前库存/日耗/ROP/建议量由来）；")
        lines.append("3. 修改后重新调用 replenish_submit 提交修订版——"
                     "修订版会先重新质量评审，通过后再等待人工审批。")
        lines.append("")
        lines.append("注意：评审标准固定（确定性算术 + 量化依据锚点），")
        lines.append("堆砌无依据的数字或措辞不会提高评分。")
        return "\n".join(lines)

    # ------------------------------------------------------------
    # 钩子
    # ------------------------------------------------------------
    @staticmethod
    def _thread_id(runtime: Any) -> str:
        try:
            cfg = getattr(runtime, "config", None) or {}
            tid = (cfg.get("configurable") or {}).get("thread_id")
            if tid:
                return str(tid)
        except Exception:
            pass
        return "unknown"

    def _build_note(self, verdict: dict) -> str:
        """轮次耗尽的清单落盘后追加的质量备注（不阻断交付）。"""
        return (
            "\n\n【质量备注】清单已存档，但未达评审及格线"
            f"（语义 {verdict['llm_avg']}/10，及格线 {self.pass_line}；"
            f"已重写 {_MAX_REWRITES} 轮）。评审意见见上，"
            "建议人工复核本清单。"
        )

    @hook_config(can_jump_to=["model"])
    async def aafter_model(
        self, state: Any, runtime: Any
    ) -> dict[str, Any] | None:
        """生成后、展示前：评审清单；不达标则批评回流并打回模型重写。

        位置在 HITL 之前（after_model 链反向执行），所以用户看到的
        永远是已过质量门的清单；通过后 approve 即直接落盘。
        """
        messages = state.get("messages", []) if isinstance(state, dict) else []
        last_ai = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)), None
        )
        if last_ai is None:
            return None

        target = next(
            (tc for tc in (getattr(last_ai, "tool_calls", None) or [])
             if tc.get("name") == "replenish_submit"),
            None,
        )
        if target is None:
            return None

        plan = (target.get("args") or {}).get("replenishment_plan") or []
        if not plan:
            return None

        thread_id = self._thread_id(runtime)
        round_no = self._count_rewrite_rounds(state) + 1

        # 评审自身异常 → 旁路放行到审批（无法判定 ≠ 不合格）
        try:
            verdict = await self._evaluate(plan)
        except Exception:
            logger.warning("report_quality: 评审异常（旁路放行到审批）", exc_info=True)
            return None

        _cache_verdict(thread_id, plan, verdict)

        if self._should_block(verdict) and round_no <= _MAX_REWRITES:
            # 拦截：不进入审批，批评回流让模型重写
            self._record(verdict, target, thread_id,
                         "blocked_before_approval", round_no)
            return {
                "messages": [ToolMessage(
                    content=self._build_critique(verdict, round_no),
                    tool_call_id=str(target.get("id") or ""),
                    status="error",
                )],
                "jump_to": "model",
            }

        # 达标，或轮次耗尽后带备注放行——统一交给后续 HITL 审批
        action = "passed_with_note" if self._should_block(verdict) else "recorded"
        self._record(verdict, target, thread_id, action, round_no)
        return None

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        """审批通过后的落盘阶段：不再评审，只给轮次耗尽的清单补质量备注。"""
        tc = request.tool_call
        name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "")
        if name != "replenish_submit":
            return await handler(request)

        result = await handler(request)
        if not isinstance(result, ToolMessage):
            return result

        try:
            thread_id = str(
                request.runtime.config["configurable"]["thread_id"]
            )
        except Exception:
            thread_id = "unknown"

        plan = ((tc.get("args") or {}) if isinstance(tc, dict) else {}).get(
            "replenishment_plan") or []
        verdict = _cached_verdict(thread_id, plan)
        if verdict is not None and self._should_block(verdict):
            result = result.model_copy(
                update={"content": str(result.content) + self._build_note(verdict)}
            )
        return result
