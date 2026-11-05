"""订单版本表：MCP 服务端的乐观锁（CAS）基础设施。

要解决的问题：`order_update` 是"读旧数据 → 人工审批 → 整段写回"。
两个用户先后改同一张订单时，后提交的会覆盖先提交的（典型的丢失更新）。

做法：给每张订单维护一个单调递增的版本号。更新时客户端必须带上
`expected_version`，服务端在同一把订单级锁内完成三件事：

    比较版本 → 写 ERP → 版本加一

版本对不上就直接返回 409，不写 ERP。这就是 CAS（compare-and-swap）：
只有"你看到的那个版本还是当前版本"时，写入才允许发生。

边界（必须如实理解）：
1. 版本表在 MCP 进程内存里，只在单个 MCP 实例内有效。多实例部署时各算各的，
   需要换成 Mongo / Redis 的原子计数器；
2. 进程重启后版本归零，重启前拿到的版本凭据会失效（通常只会产生误报冲突，
   但也存在"重启前的 0 版本 + 重启后写入"这种极小窗口）；
3. 绕过 MCP、直接改 ERP 或数据库的写入不会让版本递增，检测不到；
4. 端到端原子性最终取决于 Java ERP：如果后端有 version 字段或 If-Match，
   应把 expected_version 透传过去，让数据库做最终裁决。
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


class OrderVersionRegistry:
    """按 order_id 维护版本号，并用订单级锁串行化"比较 + 写入"。"""

    def __init__(self) -> None:
        self._versions: dict[int, int] = {}
        self._locks: dict[int, asyncio.Lock] = {}

    def version(self, order_id: int) -> int:
        """当前版本；从未登记过的订单视为版本 0。"""
        return self._versions.get(order_id, 0)

    def set_version(self, order_id: int, version: int) -> None:
        self._versions[order_id] = version

    def bump(self, order_id: int) -> int:
        """版本加一并返回新版本（调用方必须已持有该订单的锁）。"""
        next_version = self._versions.get(order_id, 0) + 1
        self._versions[order_id] = next_version
        return next_version

    @asynccontextmanager
    async def hold(self, order_id: int) -> AsyncIterator[None]:
        """持有订单级锁：同一订单的"比较 + 写入"不会交错，不同订单互不影响。"""
        lock = self._locks.setdefault(order_id, asyncio.Lock())
        async with lock:
            yield


# 单例：MCP 服务进程内共享
ORDER_VERSIONS = OrderVersionRegistry()
