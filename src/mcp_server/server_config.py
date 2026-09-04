import os

from dotenv import load_dotenv

load_dotenv(override=True)

# Java 后端 API 地址（由环境变量 JAVA_API_BASE_URL 控制，
# 默认指向本地 ERP 占位地址——实际地址在 .env 中配置，见 .env.example）
JAVA_API_BASE_URL = os.getenv(
    "JAVA_API_BASE_URL", "http://127.0.0.1:8081/api"
)

# MCP 服务监听配置
MCP_HOST = "127.0.0.1"
MCP_PORT = 8000
MCP_PATH = "/mcp"