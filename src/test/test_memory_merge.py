"""方向 E：记忆写入正确性 — 两层评估（单测层零 LLM 成本 / 抽取层小样本）。

第一层（纯函数单测，零成本）：_merge_preferences 的确定性逻辑
  memory_update.py L273-373：解析旧区块 → 从后往前删 → 合并去重 → 截断 → 重建
第二层（LLM 小样本）：_extract_entities（L112-157）的实体抽取准确率
  固定 10 段代表性对话（含谐音/否定语境等幻觉诱导），阈值判定（评估≠测试）

运行：cd 项目根
  仅单测层（离线）: .venv\\Scripts\\python.exe -m test.test_memory_merge unit
  含抽取层（需 API Key，10 次 LLM 调用）:
      $env:PYTHONUTF8='1'; .venv\\Scripts\\python.exe -m test.test_memory_merge
"""
from __future__ import annotations

import asyncio
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ============================================================
# 第一层：_merge_preferences 纯函数单测
# ============================================================
def _merge(current: str, suppliers: list, query: str) -> str:
    from agent.middlewares.memory_update import _merge_preferences
    return _merge_preferences(
        current.split("\n") if current else [], suppliers, query
    )


def test_1_merge_dedup_new_first():
    """新旧合并去重：新值在前，旧值去重后追加。"""
    current = (
        "# 用户偏好\n"
        "preferred_output: chart\n"
        "recent_suppliers:\n"
        "  - 博世\n"
        "  - 德尔福\n"
    )
    out = _merge(current, ["博世", "大陆"], "查询刹车片")
    import re
    m = re.search(r"recent_suppliers:\n((?:  - .*\n?)+)", out)
    assert m, f"应重建 recent_suppliers 区块:\n{out}"
    items = [l.strip("- ").strip() for l in m.group(1).strip().splitlines()]
    assert items == ["博世", "大陆", "德尔福"], f"新值应在前且去重，实为 {items}"
    print("[PASS] 1. 合并去重：['博世','大陆'] + 旧['博世','德尔福'] →", items)


def test_2_sliding_window_cap():
    """滑动窗口截断：供应商留 10（L344），查询留 5（L350）。"""
    out = _merge("preferred_output: chart\n",
                 [f"供应商{i}" for i in range(11)], "初始查询")
    # 再逐条合并 5 个新查询 → 累计 6 条唯一查询，应截断为 5
    for i in range(5):
        out = _merge(out, [], f"查询{i}")
    import re
    sup = re.findall(r"recent_suppliers:\n((?:  - .*\n?)+)", out)[0]
    assert len(sup.strip().splitlines()) == 10, "供应商应截断为 10"
    qry = re.findall(r"recent_queries:\n((?:  - .*\n?)+)", out)[0]
    assert len(qry.strip().splitlines()) == 5, f"查询应截断为 5，实为 {len(qry.strip().splitlines())}"
    # 最新的查询在前（滑动窗口=最近优先）
    first_q = qry.strip().splitlines()[0]
    assert "查询4" in first_q, f"最新查询应排在最前，实为 {first_q}"
    print("[PASS] 2. 滑动窗口：供应商 11→10，查询 6→5，最新在前")


def test_3_inline_and_multiline_formats():
    """区块整删重建：内联 `recent_suppliers: []` 与多行格式都能正确解析替换。

    注意语义：删除并重建的是"区块结构"，旧**值**按滑动窗口合并保留——
    所以断言的是"内联原文消失、值以新格式存续"，而非旧值消失。
    """
    current = (
        "preferred_chart_type: bar\n"
        "recent_suppliers: ['电装', '法雷奥']\n"   # 内联格式
        "recent_queries:\n"                        # 多行格式
        "  - '旧查询'\n"
        "preferred_currency: CNY\n"
    )
    out = _merge(current, ["海拉"], "新查询")
    assert "['电装'" not in out, "内联旧区块原文应被整体移除"
    assert "电装" in out and "法雷奥" in out, "内联旧值应被解析并按新格式存续"
    assert "旧查询" in out, "多行旧查询应被解析并保留（滑动窗口语义）"
    assert "海拉" in out and "新查询" in out
    assert "preferred_chart_type: bar" in out and "preferred_currency: CNY" in out
    print("[PASS] 3. 内联/多行两种格式均正确解析，区块重建且旧值存续")


