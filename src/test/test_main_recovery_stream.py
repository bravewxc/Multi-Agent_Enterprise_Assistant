"""主会话流式恢复的输入契约测试（替换 agent_loader，不连 Mongo）。

验证 recovery=True 时图为 input=None，且不重复登记/追加用户消息；
正常模式仍传原始消息并登记 running。

运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_main_recovery_stream
"""
from __future__ import annotations

import asyncio
import importlib
import sys
import types
from pathlib import Path
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR / "src"))


class FakeGraph:
    def __init__(self):
        self.calls: list[dict] = []

    async def astream(self, **kwargs):
        self.calls.append(kwargs)
        if False:
            yield {}


class FakeLoader:
    def __init__(self, graph):
        self.graph = graph
        self.saved: list[list] = []

    def create_config(self, thread_id=None, user_id=None, **kwargs):
        return {"configurable": {"thread_id": thread_id, "user_id": user_id}}

    async def get_agent_for_user(self, user_id):
        return self.graph

    async def get_display_messages(self, thread_id):
        return [{"id": "old", "role": "user", "content": "历史消息"}]

    async def save_display_messages(self, thread_id, messages):
        self.saved.append(messages)
        return True


class FakeRecoveryStore:
    def __init__(self):
        self.registered: list[tuple[str, str]] = []
        self.statuses: list[str] = []

    async def register_main(self, thread_id, user_id):
        self.registered.append((thread_id, user_id))

    async def mark(self, kind, entity_id, status, **kwargs):
        self.statuses.append(status)

    async def schedule_retry(self, kind, entity_id, error):
        self.statuses.append("retry")


async def _drain(stream):
    return [chunk async for chunk in stream]


async def main():
    graph = FakeGraph()
    loader = FakeLoader(graph)
    fake_loader_module = types.ModuleType("api_view.agent_loader")
    fake_loader_module.agent_loader = loader

    with patch.dict(sys.modules, {"api_view.agent_loader": fake_loader_module}):
        chat = importlib.import_module("api_view.api.chat")

    store = FakeRecoveryStore()
    with patch.object(chat, "recovery_store", store), patch.object(
        chat, "write_debug_log", lambda *args, **kwargs: None
    ):
        await _drain(chat.stream_chat_response(
            thread_id="thread-recovery", user_id="u1", recovery=True
        ))
        assert graph.calls[-1]["input"] is None
        assert store.registered == []
        assert store.statuses[-1] == "succeeded"
        assert loader.saved[-1] == [{"id": "old", "role": "user", "content": "历史消息"}]
        print("[OK] recovery=True 使用 input=None，不重复追加历史")

        await _drain(chat.stream_chat_response(
            message="新的需求", thread_id="thread-normal", user_id="u1"
        ))
        assert graph.calls[-1]["input"] == {
            "messages": [{"role": "user", "content": "新的需求"}]
        }
        assert store.registered[-1] == ("thread-normal", "u1")
        assert store.statuses[-1] == "succeeded"
        print("[OK] 正常请求仍传原始消息并登记运行")

    print("ALL_OK")


if __name__ == "__main__":
    asyncio.run(main())
