"""
DeepAgent Chat API - FastAPI 主应用

提供基于 DeepAgent 的 AI 对话系统后端 API
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_view.web_config import API_TITLE, API_VERSION, API_DESCRIPTION
from api_view.api import async_tasks, chat, history
from api_view.agent_loader import agent_loader


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在应用启动时初始化 Agent，在应用关闭时清理资源
    """
    # ============================================================
    # 应用启动时执行
    # ============================================================
    print("=" * 50)
    print("正在启动 DeepAgent Chat API...")
    print("=" * 50)

    # 初始化 Agent
    await agent_loader.initialize()

    print("=" * 50)
    print("DeepAgent Chat API 启动成功!")
    print("=" * 50)

    # 继续运行
    yield

    # ============================================================
    # 应用关闭时执行
    # ============================================================
    print("=" * 50)
    print("正在关闭 DeepAgent Chat API...")
    print("=" * 50)

    # 清理所有沙箱 + MongoDB 连接
    await agent_loader.shutdown()

    print("DeepAgent Chat API 已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

# ============================================================
# CORS 中间件配置
# ============================================================
# 允许跨域请求，方便前端开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 注册路由
# ============================================================
# 对话相关接口
app.include_router(chat.router, prefix="/api", tags=["对话"])
# 历史记录相关接口
app.include_router(history.router, prefix="/api", tags=["历史记录"])
# AsyncSubAgent task status API
app.include_router(async_tasks.router, prefix="/api", tags=["Async Tasks"])


# ============================================================
# 根路径
# ============================================================
@app.get("/", tags=["首页"])
async def root():
    """
    根路径

    返回 API 基本信息
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": "基于 DeepAgent 的 AI 对话系统 API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============================================================
# 健康检查
# ============================================================
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口

    用于检查服务是否正常运行
    """
    return {
        "status": "healthy",
        "service": API_TITLE,
        "version": API_VERSION
    }


# ============================================================
# 启动命令
# ============================================================
# uvicorn api_view.web_main:app --reload --host 0.0.0.0 --port 8000
