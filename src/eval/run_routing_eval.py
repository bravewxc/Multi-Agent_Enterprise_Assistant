"""路由准确性评估执行器（评估方向 B）。

对黄金集（routing_golden.yaml）逐例发起真实对话，从 SSE 流提取
首个业务工具调用（task / start_async_task 的 subagent_type）作为
"主 Agent 实际路由决策"，与黄金标签确定性比对，输出路由准确率。

判定信号（确定性断言，非文本相似度）：
    tool_start(start_async_task) + args.subagent_type → async:<name>
    tool_start(task)              + args.subagent_type → sync:<name>
    全程无业务委派工具                          → self
    （read_file/ls/write_file/web_search/check_async_task 等为噪声工具，不计）

用法（项目根目录）：
    # 全量跑 1 轮（首跑建基线）
    $env:PYTHONUTF8='1'; $env:PYTHONPATH='src'
    & .venv\\Scripts\\python.exe src/eval/run_routing_eval.py

    # 指定用例 × 3 轮取多数（置信度报告）
    & .venv\\Scripts\\python.exe src/eval/run_routing_eval.py --runs 3 --only routing_001,routing_013

前置：后端 8090 已启动（连带 8000/2024/8080/MongoDB）。
输出：终端报告 + src/eval/results/routing_<时间戳>.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

import httpx
import yaml

# 保证 Windows 控制台中文输出不炸（GBK 坑，见修改记录第 4 步同类问题）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
GOLDEN_PATH = Path(__file__).resolve().parent / "routing_golden.yaml"
RESULTS_DIR = ROOT / "src" / "eval" / "results"

CHAT_API = "http://127.0.0.1:8090/api/chat/stream"
USER_ID = "laoxiao"

# 排噪声策略：只认委派信号（白名单），其余工具一律跳过——
# 主 Agent 的 read_file/ls/write_file/web_search/check_async_task 等
# 自有与框架工具在每个会话几乎必出现（读偏好/攒技能目录/记记忆），
# 出现它们不构成"委派"路由决策；白名单对新增自有工具自动免疫，无需维护黑名单。
BUSINESS_TOOLS = ("task", "start_async_task")

_SUBAGENT_RE = re.compile(r'"subagent_type"\s*:\s*"([^"]+)"')

VALID_EXPECTS = {
    "async:procurement-analyst", "async:procurement-replenish",
    "sync:procurement-order", "self",
}


# ------------------------------------------------------------
# SSE 流解析：跑一轮真实对话，收集工具调用序列
# ------------------------------------------------------------
def run_one_conversation(query: str, thread_id: str, timeout_s: int) -> dict:
    """POST /api/chat/stream，解析 SSE 事件流。

    返回 {"tools": [{"name","args"}...], "ended_by": ..., "answer_head": str}
    ended_by ∈ done / interrupted / error / timeout / closed
    """
    tools: list[dict] = []
    answer_head: list[str] = []
    ended_by = "closed"

    body = {"message": query, "thread_id": thread_id, "user_id": USER_ID}
    try:
        with httpx.Client(timeout=httpx.Timeout(connect=10, read=timeout_s,
                                                write=30, pool=10)) as client:
            with client.stream("POST", CHAT_API, json=body) as resp:
                resp.raise_for_status()
                for raw in resp.iter_lines():
                    if not raw or not raw.startswith("data: "):
                        continue
                    try:
                        evt = json.loads(raw[6:])
                    except json.JSONDecodeError:
                        continue

                    etype = evt.get("type")
                    if etype == "tool_start":
                        tools.append({"name": evt.get("tool_name", "?"),
                                      "args": ""})
                    elif etype == "tool_args":
                        # 参数增量：累加到最近一个尚未收到结果的工具上。
                        # chat.py 的 SSE 无 tool_call_id，按"最后一个"归属
                        # （模型串行发射参数块，实践可靠）
                        if tools:
                            tools[-1]["args"] += evt.get("args", "")
                    elif etype == "token":
                        if len(answer_head) < 30:
                            answer_head.append(evt.get("content", ""))
                    elif etype == "interrupt":
                        ended_by = "interrupted"
                        break
                    elif etype == "error":
                        ended_by = "error"
                        break
                    elif etype == "done":
                        ended_by = "interrupted" if evt.get("interrupted") else "done"
                        break
    except httpx.ReadTimeout:
        ended_by = "timeout"
    except Exception as e:  # 连接失败等
        ended_by = f"error:{type(e).__name__}"

    return {
        "tools": tools,
        "ended_by": ended_by,
        "answer_head": ("".join(answer_head))[:200],
    }


# ------------------------------------------------------------
# 路由判定：从工具序列提取归一化路由标签
# ------------------------------------------------------------
def classify_routing(tools: list[dict]) -> str:
    """首个业务工具 → 归一化标签。

    subagent_type 从该工具的累计参数中正则提取；参数可能因流式
    分块不完整，正则兜底扫描其后的参数文本（同一业务调用）。
    """
    for i, t in enumerate(tools):
        if t["name"] not in BUSINESS_TOOLS:
            continue
        # 在本工具参数中找；找不到则向后扫描（并行发射时的错位兜底）
        blob = t["args"] + " " + " ".join(x["args"] for x in tools[i + 1:])
        m = _SUBAGENT_RE.search(blob)
        target = m.group(1) if m else "unknown"
        channel = "async" if t["name"] == "start_async_task" else "sync"
        return f"{channel}:{target}"
    return "self"


def error_type(expect: str, actual: str) -> str | None:
    """pass 返回 None；失败按错误模式分组（报告口径）。"""
    if actual == expect:
        return None
    if actual == "self":
        return "no_delegation"          # 该委派没委派
    if expect == "self":
        return "over_delegation"        # 不该委派乱委派
    expect_async, actual_async = expect.startswith("async"), actual.startswith("async")
    if expect_async and not actual_async:
        return "mis_sync_for_async"     # 误同步（分析/补货走 task，阻塞对话）
    if not expect_async and actual_async:
        return "mis_async_for_sync"     # 误异步（订单走后台，答非所问）
    return "wrong_target"               # 通道对但子 Agent 选错


# ------------------------------------------------------------
# 主流程
# ------------------------------------------------------------
def load_golden(only: list[str] | None) -> list[dict]:
    with open(GOLDEN_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    cases = data["cases"]
    # 载入即校验：黄金集自身的期望标签必须合法（评估资产的质量闸门）
    bad = [c["id"] for c in cases if c["expect"] not in VALID_EXPECTS]
    if bad:
        raise SystemExit(f"黄金集存在非法期望标签: {bad}")
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        raise SystemExit("黄金集存在重复 id")
    if only:
        cases = [c for c in cases if c["id"] in only]
        missing = set(only) - {c["id"] for c in cases}
        if missing:
            raise SystemExit(f"--only 中有未知用例: {missing}")
    return cases


def main() -> None:
    ap = argparse.ArgumentParser(description="路由准确性评估（方向B）")
    ap.add_argument("--runs", type=int, default=1,
                    help="每用例运行次数，>1 时取多数票（默认 1）")
    ap.add_argument("--only", type=str, default="",
                    help="逗号分隔的用例 id，仅跑这些")
    ap.add_argument("--timeout", type=int, default=300,
                    help="单轮对话超时秒数")
    ap.add_argument("--pause", type=float, default=1.0,
                    help="两轮之间的间隔秒数（给后端喘息）")
    args = ap.parse_args()

    only = [s.strip() for s in args.only.split(",") if s.strip()] or None
    cases = load_golden(only)
    print(f"黄金集载入 {len(cases)} 例 × {args.runs} 轮\n" + "=" * 72)

    records: list[dict] = []
    t_start = time.time()

    for idx, case in enumerate(cases, 1):
        labels: list[str] = []
        details: list[dict] = []
        for r in range(1, args.runs + 1):
            # 独立 thread_id —— 既是会话隔离，也是方向A指标表的归组键
            thread_id = f"eval-b-{case['id']}-r{r}-{uuid.uuid4().hex[:6]}"
            conv = run_one_conversation(case["query"], thread_id, args.timeout)
            label = classify_routing(conv["tools"])
            labels.append(label)
            details.append({
                "run": r, "thread_id": thread_id, "actual": label,
                "ended_by": conv["ended_by"],
                "tools": [t["name"] for t in conv["tools"]],
                "answer_head": conv["answer_head"],
            })
            print(f"  [{idx}/{len(cases)}] {case['id']} r{r} → {label}"
                  f" ({conv['ended_by']})")
            if r < args.runs:
                time.sleep(args.pause)

        # 多数票（1 轮时即该轮结果）
        vote, cnt = Counter(labels).most_common(1)[0]
        etype = error_type(case["expect"], vote)
        ok = etype is None
        records.append({
            "id": case["id"], "category": case["category"],
            "query": case["query"], "expect": case["expect"],
            "vote": vote, "votes": dict(Counter(labels)),
            "confidence": f"{cnt}/{args.runs}",
            "pass": ok, "error_type": etype, "runs": details,
        })
        mark = "PASS" if ok else f"FAIL({etype})"
        print(f"  [{idx}/{len(cases)}] {case['id']} expect={case['expect']}"
              f" vote={vote} {mark}\n")

    # ---------------- 汇总报告 ----------------
    total = len(records)
    passed = sum(1 for r in records if r["pass"])
    acc = passed / total * 100 if total else 0.0

    print("=" * 72)
    print(f"路由准确率: {passed}/{total} = {acc:.1f}%   "
          f"(runs={args.runs}, 耗时 {time.time()-t_start:.0f}s)")

    print("\n-- 分类别准确率 --")
    by_cat: dict[str, list] = {}
    for r in records:
        by_cat.setdefault(r["category"], []).append(r)
    for cat, rs in sorted(by_cat.items()):
        p = sum(1 for r in rs if r["pass"])
        print(f"  {cat:<20} {p}/{len(rs)}")

    fails = [r for r in records if not r["pass"]]
    if fails:
        print("\n-- 失败分组 --")
        for et, cnt in sorted(Counter(r["error_type"] for r in fails).items()):
            ids = [r["id"] for r in records if r["error_type"] == et]
            print(f"  {et:<18} {cnt} 例: {ids}")
        print("\n-- 失败明细 --")
        for r in fails:
            print(f"  {r['id']} [{r['category']}] expect={r['expect']} got={r['vote']}")
            print(f"    q: {r['query']}")
    else:
        print("\n全部通过。")

    # ---------------- 结果落盘（版本化跑分依据） ----------------
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"routing_{datetime.now():%Y%m%d_%H%M%S}.json"
    payload = {
        "meta": {
            "golden": str(GOLDEN_PATH.relative_to(ROOT)),
            "runs": args.runs, "accuracy": round(acc, 1),
            "passed": passed, "total": total,
            "elapsed_s": round(time.time() - t_start),
            "api": CHAT_API, "generated_at": datetime.now().isoformat(),
        },
        "cases": records,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n结果已保存: {out}")


if __name__ == "__main__":
    main()
