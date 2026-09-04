"""Global sandbox health check and automatic recovery middleware."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from langchain.agents.middleware import AgentMiddleware

from agent.backends.sandbox_proxy import SandboxBackendProxy

logger = logging.getLogger(__name__)


class SandboxHealthMiddleware(AgentMiddleware):
    """Ping the shared global sandbox before each agent step.

    The constructor keeps the old ``user_id`` parameter for compatibility with
    the existing main-agent call site, but recovery is global: if the shared
    sandbox is unavailable, a new global sandbox is created and the proxy is
    hot-swapped.
    """

    def __init__(
        self,
        *,
        sandbox_backend: SandboxBackendProxy,
        user_id: str,
        agents_md_content: bytes,
    ) -> None:
        super().__init__()
        self._backend = sandbox_backend
        self._user_id = user_id
        self._agents_md = agents_md_content

    def before_agent(self, state: dict[str, Any], runtime: Any) -> None:
        return None

    async def abefore_agent(self, state: dict[str, Any], runtime: Any) -> None:
        if await self._check():
            return None

        logger.warning(
            "Global sandbox is unhealthy; triggering automatic recovery. user_id=%s",
            self._user_id,
        )
        await self._recover()
        return None

    async def _check(self) -> bool:
        try:
            result = await asyncio.to_thread(self._backend.execute, "echo ok")
            return result.exit_code == 0
        except Exception:
            return False

    async def _recover(self) -> None:
        from agent.backends.global_sandbox_manager import recreate_global_sandbox

        recovered = await recreate_global_sandbox()
        if recovered is not self._backend:
            self._backend.replace_backend(recovered)

        await asyncio.to_thread(
            self._backend.upload_files,
            [("/AGENTS.md", self._agents_md)],
        )
        logger.info("Global sandbox automatic recovery completed")
