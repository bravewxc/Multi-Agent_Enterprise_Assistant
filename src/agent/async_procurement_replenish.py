"""Async procurement replenish graph for DeepAgents AsyncSubAgent.

结构复刻 async_procurement_analyst.py（异步分析图），差异点：
1. 工具组：replenish_ 前缀的 MCP 聚合工具（而非 analyst 的业务查询工具）
2. 本地工具 replenish_submit：提交补货清单（写沙箱存档），
   并通过 interrupt_on 配置触发人工审批中断——异步图的审批不经过主图，
   中断发生在本进程（2024），恢复由主 Agent 侧 resume_async_task 工具
   经 langgraph_sdk 的 command={"resume": ...} 远程驱动。
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.backends.global_sandbox_manager import get_global_sandbox_sync
from agent.middlewares.image_guard import ImageGuardMiddleware
from agent.middlewares.report_quality import ReportQualityMiddleware
from agent.middlewares.retry_guidance import RetryGuidanceMiddleware
from agent.middlewares.tool_error import ToolErrorMiddleware
from agent.middlewares.tool_metrics import ToolMetricsMiddleware
from agent.env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from agent.tools.chart_generator import create_generate_chart_tool
from agent.tools.mcp_client import (
    CHART_TOOL_PREFIXES,
    MCP_SERVER_CONFIG,
    REPLENISH_TOOL_PREFIXES,
)
from agent.tools.web_search import web_search

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "subagents" / "configs" / "procurement_replenish.yaml"
AGENTS_MD_FILENAME = "/AGENTS.md"

MAIN_MODEL = ChatOpenAI(
    model=DEEPSEEK_MODEL,
    temperature=1.1,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL,
    max_tokens=25600,
    model_kwargs={"extra_body": {"thinking": {"type": "disabled"}}},
)


def _load_replenish_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        raise RuntimeError(f"Empty async replenish config: {CONFIG_PATH}")
    return data


def _backend_factory(runtime):
    return get_global_sandbox_sync()


def create_replenish_submit_tool(sandbox_backend):
    """创建 replenish_submit 工具（本地工具，非 MCP）。

    提交补货清单：把审批通过的计划写入沙箱存档。
    该工具被 interrupt_on 配置拦截——真正执行前会先中断等待人工审批。
    """

    @tool
    async def replenish_submit(replenishment_plan: list, remark: str = "") -> str:
        """
        提交补货建议清单。

        执行前会暂停等待用户批准（approve）或拒绝（reject）：
        - 批准：清单写入沙箱 /analysis/approved_replenishment_{时间戳}.json 存档
        - 拒绝：不写入，返回拒绝说明

        Args:
            replenishment_plan: 建议补货的物料清单，每项含
                partId / partName / suggestQuantity / unitPrice /
                estimatedAmount / supplierId / urgency / abcClass / reason
            remark: 备注说明（如预算约束、特殊要求）
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = f"/analysis/approved_replenishment_{ts}.json"
        payload = {
            "submitted_at": datetime.now().isoformat(),
            "remark": remark,
            "item_count": len(replenishment_plan),
            "total_amount": round(
                sum(float(i.get("estimatedAmount") or 0) for i in replenishment_plan), 2
            ),
            "plan": replenishment_plan,
        }
        sandbox_backend.upload_files([
            (archive_path, json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")),
        ])
        return (
            f"补货清单已批准并存档：{archive_path}\n"
            f"共 {len(replenishment_plan)} 项，总金额 ¥{payload['total_amount']}。"
            f"可在报告中引用该存档路径。"
        )

    replenish_submit.name = "replenish_submit"
    return replenish_submit


async def _load_async_replenish_tools():
    client = MultiServerMCPClient(MCP_SERVER_CONFIG)
    erp_tools = await client.get_tools(server_name="erp-api")
    replenish_tools = [
        t for t in erp_tools
        if t.name.startswith(REPLENISH_TOOL_PREFIXES)
    ]

    sandbox_backend = get_global_sandbox_sync()
    tools = list(replenish_tools) + [web_search, create_replenish_submit_tool(sandbox_backend)]
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
            "Analysis MCP server is unavailable; async replenish will start without chart tools",
            exc_info=True,
        )

    return tools


def _load_replenish_tools_sync():
    try:
        return asyncio.run(_load_async_replenish_tools())
    except RuntimeError as exc:
        raise RuntimeError(
            "Failed to load async procurement replenish MCP tools. "
            "Make sure the MCP server is running before the Agent Protocol server."
        ) from exc


_config = _load_replenish_config()
_tools = _load_replenish_tools_sync()

agent = create_deep_agent(
    model=MAIN_MODEL,
    system_prompt=_config["system_prompt"],
    tools=_tools,
    skills=_config.get("skills", ["/skills/replenish/"]),
    memory=[AGENTS_MD_FILENAME],
    # 中间件栈（first=outermost：请求从列表头往尾流，结果从尾往头回流）：
    # - ToolMetrics：指标采集（最外层，记录所有工具调用成败与耗时）
    # - ReportQuality（loop 改造 A1/A2）：approve 后存档前评审清单，
    #   不达标拦截重写（评审代码与离线 judge_report.py 同源）。
    #   必须在 RetryGuidance 之外——它的批评也是 status="error" 的
    #   ToolMessage，若流经 RetryGuidance 会被误加"错误处理指引"，
    #   污染重写循环的轮次语义
    # - RetryGuidance（loop 改造 C）：给真实工具错误追加分类重试指引。
    #   必须在 ToolError 之外——工具异常被内层转成 error ToolMessage 后
    #   回流到本层才能追加指引（顺序颠倒则永不触发，已实测）
    # - ToolError：工具异常 → error ToolMessage（Agent 可自纠不崩溃）
    # - ImageGuard：图片内容防护（修复方向C坑3：图片回传纯文本模型会 400）
    middleware=[
        ToolMetricsMiddleware(),
        ReportQualityMiddleware(),
        RetryGuidanceMiddleware(),
        ToolErrorMiddleware(),
        ImageGuardMiddleware(),
    ],
    backend=_backend_factory,
    checkpointer=None,
    # HITL：补货清单提交前人工审批。
    # 注意（与同步子 Agent 的差异）：异步图的 interrupt_on 不会从主图传递，
    # 必须在远端图自身配置；中断发生在本进程，run 状态转为 interrupted。
    interrupt_on=_config.get("interrupt_on"),
    name="procurement_replenish_async",
)
