"""报告质量 LLM-as-Judge（评估方向 D，第一步：补货清单报告）。

设计纪律（对应评估文档 3.5 节）：
1. 确定性优先——能用代码断言的绝不用 Judge：
   字段完整性 / 单价×数量=金额（逐项算术）/ 总额=Σ明细 / item_count 一致
   全部走代码检查，Judge 只处理两个真正的语义项：
   - urgency_ordering  紧急度排序合理性（缺货紧迫者应更紧急）
   - actionability     建议可执行性（reason 是否给出可执行的量化依据）
2. Judge 模型 = Qwen（阿里百炼 FALLBACK_MODEL），被评对象 = DeepSeek 产出
   ——异构防自我偏好（同厂模型互评会系统性偏高）。
3. rubric 带 1/4/7/10 锚点，先 rationale 后 score，独立 JSON 输出。

数据来源（三选一）：
    --archive <文件名>   沙箱 /analysis/ 下的 approved_replenishment_*.json
                         （approve 后的存档，字段最全，含 total_amount）
    --thread <thread_id> 2024 上处于审批中断的补货任务（从 interrupt args 取清单）
    --file <本地路径>    本地 JSON（离线调试用）

运行（项目根）：
    $env:PYTHONUTF8='1'; $env:PYTHONPATH='src'
    & .venv\\Scripts\\python.exe src/eval/judge_report.py --archive approved_replenishment_xxx.json
输出：终端报告 + src/eval/results/judge_<时间戳>.json（基线数据）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "src" / "eval" / "results"

TOLERANCE = 0.01          # 金额容差（浮点）
LLM_PASS_LINE = 6         # 语义项及格线（10 分制）
CORE_FIELDS = ["partId", "partName", "suggestQuantity", "unitPrice",
               "estimatedAmount", "urgency", "reason"]


# ------------------------------------------------------------
# 数据装载
# ------------------------------------------------------------
def load_from_archive(filename: str) -> dict:
    """从全局沙箱读 approve 存档（与 2024 同一沙箱，经状态文件复用）。"""
    from agent.backends.global_sandbox_manager import get_global_sandbox_sync
    backend = get_global_sandbox_sync()
    result = backend.execute(f"cat /analysis/{filename}", timeout=30)
    if result.exit_code != 0:
        raise SystemExit(f"沙箱读取失败: {filename}")
    return json.loads(result.output)


def load_from_thread(thread_id: str) -> dict:
    """从 2024 的审批中断里提取清单（任务未 approve 也能评）。"""
    import asyncio
    from langgraph_sdk import get_client

    async def _go():
        state = await get_client(url="http://127.0.0.1:2024").threads.get_state(thread_id)
        for t in state.get("tasks", []):
            for it in t.get("interrupts") or []:
                v = it.get("value")
                if isinstance(v, dict) and "action_requests" in v:
                    req = v["action_requests"][0]
                    plan = (req.get("args") or {}).get("replenishment_plan") or []
                    return {
                        "thread_id": thread_id,
                        "item_count": len(plan),
                        "total_amount": round(
                            sum(float(i.get("estimatedAmount") or 0) for i in plan), 2),
                        "plan": plan,
                    }
        raise SystemExit(f"thread {thread_id} 无待审批中断")

    return asyncio.run(_go())


# ------------------------------------------------------------
# 第一部分：确定性检查（零 LLM 成本）
# ------------------------------------------------------------
def deterministic_checks(report: dict) -> list[dict]:
    plan = report.get("plan") or []
    checks: list[dict] = []

    def add(name, ok, detail):
        checks.append({"criterion": name, "type": "deterministic",
                       "pass": ok, "score": 1 if ok else 0, "detail": detail})

    # 1. 清单非空
    add("plan_nonempty", bool(plan), f"{len(plan)} 项")

    # 2. 逐项核心字段完整（suggestQuantity 为 0 同样视为缺失：补 0 件无意义）
    missing = []
    for i, item in enumerate(plan):
        for f in CORE_FIELDS:
            v = item.get(f)
            if v is None or v == "" or (f == "suggestQuantity" and not v):
                missing.append((i, f))
    add("fields_complete", not missing, f"缺失 {missing[:5]}" if missing else "核心字段齐全")

    # 3. 逐项算术：unitPrice × suggestQuantity == estimatedAmount
    bad_math = []
    for i, item in enumerate(plan):
        try:
            expect = round(float(item["unitPrice"]) * float(item["suggestQuantity"]), 2)
            got = round(float(item["estimatedAmount"]), 2)
            if abs(expect - got) > TOLERANCE:
                bad_math.append((i, expect, got))
        except (TypeError, ValueError, KeyError):
            bad_math.append((i, "parse_error", item.get("estimatedAmount")))
    add("item_arithmetic", not bad_math,
        f"错项 {bad_math[:5]}" if bad_math else f"{len(plan)} 项全部 单价×数量=金额")

    # 4. 总额 = Σ明细（存档自带 total_amount 才检查）
    if report.get("total_amount") is not None and plan:
        s = round(sum(float(i.get("estimatedAmount") or 0) for i in plan), 2)
        ok = abs(s - float(report["total_amount"])) <= TOLERANCE
        add("total_consistency", ok, f"Σ明细={s} vs 报告总额={report['total_amount']}")
    # 5. item_count 一致（存档自带才检查）
    if report.get("item_count") is not None:
        add("count_consistency", int(report["item_count"]) == len(plan),
            f"item_count={report['item_count']} vs len(plan)={len(plan)}")

    return checks


# ------------------------------------------------------------
# 第二部分：LLM Judge（Qwen 异构）
# ------------------------------------------------------------
RUBRICS = {
    "urgency_ordering": """
