#!/usr/bin/env python3
"""补货决策模型计算脚本（运行在 OpenSandbox 沙箱内，配合 pandas）。

输入：replenish_stock_snapshot 工具输出的 JSON 快照（--input）
输出：补货建议清单 JSON（--output），字段与 SKILL.md 速查表一致

模型公式：
  ROP    = 月消耗 × (提前期天数 / 30) + 安全库存        再订货点
  gap    = max(0, ROP − 当前库存)                        补货缺口
  suggest= ceil(max(gap, 安全库存 − 当前库存))           建议补货量
  days_left = 当前库存 / 月消耗 × 30                      预计耗尽天数
  ABC    = 按 年采购金额（月消耗×均价×12）帕累托累计：≤80% 为 A，≤95% 为 B，其余 C
  urgency: days_left ≤7 → critical; ≤15 → high; ≤30 → medium; 其余 low（无消耗的按 low）

用法：
  python reorder_calc.py --input /analysis/temp/replenish_input.json \
                         --output /analysis/temp/replenish_result.json
"""
import argparse
import json
import math

import pandas as pd

LEAD_TIME_DAYS = 14  # 默认采购提前期（天）


def compute(df: pd.DataFrame) -> pd.DataFrame:
    # 数值列兜底：缺失的消耗/价格按 0 处理，避免 NaN 传播
    for col in ("currentQuantity", "safetyStock", "monthlyConsumption", "avgUnitPrice12m"):
        df[col] = pd.to_numeric(df.get(col), errors="coerce").fillna(0)

    # 再订货点与缺口
    df["reorderPoint"] = (df["monthlyConsumption"] * LEAD_TIME_DAYS / 30.0 + df["safetyStock"]).round(1)
    df["gap"] = (df["reorderPoint"] - df["currentQuantity"]).clip(lower=0).round(1)

    # 建议补货量：不低于"回到安全线"的量，向上取整
    safety_gap = (df["safetyStock"] - df["currentQuantity"]).clip(lower=0)
    df["suggestQuantity"] = pd.concat([df["gap"], safety_gap], axis=1).max(axis=1).apply(math.ceil)

    # 预计耗尽天数（无消耗的物料记 None，不参与紧急度排序）
    with pd.option_context("mode.chained_assignment", None):
        df["daysLeft"] = df.apply(
            lambda r: round(r["currentQuantity"] / r["monthlyConsumption"] * 30.0, 1)
            if r["monthlyConsumption"] > 0 else None, axis=1)

    # 年采购金额 → ABC 帕累托分类
    df["annualSpend"] = (df["monthlyConsumption"] * df["avgUnitPrice12m"] * 12).round(2)
    total = df["annualSpend"].sum()
    if total > 0:
        df = df.sort_values("annualSpend", ascending=False)
        cum = df["annualSpend"].cumsum() / total
        df["abcClass"] = cum.apply(lambda x: "A" if x <= 0.80 else ("B" if x <= 0.95 else "C"))
    else:
        df["abcClass"] = "C"

    # 紧急度（联合缺货天数；ABC 仅作为排序辅助权重）
    def urgency(row):
        d = row["daysLeft"]
        if d is None:
            return "low"
        if d <= 7:
            return "critical"
        if d <= 15:
            return "high"
        if d <= 30:
            return "medium"
        return "low"

    df["urgency"] = df.apply(urgency, axis=1)

    # 优先级排序：先按紧急度、再按 ABC、再按建议金额降序
    rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    abc_rank = {"A": 3, "B": 2, "C": 1}
    df["_u"] = df["urgency"].map(rank)
    df["_a"] = df["abcClass"].map(abc_rank)
    df["estimatedAmount"] = (df["suggestQuantity"] * df["avgUnitPrice12m"]).round(2)
    df = df.sort_values(["_u", "_a", "estimatedAmount"], ascending=False).drop(columns=["_u", "_a"])
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="快照 JSON 文件路径")
    ap.add_argument("--output", required=True, help="建议清单输出路径")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list) or not rows:
        raise SystemExit("输入快照为空或格式不正确（应为 JSON 数组）")

    df = compute(pd.DataFrame(rows))

    # 只输出建议量 > 0 的行 + 统计摘要
    plan = df[df["suggestQuantity"] > 0]
    out_cols = [
        "partId", "partCode", "name", "category", "unit",
        "currentQuantity", "safetyStock", "reorderPoint", "gap",
        "suggestQuantity", "avgUnitPrice12m", "estimatedAmount",
        "monthlyConsumption", "daysLeft", "urgency", "abcClass",
        "supplierId", "lastOrderDate",
    ]
    result = {
        "summary": {
            "totalWarningItems": int(len(df)),
            "needReplenishItems": int(len(plan)),
            "estimatedTotalAmount": round(float(plan["estimatedAmount"].sum()), 2),
            "criticalItems": int((plan["urgency"] == "critical").sum()),
            "highItems": int((plan["urgency"] == "high").sum()),
        },
        "replenishmentPlan": plan[out_cols].where(pd.notnull(plan[out_cols]), None).to_dict("records"),
        "allItems": df[out_cols].where(pd.notnull(df[out_cols]), None).to_dict("records"),
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(plan)}/{len(df)} 项需补货，建议总额 "
          f"¥{result['summary']['estimatedTotalAmount']} → {args.output}")


if __name__ == "__main__":
    main()
