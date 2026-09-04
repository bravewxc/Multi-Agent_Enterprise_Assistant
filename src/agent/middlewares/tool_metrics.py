"""
工具调用指标采集中间件（评估方向 A：可观测性地基）。

awrap_tool_call 位于所有工具调用的必经之路，为每次调用记录结构化指标：
    {ts, tool_name, ok, latency_ms, error_type, thread_id, agent, args_digest}
写入 MongoDB 的 tool_call_metrics 集合，是评估体系（成功率/耗时/错误分布/
失败重试率等可靠性·效率指标）的唯一数据源。

设计纪律（继承 memory_update.py 的旁路原则）：
1. 指标记录失败绝不影响工具调用本身——_record 全程 try/except，
   MongoDB 不可用时降级为仅 logger 输出。
2. 与 ToolErrorMiddleware 的配合（挂载顺序：本中间件在前=外层）：
   工具抛异常 → 内层 ToolErrorMiddleware 转成 status="error" 的 ToolMessage
   → 本中间件从 ToolMessage.status 识别失败；若本中间件被挂在内层
   （异常直接穿透），也能从 except 分支记录——两种顺序都正确。

学习点：
- AgentMiddleware.wrap_tool_call 是"横切关注点"（cross-cutting concern）的
  标准注入位，等价于 Java 里的 AOP 环绕通知（@Around）；
- ToolCallRequest.runtime.config 提供 RunnableConfig，thread_id 从
  config["configurable"]["thread_id"] 取——评估轨迹归组的关键字段。
"""
from __future__ import annotations

import json
import logging
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command
from pymongo import MongoClient

from agent.env_utils import MONGODB_URI

logger = logging.getLogger(__name__)

# 与 config.py 的 MONGODB_DB_NAME 保持一致（独立声明，避免 2024 进程
# 仅为取常量而导入 config.py——后者会实例化主模型等重组件）
METRICS_DB_NAME = "langchain_db"
METRICS_COLLECTION_NAME = "tool_call_metrics"

# 进程级单例：惰性建立，Mongo 不可用时只告警一次
_metrics_collection: Any = None
_mongo_unavailable = False


def _get_collection() -> Any:
    global _metrics_collection, _mongo_unavailable
    if _metrics_collection is None:
        if _mongo_unavailable:
            return None
        try:
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
            _metrics_collection = client[METRICS_DB_NAME][METRICS_COLLECTION_NAME]
        except Exception:
            _mongo_unavailable = True
            logger.warning("tool_metrics: MongoDB 不可用，后续仅输出日志", exc_info=True)
            return None
    return _metrics_collection


def _tool_meta(request: ToolCallRequest) -> dict:
    """从请求中提取工具名/参数摘要/thread_id（任何一步失败都不影响主流程）。"""
    from agent.middlewares.redact import redact_secrets

    meta: dict[str, Any] = {"tool_name": None, "args_digest": "", "thread_id": None}
    try:
        tc = getattr(request, "tool_call", None)
        if isinstance(tc, dict):
            meta["tool_name"] = tc.get("name")
            args = tc.get("args") or {}
            # P1-6：落库参数过脱敏（工具参数若含密钥形态值不得进指标表）
            meta["args_digest"] = redact_secrets(
                json.dumps(args, ensure_ascii=False, default=str))[:200]
        else:
            meta["tool_name"] = getattr(tc, "name", None)
            meta["args_digest"] = redact_secrets(
                str(getattr(tc, "args", "")))[:200]
        runtime = getattr(request, "runtime", None)
        config = getattr(runtime, "config", None) or {}
        meta["thread_id"] = (config.get("configurable") or {}).get("thread_id")
    except Exception:
        logger.debug("tool_metrics: 提取元数据失败", exc_info=True)
    return meta


class ToolMetricsMiddleware(AgentMiddleware):
    """所有工具调用 → MongoDB 结构化指标（评估体系的数据地基）。"""

    state_schema = AgentState

    def _record(
        self,
        request: ToolCallRequest,
        *,
        ok: bool,
        latency_ms: float,
        error_type: str | None = None,
        error_msg: str | None = None,
    ) -> None:
        meta = _tool_meta(request)
        from agent.middlewares.redact import redact_secrets
        doc = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "tool_name": meta["tool_name"],
            "args_digest": meta["args_digest"],
            "thread_id": meta["thread_id"],
            "ok": ok,
            "latency_ms": round(latency_ms, 1),
            "error_type": error_type,
            # P1-6：错误摘要与参数同纪律——落库前脱敏
            "error_msg": redact_secrets(error_msg or "")[:200],
        }
        try:
            col = _get_collection()
            if col is not None:
                col.insert_one(doc)
        except Exception:
            logger.debug("tool_metrics: 写入失败（不影响工具调用）", exc_info=True)
        # 结构化日志行：即使 Mongo 挂了，grep "TOOL_METRICS" 仍可离线统计
        logger.info(
            "TOOL_METRICS tool=%s ok=%s %sms err=%s thread=%s",
            doc["tool_name"], ok, doc["latency_ms"], error_type or "-", doc["thread_id"],
        )

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        t0 = time.monotonic()
        try:
            result = handler(request)
        except Exception as e:  # 本中间件挂内层时走此分支
            self._record(
                request, ok=False, latency_ms=(time.monotonic() - t0) * 1000,
                error_type=type(e).__name__, error_msg=str(e),
            )
            raise  # 继续抛给外层（ToolErrorMiddleware）转换，不吞异常
        ok = not (isinstance(result, ToolMessage) and result.status == "error")
        self._record(request, ok=ok, latency_ms=(time.monotonic() - t0) * 1000)
        return result

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        t0 = time.monotonic()
        try:
            result = await handler(request)
        except Exception as e:
            self._record(
                request, ok=False, latency_ms=(time.monotonic() - t0) * 1000,
                error_type=type(e).__name__, error_msg=str(e),
            )
            raise
        ok = not (isinstance(result, ToolMessage) and result.status == "error")
        self._record(request, ok=ok, latency_ms=(time.monotonic() - t0) * 1000)
        return result
