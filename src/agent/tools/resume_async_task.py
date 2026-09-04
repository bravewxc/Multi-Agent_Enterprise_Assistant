"""异步子 Agent 中断恢复工具。

背景：deepagents 的 async_subagents 中间件只提供 start/check/list，
没有"恢复已中断异步任务"的工具。异步图（如 procurement-replenish）
的 HITL 审批中断发生在 Agent Protocol 进程（2024），run 状态转为
interrupted 后，需要通过 langgraph_sdk 的 runs.create(command={"resume": ...})
远程驱动恢复——本工具把这个能力暴露给主 Agent 的模型调用。
"""
from __future__ import annotations

import logging
import os

from langchain_core.tools import tool
from langgraph_sdk import get_client

logger = logging.getLogger(__name__)

ASYNC_AGENT_PROTOCOL_URL = os.environ.get(
    "ASYNC_AGENT_PROTOCOL_URL",
    "http://127.0.0.1:2024",
)

_VALID_DECISIONS = ("approve", "reject")


def create_resume_async_task_tool():
    """创建 resume_async_task 工具工厂函数。"""

    @tool
    async def resume_async_task(task_id: str, decision: str, reason: str = "") -> str:
        """
        恢复因人工审批而中断的异步后台任务（如补货清单审批）。

        当 check_async_task 返回 status=interrupted（任务正在等待人工审批）时，
        用本工具传达用户的审批决定：
        - "approve"：批准 → 任务从中断点继续执行（如：补货清单写入存档）
        - "reject"：拒绝 → 任务按拒绝分支处理。若用户给出了拒绝理由
          （如"总额超预算，砍到 1 万以内"），必须把理由原样传入 reason——
          理由会传达给任务，它会按理由修订清单并重新提交审批，
          形成"拒绝 → 修订 → 再审批"的协商循环（同一任务最多协商 3 轮）。

        Args:
            task_id: 中断任务的完整 task_id（即 check_async_task 返回的 thread_id）
            decision: 审批决定，只能是 "approve" 或 "reject"
            reason: 拒绝理由（可选，仅 reject 时有效）。用户拒绝时若给出
                理由必须传入；无理由的拒绝留空即可。
        """
        decision = decision.strip().lower()
        if decision not in _VALID_DECISIONS:
            return (
                f"错误：decision 必须是 {' 或 '.join(_VALID_DECISIONS)}，收到: {decision}。"
                f"请确认用户意图后重试。"
            )
        reason = (reason or "").strip()
        if decision == "approve" and reason:
            # approve 的理由没有透传渠道（框架 ApproveDecision 无 message 字段），
            # 明确告知而非静默丢弃——调用方（模型）可决定如何转达
            return (
                f"提示：approve 不支持附加理由（框架限制），任务 {task_id} 未恢复。"
                f"如需传达补充说明，请在恢复后用对话告知用户。"
                f"请不带 reason 参数重试以完成批准。"
            )

        client = get_client(url=ASYNC_AGENT_PROTOCOL_URL)
        try:
            # 从该 thread 最近一次 run 取 assistant_id（即当初启动的图），
            # 恢复必须用同一个 assistant 发起
            runs = await client.runs.list(task_id, limit=5)
            if not runs:
                return f"错误：未找到任务 {task_id} 的运行记录，请核对 task_id。"

            latest = runs[0]

            # 中断判定：本版本 langgraph-api（0.7.90）在图挂起等待审批时
            # run.status 仍为 "success"，真正的中断标志在 thread state 的
            # tasks[].interrupts 里（HumanInTheLoopMiddleware 挂起的 action_requests）
            state = await client.threads.get_state(task_id)
            has_interrupt = False
            tasks = state.get("tasks") if isinstance(state, dict) else getattr(state, "tasks", None)
            for t in tasks or []:
                for interrupt in (t.get("interrupts") if isinstance(t, dict) else getattr(t, "interrupts", None)) or []:
                    value = interrupt.get("value") if isinstance(interrupt, dict) else getattr(interrupt, "value", None)
                    if isinstance(value, dict) and "action_requests" in value:
                        has_interrupt = True
            if not has_interrupt:
                status = str(latest.get("status", "unknown"))
                return (
                    f"任务 {task_id} 当前没有等待审批的中断（run 状态 {status}），"
                    f"无需恢复。只有提交了清单等待审批的任务才能 resume。"
                )

            assistant_id = latest.get("assistant_id")
            # reject + reason：理由经框架 RejectDecision.message 透传给图内模型
            # （langchain HumanInTheLoopMiddleware._process_decision 会把 message
            #   作为拒绝 ToolMessage 的内容返回给模型——协商循环的传令通道）
            decision_payload = {"type": decision}
            if decision == "reject" and reason:
                decision_payload["message"] = reason
            run = await client.runs.create(
                thread_id=task_id,
                assistant_id=assistant_id,
                command={"resume": {"decisions": [decision_payload]}},
            )
        except Exception as e:
            logger.warning("Failed to resume async task %s: %s", task_id, e)
            return f"恢复失败：{e}"

        if decision == "reject" and reason:
            return (
                f"已传达拒绝决定及理由（{reason[:80]}），任务 {task_id} 将按理由"
                f"修订清单并重新提交审批（协商循环），run_id: {run.get('run_id')}。"
                f"稍后用 check_async_task 查询修订版清单。"
            )
        return (
            f"已传达审批决定（{decision}），任务 {task_id} 从中断点继续执行，"
            f"run_id: {run.get('run_id')}。稍后可用 check_async_task 查询最终结果。"
        )

    resume_async_task.name = "resume_async_task"
    return resume_async_task
