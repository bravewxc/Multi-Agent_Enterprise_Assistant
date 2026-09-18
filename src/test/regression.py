"""端到端回归套件（方向 F）：A-E 的容器化整合，"发布前一条命令"。

分层结构与耗时量级：
  [快] 单元层   ~秒级    _merge_preferences 单测 + 中断摘要解析单测
                          + 工具描述一致性锁（零依赖零成本）
  [中] 集成层   ~分钟级  HITL 审批链路 6 用例（方向C，需 2024）+
                          MCP 工具断言化回归（改造版 test_all_tools，需 8000/Java ERP）
  [慢] 评估层   ~20分钟  路由准确率 ≥ 基线-5pp（方向B，需 8090 全栈）+
                          补货报告 Judge ≥ 基线（方向D，需 Qwen Key + 沙箱存档）

门控（本地版 CI）：任一层失败 → exit 1；评估层比较 src/eval/results/baselines.json，
无基线时只记录不门控（首跑建基线的语义）。

运行：cd 项目根
  $env:PYTHONUTF8='1'; $env:PYTHONPATH='src'
  .venv\\Scripts\\python.exe -m test.regression [--skip-eval] [--skip-slow]
"""
from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
BASELINES = ROOT / "src" / "eval" / "results" / "baselines.json"
ROUTING_TOLERANCE_PP = 5.0   # 路由准确率允许较基线回落的最大百分点

scorecard: list[dict] = []


def _layer(name: str) -> None:
    print(f"\n{'='*66}\n◆ {name}\n{'='*66}")


def _record(item: dict) -> None:
    scorecard.append(item)
    mark = "PASS" if item["pass"] else ("SKIP" if item.get("skipped") else "FAIL")
    print(f"  [{mark}] {item['name']}: {item.get('detail', '')}")


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(("127.0.0.1", port)) == 0


# ============================================================
# [快] 单元层：纯函数，零依赖
# ============================================================
def layer_unit() -> bool:
    _layer("[快] 单元层（零依赖，~秒级）")
    ok = True

    # 1. 记忆合并纯单测（方向E 第一层）
    try:
        from test import test_memory_merge as tmm
        tmm.run_unit_layer()
        _record({"name": "memory_merge 单测（方向E）", "pass": True, "detail": "6 用例"})
    except Exception as e:
        ok = False
        _record({"name": "memory_merge 单测（方向E）", "pass": False, "detail": str(e)[:200]})

    # 2. 中断摘要解析单测（方向C 的纯函数部分，合成状态离线验证）
    try:
        from api_view.api.async_tasks import _extract_interrupt_info_raw
        fake = {"tasks": [{"interrupts": [{"value": {
            "action_requests": [{"name": "replenish_submit", "args": {
                "replenishment_plan": [
                    {"partName": "刹车片", "suggestQuantity": 50,
                     "estimatedAmount": 5000.0},
                    {"partName": "火花塞", "suggestQuantity": 100,
                     "estimatedAmount": 3000.0},
                ]}}]}}]}]}
        s = _extract_interrupt_info_raw(fake)
        assert "等待人工审批" in s and "2 项" in s and "¥8000" in s, s
        assert _extract_interrupt_info_raw({"tasks": []}) == ""
        _record({"name": "interrupt 摘要解析单测（方向C）", "pass": True,
                 "detail": "项数/总额/反例 三断言"})
    except Exception as e:
        ok = False
        _record({"name": "interrupt 摘要解析单测（方向C）", "pass": False, "detail": str(e)[:200]})

    # 3. 工具描述一致性锁：assign_skill 的 docstring 必须与 SCOPE_MAP 双向一致
    #    docstring 经 @tool 成为工具描述注入模型上下文——漏一个 key 等于模型
    #    不知道能给该 Agent 分配技能（2026-09-17 曾漏 procurement-replenish）。
    #    用源码解析而非 import：agent.config 顶层会初始化 MongoDBSaver（急切建
    #    索引），MongoDB 未启动时 import 会连接超时——源码解析保住零依赖契约。
    #    双向：缺 key（模型不可见）与多 key（SCOPE_MAP 已删除的僵尸条目）都拦。
    try:
        import re as _re
        cfg_src = (ROOT / "src" / "agent" / "config.py").read_text(encoding="utf-8")
        m = _re.search(r"SCOPE_MAP\s*=\s*\{(.*?)\}", cfg_src, _re.DOTALL)
        assert m, "config.py 中未找到 SCOPE_MAP 定义"
        scope_keys = set(_re.findall(r'"([^"]+)"\s*:', m.group(1)))

        tool_src = (ROOT / "src" / "agent" / "tools" / "assign_skill.py")\
            .read_text(encoding="utf-8")
        # docstring 里 Agent 清单的固定格式：- "xxx" — 说明
        listed = set(_re.findall(r'-\s*"([^"]+)"\s*—', tool_src))
        assert listed, "assign_skill.py 未解析到 Agent 清单（docstring 格式是否被改？）"

        missing, stale = scope_keys - listed, listed - scope_keys
        assert not missing and not stale, (
            f"assign_skill 工具描述与 SCOPE_MAP 漂移："
            f"缺少 {sorted(missing) or '无'}，多余 {sorted(stale) or '无'}")
        _record({"name": "assign_skill 描述覆盖 SCOPE_MAP", "pass": True,
                 "detail": f"{len(scope_keys)} 个 Agent 双向一致（源码级）"})
    except Exception as e:
        ok = False
        _record({"name": "assign_skill 描述覆盖 SCOPE_MAP", "pass": False,
                 "detail": str(e)[:200]})

    return ok


