"""
主 Agent 入口模块。

使用 DeepAgents `create_deep_agent` 将所有组件串联为一个可运行的
ERP 采购智能助手。采用 Graph Factory 模式：启动时预计算可复用组件，
每次请求基于 per-user 沙箱轻量创建 agent graph，实现用户级沙箱隔离。

使用方式:
    from agent.main_agent import precompute_agent_context, create_main_agent

    # 启动时
    precomputed = await precompute_agent_context()

    # 每次请求
    agent_graph = await create_main_agent(
        config,
        sandbox_backend=user_sandbox,
        precomputed=precomputed,
    )
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

from deepagents import AsyncSubAgent, create_deep_agent
from deepagents.backends import CompositeBackend, StoreBackend
from deepagents.backends.protocol import SandboxBackendProtocol
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain_core.runnables import RunnableConfig

from agent.config import (
    AGENTS_MD_FILENAME,
    CHECKPOINTER,
    DOWNLOAD_DIR,
    LOCAL_AGENTS_MD,
    MAIN_MODEL,
    SKILLS_STORE_NAMESPACE,
    STORE,
    SUMMARY_MODEL,
)
from agent.memory.prompts import system_prompt
from agent.middleware_config import create_order_middleware
from agent.middlewares.context_injection import ContextInjectionMiddleware
from agent.middlewares.image_guard import ImageGuardMiddleware
from agent.middlewares.memory_update import MemoryUpdateMiddleware
from agent.middlewares.retry_guidance import RetryGuidanceMiddleware
from agent.middlewares.sandbox_breaker import SandboxCircuitBreakerMiddleware
from agent.middlewares.sandbox_health import SandboxHealthMiddleware
from agent.middlewares.skills_sync import SkillsSyncMiddleware
from agent.middlewares.tool_error import ToolErrorMiddleware
from agent.middlewares.tool_metrics import ToolMetricsMiddleware
from agent.middlewares.tools_summarization import build_summarization_middleware
from agent.middlewares.user_skills_restore import UserSkillsRestoreMiddleware
from agent.schema import ProcurementContext
from agent.subagents.loader import load_subagent_configs, resolve_subagent_tools
from agent.tools.chart_generator import create_generate_chart_tool
from agent.tools.hitl_tools import request_order_info
from agent.tools.assign_skill import create_assign_skill_tool
from agent.tools.download_sandbox_file import create_download_tool
from agent.tools.resume_async_task import create_resume_async_task_tool
from agent.tools.mcp_client import load_mcp_tools
from agent.tools.web_search import web_search


ASYNC_ANALYST_GRAPH_ID = "procurement_analyst_async"
ASYNC_ANALYST_URL = os.environ.get(
    "ASYNC_AGENT_PROTOCOL_URL",
    "http://127.0.0.1:2024",
)

# 智能补货异步子 Agent：与 analyst 共用同一个 Agent Protocol 进程（2024），
# 但注册为独立的 graph（见 langgraph.json "graphs" 的第二个条目）
ASYNC_REPLENISH_GRAPH_ID = "procurement_replenish_async"
ASYNC_REPLENISH_URL = os.environ.get(
    "ASYNC_AGENT_PROTOCOL_URL",
    "http://127.0.0.1:2024",
)

ASYNC_ANALYST_INSTRUCTIONS = """
## 异步采购分析任务

当用户提出耗时的采购分析、供应商比价、行情调研、成本评估、报告生成或需要多步数据收集的任务时，
必须使用 `start_async_task` 启动 `procurement-analyst` 后台任务。

严禁使用同步 `task` 工具启动 `procurement-analyst`。`task` 工具只用于 `procurement-order` 等同步订单任务。

供应商比较类问题（"A 和 B 哪家好/哪家划算"）属于比价分析，必须走本任务（基于 ERP 真实数据），
不得用 `web_search` 泛泛回答。用户明确拒绝后台任务时仍须委派并向用户说明原因
（主 Agent 无 ERP 数据查询工具，无法凭空给出真实数据）。

### 启动后纪律（防轮询）
启动任务后，本轮回答必须立即以完整 task_id 告知用户收尾。
本轮内严禁再调用任何异步任务工具（check_async_task / list_async_tasks /
cancel_async_task / update_async_task 均禁止）——任务状态由前端自动轮询展示。
只有用户在后续轮次明确询问进度、结果、取消或补充要求时，才调用对应工具。
"""

ASYNC_REPLENISH_INSTRUCTIONS = """
## 智能补货任务（异步 + 人工审批闭环）