锚点（1-10）：
  1-2  urgency 字段与缺货事实明显矛盾（如库存充足的物料标"高紧急"）
  4-5  urgency 基本合理但存在 1-2 处排序/分级与 reason 描述不一致
  7-8  urgency 分级与 reason 的缺货紧迫性（缺货天数/库存水位/消耗速率）一致
  9-10 全部条目分级一致且有清晰的量化依据支撑
""",
    "actionability": """
锚点（1-10）：
  1-2  reason 是空话/复述品名（"建议补货""库存不足"），无法指导采购动作
  4-5  部分条目有依据（提了 ROP/预警），但关键数字缺失或含糊
  7-8  每条 reason 均含量化依据（当前库存、日消耗、ROP 对比、建议量由来）
  9-10 依据齐全且可直接据此下单（含供应商/交期等执行要素）
""",
}


def build_judge_model():
    """Judge 模型：Qwen（与被评对象 DeepSeek 异构，防自我偏好）。"""
    from langchain_openai import ChatOpenAI
    from agent.env_utils import (
        ALIBABA_API_KEY, ALIBABA_BASE_URL, FALLBACK_MODEL_NAME,
    )
    return ChatOpenAI(
        model=FALLBACK_MODEL_NAME,
        temperature=0.0,  # Judge 要稳定：温度 0
        openai_api_key=ALIBABA_API_KEY,
        openai_api_base=ALIBABA_BASE_URL,    # 本版 langchain_openai 的正确参数名
    )


def build_fallback_judge_model():
    """降级 Judge：DeepSeek（同构，仅在 Qwen 不可用时使用，结果须打标解读）。

    实测坑：qwen3.7-max 免费额度耗尽返回 403 FreeTierOnly
    （修改记录.md 第六节遗留事项 1）。降级时评审仍可进行，但失去
    异构性——结果 JSON 里 judge_degraded=True，解读时须知。
    """
    from langchain_openai import ChatOpenAI
    from agent.env_utils import (
        DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, SUMMARY_MODEL_NAME,
    )
    return ChatOpenAI(
        model=SUMMARY_MODEL_NAME,
        temperature=0.0,
        openai_api_key=DEEPSEEK_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
    )


def build_judge_prompt(criterion: str, task_desc: str, plan: list) -> str:
    """构造单准则评审 prompt（离线 CLI 与运行时中间件共用，保证同一把尺子）。"""
    items_text = json.dumps(
        [{k: i.get(k) for k in ("partName", "suggestQuantity", "unitPrice",
                                "estimatedAmount", "urgency", "reason")}
         for i in plan],
        ensure_ascii=False, indent=1,
    )
    return f"""你是采购补货清单的质量评审员。评审准则：{criterion}
{RUBRICS[criterion]}

【任务背景】{task_desc or "对库存预警物料给出补货建议"}
【清单条目】（共 {len(plan)} 项，已省略无关字段）
{items_text}

