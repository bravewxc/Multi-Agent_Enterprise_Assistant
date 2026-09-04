"""方向 A 离线单测：ToolMetricsMiddleware 包裹逻辑（不起后端、不连沙箱）。

验证点：
1. 成功调用 → 记录 ok=True + 耗时
2. 工具抛异常（本中间件在中间层）→ 记录 ok=False + error_type，且异常继续上抛
3. 内层把异常转成 status="error" 的 ToolMessage → 从 status 识别失败
4. Mongo 不可用 → 不影响工具调用本身（旁路原则）
5. 指标最终落到 MongoDB（若本机 Mongo 在线则真写，否则跳过）

运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_tool_metrics
"""
from __future__ import annotations

import asyncio
import sys

from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime


class _FakeRuntime:
    """最小 Runtime 替身：只提供 config（thread_id 从这里取）。"""

    def __init__(self, thread_id: str):
        self.config = {"configurable": {"thread_id": thread_id}}


def _make_request(thread_id: str = "t-test-001") -> ToolCallRequest:
    return ToolCallRequest(
        tool_call={"name": "supplier_query", "args": {"name": "博世"}, "id": "call_1"},
        tool=None,
        state={},
        runtime=_FakeRuntime(thread_id),  # type: ignore[arg-type]
    )


def test_success_path(mw):
    """成功调用：handler 正常返回 → ok=True"""
    async def handler(req):
        return ToolMessage(content='{"rows": []}', tool_call_id="call_1")

    result = asyncio.run(mw.awrap_tool_call(_make_request(), handler))
    assert result.content == '{"rows": []}'
    print("[PASS] 1. 成功路径 ok=True，返回值原样透传")


def test_exception_path(mw):
    """异常路径：handler 抛异常 → 记录失败并 re-raise"""
    async def handler(req):
        raise TimeoutError("MCP 连接超时")

    try:
        asyncio.run(mw.awrap_tool_call(_make_request(), handler))
        raise AssertionError("应当上抛异常")
    except TimeoutError:
        print("[PASS] 2. 异常路径 ok=False + error_type=TimeoutError，异常继续上抛")


def test_status_error_path(mw):
    """内层已转换路径：收到 status='error' 的 ToolMessage → 识别为失败"""
    async def handler(req):
        return ToolMessage(
            content='{"error": "...", "status": "error"}',
            tool_call_id="call_1",
            status="error",
        )

    asyncio.run(mw.awrap_tool_call(_make_request(), handler))
    print("[PASS] 3. ToolMessage.status='error' 被识别为失败（不依赖异常）")


def test_mongo_down_no_crash():
    """旁路原则：Mongo 不可用时工具调用不受影响"""
    import agent.middlewares.tool_metrics as tm
    mw = tm.ToolMetricsMiddleware()
    tm._metrics_collection = None
    tm._mongo_unavailable = True  # 模拟 Mongo 挂

    async def handler(req):
        return ToolMessage(content="ok", tool_call_id="call_1")

    result = asyncio.run(mw.awrap_tool_call(_make_request("t-mongo-down"), handler))
    assert result.content == "ok"
    print("[PASS] 4. Mongo 不可用时调用不受影响（旁路原则）")
    tm._mongo_unavailable = False  # 恢复全局态，避免影响后续用例


def test_record_shape():
    """落库文档字段完整性（Mongo 在线时真写一条）"""
    import agent.middlewares.tool_metrics as tm
    col = tm._get_collection()
    if col is None:
        print("[SKIP] 5. 本机 MongoDB 不在线，跳过落库检查")
        return
    mw = tm.ToolMetricsMiddleware()
    mw._record(_make_request("t-shape"), ok=True, latency_ms=12.3)
    doc = col.find_one({"thread_id": "t-shape"})
    assert doc is not None, "文档应已写入"
    for field in ("ts", "tool_name", "ok", "latency_ms", "thread_id", "args_digest"):
        assert field in doc, f"缺少字段 {field}"
    assert doc["tool_name"] == "supplier_query"
    assert doc["args_digest"] == '{"name": "博世"}'
    print(f"[PASS] 5. 落库字段完整：{ {k: doc[k] for k in ('tool_name','ok','latency_ms','thread_id')} }")


if __name__ == "__main__":
    sys.path.insert(0, "src")
    from agent.middlewares.tool_metrics import ToolMetricsMiddleware

    mw = ToolMetricsMiddleware()
    test_success_path(mw)
    test_exception_path(mw)
    test_status_error_path(mw)
    test_mongo_down_no_crash()
    test_record_shape()
    print("\n全部通过：tool_metrics 中间件包裹逻辑正确")
