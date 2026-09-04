from datetime import timedelta
from pathlib import Path

import httpx
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.store.memory import InMemoryStore
from opensandbox.config import ConnectionConfigSync
from pymongo import MongoClient

from agent.env_utils import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    ALIBABA_API_KEY, ALIBABA_BASE_URL,
    SUMMARY_MODEL_NAME, FALLBACK_MODEL_NAME,
    MONGODB_URI, SANDBOX_DOMAIN,
)

# ---------- 模型配置 ----------
# 模型名称统一由 .env 控制（DEEPSEEK_MODEL / SUMMARY_MODEL / FALLBACK_MODEL）
# 主 Agent 模型
MAIN_MODEL = ChatOpenAI(
    model=DEEPSEEK_MODEL,
    temperature=1.1,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL,
    max_tokens=25600,
    model_kwargs={
        "extra_body": {
            "thinking": {"type": "disabled"}
        }
    }
)
# 摘要专用模型（摘要需要稳定输出，temperature 设为较低值）
SUMMARY_MODEL = ChatOpenAI(
    model=SUMMARY_MODEL_NAME,
    temperature=0.3,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL,
    max_tokens=25600,
    model_kwargs={
        "extra_body": {
            "thinking": {"type": "disabled"}
        }
    }
)
# 备用模型（当主模型故障时使用）
# 阿里百炼 OpenAI 兼容模式，模型名由 .env 的 FALLBACK_MODEL 控制
FALLBACK_MODEL = ChatOpenAI(
    model=FALLBACK_MODEL_NAME,
    temperature=1.0,
    openai_api_key=ALIBABA_API_KEY,
    openai_api_base=ALIBABA_BASE_URL,
    max_tokens=8192,
)

# ---------- 沙箱配置 ----------
# OpenSandbox 沙箱配置连接（地址由 .env 的 SANDBOX_DOMAIN 控制）
SANDBOX_CONFIG = ConnectionConfigSync(
    domain=SANDBOX_DOMAIN,
    use_server_proxy=True,
    request_timeout=timedelta(seconds=60),
    transport=httpx.HTTPTransport(limits=httpx.Limits(max_connections=20)),
)

# ---------- 路径常量 ----------
EXAMPLE_DIR = Path(__file__).parent.parent
print(f'当前代码执行的工作目录为：{EXAMPLE_DIR}')
# 沙箱内技能根路径
SANDBOX_SKILLS_ROOT = "/skills"
# 沙箱内记忆根路径（用户私有记忆存放处）
SANDBOX_MEMORIES_ROOT = "/memories"
# 沙箱内分析中间文件存放目录
SANDBOX_ANALYSIS_ROOT = "/analysis"
# 沙箱内数据文件存放目录
SANDBOX_DATA_ROOT = "/data"
# 本地技能资源目录（项目内的路径，相对于项目根）
LOCAL_SKILLS_DIR = EXAMPLE_DIR / "skills"
# 本地下载目录（从沙箱下载文件的目标路径）
DOWNLOAD_DIR = EXAMPLE_DIR / "download"
# 本地子 Agent 配置目录
LOCAL_SUBAGENT_CONFIG_DIR = EXAMPLE_DIR / "agent/subagents"
# 本地的Agent记忆文件
LOCAL_AGENTS_MD = EXAMPLE_DIR / "agent/memory/AGENTS.md"

# ---------- 文件名常量 ----------
# 主 Agent 只读指引文件（上传到沙箱 /AGENTS.md）
AGENTS_MD_FILENAME = "/AGENTS.md"
# 用户偏好文件名（在 /memories/{user_id}/ 下）
USER_PREFERENCES_FILENAME = "preferences.md"

# ---------- 用户技能持久化 ----------
# 技能持久化 StoreBackend 路由路径
PERSISTED_SKILLS_ROOT = "/persisted-skills"
# 技能 StoreBackend 命名空间（按 Agent scope 组织，无用户隔离）
SKILLS_STORE_NAMESPACE = ("skills",)
# 子 Agent 名称 → 技能 scope 目录映射
SCOPE_MAP = {
    "main": "main",
    "procurement-analyst": "procurement",
    "procurement-order": "order",
    "procurement-replenish": "replenish",
}

# ---------- 中间件参数 ----------

# ---------- MongoDB 配置（用于持久化 Agent 短期记忆/checkpoint） ----------
# 连接地址由 .env 的 MONGODB_URI 控制（本地调试默认指向本机 Docker MongoDB）
MONGODB_DB_NAME = "langchain_db"
MONGODB_CHECKPOINT_COLLECTION = "checkpoints"

# ---------- 持久化存储 ----------
# InMemoryStore: 开发阶段使用。生产环境替换为持久 Store。
STORE = InMemoryStore()

# MongoDBSaver: Agent 对话状态的 MongoDB 持久化 checkpointer。
# 支持 Human-in-the-Loop（interrupt 状态持久化）和跨重启对话恢复。
_mongodb_client = MongoClient(MONGODB_URI)
CHECKPOINTER = MongoDBSaver(
    client=_mongodb_client,
    db_name=MONGODB_DB_NAME,
    checkpoint_collection_name=MONGODB_CHECKPOINT_COLLECTION,
)


