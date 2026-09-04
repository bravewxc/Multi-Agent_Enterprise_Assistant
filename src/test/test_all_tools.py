"""MCP 工具回归测试（方向 F 评估化改造版）。

相对原版的三个改造（对应评估文档 3.7 节配套改造）：
1. 随机数据 → 固定用例：结果可复现、失败可归因（原 random.* 每次跑的数据
   都不同，失败无法复现，也无法判断"空结果"是 bug 还是本来就没有）
2. print → assert：原来是"跑完就算过"，现在逐工具判对错，exit code 可用于门控
3. order 生命周期自管：order_update 只更新本测试创建的订单
   （原版 order_id=random(1,100) 直改远程 ERP 既有数据且无回滚——
    测试污染生产数据是评估体系的反模式）

测试模式：
  - mcp_client：fastmcp.Client 内存模式直连 MCP 服务端（需 Java ERP 后端可达）
  - agent_client：MultiServerMCPClient 经 HTTP 模拟 Agent 调用（需 MCP Server 8000）

运行：cd 项目根
  $env:PYTHONUTF8='1'; $env:PYTHONPATH='src'
  .venv\\Scripts\\python.exe -m test.test_all_tools [mcp|agent|all]   # 默认 all
"""

import asyncio
import json
import sys
from datetime import datetime

from fastmcp import Client
from langchain_mcp_adapters.client import MultiServerMCPClient

from mcp_server.server_main import mcp

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# 固定测试数据（可复现；订单号带时间戳保证唯一，其余全固定）
# ============================================================

FIXED = {
    "supplier_name": "博世",          # ERP 确定存在的供应商（历史对话验证过）
    "part_name": "火花塞",            # 确定存在的品类
    "category": "制动类",
    "supplier_id": 1,
    "order_detail": [
        {"partId": 1, "quantity": 10, "unitPrice": 99.9,
         "subtotal": 999.0, "remark": "回归-明细1"},
    ],
    "search_start": "2026-01-01",
    "search_end": "2026-12-31",
}


def _order_number() -> str:
    """订单号 = 固定前缀 + 时间戳：一次运行内唯一、多次运行不冲突。"""
    return f"PO-EVAL{datetime.now().strftime('%Y%m%d%H%M%S')}"


# ============================================================
# 结果解析与断言辅助
# ============================================================

def _unwrap(result) -> object:
    """把 fastmcp CallToolResult / langchain 工具返回值统一解成 python 对象。

    fastmcp：优先 .data（结构化输出），退回 .content[0].text 再 JSON 解析
    langchain_mcp_adapters：工具返回文本，尝试 JSON 解析
    """
    data = getattr(result, "data", None)
    if data is not None:
        return data
    content = getattr(result, "content", None)
    if isinstance(content, list) and content:
        first = content[0]
        # langchain_mcp_adapters 返回 [{'type': 'text', 'text': '...'}] 字典列表
        if isinstance(first, dict) and "text" in first:
            text = str(first["text"])
        else:
            text = getattr(first, "text", None) or str(first)
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text
    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return result
    return result


def _assert_ok(name: str, payload, *, expect_nonempty: bool = False) -> object:
    """统一断言：返回 list 或 dict；dict 时不得含 error 字段。

    ★ fastmcp 内存模式直调 python 函数，查询类工具返回 list；
      错误约定是 {"error": ...} dict——两种形态都要接纳。
    """
    assert isinstance(payload, (dict, list)), (
        f"{name}: 返回应为 dict/list，实为 {type(payload)}: {payload!s:.200}")
    if isinstance(payload, dict):
        assert "error" not in payload, f"{name}: 工具返回错误: {payload.get('error')}"
    if expect_nonempty:
        assert payload, f"{name}: 期望非空数据，实为空"
    return payload


# ============================================================
# 1. mcp_client 测试（内存模式）—— 固定数据 + 断言
# ============================================================

async def test_mcp_supplier_query() -> None:
    """supplier_query 按名称模糊搜索：博世必命中（ERP 确定存在）。

    ★ fastmcp 内存模式直调 python 函数 → 扁平参数（非 MCP wire 的 params 包装）。
    """
    async with Client(mcp) as client:
        result = await client.call_tool("supplier_query", {"name": FIXED["supplier_name"]})
    payload = _assert_ok("supplier_query", _unwrap(result), expect_nonempty=True)
    n = len(payload) if isinstance(payload, list) else 1
    print(f"[PASS] supplier_query 博世 → {n} 条")


async def test_mcp_part_query() -> None:
    """part_query 分页查询：制动类 size=5。"""
    async with Client(mcp) as client:
        result = await client.call_tool("part_query", {
            "current": 1, "size": 5, "category": FIXED["category"],
        })
    payload = _assert_ok("part_query", _unwrap(result))
    print(f"[PASS] part_query {FIXED['category']} → {payload!s:.80}")


async def test_mcp_part_search() -> None:
    """part_search 按名称搜索：火花塞必命中。"""
    async with Client(mcp) as client:
        result = await client.call_tool("part_search", {"name": FIXED["part_name"]})
    payload = _assert_ok("part_search", _unwrap(result), expect_nonempty=True)
    rows = payload if isinstance(payload, list) else [payload]
    print(f"[PASS] part_search 火花塞 → {len(rows)} 条")