当用户提出补货建议、缺货分析、该订多少、库存补充计划、再订货点等需求时，
必须使用 `start_async_task` 启动 `procurement-replenish` 后台任务（subagent_type 为
"procurement-replenish"）。严禁用同步 `task` 工具启动它。

任务描述中应包含用户关注的范围（如"全部预警物料"、"只看刹车类"）和输出要求。

### 启动后纪律（防轮询）
启动任务后，本轮回答必须立即以完整 task_id 告知用户收尾。
本轮内严禁再调用任何异步任务工具（check_async_task / list_async_tasks /
cancel_async_task / update_async_task 均禁止）——任务状态由前端自动轮询展示。

### 审批闭环（后续轮次的关键流程）

补货任务生成报告后会调用 `replenish_submit` 提交补货清单，此时任务会**中断等待人工审批**：
1. 用户询问任务状态时，调用 `check_async_task(task_id)`；
   若返回 status 为 "interrupted"，或 result 内容提到"提交补货清单/等待审批"，
   说明清单正在等待审批。
2. 把等待审批的清单要点转告用户，请用户明确表态（批准 / 拒绝）。
3. 用户表态后，调用 `resume_async_task(task_id, decision, reason)`：
   - 批准 → decision="approve"（不带 reason）；
   - 拒绝 → decision="reject"；**用户给出了拒绝理由（如"总额超预算，砍到 1 万以内"）
     时必须把理由原样传入 reason**——任务会按理由修订清单并重新提交审批，
     形成"拒绝 → 修订 → 再审批"的协商循环；用户未给理由则 reason 留空。
     若用户只说"拒绝"而理由不明，先问一句"需要它按什么方向调整吗？"再传达。
4. 恢复后再按需 `check_async_task` 查询最终结果，转述给用户。

