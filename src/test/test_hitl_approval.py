"""方向 C 集成回归：HITL 补货审批链路（中断 → 摘要 → approve/reject → 存档）。

被测对象（自研比重最高、框架版本最易碎的链路）：
- 2024 进程的 procurement_replenish_async 图（interrupt_on=replenish_submit）
- api_view/api/async_tasks.py 的中断判定（_extract_interrupt_info_raw）
- agent/tools/resume_async_task.py 的恢复工具（白名单/无中断拒绝）

6 个用例（确定性断言为主，顺序执行、共享 thread 状态）：
  1. 补货任务必中断      —— 直接把 0.7.90 的 run.status 坑锁成永久回归：
                           中断存在时 run.status 仍是 "success"，判定必须查
                           state.tasks[].interrupts（断言两者，缺一不可）
  2. 审批摘要提取        —— _extract_interrupt_info_raw 输出"等待审批"+项数+总额
  3. approve 后恢复且存档 —— 沙箱出现 approved_replenishment_*.json，字段齐全
  4. reject 后不执行工具  —— 无新存档 + 图正常收尾（不挂死）
  5. 非法 decision 被拒   —— 白名单校验（resume_async_task.py L44-49 行为）
  6. 无中断时 resume 被拒 —— "无挂起中断"错误（L64-77 行为）
  7. 审批参数指纹绑定     ——（安全整改 P1-5）审批时用户看到的清单与执行后
                           沙箱存档逐项一致：approve 只放行原始 tool_call，
                           不存在"确认 A、执行 B"的参数替换窗口

前置：2024 在线（否则集成用例 SKIP），MongoDB/OpenSandbox/MCP(8000) 已启动。
运行：cd 项目根 && .venv\\Scripts\\python.exe -m test.test_hitl_approval
耗时：约 3-8 分钟（两个真实补货分析任务，LLM 驱动）。
"""
from __future__ import annotations

import asyncio
import json
import sys
import time

# ---- 共享测试状态（顺序执行：1 建立 → 2/3/6 消费 thread_a；4 建立 thread_b → 5 消费）----
S: dict = {}


# ============================================================
# 基础设施：2024 客户端 / 轮询器
# ============================================================
def _client():
    from langgraph_sdk import get_client
    return get_client(url="http://127.0.0.1:2024")


async def _2024_online() -> bool:
    """2024 健康检查：建一个空 thread 并读 state（SDK 0.4.3 无 assistants.list）。"""
    try:
        client = _client()
        th = await client.threads.create()
        await client.threads.get_state(th["thread_id"])
        return True
    except Exception:
        return False


def _interrupts_of(state: dict) -> list:
    """从 thread state 提取 HITL 中断（action_requests 型）。

    兼容 dict / 对象两种形态（langgraph_sdk 返回 dict，字段缺失防御式取值）。
    """
    tasks = (state or {}).get("tasks", []) if isinstance(state, dict) else []
    found = []
    for t in tasks:
        for it in (t.get("interrupts") or []):
            v = it.get("value") if isinstance(it, dict) else None
            if isinstance(v, dict) and "action_requests" in v:
                found.append(v)
    return found


async def _get_state_retry(client, thread_id: str, retries: int = 3):
    """get_state 带瞬时网络错误重试。

    实测坑（2026-09-02）：每 5s 轮询时，httpx 连接池里的闲置连接会被
    服务端 keep-alive 超时关闭，复用死连接报 RemoteProtocolError
    "Server disconnected without sending a response"——一次网络抖动
    不应废掉整个用例，重试即可（重试时 httpx 会建新连接）。
    """
    for i in range(retries):
        try:
            return await client.threads.get_state(thread_id)
        except Exception as e:
            if i == retries - 1:
                raise
            print(f"      [retry] get_state 瞬时错误（{type(e).__name__}），1s 后重试")
            await asyncio.sleep(1)