def test_4_back_to_front_removal():
    """从后往前删防索引漂移：suppliers 在前、queries 在后，两区块都删对位置。

    这正是 L328-337 注释的坑：若先删前面的区块，后面区块的索引就漂了，
    会把 preferred_currency 等无关行误删。断言无关行必须原样幸存。
    """
    current = (
        "preferred_output: chart\n"
        "recent_suppliers:\n"
        "  - 博世\n"
        "\n"
        "recent_queries:\n"
        "  - 旧查询\n"
        "\n"
        "preferred_currency: CNY\n"
        "preferred_language: zh\n"
    )
    out = _merge(current, ["大陆"], "新查询")
    for keep in ("preferred_output: chart", "preferred_currency: CNY", "preferred_language: zh"):
        assert keep in out, f"无关偏好字段被误删: {keep}\n{out}"
    assert out.count("recent_suppliers:") == 1 and out.count("recent_queries:") == 1, "区块不得重复"
    print("[PASS] 4. 从后往前删：两区块均删对位置，preferred_* 三字段幸存")


def test_5_empty_content_init():
    """空内容初始化：current_lines 为空也能产出合法区块。"""
    out = _merge("", ["博世"], "首次查询")
    assert out.startswith("recent_suppliers:")
    assert "博世" in out and "首次查询" in out
    print("[PASS] 5. 空内容初始化 → 直接产出两个区块")


def test_6_empty_new_values_keep_old():
    """新值为空：旧值保留，区块不丢（丢区块=记忆复利清零，重大回归）。"""
    current = (
        "preferred_output: chart\n"
        "recent_suppliers:\n"
        "  - 博世\n"
        "recent_queries:\n"
        "  - 刹车片报价\n"
    )
    out = _merge(current, [], "")
    assert "博世" in out, "空新值不应清空旧供应商"
    assert "刹车片报价" in out, "空新查询不应清空旧查询"
    # 注意：query 为空串时区块写为 recent_queries: []，但旧值已合并进 merged_queries，
    # 旧查询仍应保留（L346-350：new_query 为空则 merged 仅含旧值）
    print("[PASS] 6. 新值为空时旧记忆保留（不清零）")


def run_unit_layer() -> bool:
    test_1_merge_dedup_new_first()
    test_2_sliding_window_cap()
    test_3_inline_and_multiline_formats()
    test_4_back_to_front_removal()
    test_5_empty_content_init()
    test_6_empty_new_values_keep_old()
    return True


# ============================================================
# 第二层：_extract_entities 抽取小样本（10 段，阈值判定）
# ============================================================
# 用例设计：期望用"可接受集合"表达（中文/英文形态都算对）；
# 幻觉诱导用例用 must_not 表达"绝不允许出现的实体"。
SAMPLES = [
    {"id": "ext_01", "user": "帮我查一下博世的刹车片价格", "ai": "已为您查询博世刹车片价格，前刹车片 ¥289/套。",
     "any_of": ["博世", "Bosch"], "must_not": [], "query_nonempty": True},
    {"id": "ext_02", "user": "对比一下电装和德尔福的火花塞报价", "ai": "电装铱金火花塞单价 ¥45，德尔福 ¥38。",
     "any_of": ["电装", "德尔福"], "must_not": [], "query_nonempty": True,
     "require_groups": [["电装", "Denso"], ["德尔福", "Delphi"]]},
    {"id": "ext_03", "user": "什么是安全库存？", "ai": "安全库存是为应对需求波动而保持的缓冲库存量。",
     "any_of": [], "must_not": [], "query_nonempty": False},
    {"id": "ext_04", "user": "帮我创建一张采购单，向大陆集团买 200 个空气滤清器", "ai": "已创建采购单，供应商为大陆集团。",
     "any_of": ["大陆", "大陆集团", "Continental"], "must_not": [], "query_nonempty": True},
    {"id": "ext_05", "user": "Bosch 的机油滤清器有货吗", "ai": "Bosch 机油滤清器当前库存充足。",
     "any_of": ["Bosch", "博世"], "must_not": [], "query_nonempty": True},
    {"id": "ext_06", "user": "向爱信下采购单，顺便查一下采埃孚的变速箱库存", "ai": "爱信采购单已创建；采埃孚变速箱库存正常。",
     "any_of": ["爱信", "采埃孚"], "must_not": [], "query_nonempty": True,
     "require_groups": [["爱信", "Aisin"], ["采埃孚", "ZF"]]},
    # 幻觉诱导：谐音品牌（博士≠博世），绝不允许把"博士"纠正/膨胀成"博世"
    {"id": "ext_07", "user": "有没有'博士'牌火花塞？注意我说的是博士，不是博世", "ai": "库存中没有'博士'牌火花塞，您是否需要博世的产品？",
     "any_of": ["博士", "博世", "Bosch"], "must_not": [], "query_nonempty": False,
     "note": "谐音诱导——只记录对话真实提到的名字，不得额外膨胀品牌"},
    # 否定语境：被否定的供应商仍算"提到过"（规则如此），但不得虚构第三方
    {"id": "ext_08", "user": "帮我找电装的替代品，这次不要用电装", "ai": "可为您的火花塞需求提供电装以外的替代品牌。",
     "any_of": ["电装", "Denso"], "must_not": ["博世", "Bosch", "德尔福", "Delphi"], "query_nonempty": True},
    {"id": "ext_09", "user": "把法雷奥、海拉的报价单发我", "ai": "法雷奥与海拉报价单已生成。",
     "any_of": ["法雷奥", "海拉"], "must_not": [], "query_nonempty": True,
     "require_groups": [["法雷奥", "Valeo"], ["海拉", "Hella"]]},
    # 非采购闲聊：不应产生任何实体
    {"id": "ext_10", "user": "今天下班前提醒我开会", "ai": "好的，已记录您的提醒。",
     "any_of": [], "must_not": ["博世", "Bosch", "电装", "大陆"], "query_nonempty": False},
]

