"""图片内容防护中间件（修复方向C坑3：看图崩溃）。

背景（2026-08-31 方向C回归测试发现的产品 bug）：
    补货 Agent 在沙箱用 matplotlib 生成图表后，调用 read_file "查看"图片
    ——沙箱文件系统对图片返回 base64 image content（[{'type':'image',
    'base64': 'iVBOR...'}]），该内容随对话历史回传给 deepseek-v4-flash
    （纯文本模型）→ 400 This model does not support image → run 直接崩溃。
    且该崩溃是路径相关的非确定性行为（未走图表路径的任务侥幸通过）。

修复策略（治本，框架层拦截而非堵某个工具）：
    任何工具返回的 ToolMessage.content 若为列表且包含图片项，就把图片项
    替换为文字说明——模型看到"图片已生成但内容已省略"，不再收到二进制
    图片数据，纯文本模型不会被炸；文件本身仍在沙箱，路径信息保留在
    剩余文本里，报告引用不受影响。

    兼容两种图片形态：
    - {'type': 'image', 'base64': ...}          （OpenSandbox read_file 实测形态）
    - {'type': 'image_url', 'image_url': {...}} （OpenAI 标准多模态格式）

挂载位置（与 ToolErrorMiddleware 相邻，ToolError 之后）：
    - main_agent.py 主 Agent 中间件栈
    - async_procurement_analyst.py / async_procurement_replenish.py 异步图
      （坑3实际发生地——2024 进程的补货图）
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

logger = logging.getLogger(__name__)

# 图片项替换后的文字说明（模型可读：知道图已生成、为何看不到内容）
_REPLACEMENT_NOTE = (
    "[图片内容已省略：当前模型为纯文本，无法查看图片。"
    "图片文件已保存，可按返回文本中的路径引用到报告里，请勿再次读取图片文件。]"
)


def _strip_images(content) -> object:
    """把 content 列表中的图片项替换为文字说明；无图片则原样返回。"""
    if not isinstance(content, list):
        return content
    has_image = False
    cleaned = []
    for item in content:
        if isinstance(item, dict) and item.get("type") in ("image", "image_url"):
            has_image = True
            cleaned.append({"type": "text", "text": _REPLACEMENT_NOTE})
        else:
            cleaned.append(item)
    return cleaned if has_image else content


class ImageGuardMiddleware(AgentMiddleware):
    """拦截工具返回的图片内容，防止纯文本模型被 400 击穿。"""

    state_schema = AgentState

    def _guard(self, result):
        if isinstance(result, ToolMessage) and isinstance(result.content, list):
            new_content = _strip_images(result.content)
            if new_content is not result.content:
                logger.info("image_guard: 已拦截工具返回的图片内容（替换为文字说明）")
                # ToolMessage 不可变约定下用 model_copy 构造新实例
                return result.model_copy(update={"content": new_content})
        return result

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        return self._guard(handler(request))

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        return self._guard(await handler(request))
