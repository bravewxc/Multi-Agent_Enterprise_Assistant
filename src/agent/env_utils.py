import os

from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY')
ALIBABA_API_KEY = os.getenv('ALIBABA_API_KEY')
K2_API_KEY = os.getenv('K2_API_KEY')

K2_BASE_URL = os.getenv('K2_BASE_URL')
ALIBABA_BASE_URL = os.getenv('ALIBABA_BASE_URL')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL')
ZHIPU_BASE_URL = os.getenv('ZHIPU_BASE_URL')

LOCAL_BASE_URL = os.getenv('LOCAL_BASE_URL')
DAYTONA_API_KEY = os.getenv('DAYTONA_API_KEY')
DAYTONA_BASE_URL = os.getenv('DAYTONA_BASE_URL')

# ---------- 模型名称配置（唯一来源是 .env，缺失时启动即报错 fail-fast） ----------
# 主 Agent / 异步采购分析子 Agent 模型（DeepSeek 官网）
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL')
# 摘要模型（DeepSeek 官网）
SUMMARY_MODEL_NAME = os.getenv('SUMMARY_MODEL')
# 备用模型（阿里百炼，主模型故障时兜底）
FALLBACK_MODEL_NAME = os.getenv('FALLBACK_MODEL')
# 联网搜索模型（阿里百炼，需支持 enable_search）
WEB_SEARCH_MODEL_NAME = os.getenv('WEB_SEARCH_MODEL')

# ---------- 基础设施配置（支持 .env 覆盖，便于本地调试） ----------
# MongoDB 连接地址（Agent checkpoint / 会话历史持久化）
MONGODB_URI = os.getenv(
    'MONGODB_URI',
    'mongodb://root:123456@127.0.0.1:27017/?authSource=admin',
)
# OpenSandbox 沙箱服务端地址
SANDBOX_DOMAIN = os.getenv('SANDBOX_DOMAIN', 'http://127.0.0.1:8080')

# 图表 MCP（AntV mcp-server-chart）连接地址——本机自托管。
# 启动：node "<npm 全局目录>/@antv/mcp-server-chart/build/index.js"
#       --transport streamable --port 1122 --host 127.0.0.1
# （Windows 的 npm 全局目录用 `npm root -g` 查询；
#   --host 127.0.0.1 必须显式指定，默认 localhost 只监听 IPv6 ::1，
#   httpx 经系统代理回连 IPv4 会得到 502）
# 历史方案为魔搭托管版，其 URL 每 24 小时过期（HTTP 410 Url is expired），已弃用。
ANALYSIS_MCP_URL = os.getenv('ANALYSIS_MCP_URL', 'http://127.0.0.1:1122/mcp')