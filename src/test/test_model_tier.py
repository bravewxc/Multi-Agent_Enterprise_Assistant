"""模型分级中间件离线单测（不起后端、不连模型/Mongo/沙箱）。

验证点：
1. 规则判定：寒暄/致谢/能力咨询判为简单；带业务关键词的一律不是简单轮次
2. 简单轮次第一次模型调用 → 换成快模型且 tools 置空
3. 业务问题 → 保持主模型、工具 schema 不变
4. 本轮已出现工具调用/工具结果 → 不降级（回主模型）
5. 同步与异步两条路径行为一致

运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_model_tier
（若报模块找不到，先设置 PYTHONPATH=src）
"""
from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR / "src"))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent.middlewares.model_tier import (
    ModelTierMiddleware,
    is_simple_turn,
    should_use_fast_model,
)


@dataclass
class _FakeRequest:
    """ModelRequest 的最小替身：只需要 messages / model / tools 和 override。"""

    messages: list
    model: str = "main-model"
    tools: list = field(default_factory=lambda: ["tool_a", "tool_b"])

    def override(self, **overrides):
        data = {"messages": self.messages, "model": self.model, "tools": self.tools}
        data.update(overrides)
        return _FakeRequest(**data)


def test_classifier():
    simple = ["你好", "您好！", "谢谢", "收到", "你能做什么？", "who are you"]
    complex_cases = [
        "帮我查一下订单 PO-2024-001",
        "对比博世和电装的火花塞报价",
        "对刹车类预警物料给出补货建议",
        "好的，那就按 1 万的预算改",
        "你好，我想问下这个供应商的交期",
        "",
        "你好" * 20,
    ]
    for text in simple:
        assert is_simple_turn(text), f"应判为简单轮次: {text!r}"
    for text in complex_cases:
        assert not is_simple_turn(text), f"不应判为简单轮次: {text!r}"
    print("[OK] 规则判定")


def test_should_use_fast_model():
    assert should_use_fast_model([HumanMessage("你好")]) is True
    assert should_use_fast_model([]) is False
    assert should_use_fast_model([AIMessage("hi")]) is False

    # 本轮已经调用过工具 → 不降级
    with_tool_call = [
        HumanMessage("你好"),
        AIMessage("", tool_calls=[{"name": "tool_a", "args": {}, "id": "c1"}]),
    ]
    assert should_use_fast_model(with_tool_call) is False

    with_tool_result = [
        HumanMessage("你好"),
        AIMessage("", tool_calls=[{"name": "tool_a", "args": {}, "id": "c1"}]),
        ToolMessage("result", tool_call_id="c1"),
    ]
    assert should_use_fast_model(with_tool_result) is False
    print("[OK] 降级条件")


def test_async_override():
    mw = ModelTierMiddleware(fast_model="fast-model")

    async def handler(request):
        return request

    req = _FakeRequest(messages=[HumanMessage("你好")])
    result = asyncio.run(mw.awrap_model_call(req, handler))
    assert result.model == "fast-model", result.model
    assert result.tools == [], result.tools

    req = _FakeRequest(messages=[HumanMessage("帮我查一下订单 PO-2024-001")])
    result = asyncio.run(mw.awrap_model_call(req, handler))
    assert result.model == "main-model", result.model
    assert result.tools == ["tool_a", "tool_b"], result.tools

    req = _FakeRequest(messages=[
        HumanMessage("你好"),
        AIMessage("", tool_calls=[{"name": "tool_a", "args": {}, "id": "c1"}]),
        ToolMessage("result", tool_call_id="c1"),
    ])
    result = asyncio.run(mw.awrap_model_call(req, handler))
    assert result.model == "main-model", result.model
    print("[OK] 异步路径")


def test_sync_override():
    mw = ModelTierMiddleware(fast_model="fast-model")

    def handler(request):
        return request

    req = _FakeRequest(messages=[HumanMessage("谢谢")])
    result = mw.wrap_model_call(req, handler)
    assert result.model == "fast-model", result.model
    assert result.tools == [], result.tools
    print("[OK] 同步路径")


def main():
    test_classifier()
    test_should_use_fast_model()
    test_async_override()
    test_sync_override()
    print("ALL_OK")


if __name__ == "__main__":
    main()
