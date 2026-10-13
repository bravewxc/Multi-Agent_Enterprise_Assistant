# src/agent/backends/mongo_store.py
"""MongoDB 持久化版 LangGraph Store。

背景（替换 InMemoryStore，见 文档/修改记录.md 2026-10-13 条目）：
    CompositeBackend 的两条路由 /memories/（用户长期记忆）与
    /persisted-skills/（技能资产）此前挂 InMemoryStore——数据存进程内存，
    后端重启即丢；而会话记忆（MongoDBSaver checkpointer）反而能跨重启恢复，
    "长期"记忆比会话记忆死得快。本实现把两路 Store 数据持久化到 MongoDB
    （复用 checkpoint 的同一 Mongo 实例，另立 stores collection），
    注入点只换 config.STORE 一处，全部使用点（StoreBackend / 中间件 /
    assign_skill）经 BaseStore 鸭子接口自动切换，零改动。

实现契约（对齐 langgraph.store.base.BaseStore）：
    - 抽象方法仅 batch()（sync）/ abatch()（async），get/put/search/
      list_namespaces 及其 a- 前缀版本全部由基类委托 batch 实现；
    - abatch 用 asyncio.to_thread 包装 batch（对齐 RedisStore 同款做法，
      pymongo 为同步驱动、motor 未安装）；
    - Op 契约：GetOp→Item|None；PutOp(value=None 即删除)→None；
      SearchOp→list[SearchItem]；ListNamespacesOp→list[tuple]。
      结果列表顺序与输入 ops 严格对齐。

语义取舍（与现有实现对齐）：
    - created_at：每次 put 均重置为 now（与 InMemoryStore._apply_put_ops
      一致；文件级 created_at 由 StoreBackend 的 FileData 在 value 内部
      自行维护，与 Item 时间戳无关）；
    - search filter：精确相等 + expected 为 list 时成员匹配（对齐
      RedisStore 的过滤实现），不支持 $gt 等操作符（项目内 filter 恒为
      None）；
    - query（语义搜索）：项目未配置 IndexConfig，与无索引的 InMemoryStore
      行为一致——忽略 query（后续可用 Mongo $vectorSearch 扩展）；
    - TTL：不支持（supports_ttl=False 默认）。

namespace 前缀匹配：
    ns_text = "\x1f".join(namespace)（单元分隔符，杜绝组件含"."时的
    歧义——deepagents 的 namespace 组件校验允许出现点号）。前缀匹配
    = ns_text 精确相等 OR 以 ns_text+SEP 开头，正则
    ^{escaped}({SEP}.*)?$ 兼顾"自身"与"子命名空间"。
"""
from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from langgraph.store.base import (
    BaseStore,
    GetOp,
    Item,
    ListNamespacesOp,
    Op,
    PutOp,
    Result,
    SearchItem,
    SearchOp,
)

logger = logging.getLogger(__name__)

# namespace 组件拼接分隔符：单元分隔符（ASCII 0x1F），
# deepagents 组件校验（字母数字/-/_.@+:~）不可能出现该字符
_NS_SEPARATOR = "\x1f"


def _ns_to_text(namespace: tuple[str, ...]) -> str:
    """namespace 元组 → 拼接文本（用于唯一索引与前缀正则）。"""
    return _NS_SEPARATOR.join(namespace)


def _text_to_ns(ns_text: str) -> tuple[str, ...]:
    """拼接文本 → namespace 元组（Item.namespace 要求 tuple）。"""
    return tuple(ns_text.split(_NS_SEPARATOR))


def _prefix_regex(ns_text: str) -> dict[str, Any]:
    """前缀匹配正则：精确等于自身，或以自身+SEP 开头（子命名空间）。"""
    if not ns_text:
        # 空前缀 = 搜索整个 store（BaseStore 契约：namespace_prefix=()）
        return {}
    escaped = re.escape(ns_text)
    return {"ns_text": {"$regex": f"^{escaped}({re.escape(_NS_SEPARATOR)}.*)?$"}}


def _matches_filter(value: dict[str, Any], filter_: dict[str, Any] | None) -> bool:
    """value 字段过滤：精确相等 / expected 为 list 时成员匹配。

    对齐 RedisStore._batch_search_ops 的过滤语义（redis/__init__.py L638-651）。
    """
    if not filter_:
        return True
    for key, expected in filter_.items():
        actual = value.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