async def _wait_interrupt(thread_id: str, timeout_s: int = 480) -> dict:
    """轮询 thread state 直到出现待审批中断（补货分析是 LLM 驱动，需数分钟）。"""
    client = _client()
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        state = await _get_state_retry(client, thread_id)
        ints = _interrupts_of(state)
        if ints:
            return ints[0]
        await asyncio.sleep(5)
    raise TimeoutError(f"{thread_id} 在 {timeout_s}s 内未出现审批中断")


async def _wait_settled(thread_id: str, timeout_s: int = 300) -> dict:
    """resume 后轮询到图收尾：无中断 + 最新 run 进入终态且非 error。"""
    client = _client()
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        state = await _get_state_retry(client, thread_id)
        if not _interrupts_of(state):
            runs = await client.runs.list(thread_id, limit=1)
            if runs and str(runs[0].get("status")) in {"success", "error", "timeout", "cancelled"}:
                return {"status": str(runs[0].get("status")), "state": state}
        await asyncio.sleep(5)
    raise TimeoutError(f"{thread_id} 在 {timeout_s}s 内未收尾")


def _launch_replenish(query: str) -> str:
    """在 2024 上启动一个补货图任务，返回 thread_id（即 task_id）。"""
    import uuid

    async def _go():
        thread_id = str(uuid.uuid4())
        client = _client()
        await client.threads.create(thread_id=thread_id)
        await client.runs.create(
            thread_id,
            "procurement_replenish_async",
            input={"messages": [{"role": "user", "content": query}]},
        )
        return thread_id

    return asyncio.run(_go())


def _sandbox_ls_analysis() -> list[str]:
    """连全局沙箱（与 2024 同一实例，经状态文件复用），列 /analysis 下存档。"""
    from agent.backends.global_sandbox_manager import get_global_sandbox_sync
    backend = get_global_sandbox_sync()
    result = backend.execute("ls -1 /analysis/ 2>/dev/null", timeout=30)
    return [l.strip() for l in (result.output or "").splitlines() if l.strip()]


# ============================================================
# 用例 1：补货任务必中断（run.status 坑的永久回归锁）
# ============================================================
def test_1_replenish_task_must_interrupt():
    if not asyncio.run(_2024_online()):
        print("[SKIP] 1. 2024 不在线，跳过（其余集成用例一并失效）")
        S["skip_all"] = True
        return

    thread_id = _launch_replenish(
        "对全部库存预警物料给出补货建议，完成分析后调用 replenish_submit 提交补货清单。"
    )
    S["thread_a"] = thread_id
    print(f"      任务已启动 thread_a={thread_id}，轮询等待审批中断（约1-4分钟）...")

    interrupt_value = asyncio.run(_wait_interrupt(thread_id))
    reqs = interrupt_value.get("action_requests", [])
    assert reqs, "中断应携带 action_requests"
    assert reqs[0].get("name") == "replenish_submit", (
        f"首个待审批动作应为 replenish_submit，实为 {reqs[0].get('name')}"
    )

    # ★ 核心断言：本版本 langgraph-api(0.7.90) 中断时 run.status 仍为 success。
    #   若未来升级后此断言失败——不是坏事，说明行为变了，async_tasks.py 的
    #   判定逻辑（以及本测试）需要同步修订。这正是回归测试的价值。
    async def _latest_status():
        runs = await _client().runs.list(thread_id, limit=1)
        return str(runs[0].get("status")) if runs else "none"

    status = asyncio.run(_latest_status())
    assert status == "success", f"0.7.90 行为：中断时 run.status 应仍为 success，实为 {status}"

    S["interrupt_a"] = interrupt_value
    n = len((reqs[0].get("args") or {}).get("replenishment_plan") or [])
    print(f"[PASS] 1. 补货任务必中断：action=replenish_submit，清单 {n} 项；"
          f"中断时 run.status='{status}'（坑已锁定）")