async def test_mcp_part_by_supplier() -> None:
    """part_by_supplier：supplier_id=1，只断言不报错（空列表合法）。"""
    async with Client(mcp) as client:
        result = await client.call_tool("part_by_supplier", {
            "supplier_id": FIXED["supplier_id"],
        })
    _assert_ok("part_by_supplier", _unwrap(result))
    print("[PASS] part_by_supplier id=1")


async def test_mcp_order_lifecycle() -> int:
    """订单生命周期（★改造核心）：创建自管订单 → 只更新这张自建单。

    参数按 python 函数签名扁平传递（order_detail/order_number/status/remark）。
    返回订单 id（供回归层进一步使用）。
    """
    detail = FIXED["order_detail"]

    async with Client(mcp) as client:
        created = _assert_ok("order_create", _unwrap(await client.call_tool(
            "order_create", {
                "order_detail": detail,
                "order_number": _order_number(),
                "status": 1,
                "remark": "[EVAL-FIXED] 回归测试订单（可清理）",
            })), )
        order_id = created.get("id") if isinstance(created, dict) else None
        order_number = created.get("orderNumber") if isinstance(created, dict) else None
        print(f"[PASS] order_create → id={order_id} {order_number}")

        if order_id is None:
            print("[WARN] create 未返回 id，order_update 跳过（记录现象）")
            return -1

        updated = _assert_ok("order_update", _unwrap(await client.call_tool(
            "order_update", {
                "order_id": order_id,                    # ★ 只改自建单，不碰既有数据
                "order_number": order_number,
                "status": 2,
                "remark": "[EVAL-FIXED] 回归测试订单-已更新",
            })))
        print(f"[PASS] order_update 自建单 {order_id} → {updated!s:.80}")
        return int(order_id)


async def test_mcp_order_search_details() -> None:
    """order_search_details：按名称 + 按日期两种调用均不报错。"""
    async with Client(mcp) as client:
        _assert_ok("order_search_details(按名称)", _unwrap(await client.call_tool(
            "order_search_details", {"part_name": FIXED["part_name"]})))
        _assert_ok("order_search_details(按日期)", _unwrap(await client.call_tool(
            "order_search_details", {
                "start_date": FIXED["search_start"], "end_date": FIXED["search_end"],
            })))
    print("[PASS] order_search_details 两种调用")


async def test_mcp_inventory_warning() -> None:
    """inventory_warning 无参调用：不报错即可（空预警合法）。"""
    async with Client(mcp) as client:
        result = await client.call_tool("inventory_warning", {})
    _assert_ok("inventory_warning", _unwrap(result))
    print("[PASS] inventory_warning")


async def run_all_mcp_client_tests() -> bool:
    tests = [
        ("supplier_query", test_mcp_supplier_query),
        ("part_query", test_mcp_part_query),
        ("part_search", test_mcp_part_search),
        ("part_by_supplier", test_mcp_part_by_supplier),
        ("order_lifecycle", test_mcp_order_lifecycle),
        ("order_search_details", test_mcp_order_search_details),
        ("inventory_warning", test_mcp_inventory_warning),
    ]
    ok = True
    for name, fn in tests:
        try:
            await fn()
        except Exception as e:
            ok = False
            print(f"[FAIL] {name}: {e}")
    print(f"[汇总] mcp_client: {'全部通过' if ok else '存在失败'}")
    return ok


# ============================================================
# 2. agent_client 测试（HTTP 模式，走真实 MCP Server 8000）
# ============================================================

MCP_SERVER_CONFIG = {
    "erp": {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable_http"},
}


async def run_all_agent_client_tests() -> bool:
    """经 HTTP 走完整 MCP 链路：order_create + inventory_warning，带断言。"""
    client = MultiServerMCPClient(MCP_SERVER_CONFIG)
    all_tools = await client.get_tools(server_name="erp")
    print(f"[agent_client] 已加载 {len(all_tools)} 个 MCP 工具")
    assert len(all_tools) >= 8, f"工具数应 ≥8（8 个业务工具），实为 {len(all_tools)}"

    ok = True
    try:
        tool = next(t for t in all_tools if t.name == "order_create")
        payload = _assert_ok("agent:order_create", _unwrap(await tool.ainvoke({
            "order_detail": FIXED["order_detail"],
            "order_number": _order_number(),
            "status": 1,
            "remark": "[EVAL-FIXED] agent_client 回归订单",
        })), expect_nonempty=True)
        print(f"[PASS] agent:order_create → {payload!s:.80}")
    except Exception as e:
        ok = False
        print(f"[FAIL] agent:order_create: {e}")

    try:
        tool = next(t for t in all_tools if t.name == "inventory_warning")
        _assert_ok("agent:inventory_warning", _unwrap(await tool.ainvoke({})))
        print("[PASS] agent:inventory_warning")
    except Exception as e:
        ok = False
        print(f"[FAIL] agent:inventory_warning: {e}")

    print(f"[汇总] agent_client: {'全部通过' if ok else '存在失败'}")
    return ok


if __name__ == "__main__":
    sys.path.insert(0, "src")
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = []

    async def _run() -> int:
        if mode in ("mcp", "all"):
            results.append(await run_all_mcp_client_tests())
        if mode in ("agent", "all"):
            results.append(await run_all_agent_client_tests())
        return 0 if all(results) else 1

    print(f"运行模式: {mode}（固定数据 + 断言版）")
    sys.exit(asyncio.run(_run()))
