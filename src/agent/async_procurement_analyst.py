"""Async procurement analyst graph for DeepAgents AsyncSubAgent."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import yaml
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.backends.global_sandbox_manager import get_global_sandbox_sync
from agent.middlewares.image_guard import ImageGuardMiddleware
from agent.middlewares.tool_error import ToolErrorMiddleware
from agent.middlewares.tool_metrics import ToolMetricsMiddleware
from agent.env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from agent.tools.chart_generator import create_generate_chart_tool
from agent.tools.mcp_client import (
    ANALYST_TOOL_PREFIXES,
    CHART_TOOL_PREFIXES,
    MCP_SERVER_CONFIG,
)
from agent.tools.web_search import web_search

logger = logging.getLogger(__name__)

SRC_DIR = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "subagents" / "configs" / "procurement_analyst.yaml"
AGENTS_MD_FILENAME = "/AGENTS.md"

MAIN_MODEL = ChatOpenAI(
    model=DEEPSEEK_MODEL,
    temperature=1.1,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL,
    max_tokens=25600,
    model_kwargs={"extra_body": {"thinking": {"type": "disabled"}}},
)

def _load_analyst_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        raise RuntimeError(f"Empty async analyst config: {CONFIG_PATH}")
    return data


def _backend_factory(runtime):
    return get_global_sandbox_sync()


async def _load_async_analyst_tools():
    client = MultiServerMCPClient(MCP_SERVER_CONFIG)
    erp_tools = await client.get_tools(server_name="erp-api")
    analyst_tools = [
        t for t in erp_tools
        if t.name.startswith(ANALYST_TOOL_PREFIXES)
    ]

    tools = list(analyst_tools) + [web_search]
    try:
        analysis_tools = await client.get_tools(server_name="analysis")
        chart_tools = [
            t for t in analysis_tools
            if t.name.startswith(CHART_TOOL_PREFIXES)
        ]
        if chart_tools:
            generate_visualization, extra_mcp_tools = create_generate_chart_tool(chart_tools)
            tools.extend(extra_mcp_tools)
            tools.append(generate_visualization)
    except Exception:
        logger.warning(
            "Analysis MCP server is unavailable; async analyst will start without chart tools",
            exc_info=True,
        )

    return tools


def _load_analyst_tools_sync():
    try:
        return asyncio.run(_load_async_analyst_tools())
    except RuntimeError as exc:
        raise RuntimeError(
            "Failed to load async procurement analyst MCP tools. "
            "Make sure the MCP server is running before the Agent Protocol server."
        ) from exc


_config = _load_analyst_config()
_tools = _load_analyst_tools_sync()

agent = create_deep_agent(  # 创建了一个Agent
    model=MAIN_MODEL,
    system_prompt=_config["system_prompt"],
    tools=_tools,
    skills=_config.get("skills", ["/skills/procurement/"]),
    memory=[AGENTS_MD_FILENAME],
    # 评估方向 A/B：指标采集（最外层）+ 错误分类重试指引（loop 改造 C，
    # 在 ToolError 之外——异常被内层转换成 error ToolMessage 后回流至此追加指引）
    # + 异常转 ToolMessage（内层，Agent 可自纠）+ 图片内容防护
    middleware=[
        ToolMetricsMiddleware(),
        RetryGuidanceMiddleware(),
        ToolErrorMiddleware(),
        ImageGuardMiddleware(),
    ],
    backend=_backend_factory,
    checkpointer=None,
    name="procurement_analyst_async",
)