# ============================================================
# 用例 2：审批摘要提取（_extract_interrupt_info_raw 单元级验证）
# ============================================================
def test_2_interrupt_summary_extraction():
    if S.get("skip_all"):
        return
    from api_view.api.async_tasks import _extract_interrupt_info_raw

    state = {"tasks": [{"interrupts": [{"value": S["interrupt_a"]}]}]}
    summary = _extract_interrupt_info_raw(state)
    assert "等待人工审批" in summary
    assert "replenish_submit" in summary
    assert "项" in summary and "¥" in summary, "摘要应含清单项数与总额"

    # 反例：无中断的 state 必须返回空串（前端轮询据此判定状态）
    assert _extract_interrupt_info_raw({"tasks": []}) == ""
    assert _extract_interrupt_info_raw({}) == ""
    print(f"[PASS] 2. 摘要提取正确：{summary.splitlines()[1][:60]}...")


# ============================================================
# 用例 3：approve 恢复 → 存档真实落沙箱
# ============================================================
def test_3_approve_resume_and_archive():
    if S.get("skip_all"):
        return
    from agent.tools.resume_async_task import create_resume_async_task_tool

    tool = create_resume_async_task_tool()
    before = set(_sandbox_ls_analysis())

    r = asyncio.run(tool.ainvoke({"task_id": S["thread_a"], "decision": "approve"}))
    assert "已传达" in r, f"approve 应成功，实为: {r}"
    settled = asyncio.run(_wait_settled(S["thread_a"]))
    assert settled["status"] == "success", f"恢复后应正常收尾，实为 {settled['status']}"

    after = set(_sandbox_ls_analysis())
    new_files = [f for f in after - before if "approved_replenishment" in f]
    assert new_files, "approve 后沙箱 /analysis 应出现 approved_replenishment_*.json"

    # 读回存档，验证 JSON 可解析且字段齐全
    from agent.backends.global_sandbox_manager import get_global_sandbox_sync
    backend = get_global_sandbox_sync()
    fname = sorted(new_files)[-1]
    cat = backend.execute(f"cat /analysis/{fname}", timeout=30)
    payload = json.loads(cat.output)
    for field in ("submitted_at", "item_count", "total_amount", "plan"):
        assert field in payload, f"存档缺少字段 {field}"
    assert isinstance(payload["plan"], list) and payload["plan"], "plan 应为非空清单"
    assert payload["item_count"] == len(payload["plan"]), "item_count 与 plan 长度一致"
    # P1-5 存证：供用例 7 做"审批参数 = 执行参数"指纹比对
    S["archive_payload_a"] = payload
    print(f"[PASS] 3. approve→存档：/analysis/{fname}"
          f"（{payload['item_count']} 项，总额 ¥{payload['total_amount']}）")


# ============================================================
# 用例 4：reject 恢复 → 不产生存档且不挂死
# ============================================================
def test_4_reject_no_archive():
    if S.get("skip_all"):
        return
    from agent.tools.resume_async_task import create_resume_async_task_tool

    # 新任务（小范围，更快到达中断）：只看刹车类。
    # 措辞已还原为普通任务（2026-09-02 修复方向C坑3后不再需要规避图表）：
    # 新增 ImageGuardMiddleware 在框架层拦截图片内容回传纯文本模型，
    # 即使 Agent 生成图表并查看图片也不会 400 崩溃——本用例即验证该修复。
    thread_id = _launch_replenish(
        "只对刹车类预警物料给出补货建议，完成分析后调用 replenish_submit 提交清单。"
    )
    S["thread_b"] = thread_id
    print(f"      任务已启动 thread_b={thread_id}，轮询等待审批中断...")
    asyncio.run(_wait_interrupt(thread_id, timeout_s=720))

    tool = create_resume_async_task_tool()
    before = set(_sandbox_ls_analysis())
    r = asyncio.run(tool.ainvoke({"task_id": thread_id, "decision": "reject"}))
    assert "已传达" in r, f"reject 应成功送达，实为: {r}"

    settled = asyncio.run(_wait_settled(thread_id))
    assert settled["status"] == "success", f"reject 后应正常收尾不挂死，实为 {settled['status']}"

    after = set(_sandbox_ls_analysis())
    leaked = [f for f in after - before if "approved_replenishment" in f]
    assert not leaked, f"reject 不应写存档，但出现: {leaked}"
    print("[PASS] 4. reject→无存档且正常收尾（拒绝分支不执行写入工具）")