class MongoDBStore(BaseStore):
    """基于 pymongo 的持久化 Store，替换 InMemoryStore。

    构造时不连库、不建索引（MongoClient 本身惰性连接）——保住
    regression.py "不 import config 也能跑零依赖单测"的契约；索引在
    首次 batch 时惰性创建，失败仅告警不阻断（正确性不依赖索引）。
    """

    def __init__(self, client, db_name: str, collection_name: str) -> None:
        self._collection = client[db_name][collection_name]
        self._indexes_ready = False

    # ------------------------------------------------------------------
    # 索引（惰性创建）
    # ------------------------------------------------------------------

    def _ensure_indexes(self) -> None:
        if self._indexes_ready:
            return
        try:
            self._collection.create_index(
                [("ns_text", 1), ("key", 1)], unique=True, name="ns_key_unique"
            )
            self._collection.create_index("ns_text", name="ns_prefix")
            self._indexes_ready = True
        except Exception:
            # Mongo 未启动 / 权限不足：放行（唯一性退化由 last-write-wins 兜底），
            # 下次 batch 重试
            logger.warning("MongoDBStore 索引创建失败（将继续重试）", exc_info=True)

    # ------------------------------------------------------------------
    # BaseStore 抽象方法
    # ------------------------------------------------------------------

    def batch(self, ops: Iterable[Op]) -> list[Result]:
        self._ensure_indexes()
        results: list[Result] = []
        for op in ops:
            if isinstance(op, GetOp):
                results.append(self._handle_get(op))
            elif isinstance(op, PutOp):
                self._handle_put(op)
                results.append(None)
            elif isinstance(op, SearchOp):
                results.append(self._handle_search(op))
            elif isinstance(op, ListNamespacesOp):
                results.append(self._handle_list_namespaces(op))
            else:
                raise ValueError(f"Unknown operation type: {type(op)}")
        return results

    async def abatch(self, ops: Iterable[Op]) -> list[Result]:
        # pymongo 为同步驱动，对齐 RedisStore.abatch 的 to_thread 模式
        return await asyncio.to_thread(self.batch, ops)

    # ------------------------------------------------------------------
    # 各 Op 实现
    # ------------------------------------------------------------------

    def _doc_to_item(self, doc: dict[str, Any]) -> Item:
        return Item(
            value=doc["value"],
            key=doc["key"],
            namespace=_text_to_ns(doc["ns_text"]),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    def _handle_get(self, op: GetOp) -> Item | None:
        doc = self._collection.find_one(
            {"ns_text": _ns_to_text(op.namespace), "key": op.key}
        )
        return self._doc_to_item(doc) if doc else None

    def _handle_put(self, op: PutOp) -> None:
        ns_text = _ns_to_text(op.namespace)
        if op.value is None:
            # BaseStore 契约：value=None 表示删除
            self._collection.delete_one({"ns_text": ns_text, "key": op.key})
            return
        now = datetime.now(timezone.utc)
        # 与 InMemoryStore._apply_put_ops 一致：每次 put 均重置 created_at
        self._collection.replace_one(
            {"ns_text": ns_text, "key": op.key},
            {
                "ns_text": ns_text,
                "namespace": list(op.namespace),
                "key": op.key,
                "value": op.value,
                "created_at": now,
                "updated_at": now,
            },
            upsert=True,
        )

    def _handle_search(self, op: SearchOp) -> list[SearchItem]:
        query: dict[str, Any] = dict(_prefix_regex(_ns_to_text(op.namespace_prefix)))
        # filter 深入 value 字段（精确相等 / 列表成员，对齐 RedisStore）
        if op.filter:
            for key, expected in op.filter.items():
                if isinstance(expected, list):
                    query[f"value.{key}"] = {"$in": expected}
                else:
                    query[f"value.{key}"] = expected

        cursor = (
            self._collection.find(query)
            .sort([("ns_text", 1), ("key", 1)])
            .skip(op.offset)
            .limit(op.limit)
        )
        items = []
        for doc in cursor:
            item = self._doc_to_item(doc)
            items.append(
                SearchItem(
                    namespace=item.namespace,
                    key=item.key,
                    value=item.value,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        return items

    def _handle_list_namespaces(self, op: ListNamespacesOp) -> list[tuple[str, ...]]:
        ns_texts = self._collection.distinct("ns_text")

        def _matches(ns: tuple[str, ...]) -> bool:
            for cond in op.match_conditions or ():
                path = cond.path
                if cond.match_type == "prefix":
                    if ns[: len(path)] != path:
                        return False
                elif cond.match_type == "suffix":
                    if ns[-len(path):] != path:
                        return False
            return True

        namespaces: list[tuple[str, ...]] = []
        for text in ns_texts:
            ns = _text_to_ns(text)
            if _matches(ns):
                namespaces.append(ns)

        if op.max_depth is not None:
            namespaces = sorted({ns[: op.max_depth] for ns in namespaces})
        else:
            namespaces = sorted(namespaces)
        return namespaces[op.offset : op.offset + op.limit]
