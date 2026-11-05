import json
import random
from datetime import datetime
from decimal import Decimal

from fastmcp import FastMCP, Context

from mcp_server.order_idempotency import ORDER_CREATES
from mcp_server.order_version import ORDER_VERSIONS

from typing import Optional, List

GROUP_NAME = "order"


def _generate_order_number() -> str:
    """生成订单编号：PO + 年月日(8位) + 3位随机数字"""
    today = datetime.now().strftime("%Y%m%d")
    suffix = str(random.randint(0, 999)).zfill(3)
    return f"PO{today}{suffix}"


def _prepare_request(data: dict) -> dict:
    """填充默认值并序列化请求体：Decimal→float，date→ISO字符串"""
    # 自动生成 orderNumber
    if not data.get("orderNumber"):
        data["orderNumber"] = _generate_order_number()

    # 默认 orderTime（格式：yyyy-MM-ddTHH:mm:ss.SSS，匹配后端 CustomLocalDateTimeDeserializer）
    if not data.get("orderTime"):
        now = datetime.now()
        data["orderTime"] = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}"

    # 递归序列化
    return _serialize_request(data)


def _serialize_request(data: dict) -> dict:
    """递归处理：Decimal → float，date/datetime → ISO 字符串"""
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
        elif hasattr(value, "isoformat"):
            data[key] = value.isoformat()
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _serialize_request(item)
        elif isinstance(value, dict):
            _serialize_request(value)
    return data


