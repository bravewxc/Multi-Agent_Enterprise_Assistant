"""敏感信息脱敏工具（安全整改 P1-4/P1-6，见 文档/安全/本项目安全分析.md）。

前因：
    本项目后端进程持有 7 个 API Key + MongoDB URI（env_utils.py）。
    两条通道会把运行时文本"带出进程边界"：
    ① 给模型的通道——ToolErrorMiddleware 把 str(e) 直接塞进 ToolMessage，
       pymongo/openai 等库的异常消息可能包含带凭据的连接串；
    ② 落库的通道——tool_call_metrics 存完整工具参数与错误摘要。
    "模型看得到的内容都可能被注入利用，落库的内容都可能被导出"——
    两条通道必须统一过脱敏。

规则（模式匹配，宁可多打码——多打码的代价是可调试性，漏打码的
代价是凭据泄漏，两者不成比例）：
    1. 带凭据的 URI：scheme://user:password@host → scheme://***:***@host
    2. Bearer 头：Bearer <token> → Bearer ***
    3. API Key 形态：sk-xxxx… → sk-***
    4. 敏感 KEY=VALUE 赋值：*KEY/*TOKEN/*SECRET/*PASSWD/MONGO*=value → =***

使用位置：
    - tool_error.py（给模型的错误通道）
    - tool_metrics.py（落库的指标通道）
    - web_search.py（搜索失败消息）
"""
from __future__ import annotations

import re

# scheme://user:password@host（user:pass 部分整体打码；允许空用户名 redis://:pass@）
_URI_CREDS = re.compile(r"(\w+://)([^:/\s'\"]*):([^@/\s'\"]+)@", re.IGNORECASE)

# Authorization: Bearer <token>
_BEARER = re.compile(r"(bearer\s+)(\S{8,})", re.IGNORECASE)

# OpenAI/DeepSeek 风格 key：sk- 开头 ≥8 位
_API_KEY = re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}\b")

# 敏感环境变量赋值形态（MONGODB_URI=xxx / API_KEY=xxx / TOKEN=xxx …）。
# 值的负向前瞻 (?!//)：排除 "mongodb://…" 这类 URI——否则 URI 的
# 协议头 "mongodb:" 会被误判成 KEY: VALUE 赋值，把整串打码成 "mongodb=***"
# （实测踩坑：URI 规则先打码后，KV 规则二次误伤）。
_KV_SECRET = re.compile(
    r"\b([A-Za-z0-9_]*(?:API_?KEY|_?TOKEN|_?SECRET|PASSW(?:O)?RD|PASSWD|MONGO[A-Za-z0-9_]*)"
    r"[A-Za-z0-9_]*)\s*[=:]\s*(?!//)([^\s&'\"]+)",
    re.IGNORECASE,
)


def redact_secrets(text: str) -> str:
    """对文本中的敏感凭据模式打码。非字符串输入原样返回。"""
    if not text or not isinstance(text, str):
        return text
    text = _URI_CREDS.sub(r"\1***:***@", text)
    text = _BEARER.sub(r"\1***", text)
    text = _API_KEY.sub("sk-***", text)
    text = _KV_SECRET.sub(r"\1=***", text)
    return text
