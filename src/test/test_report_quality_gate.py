"""报告质量门禁位置回归（离线，不依赖 MongoDB / 2024 / MCP）。

验证两件事：
1. LangGraph 的 after_model 链按中间件列表**反向**执行——这是"质量门禁
   先于 HITL 审批"的前提，框架升级若改变顺序，本用例会先失败；
2. ReportQualityMiddleware.aafter_model 的三种决策：
   不达标→批评回流 + jump_to=model；达标→放行到审批；轮次耗尽→放行。

运行：python -m test.test_report_quality_gate
"""
from __future__ import annotations

import asyncio
import sys
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

sys.path.insert(0, "src")

from agent.middlewares.report_quality import (  # noqa: E402
    _CRITIQUE_MARKER,
    ReportQualityMiddleware,
)

ORDER: list[str] = []


class _RecorderBase(AgentMiddleware):
    TAG = "base"

    async def aafter_model(self, state: Any, runtime: Any):
        ORDER.append(self.TAG)
        return None


class _RecorderFirst(_RecorderBase):
    TAG = "earlier-in-list"


class _RecorderLast(_RecorderBase):
    TAG = "later-in-list"


def test_after_model_runs_in_reverse_list_order() -> None:
    ORDER.clear()
    model = FakeMessagesListChatModel(responses=[AIMessage(content="ok")])
    agent = create_agent(
        model=model,
        tools=[],
        middleware=[_RecorderFirst(), _RecorderLast()],
    )
    asyncio.run(agent.ainvoke({"messages": [HumanMessage(content="hi")]}))
    assert ORDER == ["later-in-list", "earlier-in-list"], ORDER
    print(f"[PASS] after_model 反向执行：{ORDER}")


def _bad_verdict() -> dict:
    return {
        "det_pass": True,
        "det_checks": [{"criterion": "amount_sum", "pass": True, "detail": ""}],
        "llm_avg": 4.0,
        "llm_available": True,
        "llm_results": [{
            "criterion": "actionability", "type": "llm", "pass": False,
            "score": 4.0, "rationale": "reason 全是空话", "judge_model": "stub",
        }],
    }


def _good_verdict() -> dict:
    v = _bad_verdict()
    v["llm_avg"] = 8.0
    v["llm_results"] = [{
        "criterion": "actionability", "type": "llm", "pass": True,
        "score": 8.0, "rationale": "有量化依据", "judge_model": "stub",
    }]
    return v


class _StubQuality(ReportQualityMiddleware):
    """固定评审结论，避免真实调用 Judge。"""

    def __init__(self, verdict: dict) -> None:
        super().__init__(pass_line=6.0)
        self._verdict = verdict
        self.actions: list[str] = []

    async def _evaluate(self, plan: list) -> dict:  # type: ignore[override]
        return self._verdict

    def _record(self, verdict, tool_call, thread_id, action, round_no):  # type: ignore[override]
        self.actions.append(action)


class _Runtime:
    def __init__(self, thread_id: str = "t-quality") -> None:
        self.config = {"configurable": {"thread_id": thread_id}}


def _state(plan: list | None = None, critiques: int = 0) -> dict:
    plan = plan if plan is not None else [{"partId": 1, "suggestQuantity": 10}]
    msgs = [HumanMessage(content="给我补货建议")]
    for i in range(critiques):
        msgs.append(ToolMessage(
            content=f"{_CRITIQUE_MARKER} 第 {i + 1} 轮", tool_call_id=f"c{i}",
            status="error"))
    msgs.append(AIMessage(
        content="",
        tool_calls=[{"name": "replenish_submit", "id": "call_1",
                     "args": {"replenishment_plan": plan}}],
    ))
    return {"messages": msgs}


def test_block_before_approval() -> None:
    mw = _StubQuality(_bad_verdict())
    out = asyncio.run(mw.aafter_model(_state(), _Runtime()))
    assert isinstance(out, dict), out
    assert out.get("jump_to") == "model", out
    msgs = out["messages"]
    assert len(msgs) == 1 and isinstance(msgs[0], ToolMessage), msgs
    assert msgs[0].status == "error" and msgs[0].tool_call_id == "call_1"
    assert str(msgs[0].content).startswith(_CRITIQUE_MARKER)
    assert mw.actions == ["blocked_before_approval"], mw.actions
    print("[PASS] 不达标：批评回流 + jump_to=model（不进入审批）")


def test_pass_goes_to_approval() -> None:
    mw = _StubQuality(_good_verdict())
    out = asyncio.run(mw.aafter_model(_state(), _Runtime()))
    assert out is None, out          # None 表示交给后续 HITL 中断
    assert mw.actions == ["recorded"], mw.actions
    print("[PASS] 达标：放行到审批（approve 后直接落盘）")


def test_rounds_exhausted_goes_to_approval() -> None:
    mw = _StubQuality(_bad_verdict())
    out = asyncio.run(mw.aafter_model(_state(critiques=2), _Runtime()))
    assert out is None, out          # 已重写 2 轮 → 第 3 次带备注放行
    assert mw.actions == ["passed_with_note"], mw.actions
    print("[PASS] 轮次耗尽：带质量备注放行到审批")


def test_other_tool_ignored() -> None:
    mw = _StubQuality(_bad_verdict())
    state = {"messages": [AIMessage(
        content="", tool_calls=[{"name": "web_search", "id": "c9", "args": {}}])]}
    assert asyncio.run(mw.aafter_model(state, _Runtime())) is None
    assert mw.actions == []
    print("[PASS] 非 replenish_submit 调用不触发评审")


if __name__ == "__main__":
    test_after_model_runs_in_reverse_list_order()
    test_block_before_approval()
    test_pass_goes_to_approval()
    test_rounds_exhausted_goes_to_approval()
    test_other_tool_ignored()
    print("\nALL_OK")