先给出 rationale（不超过 120 字，指名道姓引用具体条目），再给 score（1-10 整数）。
只输出一个 JSON 对象，格式：{{"rationale": "...", "score": 7}}"""


def parse_judge_output(text: str, criterion: str, model_name: str) -> dict:
    """解析 Judge 的 JSON 输出。失败抛 ValueError（调用方自行决定重试/降级）。"""
    text = text if isinstance(text, str) else str(text)
    m = re.search(r"\{.*\}", text, re.S)
    data = json.loads(m.group(0))
    score = int(data["score"])
    assert 1 <= score <= 10
    return {"criterion": criterion, "type": "llm",
            "pass": score >= LLM_PASS_LINE, "score": score,
            "rationale": str(data.get("rationale", ""))[:300],
            "judge_model": model_name}


def judge_one(model, criterion: str, task_desc: str, plan: list) -> dict:
    """单准则评审（离线 CLI 用，asyncio.run 同步包装）。

    API 层错误（403 额度/网络）上抛 RuntimeError 由调用方降级，
    不与"输出解析失败"混为一谈（错误归因要准）。
    运行时路径请用 build_judge_prompt + parse_judge_output 自行异步调用。
    """
    prompt = build_judge_prompt(criterion, task_desc, plan)

    import asyncio
    last_err = ""
    for attempt in range(2):
        try:
            resp = asyncio.run(model.ainvoke(prompt))
        except Exception as e:  # API 层错误：额度/网络，重试无意义
            raise RuntimeError(f"Judge API 调用失败: {type(e).__name__}: {str(e)[:160]}")
        try:
            return parse_judge_output(resp.content, criterion, model.model_name)
        except Exception:
            last_err = f"输出解析失败（attempt {attempt + 1}）"
    return {"criterion": criterion, "type": "llm", "pass": False,
            "score": 0, "rationale": last_err, "judge_model": model.model_name}


def main() -> None:
    ap = argparse.ArgumentParser(description="补货报告质量 Judge（方向D）")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--archive", help="沙箱 /analysis/ 下的存档文件名")
    src.add_argument("--thread", help="2024 上待审批任务的 thread_id")
    src.add_argument("--file", help="本地 JSON 路径")
    ap.add_argument("--task", default="", help="任务背景描述（judge 上下文）")
    args = ap.parse_args()

    if args.archive:
        report = load_from_archive(args.archive)
        source = f"sandbox:/analysis/{args.archive}"
    elif args.thread:
        report = load_from_thread(args.thread)
        source = f"thread:{args.thread}"
    else:
        report = json.loads(Path(args.file).read_text(encoding="utf-8"))
        source = f"file:{args.file}"

    print(f"评审对象: {source}（{len(report.get('plan') or [])} 项清单）")
    print("=" * 66)

    results = deterministic_checks(report)
    for c in results:
        mark = "PASS" if c["pass"] else "FAIL"
        print(f"  [{mark}] {c['criterion']:<20} {c['detail']}")

    model = build_judge_model()
    degraded = False
    print(f"\n-- LLM Judge（{model.model_name}，与被评对象 DeepSeek 异构）--")
    for crit in RUBRICS:
        try:
            r = judge_one(model, crit, args.task, report.get("plan") or [])
        except RuntimeError as e:
            # Qwen 不可用（如 403 免费额度耗尽）→ 降级 DeepSeek（同构，打标）
            if not degraded:
                print(f"  [WARN] {e}")
                print(f"         → 降级为 DeepSeek 同构评审（结果须按降级解读）")
                model = build_fallback_judge_model()
                degraded = True
                r = judge_one(model, crit, args.task, report.get("plan") or [])
            else:
                r = {"criterion": crit, "type": "llm", "pass": False, "score": 0,
                     "rationale": str(e), "judge_model": model.model_name}
        results.append(r)
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"  [{mark}] {crit:<20} score={r['score']}/10")
        print(f"         {r['rationale']}")

    # 汇总：确定性项全过 + 语义项过及格线
    det_ok = all(c["pass"] for c in results if c["type"] == "deterministic")
    llm_avg = (sum(c["score"] for c in results if c["type"] == "llm")
               / max(1, sum(1 for c in results if c["type"] == "llm")))
    overall = det_ok and all(c["pass"] for c in results if c["type"] == "llm")

    print("=" * 66)
    print(f"确定性检查: {'全部通过' if det_ok else '存在失败'} | "
          f"语义均分: {llm_avg:.1f}/10 (及格线 {LLM_PASS_LINE}) | "
          f"综合: {'PASS' if overall else 'FAIL'}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"judge_{datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps({
        "meta": {"source": source, "judge_model": model.model_name,
                 "judge_degraded": degraded,
                 "llm_pass_line": LLM_PASS_LINE, "generated_at": datetime.now().isoformat(),
                 "overall_pass": overall, "llm_avg": round(llm_avg, 1)},
        "report_head": {"item_count": report.get("item_count"),
                        "total_amount": report.get("total_amount")},
        "criteria": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"结果已保存: {out}")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
