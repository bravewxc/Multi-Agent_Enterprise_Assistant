"""
Async task status API.

This route lets the Vue frontend poll AsyncSubAgent tasks directly from the
local LangGraph / Agent Protocol server. The task id returned by DeepAgents is
the subagent thread id.
"""

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from langgraph_sdk import get_client


router = APIRouter()

ASYNC_AGENT_PROTOCOL_URL = os.environ.get(
    "ASYNC_AGENT_PROTOCOL_URL",
    "http://127.0.0.1:2024",
)

TERMINAL_RUN_STATUSES = {"success", "error", "interrupted", "cancelled", "timeout"}


def _get_attr(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _message_role(message: Any) -> str:
    role = _get_attr(message, "role")
    if role:
        if role == "human":
            return "user"
        if role == "ai":
            return "assistant"
        return role

    message_type = _get_attr(message, "type") or type(message).__name__
    message_type = str(message_type).lower()
    if "human" in message_type:
        return "user"
    if "tool" in message_type:
        return "tool"
    return "assistant"


def _message_content(message: Any) -> str:
    content = _get_attr(message, "content", "")
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
                elif "text" in item:
                    parts.append(str(item["text"]))
                elif "content" in item:
                    parts.append(str(item["content"]))
            else:
                parts.append(str(item))
        return "".join(parts)
    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or content)
    return str(content) if content else ""


def _extract_final_text(values: Any) -> str:
    if not isinstance(values, dict):
        return ""

    messages = values.get("messages") or []
    if not isinstance(messages, list):
        return ""

    for message in reversed(messages):
        if _message_role(message) == "assistant":
            text = _message_content(message).strip()
            if text:
                return text
    return ""


def _has_pending_interrupt(state: Any) -> bool:
    """thread state 是否挂着待审批的 HITL 中断。

    注意：本版本 langgraph-api（0.7.90）在图挂起等待审批时 run.status
    仍是 "success"，真正的中断标志只在 state 的 tasks[].interrupts 里。
    """
    return bool(_extract_interrupt_info_raw(state))


def _extract_interrupt_info_raw(state: Any) -> str:
    """同 _extract_interrupt_info，但不依赖 run.status（见上）。"""
    tasks = _get_attr(state, "tasks", []) or []
    for task in tasks:
        interrupts = _get_attr(task, "interrupts", []) or []
        for interrupt in interrupts:
            value = _get_attr(interrupt, "value", {}) or {}
            if not isinstance(value, dict):
                continue
            if "action_requests" not in value:
                continue

            parts = ["任务正在等待人工审批。待审批操作："]
            for req in value.get("action_requests", []):
                tool = req.get("name", "unknown")
                args = req.get("args") or {}
                parts.append(f"- 工具 `{tool}`")
                if tool == "replenish_submit":
                    plan = args.get("replenishment_plan") or []
                    total = sum(
                        float(i.get("estimatedAmount") or 0) for i in plan
                        if isinstance(i, dict)
                    )
                    parts.append(
                        f"  补货清单共 {len(plan)} 项，预计总额 ¥{round(total, 2)}。"
                        f"回复批准（approve）或拒绝（reject）以继续。"
                    )
                    top = [
                        f"{i.get('partName', '?')}×{i.get('suggestQuantity', '?')}"
                        for i in plan[:5] if isinstance(i, dict)
                    ]
                    if top:
                        parts.append(f"  前 5 项：{'、'.join(top)}")
                else:
                    args_str = str(args)
                    parts.append(f"  参数：{args_str[:200]}")
            return "\n".join(parts)
    return ""


def _extract_error(run: Any, state: Any) -> str | None:
    metadata = _get_attr(run, "metadata", {}) or {}
    if isinstance(metadata, dict):
        for key in ("error", "exception", "message"):
            if metadata.get(key):
                return str(metadata[key])

    tasks = _get_attr(state, "tasks", []) or []
    for task in tasks:
        error = _get_attr(task, "error")
        if error:
            return str(error)
    return None


@router.get("/async-tasks/{task_id}")
async def get_async_task_status(task_id: str):
    """
    Return the latest known status and final assistant text for an AsyncSubAgent task.
    """
    client = get_client(url=ASYNC_AGENT_PROTOCOL_URL)

    try:
        runs = await client.runs.list(task_id, limit=10)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to query async task runs from Agent Protocol server: {exc}",
        ) from exc

    if not runs:
        return {
            "task_id": task_id,
            "status": "pending",
            "done": False,
            "content": "",
            "error": None,
        }

    latest_run = runs[0]
    status = str(_get_attr(latest_run, "status", "unknown"))

    state = None
    content = ""
    try:
        state = await client.threads.get_state(task_id)
        content = _extract_final_text(_get_attr(state, "values", {}))
    except Exception:
        # The run status is still useful while the state endpoint is unavailable
        # or the task is still materializing.
        state = None

    # HITL 审批中断：本版本 langgraph-api 在图挂起等待审批时 run.status
    # 仍是 success，须以 thread state 的 tasks[].interrupts 为准。
    # 检测到待审批中断时：状态改写为 interrupted、content 附加审批信息
    if state is not None and _has_pending_interrupt(state):
        interrupt_info = _extract_interrupt_info_raw(state)
        if interrupt_info:
            status = "interrupted"
            content = interrupt_info if not content else f"{content}\n\n{interrupt_info}"

    error = _extract_error(latest_run, state) if status == "error" else None
    done = status in TERMINAL_RUN_STATUSES

    return {
        "task_id": task_id,
        "status": status,
        "done": done,
        "content": content,
        "error": error,
        "run_id": _get_attr(latest_run, "run_id"),
        "updated_at": str(_get_attr(latest_run, "updated_at", "")),
    }
