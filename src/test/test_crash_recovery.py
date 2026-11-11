"""崩溃恢复离线测试：不依赖 MongoDB、2024 或真实模型。

覆盖：
- 主会话恢复调用使用 recovery=True，不重放原用户输入；
- 异步任务有检查点时 input=None，无检查点时才用原描述；
- 远端仍在运行/已完成/等待审批时不重复创建 run；
- start_async_task 的 graph_id/description 被登记；
- 2024 丢失 run 后，resume_async_task 仍能按登记 graph_id 恢复审批。

运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_crash_recovery
"""
from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from langchain_core.messages import ToolMessage
from langgraph.types import Command

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR / "src"))

from agent.middlewares.async_task_recovery import AsyncTaskRecoveryMiddleware
from agent.tools.resume_async_task import create_resume_async_task_tool
from api_view import recovery


class FakeStore:
    def __init__(self):
        self.records: dict[tuple[str, str], dict] = {}
        self.retries: list[tuple[str, str, str]] = []
        self.approval_claims: set[tuple[str, str]] = set()

    async def claim_approval(self, task_id: str, interrupt_key: str, decision: str) -> bool:
        key = (task_id, interrupt_key)
        if key in self.approval_claims:
            return False
        self.approval_claims.add(key)
        return True

    async def release_approval(self, task_id: str, interrupt_key: str) -> None:
        self.approval_claims.discard((task_id, interrupt_key))

    def put(self, kind: str, entity_id: str, **values):
        self.records[(kind, entity_id)] = values

    async def pending(self, kind: str, *, limit: int = 20):
        return [r for (k, _), r in self.records.items()
                if k == kind and r.get("status") in {"running", "recovering"}]

    async def get(self, kind: str, entity_id: str):
        return self.records.get((kind, entity_id))

    async def claim(self, kind: str, entity_id: str):
        record = self.records[(kind, entity_id)]
        record["attempts"] = record.get("attempts", 0) + 1
        record["status"] = "recovering"
        return record

    async def mark(self, kind: str, entity_id: str, status: str, **kwargs):
        record = self.records.setdefault((kind, entity_id), {})
        record["status"] = status
        for key, value in kwargs.items():
            if value is not None:
                record[key] = value

    async def schedule_retry(self, kind: str, entity_id: str, error: str):
        self.retries.append((kind, entity_id, error))

    async def register_async(self, task: dict, *, graph_id: str, description: str):
        self.put("async", task["task_id"], **task,
                 graph_id=graph_id, description=description)

    async def update_async(self, task: dict):
        self.records[("async", task["task_id"])].update(task)


class FakeRuns:
    def __init__(self, client):
        self.client = client
        self.create_calls: list[dict] = []

    async def list(self, task_id: str, limit: int = 1):
        return list(self.client.runs_list)

    async def create(self, **kwargs):
        self.create_calls.append(kwargs)
        return {"run_id": f"recovery-run-{len(self.create_calls)}", "status": "running"}


class FakeThreads:
    def __init__(self, client):
        self.client = client
        self.create_calls: list[dict] = []

    async def create(self, **kwargs):
        self.create_calls.append(kwargs)
        return {"thread_id": kwargs["thread_id"]}

    async def get_state(self, task_id: str):
        return self.client.state


class FakeClient:
    def __init__(self, *, runs_list=None, state=None):
        self.runs_list = runs_list or []
        self.state = state or {"values": {}, "tasks": []}
        self.runs = FakeRuns(self)
        self.threads = FakeThreads(self)


def _record(task_id="task-1"):
    return {
        "task_id": task_id,
        "graph_id": "procurement_replenish_async",
        "description": "计算刹车片补货量",
        "run_id": "old-run",
        "status": "running",
        "attempts": 0,
    }


def _interrupt_state(interrupt_id: str = "intr-1"):
    return {
        "values": {},
        "tasks": [{"interrupts": [{
            "id": interrupt_id,
            "value": {"action_requests": [{"name": "replenish_submit"}]},
        }]}],
    }


async def test_main_recovery_uses_recovery_mode():
    store = FakeStore()
    store.put("main", "thread-1", thread_id="thread-1", user_id="u1", status="running")
    calls = []
    fake_chat = types.ModuleType("api_view.api.chat")

    async def guarded_stream_chat_response(**kwargs):
        calls.append(kwargs)
        await store.mark("main", kwargs["thread_id"], "succeeded")
        if False:
            yield ""

    fake_chat.guarded_stream_chat_response = guarded_stream_chat_response
    with patch.object(recovery, "recovery_store", store), patch.dict(
        sys.modules, {"api_view.api.chat": fake_chat}
    ):
        count = await recovery.recover_main_runs_once()

    assert count == 1
    assert calls[0]["recovery"] is True
    assert "message" not in calls[0] or calls[0]["message"] is None
    assert "resume_data" not in calls[0] or calls[0]["resume_data"] is None
    print("[OK] 主会话恢复使用 recovery=True，不重放输入")


async def test_async_resume_from_checkpoint():
    store = FakeStore()
    store.put("async", "task-1", **_record())
    client = FakeClient(state={"values": {"messages": [{"role": "user", "content": "old"}]}, "tasks": []})
    with patch.object(recovery, "recovery_store", store):
        created = await recovery.recover_async_task(_record(), client=client)
    assert created is True
    call = client.runs.create_calls[0]
    assert call["thread_id"] == "task-1"
    assert call["assistant_id"] == "procurement_replenish_async"
    assert call["input"] is None
    assert store.records[("async", "task-1")]["status"] == "running"
    print("[OK] 异步有检查点时 input=None")


