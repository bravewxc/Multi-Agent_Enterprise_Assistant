"""沙箱生命周期中间件：清理过期临时文件、执行临时目录配额检查。

背景：全局沙箱 TTL 23h，但 `/analysis/temp/` 下的工具落盘、脚本输入输出、
中间 JSON 会持续累积；没有配额和清理策略时，2Gi 资源会被历史临时文件占满。

策略（只在主 Agent 的 before_agent 执行，默认 10 分钟节流一次）：
1. 删除 `/analysis/temp/` 下超过 N 小时未修改的文件；
2. 统计 temp 目录大小；超过配额时按 mtime 删除最旧的一批文件（最多 3 批）；
3. 清理空目录，记录清理前后大小。

只清理 temp 目录，不动 `/analysis/` 下的报告与审批存档。清理失败只告警，
不阻断 Agent 运行。
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from langchain.agents.middleware import AgentMiddleware

logger = logging.getLogger(__name__)

# 进程级节流：全局沙箱共享，多个请求不需要各自重复扫描
_last_cleanup_at: float = 0.0


class SandboxLifecycleMiddleware(AgentMiddleware):
    """按时间与配额清理沙箱临时目录。"""

    def __init__(
        self,
        *,
        backend: Any,
        temp_dir: str = "/analysis/temp",
        max_temp_mb: int = 200,
        max_age_hours: int = 24,
        min_interval_seconds: int = 600,
        delete_batch: int = 50,
    ) -> None:
        super().__init__()
        self.backend = backend
        self.temp_dir = temp_dir.rstrip("/")
        self.max_temp_kb = max_temp_mb * 1024
        self.max_age_minutes = max_age_hours * 60
        self.min_interval_seconds = min_interval_seconds
        self.delete_batch = delete_batch

    async def abefore_agent(self, state: dict[str, Any], runtime: Any) -> None:
        global _last_cleanup_at

        now = time.monotonic()
        if now - _last_cleanup_at < self.min_interval_seconds:
            return None
        _last_cleanup_at = now

        try:
            await asyncio.to_thread(self._cleanup)
        except Exception:
            logger.warning("Sandbox lifecycle cleanup failed", exc_info=True)
        return None

    def before_agent(self, state: dict[str, Any], runtime: Any) -> None:
        return None

    def _cleanup(self) -> None:
        self._exec(
            f"find {self.temp_dir} -type f -mmin +{self.max_age_minutes} "
            "-delete 2>/dev/null || true"
        )

        before_kb = self._temp_size_kb()
        for _ in range(3):
            if before_kb <= self.max_temp_kb:
                break
            self._delete_oldest_batch()
            before_kb = self._temp_size_kb()

        self._exec(f"find {self.temp_dir} -type d -empty -delete 2>/dev/null || true")
        after_kb = self._temp_size_kb()
        logger.info(
            "Sandbox temp cleanup: before=%dKB after=%dKB quota=%dKB path=%s",
            before_kb,
            after_kb,
            self.max_temp_kb,
            self.temp_dir,
        )
        if after_kb > self.max_temp_kb:
            logger.warning(
                "Sandbox temp still exceeds quota after cleanup: %dKB > %dKB",
                after_kb,
                self.max_temp_kb,
            )

    def _temp_size_kb(self) -> int:
        out = self._exec(f"du -sk {self.temp_dir} 2>/dev/null | cut -f1")
        try:
            return int(out.strip().splitlines()[0])
        except Exception:
            return 0

    def _delete_oldest_batch(self) -> None:
        self._exec(
            f"find {self.temp_dir} -type f -printf '%T@ %p\\n' 2>/dev/null "
            f"| sort -n | head -n {self.delete_batch} | cut -d' ' -f2- "
            "| xargs -r rm -f 2>/dev/null || true"
        )

    def _exec(self, command: str) -> str:
        try:
            result = self.backend.execute(command)
            return getattr(result, "output", "") or ""
        except Exception:
            logger.warning("Sandbox cleanup command failed: %s", command, exc_info=True)
            return ""
