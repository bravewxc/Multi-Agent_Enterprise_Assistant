"""Global sandbox health check and automatic recovery middleware."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from langchain.agents.middleware import AgentMiddleware

from agent.backends.sandbox_proxy import SandboxBackendProxy
from agent.middlewares.user_skills_restore import restore_persisted_skills

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
        await self._recover(runtime)
        return None

    async def _check(self) -> bool:
        try:
            result = await asyncio.to_thread(self._backend.execute, "echo ok")
            return result.exit_code == 0
        except Exception:
            return False

    async def _recover(self, runtime: Any) -> None:
        from agent.backends.global_sandbox_manager import recreate_global_sandbox
        from agent.config import SKILLS_STORE_NAMESPACE

        recovered = await recreate_global_sandbox()
        if recovered is not self._backend:
            self._backend.replace_backend(recovered)

        await asyncio.to_thread(
            self._backend.upload_files,
            [("/AGENTS.md", self._agents_md)],
        )

        # 新沙箱创建时会播种内置技能，但用户安装的持久化技能在 Store 中；
        # 这里立即回灌，避免热替换后要等到下一个 before_agent 才可用。
        store = getattr(runtime, "store", None)
        if store is None:
            logger.warning(
                "runtime.store unavailable; persisted skills were not restored "
                "after sandbox recovery"
            )
        else:
            restored = await restore_persisted_skills(
                store, self._backend, SKILLS_STORE_NAMESPACE
            )
            logger.info(
                "Restored %d persisted skill file(s) after sandbox recovery",
                restored,
            )

        logger.info("Global sandbox automatic recovery completed")