def register_order_tools(mcp: FastMCP):
    """注册订单分组的所有工具"""

    @mcp.tool(name=f"{GROUP_NAME}_create")
    async def create_order(
        order_detail: List[dict],
        idempotency_key: str,
        order_number: Optional[str] = None,
        total_amount: Optional[float] = None,
        status: Optional[int] = None,
        order_time: Optional[str] = None,
        expected_delivery_date: Optional[str] = None,
        actual_delivery_date: Optional[str] = None,
        created_by: Optional[int] = None,
        remark: Optional[str] = None,
        ctx: Context = None,
    ) -> dict:
        """
        创建采购订单（POST /orders/create），带幂等防重。

        orderNumber 不传则自动生成（规则：PO+年月日+3位随机数字）。
        orderTime 不传则默认当前时间（格式：yyyy-MM-ddTHH:mm:ss.SSS）。
        orderDetail 必填，至少包含一个明细项；每项需提供 partId、quantity、unitPrice。

        同一个 idempotency_key 只真正创建一次：并发或重试时直接返回首次成功
        结果，并带 idempotentReplay=true。新采购意图必须使用新键；同一审批的
        重试必须复用原键。同一个键若携带不同订单参数，返回 409 而不写 ERP。

        Args:
            order_detail: 订单明细列表，每项需提供 partId, quantity, unitPrice，可选 subtotal, remark
            idempotency_key: 创建请求的唯一幂等键（必填，建议 UUID）
            order_number: 订单编号（唯一标识），不传则自动生成
            total_amount: 订单总金额，不传则自动根据明细计算
            status: 订单状态(1-待审核, 2-已审核, 3-采购中, 4-已入库, 5-已取消)，默认1
            order_time: 下单时间，格式 yyyy-MM-ddTHH:mm:ss.SSS，不传则默认当前时间
            expected_delivery_date: 预计交货日期，格式 yyyy-MM-dd
            actual_delivery_date: 实际交货日期，格式 yyyy-MM-dd
            created_by: 创建人 ID
            remark: 备注
        """
        http_client = ctx.request_context.lifespan_context.get("http_client")
        idempotency_key = idempotency_key.strip()
        if not idempotency_key:
            return {"error": "idempotency_key 不能为空"}

        # 构建请求体（映射到 API 字段名）
        request_data = {}
        if order_number is not None:
            request_data["orderNumber"] = order_number
        if total_amount is not None:
            request_data["totalAmount"] = total_amount
        if status is not None:
            request_data["status"] = status
        if order_time is not None:
            request_data["orderTime"] = order_time
        if expected_delivery_date is not None:
            request_data["expectedDeliveryDate"] = expected_delivery_date
        if actual_delivery_date is not None:
            request_data["actualDeliveryDate"] = actual_delivery_date
        if created_by is not None:
            request_data["createdBy"] = created_by
        if remark is not None:
            request_data["remark"] = remark
        if order_detail is not None:
            request_data["orderDetail"] = order_detail

        # 指纹只取业务参数，不含自动生成的订单号/时间，识别"同键不同单"
        fingerprint = json.dumps(
            request_data, ensure_ascii=False, sort_keys=True, default=str
        )

        # 同一幂等键串行：第一个请求写 ERP，其余请求等待并复用首次结果
        async with ORDER_CREATES.hold(idempotency_key):
            record = ORDER_CREATES.get(idempotency_key)
            if record is not None:
                if record.fingerprint != fingerprint:
                    return {
                        "code": 409,
                        "error": "idempotency_key_conflict",
                        "message": "同一 idempotency_key 不能用于不同的订单参数",
                    }
                return {**record.result, "idempotentReplay": True}

            request_data = _prepare_request(request_data)
            try:
                print(request_data)
                response = await http_client.post(
                    "/orders/create",
                    json=request_data
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 200:
                    return {
                        "error": f"API error: code={result.get('code')}, message={result.get('message')}"
                    }

                data = result.get("data", {})
                if isinstance(data, dict):
                    # 只缓存成功结果；失败不缓存，允许同一键安全重试
                    ORDER_CREATES.put(idempotency_key, fingerprint, data)
                    # 新订单登记版本 1；重放不会再次登记或覆盖后续更新版本
                    if data.get("id") is not None:
                        ORDER_VERSIONS.set_version(int(data["id"]), 1)
                return data
            except Exception as e:
                return {"error": str(e)}

    @mcp.tool(name=f"{GROUP_NAME}_version")
    async def get_order_version(order_id: int) -> dict:
        """
        读取订单当前版本号（MCP 服务端维护的写入版本，不读 ERP）。

        修改订单前必须先调用本工具，把返回的 version 作为
        `order_update` 的 `expected_version` 传回去。版本不一致时更新会被
        拒绝（code=409），说明订单在读取之后被别人改过，需要重新读取。

        Args:
            order_id: 订单 ID
        """
        return {"orderId": order_id, "version": ORDER_VERSIONS.version(order_id)}

    @mcp.tool(name=f"{GROUP_NAME}_update")
    async def update_order(
        order_id: int,
        expected_version: int,
        order_detail: Optional[List[dict]] = None,
        order_number: Optional[str] = None,
        total_amount: Optional[float] = None,
        status: Optional[int] = None,
        order_time: Optional[str] = None,
        expected_delivery_date: Optional[str] = None,
        actual_delivery_date: Optional[str] = None,
        created_by: Optional[int] = None,
        remark: Optional[str] = None,
        ctx: Context = None,
    ) -> dict:
        """
        更新采购订单（PUT /orders/update/{id}），带版本 CAS 校验。

        orderDetail 为可选，传入则替换原有明细。
        其他字段与创建订单格式一致。

        版本校验：调用前先用 `order_version` 读取当前版本，原样传入
        `expected_version`。服务端会在一把订单级锁内做"比较版本 → 写 ERP
        → 版本加一"；版本不一致时返回 code=409、不写 ERP，说明订单在你
        读取之后已经被别人改过。

        Args:
            order_id: 订单 ID（路径参数，必填）
            expected_version: 你读到的订单版本（必填），来自 order_version
            order_detail: 订单明细列表（可选），每项需提供 partId, quantity, unitPrice
            order_number: 订单编号
            total_amount: 订单总金额
            status: 订单状态(1-待审核, 2-已审核, 3-采购中, 4-已入库, 5-已取消)
            order_time: 下单时间
            expected_delivery_date: 预计交货日期
            actual_delivery_date: 实际交货日期
            created_by: 创建人 ID
            remark: 备注
        """
        http_client = ctx.request_context.lifespan_context.get("http_client")

        # 构建请求体（映射到 API 字段名，只包含非 None 字段）
        request_data = {}
        if order_number is not None:
            request_data["orderNumber"] = order_number
        if total_amount is not None:
            request_data["totalAmount"] = total_amount
        if status is not None:
            request_data["status"] = status
        if order_time is not None:
            request_data["orderTime"] = order_time
        if expected_delivery_date is not None:
            request_data["expectedDeliveryDate"] = expected_delivery_date
        if actual_delivery_date is not None:
            request_data["actualDeliveryDate"] = actual_delivery_date
        if created_by is not None:
            request_data["createdBy"] = created_by
        if remark is not None:
            request_data["remark"] = remark
        if order_detail is not None:
            request_data["orderDetail"] = order_detail

        request_data = _prepare_request(request_data)

        # ---- CAS：同一订单的"比较版本 + 写入 ERP + 版本加一"必须在同一把锁内 ----
        async with ORDER_VERSIONS.hold(order_id):
            current_version = ORDER_VERSIONS.version(order_id)
            if expected_version != current_version:
                return {
                    "code": 409,
                    "error": "order_version_conflict",
                    "message": (
                        f"订单 {order_id} 已被他人修改：期望版本 {expected_version}，"
                        f"当前版本 {current_version}；请重新读取订单后再提交审批"
                    ),
                    "expectedVersion": expected_version,
                    "currentVersion": current_version,
                }

            try:
                print(request_data)
                response = await http_client.put(
                    f"/orders/update/{order_id}",
                    json=request_data
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") != 200:
                    return {
                        "error": f"API error: code={result.get('code')}, message={result.get('message')}"
                    }

                # 写成功才推进版本；失败保持原版本，允许安全重试
                next_version = ORDER_VERSIONS.bump(order_id)
                data = result.get("data", {})
                if isinstance(data, dict):
                    data["version"] = next_version
                return data
            except Exception as e:
                return {"error": str(e)}

    @mcp.tool(name=f"{GROUP_NAME}_search_details")
    async def search_order_details(
        part_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ctx: Context = None,
    ) -> list:
        """
        搜索采购订单明细。

        支持按零部件名称、日期范围筛选，所有参数均为可选。
        返回的每条明细包含零部件详情（partDetail）及供应商信息（supplier）。

        Args:
            part_name: 零部件名称（模糊查询），可选
            start_date: 开始日期（yyyy-MM-dd 格式），可选
            end_date: 结束日期（yyyy-MM-dd 格式），可选
        """
        http_client = ctx.request_context.lifespan_context.get("http_client")

        # 构建请求参数（过滤 None 值，映射到 API 字段名）
        request_params = {}
        if part_name is not None:
            request_params["partName"] = part_name
        if start_date is not None:
            request_params["startDate"] = start_date
        if end_date is not None:
            request_params["endDate"] = end_date

        try:
            response = await http_client.get(
                "/orders/search-details",
                params=request_params
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 200:
                return [f"API error: code={result.get('code')}"]

            return result.get("data", [])
        except Exception as e:
            return [f'没有查询到任何信息，而且报错: {e}']