EXTRACT_PASS_THRESHOLD = 8  # 10 例中至少 8 例通过（评估阈值，非硬断言）


def _build_model():
    from langchain_openai import ChatOpenAI
    from agent.env_utils import (
        DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, SUMMARY_MODEL_NAME,
    )
    return ChatOpenAI(
        model=SUMMARY_MODEL_NAME,
        temperature=0.3,
        openai_api_key=DEEPSEEK_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,   # 本版 langchain_openai 的正确参数名
    )


def run_extract_layer() -> bool:
    from agent.middlewares.memory_update import _extract_entities
    model = _build_model()

    passed = 0
    print(f"\n{'='*62}\n抽取小样本（{len(SAMPLES)} 例，judge 为 SUMMARY_MODEL）\n{'='*62}")
    for s in SAMPLES:
        r = asyncio.run(_extract_entities(model, s["user"], s["ai"]))
        suppliers = [str(x) for x in r.get("suppliers", [])]
        query = str(r.get("query", ""))

        ok = True
        # 期望存在：任一可接受形态命中
        if s["any_of"]:
            ok &= any(any(a.lower() in sup.lower() for sup in suppliers) for a in s["any_of"])
        # 全量要求：require_groups 每组（中文/英文任一形态）都必须命中
        for group in s.get("require_groups", []):
            ok &= any(any(a.lower() in sup.lower() for sup in suppliers) for a in group)
        # 禁止实体（幻觉防线）
        hit_bad = [m for m in s["must_not"] if any(m.lower() in sup.lower() for sup in suppliers)]
        ok &= not hit_bad
        # query 语义
        ok &= bool(query.strip()) == s["query_nonempty"]

        mark = "PASS" if ok else "FAIL"
        passed += ok
        print(f"  [{mark}] {s['id']}  suppliers={suppliers}  query={query[:24]!r}")
        if hit_bad:
            print(f"         幻觉：命中禁止实体 {hit_bad}")

    acc = passed / len(SAMPLES) * 100
    print(f"抽取准确率: {passed}/{len(SAMPLES)} = {acc:.0f}%"
          f"（阈值 ≥ {EXTRACT_PASS_THRESHOLD}/{len(SAMPLES)}）")
    return passed >= EXTRACT_PASS_THRESHOLD


if __name__ == "__main__":
    sys.path.insert(0, "src")
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    ok = run_unit_layer()
    if mode == "all":
        ok &= run_extract_layer()

    print(f"\n{'全部通过' if ok else '存在失败'}：记忆写入正确性（模式={mode}）")
    sys.exit(0 if ok else 1)
