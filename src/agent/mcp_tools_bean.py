from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

# 分组名称常量
GROUP_PART = "part"  # 零配件分组
GROUP_SUPPLIER = "supplier"  # 供应商和零配件分组

class SupplierQueryInput(BaseModel):
    """供应商查询参数模型"""
    name: str = Field(..., description="供应商名称（模糊查询），必填")


class PartSearchInput(BaseModel):
    """零配件搜索参数模型"""
    name: str = Field(..., description="零件名称（模糊查询），必填")


class PartQueryInput(BaseModel):
    """采购零部件查询参数模型"""
    current: Optional[int] = Field(1, description="当前页码，从1开始")
    size: Optional[int] = Field(10, description="每页大小")
    name: Optional[str] = Field(None, description="零件名称（模糊查询）,可以不传，则搜索所有采购零部件")
    category: Optional[str] = Field(None, description="分类(发动机类/车架类/电气类/制动类/传动类/外观件)")
    supplierId: Optional[int] = Field(None, description="供应商ID，根据供应商查询采购零件列表，可以先根据供应商的名字查询出供应商ID。")


class OrderDetailItem(BaseModel):
    """采购订单明细项"""
    partId: int = Field(..., description="零部件 ID，必填")
    quantity: int = Field(..., description="采购数量，必填，最小值为1")
    unitPrice: Decimal = Field(..., description="单价，必填")
    subtotal: Optional[Decimal] = Field(None, description="小计金额，不传则自动计算 = quantity × unitPrice")
    remark: Optional[str] = Field(None, description="明细备注")


class OrderInput(BaseModel):
    """采购订单请求体模型（创建和更新共用）"""
    orderNumber: Optional[str] = Field(
        None,
        description="订单编号（唯一标识，不可重复）。规则：PO+年月日(8位)+3位随机数字。不传则自动生成"
    )
    totalAmount: Optional[Decimal] = Field(None, description="订单总金额，不传则自动根据明细计算")
    status: Optional[int] = Field(
        None,
        description="订单状态(1-待审核, 2-已审核, 3-采购中, 4-已入库, 5-已取消)，默认1"
    )
    orderTime: Optional[str] = Field(
        None,
        description="下单时间，格式：yyyy-MM-ddTHH:mm:ss.SSS。不传则默认当前时间"
    )
    expectedDeliveryDate: Optional[date] = Field(
        None,
        description="预计交货日期，格式：yyyy-MM-dd"
    )
    actualDeliveryDate: Optional[date] = Field(None, description="实际交货日期，格式：yyyy-MM-dd")
    createdBy: Optional[int] = Field(None, description="创建人 ID")
    remark: Optional[str] = Field(None, description="备注")
    orderDetail: Optional[List[OrderDetailItem]] = Field(
        None,
        description="订单明细列表（创建时必填，更新时可选）。每项需提供 partId、quantity、unitPrice"
    )


class OrderSearchInput(BaseModel):
    """采购订单明细搜索参数模型"""
    partName: Optional[str] = Field(None, description="零部件名称（模糊查询）")
    startDate: Optional[str] = Field(None, description="开始日期（yyyy-MM-dd 格式）")
    endDate: Optional[str] = Field(None, description="结束日期（yyyy-MM-dd 格式）")


# create_deep_agent()
# create_summarization_tool_middleware