from contextlib import asynccontextmanager
import httpx
from fastmcp import FastMCP

from mcp_server.server_config import JAVA_API_BASE_URL


# 关键点：lifespan 返回的字典会通过 ctx.request_context.lifespan_context 传递给每个工具函数，
# 避免了全局变量或手动关闭的麻烦。

@asynccontextmanager  # 约定：yield 之前的代码在启动时执行，yield 之后的代码在关闭时执行
async def mcp_lifespan(server: FastMCP):
    """
    FastMCP 生命周期管理：初始化 / 关闭 HTTP 客户端

    Args:
        server: FastMCP 实例（由框架自动传入）
    """
    # 启动时创建 HTTP 客户端（连接池）
    http_client = httpx.AsyncClient(
        base_url=JAVA_API_BASE_URL,
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    # http_client.put()
    # 将 http_client 存入 lifespan_context，供工具函数通过 ctx 获取
    yield {"http_client": http_client}

    # 关闭时清理资源
    await http_client.aclose()