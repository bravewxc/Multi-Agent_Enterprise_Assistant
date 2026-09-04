"""
工具错误处理中间件。

wrap_tool_call 捕获所有工具调用异常，转换为 ToolMessage（status="error"），
避免单个工具失败导致整个 Agent 运行崩溃。
"""
from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain.agents.middleware.types import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)


def _tool_call_id(request: ToolCallRequest) -> str | None:
    tc = getattr(request, "tool_call", None)
    if isinstance(tc, dict):
        return tc.get("id")
    return getattr(tc, "id", None)


def _tool_name(request: ToolCallRequest) -> str | None:
    tc = getattr(request, "tool_call", None)
    if isinstance(tc, dict):
        return tc.get("name")
    return getattr(tc, "name", None)


def _build_error_payload(e: Exception, request: ToolCallRequest) -> dict[str, str]:
    from agent.middlewares.redact import redact_secrets

    # P1-4：错误消息可能携带连接串/密钥（pymongo/openai 异常常见），
    # 先脱敏再截断——模型看得到的内容都可能被注入利用
    data: dict[str, str] = {
        "error": redact_secrets(str(e))[:500],
        "error_type": type(e).__name__,
        "status": "error",
    }
    name = _tool_name(request)
    if name:
        data["name"] = name
    return data


class ToolErrorMiddleware(AgentMiddleware):
    """捕获工具调用异常 → ToolMessage，Agent 可自我纠正而不崩溃。"""

    state_schema = AgentState

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        try:
            return handler(request)
        except Exception as e:
            logger.warning(
                "工具调用异常: tool=%s, error=%s: %s",
                _tool_name(request), type(e).__name__, str(e)[:200],
            )
            return ToolMessage(
                content=json.dumps(_build_error_payload(e, request), ensure_ascii=False),
                tool_call_id=_tool_call_id(request),
                status="error",
            )

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        try:
            return await handler(request)
        except Exception as e:
            logger.warning(
                "工具调用异常: tool=%s, error=%s: %s",
                _tool_name(request), type(e).__name__, str(e)[:200],
            )
            return ToolMessage(
                content=json.dumps(_build_error_payload(e, request), ensure_ascii=False),
                tool_call_id=_tool_call_id(request),
                status="error",
            )
