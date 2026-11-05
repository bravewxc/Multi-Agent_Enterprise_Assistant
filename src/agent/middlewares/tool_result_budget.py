"""工具结果预算中间件：大结果落沙箱文件，上下文只保留摘要与分页指引。

背景：不同工具（MCP 查询、网页抓取、脚本输出）各自返回，缺少统一的大小
上限。单次结果过大时会把上下文窗口一次撑爆，且压缩后原始信息不可再取。

策略：
- 结果字符数 / 行数超过阈值 → 写入
  /analysis/temp/tool_results/{thread_id}/{tool_call_id}.txt
- ToolMessage 只保留：工具名、原大小、文件路径、前 N 行预览、分页读取命令
- 落盘失败时返回原结果，不阻断工具调用
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.types import Command

logger = logging.getLogger(__name__)

# 这些工具的结果是“控制/短确认/再次读取”，不参与落盘，避免读大文件时
# 再生成一个更大的副本，或把短确认写成文件。
_SKIP_TOOLS = {
    "read_file",
    "write_file",
    "edit_file",
    "ls",
    "glob",
    "grep",
    "compact_conversation",
}

# 摘要里保留的预览上限，避免“落盘摘要”本身又变成大结果
_PREVIEW_LINES = 20
_PREVIEW_CHARS = 2000


def _tool_name(request: ToolCallRequest) -> str:
    tc = getattr(request, "tool_call", None)
    if isinstance(tc, dict):
        return str(tc.get("name") or "unknown")
    return str(getattr(tc, "name", None) or "unknown")


def _tool_call_id(request: ToolCallRequest) -> str:
    tc = getattr(request, "tool_call", None)
    if isinstance(tc, dict):
        return str(tc.get("id") or "unknown")
    return str(getattr(tc, "id", None) or "unknown")


def _thread_id(request: ToolCallRequest) -> str:
    """取当前 thread_id；缺失时退回 unknown（仍能落盘，只是目录不隔离）。"""
    try:
        tid = request.runtime.config["configurable"]["thread_id"]
        if tid:
            return str(tid)
    except Exception:
        pass
    return "unknown"


def _safe_path_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value)[:80] or "unknown"


def _content_to_text(content: Any) -> str:
    """把 ToolMessage.content（str 或 content blocks）转成可落盘文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False, default=str)


class ToolResultBudgetMiddleware(AgentMiddleware):
    """把超大工具结果落盘，并返回可继续分页读取的摘要。"""

    def __init__(
        self,
        *,
        backend: Any = None,
        backend_provider: Callable[[], Any] | None = None,
        max_chars: int = 20_000,
        max_lines: int = 500,
        temp_dir: str = "/analysis/temp/tool_results",
    ) -> None:
        super().__init__()
        self.backend = backend
        self.backend_provider = backend_provider
        self.max_chars = max_chars
        self.max_lines = max_lines
        self.temp_dir = temp_dir.rstrip("/")

    async def _resolve_backend(self) -> Any:
        if self.backend is not None:
            return self.backend
        if self.backend_provider is None:
            raise RuntimeError("ToolResultBudgetMiddleware has no backend")
        return await asyncio.to_thread(self.backend_provider)

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[Any]],
    ) -> Any:
        result = await handler(request)

        if isinstance(result, Command):
            return result
        if not isinstance(result, ToolMessage):
            return result
        if getattr(result, "status", None) == "error":
            return result

        name = _tool_name(request)
        if name in _SKIP_TOOLS:
            return result

        text = _content_to_text(result.content)
        if not text:
            return result

        lines = text.count("\n") + 1
        if len(text) <= self.max_chars and lines <= self.max_lines:
            return result

        path = (
            f"{self.temp_dir}/{_safe_path_part(_thread_id(request))}/"
            f"{_safe_path_part(_tool_call_id(request))}.txt"
        )
        try:
            backend = await self._resolve_backend()
            await asyncio.to_thread(
                backend.upload_files,
                [(path, text.encode("utf-8"))],
            )
        except Exception:
            logger.warning(
                "Failed to offload oversized tool result for %s; returning original",
                name,
                exc_info=True,
            )
            return result

        preview = "\n".join(text.splitlines()[:_PREVIEW_LINES])[:_PREVIEW_CHARS]
        summary = (
            "【工具结果过大，已落盘】\n"
            f"工具: {name}\n"
            f"原始大小: {len(text)} 字符 / {lines} 行\n"
            f"文件路径: {path}\n"
            f"预览（前 {_PREVIEW_LINES} 行）:\n{preview}\n\n"
            "读取方式: 使用 execute(\"sed -n '1,200p' "
            f"{path}\") 分页查看；不要把整份文件一次性读回上下文。"
        )
        logger.info(
            "Offloaded oversized tool result: tool=%s chars=%d lines=%d path=%s",
            name,
            len(text),
            lines,
            path,
        )
        return ToolMessage(
            content=summary,
            tool_call_id=result.tool_call_id,
            name=result.name,
            status=result.status or "success",
        )
