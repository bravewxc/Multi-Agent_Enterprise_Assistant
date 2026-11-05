"""主图实例缓存：按用户复用已编译的 agent graph，降低每请求建图成本。

约束：
- graph 捕获的是 SandboxBackendProxy，沙箱重建时 proxy 内部热替换，
  graph 引用仍有效，因此缓存 graph 不会绑定某个具体沙箱实例；
- 配置/技能变更不热更新 graph，用 TTL 控制最终一致性；
- 缓存键是 user_id（graph 内注入的用户上下文是固定的）；
- 有界 LRU + TTL，避免用户增多后内存无界增长。
"""
from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Any


class AgentGraphCache:
    """按 key 缓存 agent graph，支持 TTL、LRU 淘汰和显式失效。"""

    def __init__(self, *, ttl_seconds: float = 600.0, max_entries: int = 100) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get_or_create(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
    ) -> Any:
        async with self._lock:
            now = time.monotonic()
            entry = self._entries.get(key)
            if entry is not None:
                created_at, graph = entry
                if now - created_at <= self.ttl_seconds:
                    self._entries.move_to_end(key)
                    self._hits += 1
                    return graph
                self._entries.pop(key, None)

            self._misses += 1
            graph = await factory()
            self._entries[key] = (now, graph)
            self._entries.move_to_end(key)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
            return graph

    async def invalidate(self, key: str | None = None) -> None:
        async with self._lock:
            if key is None:
                self._entries.clear()
            else:
                self._entries.pop(key, None)

    def stats(self) -> dict[str, int]:
        return {
            "entries": len(self._entries),
            "hits": self._hits,
            "misses": self._misses,
        }
