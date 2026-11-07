"""崩溃恢复的运行登记表（MongoDB）与主会话进程内执行锁。

checkpointer 保存“图执行到哪里”，本模块保存“哪次请求还没有结束”：
- main：8090 主会话的一次流式执行；
- async：2024 上的一个异步子 Agent 任务。

进程正常结束时状态改为 succeeded / interrupted / failed；进程崩溃时记录会
停留在 running / recovering，重启后由恢复循环认领并续跑。

多实例说明：当前认领按单实例开发部署设计。多实例必须把 owner 心跳和
findOneAndUpdate 的租约条件一起启用，不能仅依赖本模块的进程内锁。
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import MongoClient, ReturnDocument

from agent.env_utils import MONGODB_URI

logger = logging.getLogger(__name__)

OWNER_ID = uuid.uuid4().hex
MAX_RECOVERY_ATTEMPTS = int(os.getenv("RECOVERY_MAX_ATTEMPTS", "3"))
TERMINAL_STATUSES = {"succeeded", "success", "interrupted", "failed", "error", "cancelled"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RecoveryStore:
    """recovery_runs 集合的轻量封装；数据库异常不阻断正常对话。"""

    def __init__(self, *, mongo_uri: str = MONGODB_URI) -> None:
        self.mongo_uri = mongo_uri
        self._client: MongoClient | None = None
        self._collection: Any = None

    def _col(self):
        if self._collection is None:
            self._client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=3000)
            self._collection = self._client["langchain_db"]["recovery_runs"]
        return self._collection

    @staticmethod
    def _id(kind: str, entity_id: str) -> str:
        return f"{kind}:{entity_id}"

    async def register_main(self, thread_id: str, user_id: str) -> None:
        now = _utcnow()
        try:
            await asyncio.to_thread(
                self._col().replace_one,
                {"_id": self._id("main", thread_id)},
                {
                    "_id": self._id("main", thread_id),
                    "kind": "main",
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "status": "running",
                    "owner_id": OWNER_ID,
                    "attempts": 0,
                    "next_retry_at": now,
                    "error": None,
                    "created_at": now,
                    "updated_at": now,
                },
                True,
            )
        except Exception:
            logger.warning("recovery: 登记主会话失败 thread=%s", thread_id, exc_info=True)

    async def register_async(
        self,
        task: dict[str, Any],
        *,
        graph_id: str,
        description: str,
    ) -> None:
        now = _utcnow()
        task_id = str(task["task_id"])
        doc = {
            "_id": self._id("async", task_id),
            "kind": "async",
            "task_id": task_id,
            "agent_name": task.get("agent_name"),
            "graph_id": graph_id,
            "description": description,
            "run_id": task.get("run_id"),
            "status": task.get("status", "running"),
            "owner_id": OWNER_ID,
            "attempts": 0,
            "next_retry_at": now,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }
        try:
            await asyncio.to_thread(
                self._col().replace_one,
                {"_id": doc["_id"]},
                doc,
                True,
            )
        except Exception:
            logger.warning("recovery: 登记异步任务失败 task=%s", task_id, exc_info=True)

    async def update_async(self, task: dict[str, Any]) -> None:
        task_id = str(task["task_id"])
        try:
            await asyncio.to_thread(
                self._col().update_one,
                {"_id": self._id("async", task_id)},
                {
                    "$set": {
                        "status": task.get("status", "running"),
                        "run_id": task.get("run_id"),
                        "updated_at": _utcnow(),
                    }
                },
            )
        except Exception:
            logger.warning("recovery: 更新异步任务失败 task=%s", task_id, exc_info=True)

    async def get(self, kind: str, entity_id: str) -> dict[str, Any] | None:
        try:
            return await asyncio.to_thread(
                self._col().find_one, {"_id": self._id(kind, entity_id)}
            )
        except Exception:
            logger.warning("recovery: 读取运行记录失败 %s/%s", kind, entity_id, exc_info=True)
            return None

    async def mark(
        self,
        kind: str,
        entity_id: str,
        status: str,
        *,
        error: str | None = None,
        run_id: str | None = None,
    ) -> None:
        values: dict[str, Any] = {
            "status": status,
            "updated_at": _utcnow(),
            "error": (error or "")[:2000] or None,
        }
        if run_id is not None:
            values["run_id"] = run_id
        try:
            await asyncio.to_thread(
                self._col().update_one,
                {"_id": self._id(kind, entity_id)},
                {"$set": values},
            )
        except Exception:
            logger.warning("recovery: 标记状态失败 %s/%s", kind, entity_id, exc_info=True)

    async def pending(self, kind: str, *, limit: int = 20) -> list[dict[str, Any]]:
        query = {
            "kind": kind,
            "status": {"$in": ["running", "recovering"]},
            "attempts": {"$lt": MAX_RECOVERY_ATTEMPTS},
            "next_retry_at": {"$lte": _utcnow()},
        }
        try:
            cursor = self._col().find(query).sort("updated_at", 1).limit(limit)
            return await asyncio.to_thread(list, cursor)
        except Exception:
            logger.warning("recovery: 查询待恢复任务失败 kind=%s", kind, exc_info=True)
            return []

    async def claim(self, kind: str, entity_id: str) -> dict[str, Any] | None:
        """原子认领一次恢复，防止恢复循环与手动恢复重复执行。"""
        query = {
            "_id": self._id(kind, entity_id),
            "status": {"$in": ["running", "recovering"]},
            "attempts": {"$lt": MAX_RECOVERY_ATTEMPTS},
            "next_retry_at": {"$lte": _utcnow()},
        }
        update = {
            "$set": {
                "status": "recovering",
                "owner_id": OWNER_ID,
                "updated_at": _utcnow(),
            },
            "$inc": {"attempts": 1},
        }
        try:
            return await asyncio.to_thread(
                self._col().find_one_and_update,
                query,
                update,
                return_document=ReturnDocument.AFTER,
            )
        except Exception:
            logger.warning("recovery: 认领失败 %s/%s", kind, entity_id, exc_info=True)
            return None

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None
        self._collection = None

    async def schedule_retry(self, kind: str, entity_id: str, error: str) -> None:
        record = await self.get(kind, entity_id)
        attempts = int((record or {}).get("attempts", MAX_RECOVERY_ATTEMPTS))
        if attempts >= MAX_RECOVERY_ATTEMPTS:
            await self.mark(kind, entity_id, "failed", error=error)
            return
        delay = min(60, 5 * (2 ** max(0, attempts - 1)))
        try:
            await asyncio.to_thread(
                self._col().update_one,
                {"_id": self._id(kind, entity_id)},
                {
                    "$set": {
                        "status": "running",
                        "next_retry_at": _utcnow() + timedelta(seconds=delay),
                        "updated_at": _utcnow(),
                        "error": error[:2000],
                    }
                },
            )
        except Exception:
            logger.warning("recovery: 安排重试失败 %s/%s", kind, entity_id, exc_info=True)


recovery_store = RecoveryStore()

# 同一进程内，同一主会话只能有一个执行者（正常请求或恢复请求）。
_active_main_threads: set[str] = set()
_active_main_lock = asyncio.Lock()


async def acquire_main_thread(thread_id: str) -> bool:
    async with _active_main_lock:
        if thread_id in _active_main_threads:
            return False
        _active_main_threads.add(thread_id)
        return True


def release_main_thread(thread_id: str) -> None:
    _active_main_threads.discard(thread_id)
