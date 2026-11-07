"""8090 / 2024 进程崩溃后的任务恢复协调器。

恢复原则：
- 主会话：用 input=None 从 MongoDB checkpoint 续跑，不重放用户消息；
- 异步任务：先查 2024 是否仍有 run；仍在运行则不处理，run 丢失时才用
  原 task_id + graph_id 创建恢复 run；
- HITL 中断不自动批准，只把状态标记为 interrupted，等待用户决定。
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from langgraph_sdk import get_client

from agent.recovery_store import recovery_store

logger = logging.getLogger(__name__)

ASYNC_AGENT_PROTOCOL_URL = os.environ.get(
    "ASYNC_AGENT_PROTOCOL_URL", "http://127.0.0.1:2024"
)
RECOVERY_SCAN_INTERVAL = float(os.getenv("RECOVERY_SCAN_INTERVAL", "30"))


def _has_pending_interrupt(state: Any) -> bool:
    tasks = state.get("tasks") if isinstance(state, dict) else getattr(state, "tasks", None)
    for task in tasks or []:
        interrupts = task.get("interrupts") if isinstance(task, dict) else getattr(task, "interrupts", None)
        for interrupt in interrupts or []:
            value = interrupt.get("value") if isinstance(interrupt, dict) else getattr(interrupt, "value", None)
            if isinstance(value, dict) and "action_requests" in value:
                return True
    return False


async def recover_main_runs_once() -> int:
    """扫描并恢复崩溃时仍未结束的主会话，返回本次认领数量。"""
    from api_view.api.chat import guarded_stream_chat_response

    claimed_count = 0
    for record in await recovery_store.pending("main"):
        thread_id = record["thread_id"]
        claimed = await recovery_store.claim("main", thread_id)
        if not claimed:
            continue
        claimed_count += 1
        logger.info("开始恢复主会话 thread=%s attempt=%s", thread_id, claimed.get("attempts"))
        try:
            # 复用正常流式链路保存展示消息和最终状态；旧 SSE 已断开，这里丢弃事件。
            async for _ in guarded_stream_chat_response(
                thread_id=thread_id,
                user_id=record.get("user_id") or "laoxiao",
                recovery=True,
            ):
                pass
        except Exception as exc:
            # 建图等流式 try 块之外的异常也要进入重试，不能卡在 recovering
            await recovery_store.schedule_retry("main", thread_id, str(exc))
    return claimed_count


async def recover_async_task(record: dict[str, Any], *, client: Any = None) -> bool:
    """核对并恢复一个异步任务；返回是否创建了新的恢复 run。"""
    client = client or get_client(url=ASYNC_AGENT_PROTOCOL_URL)
    task_id = record["task_id"]
    graph_id = record["graph_id"]

    try:
        runs = await client.runs.list(task_id, limit=1)
    except Exception as exc:
        await recovery_store.schedule_retry("async", task_id, str(exc))
        return False

    if runs:
        latest = runs[0]
        status = str(latest.get("status", "unknown"))
        if status in {"running", "pending"}:
            # 2024 仍在执行，不能再创建一个 run
            return False
        if status == "success":
            try:
                state = await client.threads.get_state(task_id)
            except Exception:
                state = None
            if state is not None and _has_pending_interrupt(state):
                await recovery_store.mark("async", task_id, "interrupted")
            else:
                await recovery_store.mark("async", task_id, "success")
            return False
        if status in {"error", "cancelled", "timeout"}:
            await recovery_store.mark("async", task_id, status)
            return False
        return False

    # runs 为空通常意味着 2024 的内存 run 注册表随进程丢失。
    # 先按原 task_id 建回 thread，再由服务端 checkpointer 读取状态。
    try:
        await client.threads.create(
            thread_id=task_id,
            graph_id=graph_id,
            if_exists="do_nothing",
        )
        state = await client.threads.get_state(task_id)
    except Exception as exc:
        await recovery_store.schedule_retry("async", task_id, str(exc))
        return False

    if _has_pending_interrupt(state):
        await recovery_store.mark("async", task_id, "interrupted")
        return False

    claimed = await recovery_store.claim("async", task_id)
    if not claimed:
        return False

    values = state.get("values", {}) if isinstance(state, dict) else {}
    if values:
        # 有检查点：从最后一个 super-step 继续，不重复最初任务描述
        run_input = None
    else:
        # 兼容没有检查点的旧任务：只能按登记时的描述重新开始
        description = (record.get("description") or "").strip()
        if not description:
            await recovery_store.mark(
                "async", task_id, "failed", error="无检查点且缺少原始任务描述"
            )
            return False
        run_input = {"messages": [{"role": "user", "content": description}]}
        logger.warning("异步任务无检查点，只能按原描述重新开始 task=%s", task_id)

    try:
        run = await client.runs.create(
            thread_id=task_id,
            assistant_id=graph_id,
            input=run_input,
            metadata={"recovery": True, "previous_run_id": record.get("run_id")},
        )
    except Exception as exc:
        await recovery_store.schedule_retry("async", task_id, str(exc))
        return False

    await recovery_store.mark(
        "async", task_id, "running", run_id=run.get("run_id")
    )
    logger.info(
        "已创建异步恢复 run task=%s run=%s checkpoint=%s",
        task_id,
        run.get("run_id"),
        bool(values),
    )
    return True


async def recover_async_task_by_id(task_id: str) -> bool:
    """供前端轮询或手动恢复使用；任务不存在时返回 False。"""
    record = await recovery_store.get("async", task_id)
    if not record:
        return False
    if record.get("status") not in {"running", "recovering"}:
        return False
    return await recover_async_task(record)


async def recover_async_runs_once() -> int:
    recovered = 0
    for record in await recovery_store.pending("async"):
        if await recover_async_task(record):
            recovered += 1
    return recovered


async def recovery_loop() -> None:
    """启动后立即扫描一次，之后周期处理服务不可用时的延迟重试。"""
    while True:
        try:
            main_count = await recover_main_runs_once()
            async_count = await recover_async_runs_once()
            if main_count or async_count:
                logger.info("本轮恢复认领：main=%d async=%d", main_count, async_count)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("恢复循环执行失败", exc_info=True)
        await asyncio.sleep(RECOVERY_SCAN_INTERVAL)
