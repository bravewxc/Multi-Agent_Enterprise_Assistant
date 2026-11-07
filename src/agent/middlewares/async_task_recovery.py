"""异步任务恢复登记：监听框架 start/check_async_task 的工具结果。

框架仍负责创建 thread/run；本中间件只把任务标识写入 MongoDB，
不改造 start_async_task 的返回协议。若恢复后 run_id 已变化，
check_async_task 的旧 run 查询失败时，用登记表中的新 run_id 兜底。
"""
from __future__ import annotations

import json
import logging
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph_sdk import get_client

from agent.recovery_store import recovery_store

logger = logging.getLogger(__name__)

ASYNC_GRAPH_IDS = {
    "procurement-analyst": "procurement_analyst_async",
    "procurement-replenish": "procurement_replenish_async",
}
ASYNC_AGENT_PROTOCOL_URL = os.environ.get(
    "ASYNC_AGENT_PROTOCOL_URL", "http://127.0.0.1:2024"
)


def _tool_name(request: Any) -> str:
    tool_call = getattr(request, "tool_call", None)
    if isinstance(tool_call, dict):
        return str(tool_call.get("name") or "")
    return str(getattr(tool_call, "name", "") or "")


def _tool_args(request: Any) -> dict:
    tool_call = getattr(request, "tool_call", None)
    if isinstance(tool_call, dict):
        return tool_call.get("args") or {}
    return getattr(tool_call, "args", {}) or {}


def _tasks_from_result(result: Any) -> dict[str, dict]:
    if not isinstance(result, Command):
        return {}
    update = result.update if isinstance(result.update, dict) else {}
    return update.get("async_tasks") or {}


class AsyncTaskRecoveryMiddleware(AgentMiddleware):
    """把异步任务标识持久化，并兼容恢复后的 check_async_task。"""

    async def awrap_tool_call(
        self,
        request: Any,
        handler: Callable[[Any], Awaitable[Any]],
    ) -> Any:
        result = await handler(request)
        name = _tool_name(request)
        if name not in {"start_async_task", "check_async_task"}:
            return result

        try:
            if name == "start_async_task":
                args = _tool_args(request)
                description = str(args.get("description") or "")
                for task in _tasks_from_result(result).values():
                    graph_id = ASYNC_GRAPH_IDS.get(str(task.get("agent_name")))
                    if graph_id:
                        await recovery_store.register_async(
                            task, graph_id=graph_id, description=description
                        )
            else:
                for task in _tasks_from_result(result).values():
                    await recovery_store.update_async(task)

                # 恢复后旧 run_id 已失效：用 Mongo 中登记的新 run_id 再查一次
                if isinstance(result, ToolMessage) and "Failed to get run status" in str(result.content):
                    return await self._check_with_recovered_run(request, result)
        except Exception:
            # 恢复登记是旁路能力，不能影响正常工具调用
            logger.warning("异步任务恢复登记失败 tool=%s", name, exc_info=True)
        return result

    async def _check_with_recovered_run(self, request: Any, original: ToolMessage) -> Any:
        args = _tool_args(request)
        task_id = str(args.get("task_id") or "").strip()
        runtime = getattr(request, "runtime", None)
        state = getattr(runtime, "state", {}) or {}
        tracked = (state.get("async_tasks") or {}).get(task_id)
        record = await recovery_store.get("async", task_id)
        run_id = (record or {}).get("run_id") or (tracked or {}).get("run_id")
        if not task_id or not tracked or not run_id:
            return original

        client = get_client(url=ASYNC_AGENT_PROTOCOL_URL)
        try:
            run = await client.runs.get(thread_id=task_id, run_id=run_id)
        except Exception:
            return original

        status = str(run.get("status", "unknown"))
        check_result: dict[str, Any] = {"status": status, "thread_id": task_id}
        if status == "success":
            state_value = await client.threads.get_state(task_id)
            values = state_value.get("values", {}) if isinstance(state_value, dict) else {}
            messages = values.get("messages") or []
            if messages:
                last = messages[-1]
                check_result["result"] = (
                    last.get("content", "") if isinstance(last, dict) else str(last)
                )
            else:
                check_result["result"] = "(completed with no output messages)"
        elif status == "error":
            check_result["error"] = str(run.get("error") or "异步任务执行失败")

        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        updated_task = {
            **tracked,
            "run_id": run_id,
            "status": status,
            "last_checked_at": now,
            "last_updated_at": now if tracked.get("status") != status else tracked.get("last_updated_at", now),
        }
        await recovery_store.update_async(updated_task)
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        json.dumps(check_result, ensure_ascii=False),
                        tool_call_id=original.tool_call_id,
                    )
                ],
                "async_tasks": {task_id: updated_task},
            }
        )
