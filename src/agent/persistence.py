"""Agent Protocol（2024）服务端级 MongoDB checkpointer 工厂。

langgraph dev 不允许在图定义里直接传自定义 checkpointer，但支持在
langgraph.json 中配置 checkpointer.path。服务端启动时会调用本工厂，
之后 thread/run 的图状态都写入 MongoDB，进程重启后可按原 thread_id 恢复。

与 8090 主图共用 langchain_db.checkpoints；异步任务的 thread_id 是独立 UUID，
不会与主会话冲突。
"""
from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

from agent.env_utils import MONGODB_URI


@contextmanager
def mongo_checkpointer() -> Iterator[MongoDBSaver]:
    """由 langgraph-api 进入/退出上下文，关闭时释放 Mongo 连接。"""
    client = MongoClient(MONGODB_URI)
    saver = MongoDBSaver(
        client=client,
        db_name="langchain_db",
        checkpoint_collection_name="checkpoints",
    )
    try:
        yield saver
    finally:
        client.close()
