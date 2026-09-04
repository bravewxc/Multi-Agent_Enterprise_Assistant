"""
Agent 加载器

使用 Graph Factory 模式管理 DeepAgent 实例，实现用户级沙箱隔离。
启动时预计算 MCP 工具/YAML 配置，每次请求基于 per-user 沙箱创建 agent graph。
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid
from dataclasses import dataclass
from datetime import datetime

# 将项目根目录添加到 Python 路径
PROJECT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from pymongo import MongoClient

from api_view.web_config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_CHECKPOINT_COLLECTION,
)

from agent.main_agent import create_main_agent, precompute_agent_context, PrecomputedContext
from agent.backends import global_sandbox_manager
from agent.config import CHECKPOINTER


# CheckpointTuple 到 StateSnapshot 的轻量适配器
@dataclass
class _StateSnapshot:
    values: dict
    config: dict
    created_at: datetime | str | None = None
    parent_config: dict | None = None
    metadata: dict | None = None


class AgentLoader:
    """
    Agent 加载器单例类

    负责管理 Agent 生命周期、MongoDB 连接、沙箱管理和会话相关操作。
    采用 Graph Factory 模式：每次请求基于 per-user 沙箱创建 agent graph。
    """

    _instance: Optional['AgentLoader'] = None
    _mongodb_client: Optional[MongoClient] = None
    _initialized: bool = False
    _precomputed: PrecomputedContext = None
    # 最近创建的 agent graph（用于状态查询；所有 graph 共享同一 checkpointer）
    _agent = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        启动时初始化：MongoDB + 沙箱管理器 + 预计算 + 预热沙箱。

        预计算（MCP 工具/YAML 配置）执行一次，所有请求复用。
        预热沙箱在启动阶段完成（~15s），首个用户连接时零等待。
        """
        if self._initialized and self._precomputed is not None:
            return self._agent

        print("[AgentLoader] 开始初始化...")

        try:
            # 1. MongoDB 连接
            self._mongodb_client = MongoClient(MONGODB_URI)
            print("[AgentLoader] MongoDB 连接已建立")

            # 2. 全局沙箱预热。所有用户共享同一个 OpenSandbox。
            await global_sandbox_manager.ensure_global_sandbox()

            # 3. 预计算 MCP 工具 + 图表工具 + YAML 配置
            self._precomputed = await precompute_agent_context()
            print("[AgentLoader] 预计算完成（MCP 工具 + 图表工具 + YAML 配置）")

            self._initialized = True
            print("[AgentLoader] 初始化完成")
        except Exception:
            if self._mongodb_client is not None:
                self._mongodb_client.close()
                self._mongodb_client = None
            raise

    async def get_agent_for_user(self, user_id: str):
        """
        获取 per-user agent graph。

        每次请求调用：获取/创建 per-user 沙箱 → 创建 agent graph。
        同一用户的多个 thread 共享沙箱（缓存命中 < 0.1s）。

        Args:
            user_id: 用户唯一标识。

        Returns:
            CompiledStateGraph: 该用户的 agent graph。
        """
        sandbox_backend = await global_sandbox_manager.ensure_global_sandbox()
        config = self.create_config(user_id=user_id)
        config["configurable"]["user_id"] = user_id
        agent_graph = await create_main_agent(
            config,
            sandbox_backend=sandbox_backend,
            precomputed=self._precomputed,
        )
        # 保存引用用于状态查询（所有 graph 共享同一 checkpointer）
        self._agent = agent_graph
        return agent_graph

    async def cleanup_user(self, user_id: str) -> None:
        """全局沙箱模式下，单个用户退出不销毁沙箱。"""
        return None

    async def shutdown(self) -> None:
        """应用关闭时清理 MongoDB 连接。全局沙箱保留以便下次重连。"""
        print("[AgentLoader] 正在关闭...")
        if self._mongodb_client is not None:
            self._mongodb_client.close()
            self._mongodb_client = None
            print("[AgentLoader] MongoDB 连接已关闭")
        self._initialized = False
        self._precomputed = None
        self._agent = None

    @property
    def agent(self):
        """
        获取最近创建的 Agent 实例（用于状态查询）。

        所有 agent graph 共享同一 MongoDBSaver checkpointer，
        因此状态查询不依赖于特定用户的 graph。
        """
        if self._agent is None:
            raise RuntimeError("Agent 未初始化，请先调用 initialize() 方法")
        return self._agent

    def create_config(
        self,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        return {
            "configurable": {
                "thread_id": thread_id or str(uuid.uuid4()),
                "user_id": user_id or "laoxiao",
                **kwargs
            }
        }

    async def get_state_history(
        self,
        thread_id: str,
        limit: int = 50
    ) -> List[Any]:
        """直接通过 checkpointer 查询，不依赖 agent graph。"""
        config = self.create_config(thread_id)
        states = []
        async for ct in CHECKPOINTER.alist(config, limit=limit):
            snapshot = _StateSnapshot(
                values=ct.checkpoint.get("channel_values", {}),
                config=ct.config,
                created_at=ct.metadata.get("timestamp") if ct.metadata else None,
                parent_config=ct.parent_config,
            )
            states.append(snapshot)
        return states

    async def get_current_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """直接通过 checkpointer 查询，不依赖 agent graph。"""
        config = self.create_config(thread_id)
        try:
            ct = await CHECKPOINTER.aget_tuple(config)
            if ct and ct.checkpoint:
                return ct.checkpoint.get("channel_values", {}).get("messages", [])
        except Exception as e:
            print(f"[AgentLoader] 获取消息失败: {e}")
        return []

    def get_all_thread_ids(self) -> List[str]:
        if self._mongodb_client is None:
            return []
        db = self._mongodb_client[MONGODB_DB_NAME]
        collection = db[MONGODB_CHECKPOINT_COLLECTION]
        thread_ids = collection.distinct("thread_id")
        return [tid for tid in thread_ids if tid and tid != "*" and tid != "" and tid is not None]

    def get_session_updated_at(self, thread_id: str) -> datetime:
        if self._mongodb_client is None:
            return datetime.now()
        db = self._mongodb_client[MONGODB_DB_NAME]
        collection = db[MONGODB_CHECKPOINT_COLLECTION]
        try:
            latest_doc = collection.find_one(
                {"thread_id": thread_id},
                sort=[("_id", -1)]
            )
            if latest_doc:
                if "_id" in latest_doc and hasattr(latest_doc["_id"], 'generation_time'):
                    return latest_doc["_id"].generation_time
                elif "_id" in latest_doc:
                    import bson
                    if isinstance(latest_doc["_id"], bson.objectid.ObjectId):
                        return latest_doc["_id"].generation_time
            return datetime.now()
        except Exception as e:
            print(f"[AgentLoader] 获取会话时间失败: {e}")
            return datetime.now()

    async def delete_session(self, thread_id: str) -> bool:
        if self._mongodb_client is None:
            return False
        db = self._mongodb_client[MONGODB_DB_NAME]
        collection = db[MONGODB_CHECKPOINT_COLLECTION]
        try:
            result = collection.delete_many({"thread_id": thread_id})
            display_collection = db["session_display_messages"]
            display_result = display_collection.delete_many({"thread_id": thread_id})
            print(f"[AgentLoader] 已删除会话 {thread_id}，checkpoint {result.deleted_count} 条，展示消息 {display_result.deleted_count} 条")
            return True
        except Exception as e:
            print(f"[AgentLoader] 删除会话失败: {e}")
            return False

    # ============================================================
    # 完整展示消息存取
    # ============================================================

    _MAX_FIELD_LENGTH = 500_000

    @classmethod
    def _truncate_message_fields(cls, msg: Dict[str, Any]) -> Dict[str, Any]:
        for field in ("text", "content", "args"):
            if field in msg and isinstance(msg[field], str) and len(msg[field]) > cls._MAX_FIELD_LENGTH:
                msg[field] = msg[field][:cls._MAX_FIELD_LENGTH] + "\n\n...(内容过长已截断)"
        return msg

    async def save_display_messages(self, thread_id: str, messages: List[Dict[str, Any]]) -> bool:
        if self._mongodb_client is None:
            return False
        try:
            db = self._mongodb_client[MONGODB_DB_NAME]
            collection = db["session_display_messages"]
            try:
                collection.create_index([("thread_id", 1), ("index", 1)])
            except Exception:
                pass
            collection.delete_many({"thread_id": thread_id})
            if messages:
                now = datetime.now()
                docs = []
                for i, msg in enumerate(messages):
                    msg = self._truncate_message_fields(msg)
                    docs.append({
                        "thread_id": thread_id,
                        "index": i,
                        "message": msg,
                        "updated_at": now
                    })
                collection.insert_many(docs)
                print(f"[AgentLoader] 已保存 {len(docs)} 条展示消息，thread_id={thread_id}")
            return True
        except Exception as e:
            print(f"[AgentLoader] 保存展示消息失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def get_display_messages(self, thread_id: str) -> Optional[List[Dict[str, Any]]]:
        if self._mongodb_client is None:
            return None
        try:
            db = self._mongodb_client[MONGODB_DB_NAME]
            collection = db["session_display_messages"]
            cursor = collection.find({"thread_id": thread_id}).sort("index", 1)
            docs = list(cursor)
            if not docs:
                return None
            messages = [doc["message"] for doc in docs]
            print(f"[AgentLoader] 已读取 {len(messages)} 条展示消息，thread_id={thread_id}")
            return messages
        except Exception as e:
            print(f"[AgentLoader] 读取展示消息失败: {e}")
            import traceback
            traceback.print_exc()
            return None


# 全局单例实例
agent_loader = AgentLoader()
