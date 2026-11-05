"""创建订单幂等并发测试：内存 MCP Client + 假 ERP，不依赖真实后端。

验证点：
1. 同一幂等键 10 个并发创建，ERP 只收到 1 次 POST，其余返回首次结果
2. 创建成功后的重放不会把后续订单更新版本重置为 1
3. 不同幂等键是不同采购意图，允许分别创建
4. 同一键携带不同订单参数返回 409，不写 ERP
5. 首次失败不缓存，同键重试仍可成功

运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_order_create_idempotency
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import httpx
from fastmcp import Client

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR / "src"))

from mcp_server.order_version import ORDER_VERSIONS
from mcp_server.server_main import mcp


def _args(key: str, quantity: int = 10) -> dict:
    return {
        "order_detail": [
            {"partId": 1, "quantity": quantity, "unitPrice": 99.9},
        ],
        "idempotency_key": key,
        "order_number": f"PO-TEST-{key[:12]}",
        "status": 1,
    }


def _fake_post(calls: list, failures: list[int] | None = None):
    async def post(self, url, json=None, **kwargs):
        calls.append(json)
        await asyncio.sleep(0.02)  # 放大并发交错窗口
        if failures:
            failures.pop()
            return httpx.Response(
                500,
                json={"message": "simulated ERP failure"},
                request=httpx.Request("POST", url),
            )
        order_id = 10_000 + len(calls)
        return httpx.Response(
            200,
            json={
                "code": 200,
                "data": {"id": order_id, "orderNumber": json["orderNumber"]},
            },
            request=httpx.Request("POST", url),
        )

    return post


async def test_concurrent_same_key():
    key = uuid.uuid4().hex
    calls: list = []
    with patch("httpx.AsyncClient.post", new=_fake_post(calls)):
        async with Client(mcp) as client:
            results = await asyncio.gather(*[
                client.call_tool("order_create", _args(key)) for _ in range(10)
            ])
    assert len(calls) == 1, f"同键并发应只创建一次，实际 POST={len(calls)}"
    payloads = [r.data for r in results]
    order_ids = {p["id"] for p in payloads}
    assert len(order_ids) == 1, payloads
    assert sum(p.get("idempotentReplay") is True for p in payloads) == 9
    assert ORDER_VERSIONS.version(payloads[0]["id"]) == 1
    print("[OK] 同键 10 并发只创建一次")


async def test_replay_does_not_reset_version():
    key = uuid.uuid4().hex
    calls: list = []
    with patch("httpx.AsyncClient.post", new=_fake_post(calls)):
        async with Client(mcp) as client:
            first = (await client.call_tool("order_create", _args(key))).data
            ORDER_VERSIONS.set_version(first["id"], 4)  # 模拟之后已更新到版本 4
            replay = (await client.call_tool("order_create", _args(key))).data
    assert replay["id"] == first["id"]
    assert replay["idempotentReplay"] is True
    assert ORDER_VERSIONS.version(first["id"]) == 4
    assert len(calls) == 1
    print("[OK] 重放不重置更新版本")


async def test_different_keys_create_independently():
    calls: list = []
    with patch("httpx.AsyncClient.post", new=_fake_post(calls)):
        async with Client(mcp) as client:
            first = (await client.call_tool(
                "order_create", _args(uuid.uuid4().hex))).data
            second = (await client.call_tool(
                "order_create", _args(uuid.uuid4().hex))).data
    assert first["id"] != second["id"]
    assert len(calls) == 2
    print("[OK] 不同键独立创建")


async def test_same_key_different_payload_conflicts():
    key = uuid.uuid4().hex
    calls: list = []
    with patch("httpx.AsyncClient.post", new=_fake_post(calls)):
        async with Client(mcp) as client:
            await client.call_tool("order_create", _args(key, quantity=10))
            conflict = (await client.call_tool(
                "order_create", _args(key, quantity=20))).data
    assert conflict["code"] == 409
    assert conflict["error"] == "idempotency_key_conflict"
    assert len(calls) == 1
    print("[OK] 同键不同参数返回 409")


async def test_failure_is_retryable():
    key = uuid.uuid4().hex
    calls: list = []
    failures = [1]
    with patch("httpx.AsyncClient.post", new=_fake_post(calls, failures)):
        async with Client(mcp) as client:
            failed = (await client.call_tool("order_create", _args(key))).data
            succeeded = (await client.call_tool("order_create", _args(key))).data
    assert "error" in failed
    assert succeeded["id"] > 0
    assert len(calls) == 2
    print("[OK] 首次失败不缓存，可重试")


async def test_schema_requires_key():
    async with Client(mcp) as client:
        tools = await client.list_tools()
    create = next(t for t in tools if t.name == "order_create")
    assert "idempotency_key" in create.inputSchema.get("required", [])
    print("[OK] 工具 schema 要求幂等键")


async def main():
    await test_concurrent_same_key()
    await test_replay_does_not_reset_version()
    await test_different_keys_create_independently()
    await test_same_key_different_payload_conflicts()
    await test_failure_is_retryable()
    await test_schema_requires_key()
    print("ALL_OK")


if __name__ == "__main__":
    asyncio.run(main())