async def test_async_legacy_uses_description_only_without_checkpoint():
    store = FakeStore()
    store.put("async", "task-1", **_record())
    client = FakeClient(state={"values": {}, "tasks": []})
    with patch.object(recovery, "recovery_store", store):
        created = await recovery.recover_async_task(_record(), client=client)
    assert created is True
    call = client.runs.create_calls[0]
    assert call["input"]["messages"][0]["content"] == "计算刹车片补货量"
    print("[OK] 无检查点旧任务才使用原描述")


async def test_async_running_or_terminal_not_duplicated():
    store = FakeStore()
    running_client = FakeClient(runs_list=[{"status": "running", "run_id": "old-run"}])
    with patch.object(recovery, "recovery_store", store):
        assert await recovery.recover_async_task(_record(), client=running_client) is False
    assert running_client.runs.create_calls == []

    success_client = FakeClient(runs_list=[{"status": "success", "run_id": "old-run"}])
    with patch.object(recovery, "recovery_store", store):
        assert await recovery.recover_async_task(_record(), client=success_client) is False
    assert success_client.runs.create_calls == []
    assert store.records[("async", "task-1")]["status"] == "success"
    print("[OK] 远端运行/终态不重复建 run")


async def test_async_interrupt_waits_for_user():
    store = FakeStore()
    store.put("async", "task-1", **_record())
    client = FakeClient(runs_list=[], state=_interrupt_state())
    with patch.object(recovery, "recovery_store", store):
        created = await recovery.recover_async_task(_record(), client=client)
    assert created is False
    assert client.runs.create_calls == []
    assert store.records[("async", "task-1")]["status"] == "interrupted"
    print("[OK] 审批中断不自动恢复")


async def test_start_tool_is_registered():
    store = FakeStore()
    middleware = AsyncTaskRecoveryMiddleware()
    task = {
        "task_id": "task-9",
        "agent_name": "procurement-replenish",
        "run_id": "run-9",
        "status": "running",
    }
    result = Command(update={"async_tasks": {"task-9": task}})
    request = SimpleNamespace(tool_call={
        "name": "start_async_task",
        "args": {"description": "生成补货建议", "subagent_type": "procurement-replenish"},
    })

    async def handler(_):
        return result

    with patch("agent.middlewares.async_task_recovery.recovery_store", store):
        returned = await middleware.awrap_tool_call(request, handler)
    assert returned is result
    saved = store.records[("async", "task-9")]
    assert saved["graph_id"] == "procurement_replenish_async"
    assert saved["description"] == "生成补货建议"
    print("[OK] start_async_task 登记 graph_id/description")


async def test_resume_after_2024_restart_uses_registered_graph():
    store = FakeStore()
    store.put("async", "task-1", **_record())
    client = FakeClient(runs_list=[], state=_interrupt_state())
    tool = create_resume_async_task_tool()
    with patch("agent.tools.resume_async_task.recovery_store", store), patch(
        "agent.tools.resume_async_task.get_client", return_value=client
    ):
        result = await tool.ainvoke({"task_id": "task-1", "decision": "approve"})
    call = client.runs.create_calls[0]
    assert call["assistant_id"] == "procurement_replenish_async"
    assert call["command"]["resume"]["decisions"][0]["type"] == "approve"
    assert "已传达审批决定" in result
    print("[OK] 2024 丢失 run 后仍可恢复审批")


async def test_duplicate_approval_blocked_by_idempotency_key():
    """同一中断二次批准被幂等键拦截；发起失败时释放占位可重试。"""
    store = FakeStore()
    store.put("async", "task-1", **_record())
    client = FakeClient(runs_list=[], state=_interrupt_state())
    tool = create_resume_async_task_tool()
    with patch("agent.tools.resume_async_task.recovery_store", store), patch(
        "agent.tools.resume_async_task.get_client", return_value=client
    ):
        first = await tool.ainvoke({"task_id": "task-1", "decision": "approve"})
        # 模拟并发/双击：第一次 resume run 还没消费中断，第二次看到同样的中断
        second = await tool.ainvoke({"task_id": "task-1", "decision": "approve"})
    assert "已传达审批决定" in first, first
    assert "已提交过" in second and "不会重复恢复" in second, second
    assert len(client.runs.create_calls) == 1, client.runs.create_calls
    assert store.approval_claims == {("task-1", "intr-1")}

    # 发起失败（2024 不可达）→ 释放占位，用户可对同一中断重试
    store.put("async", "task-2", **_record("task-2"))
    broken = FakeClient(runs_list=[], state=_interrupt_state("intr-2"))

    async def _create_fails(**kwargs):
        raise RuntimeError("2024 unreachable")

    broken.runs.create = _create_fails
    with patch("agent.tools.resume_async_task.recovery_store", store), patch(
        "agent.tools.resume_async_task.get_client", return_value=broken
    ):
        failed = await tool.ainvoke({"task_id": "task-2", "decision": "approve"})
    assert "恢复失败" in failed, failed
    assert store.approval_claims == {("task-1", "intr-1")}
    print("[OK] 重复批准被幂等键拦截；发起失败释放占位")


async def main():
    await test_main_recovery_uses_recovery_mode()
    await test_async_resume_from_checkpoint()
    await test_async_legacy_uses_description_only_without_checkpoint()
    await test_async_running_or_terminal_not_duplicated()
    await test_async_interrupt_waits_for_user()
    await test_start_tool_is_registered()
    await test_resume_after_2024_restart_uses_registered_graph()
    await test_duplicate_approval_blocked_by_idempotency_key()
    print("ALL_OK")


if __name__ == "__main__":
    asyncio.run(main())
