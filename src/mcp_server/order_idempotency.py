"""创建订单的幂等登记表：防止同一请求并发/重试时重复下单。

与订单更新使用版本 CAS 不同，创建时没有旧版本可比较，要用幂等键：
同一个 `idempotency_key` 只允许一个真正调用 ERP，后续相同请求直接返回
首次创建成功的结果。

服务端在幂等键级锁内完成：查询首次结果 → 调 ERP 创建 → 保存结果。
并发请求会等待首个请求结束；首个请求失败时不保存结果，允许重试。

边界：登记表在 MCP 进程内存里，重启或多实例时不能去重；ERP 超时等
"结果未知"的失败也无法判断是否已经创建。跨重启/实例和超时兜底，需要
Java ERP / 数据库对幂等键建立唯一约束，并支持按幂等键查询已有订单。
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass(frozen=True)
class CreateOrderRecord:
    """一次成功创建的请求指纹与返回结果。"""

    fingerprint: str
    result: dict


class OrderCreateRegistry:
    """按 idempotency_key 保存首次创建结果，并串行化同键创建。"""

    def __init__(self) -> None:
        self._records: dict[str, CreateOrderRecord] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def get(self, key: str) -> CreateOrderRecord | None:
        return self._records.get(key)

    def put(self, key: str, fingerprint: str, result: dict) -> None:
        self._records[key] = CreateOrderRecord(fingerprint, result)

    @asynccontextmanager
    async def hold(self, key: str) -> AsyncIterator[None]:
        """同一幂等键的创建互斥，不同键可并行。"""
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            yield


# 单例：MCP 服务进程内共享
ORDER_CREATES = OrderCreateRegistry()