不要替用户决定 approve/reject；用户表述模糊时先确认。
同一任务的协商循环最多 3 轮，超过后建议用户重新发起任务。
"""


def _setup_logging() -> None:
    env = os.environ.get("APP_ENV", "development")
    if env == "production":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            filename="erp_agent.log",
            filemode="a",
        )
    else:
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
        )

_setup_logging()
logger = logging.getLogger(__name__)


# ============================================================
# PrecomputedContext — 启动时预计算的可复用组件
# ============================================================

@dataclass
class PrecomputedContext:
    """Phase 2/3/5 预计算结果的不可变容器。

    仅包含不依赖 sandbox_backend 的组件（MCP 工具、图表工具、YAML 配置）。
    sandbox 依赖的工具（assign_skill、download_sandbox_file）和 backend 依赖的
    中间件在 create_main_agent() 中按请求动态创建。
    """
    all_mcp_tools: list = field(default_factory=list)
    analyst_mcp_tools: list = field(default_factory=list)
    order_mcp_tools: list = field(default_factory=list)
    chart_mcp_tools: list = field(default_factory=list)
    extra_mcp_tools: list = field(default_factory=list)
    generate_visualization: object = None
    raw_subagent_configs: list = field(default_factory=list)


async def precompute_agent_context() -> PrecomputedContext:
    """Phase 2/3/5 预计算，启动时执行一次，所有请求复用。"""
    logger.info("=== 预计算 Agent 上下文（Phase 2/3/5）===")

    # Phase 2: MCP 工具加载
    logger.info("Phase 2: 加载 MCP 工具...")
    try:
        all_mcp_tools, analyst_mcp_tools, order_mcp_tools, chart_mcp_tools = (
            await load_mcp_tools()
        )
    except Exception:
        logger.exception("MCP 工具加载失败")
        raise RuntimeError("MCP 工具加载失败，无法预计算")

    # Phase 3: 可视化工具合并
    logger.info("Phase 3: 合并可视化工具 (26→1)...")
    generate_visualization, extra_mcp_tools = create_generate_chart_tool(chart_mcp_tools)
    if extra_mcp_tools:
        logger.info(f"  保留独立工具: {[t.name for t in extra_mcp_tools]}")

    # Phase 5: 子 Agent YAML 配置加载
    logger.info("Phase 5: 加载子 Agent YAML 配置...")
    raw_configs = load_subagent_configs()
    if not raw_configs:
        logger.warning("  未找到任何子 Agent 配置")
    else:
        logger.info(f"  已加载 {len(raw_configs)} 个子 Agent 配置")

    logger.info("=== 预计算完成 ===")
    return PrecomputedContext(
        all_mcp_tools=all_mcp_tools,
        analyst_mcp_tools=analyst_mcp_tools,
        order_mcp_tools=order_mcp_tools,
        chart_mcp_tools=chart_mcp_tools,
        extra_mcp_tools=extra_mcp_tools,
        generate_visualization=generate_visualization,
        raw_subagent_configs=raw_configs,
    )


# ============================================================
# create_main_agent — 每次请求基于 per-user 沙箱创建 agent graph
# ============================================================

async def create_main_agent(
    config: RunnableConfig,
    *,
    sandbox_backend: SandboxBackendProtocol,
    precomputed: PrecomputedContext,
):
    """创建 ERP 采购智能助手的 per-request graph factory。

    每次请求调用，使用预计算的 MCP 工具/YAML 配置 + 外部传入的 per-user 沙箱，
    轻量创建 agent graph。SandboxBackendProxy 保证沙箱热替换不丢引用。

    Args:
        config: LangGraph RunnableConfig，含 thread_id + user_id。
        sandbox_backend: per-user 沙箱后端（SandboxBackendProxy）。
        precomputed: 启动时预计算的 MCP 工具/YAML 配置。
    """
    user_id = config["configurable"]["user_id"]
    logger.info(f"=== 为用户 {user_id} 创建 Agent Graph ===")

    # ---- Phase 1: CompositeBackend（路由：默认走沙箱，持久化路径走 Store）----
    # deepagents 0.5+ 的 StoreBackend 通过 get_store()/get_runtime() 在每次
    # 文件操作时自取 store 与运行时上下文，构造时不再需要传 runtime
    # （旧写法已废弃，0.7.0 移除）。namespace 工厂延迟到操作时求值，
    # 仍能按当次请求解析 user_id。
    # 内部 sandbox_backend 是 SandboxBackendProxy（热替换不丢引用）。
    composite_backend = CompositeBackend(
        default=sandbox_backend,
        routes={
            "/memories/": StoreBackend(  # langgraph 框架的store来存数据
                store=STORE,
                namespace=lambda rt: (getattr(rt.context, "user_id", "laoxiao"),),
            ),
            "/persisted-skills/": StoreBackend(
                store=STORE,
                namespace=lambda rt: SKILLS_STORE_NAMESPACE,
            ),
        },
    )

    # ---- Phase 1.4: 上传 AGENTS.md 到沙箱 ----
    logger.info("Phase 1.4: 上传 AGENTS.md 到沙箱...")
    ag_md_content = LOCAL_AGENTS_MD.read_text(encoding="utf-8")
    sandbox_backend.upload_files([("/AGENTS.md", ag_md_content.encode("utf-8"))])

    # ---- Phase 2/3/5: 使用预计算结果 ----
    logger.info("Phase 2-5: 使用预计算的 MCP 工具 + 图表工具 + YAML 配置...")
    generate_visualization = precomputed.generate_visualization
    extra_mcp_tools = precomputed.extra_mcp_tools

    # ---- Phase 3.6: 创建 sandbox 依赖工具（per-request）----
    logger.info("Phase 3.6: 创建 sandbox 依赖工具...")
    assign_skill = create_assign_skill_tool(
        sandbox_backend,
        store=STORE,
        skills_namespace=SKILLS_STORE_NAMESPACE,
    )
    download_sandbox_file = create_download_tool(sandbox_backend, DOWNLOAD_DIR)
    # 异步任务中断恢复（HITL 审批闭环：补货清单批准/拒绝）
    resume_async_task = create_resume_async_task_tool()

    # ---- Phase 4: 构建工具池 ----
    logger.info("Phase 4: 构建工具池...")
    available_tools = (
        list(precomputed.analyst_mcp_tools)
        + list(precomputed.order_mcp_tools)
        + list(extra_mcp_tools)
        + [generate_visualization]
        + [web_search]
        + [request_order_info]
        + [assign_skill]
        + [download_sandbox_file]
    )
    logger.info(f"  工具池: {len(available_tools)} 个工具")

    # ---- Phase 6: 子 Agent 中间件 ----
    logger.info("Phase 6: 创建子 Agent 中间件...")
    extra_middleware = {
        "procurement-order": create_order_middleware(),
    }

    # ---- Phase 7: 子 Agent 工具解析 ----
    logger.info("Phase 7: 解析子 Agent 工具名称...")
    # 走异步通道的子 Agent（图定义在独立 Agent Protocol 进程）要排除出同步列表，
    # 否则会被 resolve_subagent_tools 编译进主图（其工具名也解析不到）
    async_subagent_names = {"procurement-analyst", "procurement-replenish"}
    sync_subagent_configs = [
        c for c in precomputed.raw_subagent_configs
        if c.get("name") not in async_subagent_names
    ]
    sync_subagents = resolve_subagent_tools(
        sync_subagent_configs,
        available_tools,
        extra_middleware=extra_middleware,
    )
    async_subagents: list[AsyncSubAgent] = [
        {
            "name": "procurement-analyst",
            "description": (
                "耗时采购分析专家。负责供应商比价、物料行情分析、采购策略建议、"
                "市场调研、成本评估和报告生成。后台运行，适合长任务。"
            ),
            "graph_id": ASYNC_ANALYST_GRAPH_ID,
            "url": ASYNC_ANALYST_URL,
        },
        {
            "name": "procurement-replenish",
            "description": (
                "智能补货专家。基于库存预警与采购历史计算再订货点（ROP）、建议补货量、"
                "ABC 分类与优先级，生成补货建议报告，并提交清单等待人工审批。"
                "后台运行，适合长任务。"
            ),
            "graph_id": ASYNC_REPLENISH_GRAPH_ID,
            "url": ASYNC_REPLENISH_URL,
        },
    ]
    subagents = sync_subagents + async_subagents
    logger.info(f"  已解析 {len(subagents)} 个子 Agent")

    # ---- Phase 8: 主 Agent 中间件栈 ----
    logger.info("Phase 8: 构建主 Agent 中间件栈...")
    main_middleware = [
        # 0a. 工具指标采集（评估方向 A）：所有工具调用 → MongoDB tool_call_metrics
        #     必须最外层（first=outermost，先计时后转换）
        ToolMetricsMiddleware(),
        # 0b. 错误分类重试指引（loop 改造 C）：transient/permanent + hint + 预算。
        #     必须在 ToolErrorMiddleware 之外（列表更靠前）——工具抛出的异常由
        #     内层 ToolError 转换成 status="error" 的 ToolMessage 后，回流到
        #     本层才能追加指引（实测：顺序颠倒则指引永远不触发）
        RetryGuidanceMiddleware(),
        # 0c. 工具异常 → status="error" 的 ToolMessage（Agent 可自我纠正不崩溃）
        ToolErrorMiddleware(),
        # 0d. 图片内容防护（修复方向C坑3）：工具返回的 image content 替换为
        #     文字说明，防止纯文本模型被 400 击穿（详见 image_guard.py）
        ImageGuardMiddleware(),
        # 1. 沙箱健康守护：每次 agent step 前 ping → 失败自动恢复
        SandboxHealthMiddleware(
            sandbox_backend=sandbox_backend,
            user_id=user_id,
            agents_md_content=ag_md_content.encode("utf-8"),
        ),
        # 2. 用户上下文注入
        ContextInjectionMiddleware(),
        # 3. 技能同步（本地 → 沙箱）
        SkillsSyncMiddleware(sandbox_backend),
        # 4. 持久化技能恢复（StoreBackend → 沙箱）
        UserSkillsRestoreMiddleware(sandbox_backend, SKILLS_STORE_NAMESPACE),
        # 5. 对话摘要 + compact_conversation 工具
        build_summarization_middleware(composite_backend, SUMMARY_MODEL),
        # 6. 用户记忆更新
        MemoryUpdateMiddleware(model=SUMMARY_MODEL),
        # 7. 沙箱熔断：连续沙箱错误 ≥ 阈值 → jump_to=end
        SandboxCircuitBreakerMiddleware(),
        # 8. 调用限制
        ModelCallLimitMiddleware(run_limit=50),
        # 9. 工具调用限制
        ToolCallLimitMiddleware(run_limit=200),
    ]

    # ---- Phase 9: create_deep_agent ----
    logger.info("Phase 9: 创建 Deep Agent...")
    agent_graph = create_deep_agent(
        model=MAIN_MODEL,
        system_prompt=(
            system_prompt + "\n\n" + ASYNC_ANALYST_INSTRUCTIONS
            + "\n\n" + ASYNC_REPLENISH_INSTRUCTIONS
        ),
        skills=["/skills/main/"],
        memory=[AGENTS_MD_FILENAME],
        tools=[web_search, assign_skill, download_sandbox_file, resume_async_task],
        subagents=subagents,
        middleware=main_middleware,
        backend=composite_backend,
        store=STORE,
        checkpointer=CHECKPOINTER,
        context_schema=ProcurementContext,
    )

    logger.info(f"=== 用户 {user_id} Agent Graph 创建完成 ===")
    return agent_graph