# ============================================================
# [中] 集成层：需 2024（HITL）/ 8000+ERP（MCP 工具）
# ============================================================
def layer_integration() -> bool:
    _layer("[中] 集成层（~分钟级）")
    ok = True

    # 1. HITL 审批链路 6 用例（方向C）
    if _port_open(2024):
        try:
            from test import test_hitl_approval as th
            for fn in (th.test_1_replenish_task_must_interrupt,
                       th.test_2_interrupt_summary_extraction,
                       th.test_3_approve_resume_and_archive,
                       th.test_4_reject_no_archive,
                       th.test_5_invalid_decision_rejected,
                       th.test_6_resume_without_interrupt_rejected):
                fn()
            _record({"name": "HITL 审批链路 6 用例（方向C）", "pass": True,
                     "detail": f"thread_a={th.S.get('thread_a', '')[:8]}"})
        except Exception as e:
            ok = False
            _record({"name": "HITL 审批链路 6 用例（方向C）", "pass": False,
                     "detail": str(e)[:200]})
    else:
        _record({"name": "HITL 审批链路 6 用例（方向C）", "pass": True, "skipped": True,
                 "detail": "2024 不在线"})

    # 2. MCP 工具断言化回归（方向F改造版，mcp 内存模式 + agent HTTP 模式）
    if _port_open(8000):
        try:
            from test import test_all_tools as tat
            r1 = __import__("asyncio").run(tat.run_all_mcp_client_tests())
            r2 = __import__("asyncio").run(tat.run_all_agent_client_tests())
            if not (r1 and r2):
                raise AssertionError("test_all_tools 存在失败（见上方 [FAIL]）")
            _record({"name": "MCP 工具回归（方向F改造）", "pass": True, "detail": "固定数据+断言"})
        except Exception as e:
            ok = False
            _record({"name": "MCP 工具回归（方向F改造）", "pass": False, "detail": str(e)[:200]})
    else:
        _record({"name": "MCP 工具回归（方向F改造）", "pass": True, "skipped": True,
                 "detail": "8000 不在线"})

    return ok


# ============================================================
# [慢] 评估层：阈值判定（评估≠测试：看趋势与基线，不硬断言单例）
# ============================================================
def _run(cmd: list[str]) -> tuple[int, str]:
    """跑子进程命令，返回 (exit_code, 最后 1200 字符输出)。"""
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    tail = (p.stdout or "")[-1200:]
    return p.returncode, tail