# ============================================================
# 用例 5：非法 decision 白名单拒绝（纯离线，无网络调用）
# ============================================================
def test_5_invalid_decision_rejected():
    from agent.tools.resume_async_task import create_resume_async_task_tool
    tool = create_resume_async_task_tool()
    r = asyncio.run(tool.ainvoke({"task_id": "whatever", "decision": "maybe"}))
    assert "必须是" in r and "approve" in r and "reject" in r, (
        f"应返回白名单错误提示，实为: {r}"
    )
    assert "run_id" not in r, "非法 decision 不得发起任何 run"
    print("[PASS] 5. 非法 decision='maybe' 被白名单拦截（校验先于任何网络调用）")


# ============================================================
# 用例 6：无中断时 resume 被拒（消费 thread_a——已 approve 收尾）
# ============================================================
def test_6_resume_without_interrupt_rejected():
    if S.get("skip_all"):
        return
    from agent.tools.resume_async_task import create_resume_async_task_tool
    tool = create_resume_async_task_tool()
    r = asyncio.run(tool.ainvoke({"task_id": S["thread_a"], "decision": "approve"}))
    assert "没有等待审批的中断" in r, f"应返回无中断错误，实为: {r}"
    print("[PASS] 6. 对已完成的 thread 调 resume 被拒（防止重复审批）")


# ============================================================
# 用例 7：审批参数指纹绑定（安全整改 P1-5）
# ============================================================
def _norm_plan_item(item: dict) -> dict:
    """归一化单个清单项（数量/金额做 float 化，键限定指纹字段）。"""
    return {
        "partId": str(item.get("partId")),
        "qty": float(item.get("suggestQuantity") or 0),
        "price": round(float(item.get("unitPrice") or 0), 2),
        "amount": round(float(item.get("estimatedAmount") or 0), 2),
        "supplier": str(item.get("supplierId")),
    }


def test_7_approval_parameter_fingerprint():
    """审批时用户看到的清单 == 执行后落盘的清单（防参数替换）。

    攻击场景（面试官爱追问的）：审批界面展示的是清单 A，用户点 approve
    后实际执行的却是清单 B——"确认 A、执行 B"。本用例比对中断载荷里
    action_requests[0].args（用户审批时看到的内容）与沙箱存档 plan
    （工具真实执行的内容）的逐项指纹，锁定"approve 只放行原始
    tool_call"这一框架保证。
    """
    if S.get("skip_all"):
        return

    approved_reqs = (S.get("interrupt_a") or {}).get("action_requests") or []
    assert approved_reqs, "用例 1 应已存证中断载荷"
    approved_plan = (approved_reqs[0].get("args") or {}).get("replenishment_plan") or []
    archived_plan = (S.get("archive_payload_a") or {}).get("plan") or []
    assert approved_plan and archived_plan, "用例 1/3 应已存证两侧清单"

    assert len(approved_plan) == len(archived_plan), (
        f"项数不一致：审批 {len(approved_plan)} 项 vs 存档 {len(archived_plan)} 项"
    )
    for i, (a, b) in enumerate(zip(approved_plan, archived_plan)):
        fa, fb = _norm_plan_item(a), _norm_plan_item(b)
        assert fa == fb, (
            f"第 {i} 项指纹不一致（审批与执行之间发生了参数替换？）：\n"
            f"  审批时: {fa}\n  存档时: {fb}"
        )
    print(f"[PASS] 7. 参数指纹绑定：审批 {len(approved_plan)} 项与存档逐项一致"
          f"（approve 未篡改 tool_call 参数）")


if __name__ == "__main__":
    sys.path.insert(0, "src")
    t0 = time.time()
    test_1_replenish_task_must_interrupt()
    test_2_interrupt_summary_extraction()
    test_3_approve_resume_and_archive()
    test_4_reject_no_archive()
    test_5_invalid_decision_rejected()
    test_6_resume_without_interrupt_rejected()
    test_7_approval_parameter_fingerprint()
    print(f"\n全部通过：HITL 审批链路回归 OK（耗时 {time.time()-t0:.0f}s）")
