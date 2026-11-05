"""订单版本表（CAS）离线单测：不连 ERP、不起 MCP 服务。

验证点：
1. 未登记的订单版本为 0；写入成功后版本单调递增
2. 期望版本等于当前版本才放行，旧版本凭据立即失效
3. 并发场景：10 个调用者拿同一个旧版本同时提交，只有 1 个成功，
   其余全部拿到冲突（不会出现丢失更新）
4. 一次写入失败不推进版本，原版本凭据仍可安全重试

运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_order_version
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR / "src"))

from mcp_server.order_version import OrderVersionRegistry


async def test_version_basics():
    registry = OrderVersionRegistry()
    assert registry.version(100) == 0

    registry.set_version(100, 1)          # order_create 成功后登记为 1
    assert registry.version(100) == 1
    assert registry.bump(100) == 2        # 一次成功更新后 +1
    print("[OK] 版本登记与递增")


async def test_conflict_after_write():
    registry = OrderVersionRegistry()
    registry.set_version(7, 3)

    # 第一个调用者拿版本 3 提交，成功
    async with registry.hold(7):
        assert registry.version(7) == 3
        registry.bump(7)
    assert registry.version(7) == 4

    # 第二个调用者还拿着版本 3，必须冲突
    async with registry.hold(7):
        assert registry.version(7) != 3
    print("[OK] 旧版本凭据失效")


async def test_failed_write_keeps_version():
    registry = OrderVersionRegistry()
    registry.set_version(8, 2)

    async with registry.hold(8):
        assert registry.version(8) == 2
        # 模拟 ERP 写入失败：不 bump，版本保持不变
    assert registry.version(8) == 2

    async with registry.hold(8):
        assert registry.version(8) == 2   # 原凭据仍可安全重试
    print("[OK] 写失败不推进版本")


async def test_concurrent_only_one_wins():
    registry = OrderVersionRegistry()
    registry.set_version(9, 5)
    results: list[str] = []

    async def updater():
        async with registry.hold(9):
            if registry.version(9) != 5:
                results.append("conflict")
                return
            await asyncio.sleep(0.01)   # 模拟 ERP 写入耗时，放大交错窗口
            registry.bump(9)
            results.append("ok")

    await asyncio.gather(*(updater() for _ in range(10)))
    assert results.count("ok") == 1, results
    assert results.count("conflict") == 9, results
    assert registry.version(9) == 6, registry.version(9)
    print("[OK] 10 并发只有 1 个成功")


async def test_different_orders_not_blocked():
    registry = OrderVersionRegistry()
    registry.set_version(1, 1)
    registry.set_version(2, 1)

    async def updater(order_id: int):
        async with registry.hold(order_id):
            await asyncio.sleep(0.05)
            registry.bump(order_id)

    loop = asyncio.get_running_loop()
    t0 = loop.time()
    await asyncio.gather(updater(1), updater(2))
    assert registry.version(1) == 2 and registry.version(2) == 2
    # 两单并行，总耗时接近 0.05s 而不是 0.1s
    assert loop.time() - t0 < 0.09
    print("[OK] 不同订单互不阻塞")


async def main():
    await test_version_basics()
    await test_conflict_after_write()
    await test_failed_write_keeps_version()
    await test_concurrent_only_one_wins()
    await test_different_orders_not_blocked()
    print("ALL_OK")


if __name__ == "__main__":
    asyncio.run(main())