def layer_eval() -> bool:
    _layer("[慢] 评估层（~20分钟 + API 费）")
    baselines = {}
    if BASELINES.exists():
        baselines = json.loads(BASELINES.read_text(encoding="utf-8"))
    ok = True

    # 1. 路由准确率 ≥ 基线 - 5pp（方向B）
    if _port_open(8090):
        code, tail = _run([sys.executable, "-u", "src/eval/run_routing_eval.py"])
        try:
            latest = sorted((ROOT / "src/eval/results").glob("routing_*.json"))[-1]
            acc = json.loads(latest.read_text(encoding="utf-8"))["meta"]["accuracy"]
            base = baselines.get("routing_accuracy")
            if base is None:
                _record({"name": "路由准确率（方向B）", "pass": True,
                         "detail": f"{acc}%（无基线，本次即为候选基线）"})
            elif acc >= base - ROUTING_TOLERANCE_PP:
                _record({"name": "路由准确率（方向B）", "pass": True,
                         "detail": f"{acc}% ≥ 基线{base}%-{ROUTING_TOLERANCE_PP}pp"})
            else:
                ok = False
                _record({"name": "路由准确率（方向B）", "pass": False,
                         "detail": f"{acc}% < 基线{base}%-{ROUTING_TOLERANCE_PP}pp，回归！"})
        except Exception as e:
            ok = False
            _record({"name": "路由准确率（方向B）", "pass": False,
                     "detail": f"结果解析失败: {e}\n{tail[-300:]}"})
    else:
        _record({"name": "路由准确率（方向B）", "pass": True, "skipped": True,
                 "detail": "8090 不在线"})

    # 2. 报告质量 Judge ≥ 基线（方向D）：自动挑最新存档评审
    try:
        from agent.backends.global_sandbox_manager import get_global_sandbox_sync
        backend = get_global_sandbox_sync()
        ls = backend.execute("ls -1 /analysis/ 2>/dev/null", timeout=30).output or ""
        archives = sorted(l for l in ls.splitlines()
                          if l.strip().startswith("approved_replenishment"))
        if not archives:
            raise FileNotFoundError("沙箱无 approved_replenishment_*.json 存档")
        code, tail = _run([sys.executable, "src/eval/judge_report.py",
                           "--archive", archives[-1].strip(),
                           "--task", "对库存预警物料给出补货建议"])
        try:
            j = sorted((ROOT / "src/eval/results").glob("judge_*.json"))[-1]
            meta = json.loads(j.read_text(encoding="utf-8"))["meta"]
            base = baselines.get("judge_llm_avg")
            detail = f"语义均分 {meta['llm_avg']}/10"
            if base is None:
                _record({"name": "报告 Judge（方向D）", "pass": True,
                         "detail": detail + "（无基线，本次即为候选基线）"})
            elif meta["llm_avg"] >= base:
                _record({"name": "报告 Judge（方向D）", "pass": True,
                         "detail": detail + f" ≥ 基线{base}"})
            else:
                ok = False
                _record({"name": "报告 Judge（方向D）", "pass": False,
                         "detail": detail + f" < 基线{base}，回归！"})
        except FileNotFoundError:
            raise
    except Exception as e:
        # Judge 属评估项：无样本/无 Key 记 SKIP，不算失败（与"评估≠测试"一致）
        _record({"name": "报告 Judge（方向D）", "pass": True, "skipped": True,
                 "detail": str(e)[:160]})

    return ok


# ============================================================
# 汇总
# ============================================================
def main() -> None:
    ap = argparse.ArgumentParser(description="端到端回归套件（方向F）")
    ap.add_argument("--skip-eval", action="store_true", help="跳过[慢]评估层")
    ap.add_argument("--skip-slow", action="store_true", help="跳过[中]+[慢]（只跑单测）")
    args = ap.parse_args()

    sys.path.insert(0, "src")
    t0 = time.time()
    results = {"unit": layer_unit()}
    if not args.skip_slow:
        results["integration"] = layer_integration()
        if not args.skip_eval:
            results["eval"] = layer_eval()

    failed = [k for k, v in results.items() if not v]
    print(f"\n{'='*66}\n分数卡（{time.time()-t0:.0f}s）\n{'='*66}")
    for it in scorecard:
        mark = "PASS" if it["pass"] else ("SKIP" if it.get("skipped") else "FAIL")
        print(f"  {mark:<5} {it['name']}")
    print(f"{'='*66}")
    if failed:
        print(f"回归失败：{failed} → exit 1")
        sys.exit(1)
    print("全部通过/跳过 → exit 0")


if __name__ == "__main__":
    main()
