from datetime import datetime, timedelta, timezone

from fastmcp import FastMCP, Context

GROUP_NAME = "replenish"

# 历史统计窗口（天）：用于计算物料消耗速率与采购频次
HISTORY_WINDOW_DAYS = 365


def _parse_time(value) -> datetime | None:
    """解析 Java 后端返回的时间字符串（兼容 'T' 分隔与空格分隔两种格式）。"""
    if not value or not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:26] if "." in value else value[:19], fmt)
        except ValueError:
            continue
    return None


def _aggregate_history(details: list, window_days: int) -> dict:
    """按 partId 聚合订单明细：采购次数 / 总量 / 均价 / 月消耗 / 最近采购日。"""
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=window_days)
    stats: dict[int, dict] = {}

    for d in details:
        part_id = d.get("partId")
        if part_id is None:
            continue
        created = _parse_time(d.get("createTime"))
        # 只统计窗口内的明细；时间缺失的行跳过（无法判断归属期）
        if created is None or created < cutoff:
            continue

        s = stats.setdefault(part_id, {
            "order_count": 0,
            "total_quantity": 0,
            "total_amount": 0.0,
            "last_order_date": None,
        })
        qty = d.get("quantity") or 0
        price = d.get("unitPrice") or 0.0
        s["order_count"] += 1
        s["total_quantity"] += qty
        s["total_amount"] += float(qty) * float(price)
        if s["last_order_date"] is None or created > s["last_order_date"]:
            s["last_order_date"] = created

    # 派生指标：平均单价、月消耗速率
    for s in stats.values():
        avg_price = (s["total_amount"] / s["total_quantity"]) if s["total_quantity"] else 0.0
        s["avg_unit_price"] = round(avg_price, 2)
        s["monthly_consumption"] = round(s["total_quantity"] * 30.0 / window_days, 2)
        s["last_order_date"] = (
            s["last_order_date"].strftime("%Y-%m-%d") if s["last_order_date"] else None
        )
    return stats


def register_replenishment_tools(mcp: FastMCP):
    """注册智能补货分组的所有工具。

    与其他分组（suppliers/parts/order/inventory）的"透传型"工具不同，
    本分组是"聚合型"工具：服务端调用多个 Java 端点并做 join / 统计，
    客户端（Agent）一次调用即可拿到分析原料，减少往返与上下文消耗。
    """

    @mcp.tool(name=f"{GROUP_NAME}_stock_snapshot")
    async def replenish_stock_snapshot(ctx: Context) -> list:
        """
        获取补货分析快照：库存预警列表 × 近12个月采购历史的聚合数据。
        对每个库存低于安全库存的物料，返回：
        当前库存、安全库存、预警值、采购价、供应商ID、类别、单位，
        以及近12个月的采购次数、采购总量、平均单价、月消耗速率、最近采购日期。
        这是补货建议模型（ROP/EOQ/ABC）的输入原料，无需传参。
        """
        http_client = ctx.request_context.lifespan_context.get("http_client")

        try:
            # 聚合数据源 1：库存预警（含内嵌 partDetail）
            inv_resp = await http_client.get("/inventory/warning")
            inv_resp.raise_for_status()
            inv_result = inv_resp.json()
            if inv_result.get("code") != 200:
                return [f"API error: code={inv_result.get('code')}"]

            # 聚合数据源 2：订单明细（全量历史）
            order_resp = await http_client.get("/orders/search-details")
            order_resp.raise_for_status()
            order_result = order_resp.json()
            if order_result.get("code") != 200:
                return [f"API error: code={order_result.get('code')}"]
        except Exception as e:
            return [f'没有查询到任何信息，而且报错: {e}']

        warnings = inv_result.get("data", []) or []
        details = order_result.get("data", []) or []

        # 服务端 join：按 partId 把历史消耗统计合并进库存预警行
        history = _aggregate_history(details, HISTORY_WINDOW_DAYS)

        snapshot = []
        for w in warnings:
            part = w.get("partDetail") or {}
            part_id = w.get("partId")
            h = history.get(part_id, {})
            snapshot.append({
                # 库存侧
                "partId": part_id,
                "partCode": part.get("partCode"),
                "name": part.get("name"),
                "model": part.get("model"),
                "category": part.get("category"),
                "unit": part.get("unit"),
                "currentQuantity": w.get("currentQuantity"),
                "safetyStock": w.get("safetyStock"),
                "stockWarningValue": part.get("stockWarningValue"),
                "warehouseLocation": w.get("warehouseLocation"),
                # 采购侧（近 12 个月）
                "purchasePrice": part.get("purchasePrice"),
                "supplierId": part.get("supplierId"),
                "orderCount12m": h.get("order_count", 0),
                "totalQuantity12m": h.get("total_quantity", 0),
                "avgUnitPrice12m": h.get("avg_unit_price", 0.0),
                "monthlyConsumption": h.get("monthly_consumption", 0.0),
                "lastOrderDate": h.get("last_order_date"),
            })
        return snapshot

    @mcp.tool(name=f"{GROUP_NAME}_part_history")
    async def replenish_part_history(part_name: str, ctx: Context) -> list:
        """
        按物料名称深挖其全部采购历史明细（不限于近12个月）。
        返回每次采购的：订单ID、数量、单价、小计、采购时间。
        用于对某一重点物料做更细的采购节奏分析（如季节性波动）。

        Args:
            part_name: 物料名称关键词（模糊匹配，如"火花塞"）
        """
        http_client = ctx.request_context.lifespan_context.get("http_client")

        try:
            response = await http_client.get(
                "/orders/search-details", params={"partName": part_name}
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 200:
                return [f"API error: code={result.get('code')}"]
        except Exception as e:
            return [f'没有查询到任何信息，而且报错: {e}']

        details = result.get("data", []) or []
        # 服务端只保留分析所需字段并按时间倒序（明细可能很多，压缩上下文）
        rows = []
        for d in sorted(details, key=lambda x: str(x.get("createTime") or ""), reverse=True):
            part = d.get("partDetail") or {}
            rows.append({
                "orderId": d.get("orderId"),
                "partId": d.get("partId"),
                "partName": part.get("name"),
                "quantity": d.get("quantity"),
                "unitPrice": d.get("unitPrice"),
                "subtotal": d.get("subtotal"),
                "createTime": d.get("createTime"),
                "supplierId": part.get("supplierId"),
            })
        return rows
