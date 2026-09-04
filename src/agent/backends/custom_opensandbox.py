# src/backends/open_sandbox_backend.py
"""OpenSandbox 沙箱后端实现，遵循 SandboxBackendProtocol 协议。

安全整改 P0-2（供应链防线，见 文档/安全/本项目安全分析.md）：
    execute() 在命令下发前做 pip 包白名单检查——沙箱能 pip install
    意味着网络出口未默认拒绝，恶意 PyPI 包的 setup.py 可任意执行
    （注入→诱导装包→数据外传是完整 RCE 链）。白名单外的包名直接
    拦截并返回结构化指引（permanent 类错误：请用户决定是否扩充白名单），
    不把供应链决策留给模型。
"""
from __future__ import annotations
import logging
import re
from collections.abc import Callable
from typing import cast

from opensandbox import SandboxSync
from opensandbox.models import WriteEntry

from deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox

SyncPollingInterval = float | Callable[[float], float]
PollingStrategy = Callable[[float], float]
# 配置日志
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.ERROR)

# 如果没有配置日志处理器，则添加一个
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ---- P0-2：pip 包白名单（供应链防线）----
# 只允许安装数据分析场景的常用包。扩充白名单 = 人的决策，不是模型的。
_PIP_PACKAGE_WHITELIST: set[str] = {
    "pandas", "numpy", "matplotlib", "openpyxl", "xlsxwriter",
    "requests", "jsonschema", "pyyaml", "scipy", "seaborn",
    "pillow", "python-dateutil", "pytz", "tabulate",
}

# 匹配 pip install 段：兼容 pip/pip3、-r 前缀选项、&&/;/|/换行 结束
_PIP_INSTALL_RE = re.compile(
    r"\bpip3?\s+install((?:\s+-{1,2}[\w-]+(?:\s+[\w./=-]+)?)*)\s+([^\s;&|]+(?:\s+[^\s;&|]+)*)"
)


# 文件型安装选项：无法从命令行枚举实际包名，是绕过白名单的天然通道
_PIP_FILE_OPT_RE = re.compile(r"(?:^|\s)-(?:r|c)(?:\s|$)|\s--(?:requirement|constraint)\b")


def _pip_violation(command: str) -> str | None:
    """检查命令中的 pip install 是否全在白名单内。

    Returns:
        None = 通过（无 pip install，或所有包都在白名单内）；
        str  = 拦截原因（第一个白名单外的包名，或 "requirements-file"）。
    """
    for m in _PIP_INSTALL_RE.finditer(command):
        opts = (m.group(1) or "").strip()
        # -r/-c/--requirement/--constraint 文件型安装：文件内容不可见，
        # 白名单无从校验——整体拦截（含误报容忍：宁可拦下重写为显式包名）
        if _PIP_FILE_OPT_RE.search(f" {opts} " if opts else ""):
            return "requirements-file"
        pkgs = m.group(2).split()
        for p in pkgs:
            # 归一化：去掉版本约束（pandas==2.0 / numpy>=1.20）与引号；
            # git+https://… / . / ../local 等本地与 URL 源不在白名单内，自然被拦
            name = re.split(r"[=<>!\[~#@]", p)[0].strip("'\"").lower()
            if name and name not in _PIP_PACKAGE_WHITELIST:
                return name
    return None

class OpenSandboxBackend(BaseSandbox):
    """基于 OpenSandbox 的沙箱后端。

    继承 BaseSandbox 的文件操作方法，仅实现 execute、download_files 和 upload_files。
    """

    def __init__(
            self,
            *,
            sandbox: SandboxSync,
            timeout: int = 60 * 60,
            sync_polling_interval: SyncPollingInterval = 0.1,
    ) -> None:
        """创建一个包装已有 OpenSandbox 沙盒的后端实例。

        Args：
            sandbox：要包装的现有 OpenSandbox 沙盒实例。
            timeout：调用 `execute()` 且未显式指定 `timeout` 时使用的默认命令超时时间（秒）。
            sync_polling_interval：在同步执行路径上，轮询 OpenSandbox 命令完成状态的间隔时间（秒）；
                也可以是一个可调用对象，接收已执行的秒数并返回下一次轮询的延迟时间。
        """
        logger.info(f"正在初始化 OpenSandbox，沙盒 ID: {sandbox.id}")
        self._sandbox = sandbox
        # sandbox.kill()  # 手动关闭沙箱
        self._default_timeout = timeout

        # 处理轮询策略
        if callable(sync_polling_interval):
            polling_strategy = cast("PollingStrategy", sync_polling_interval)
        else:
            def polling_strategy(_elapsed: float) -> float:
                return sync_polling_interval

        self._sync_polling_interval = polling_strategy
        logger.debug(f"OpenSandbox 初始化完成，默认超时时间={timeout}秒")

    @property
    def id(self) -> str:
        """返回 OpenSandbox 沙盒的 ID。"""
        sandbox_id = self._sandbox.id
        logger.debug(f"获取沙盒 ID: {sandbox_id}")
        return sandbox_id

    # 沙箱中非交互式 shell 不会加载 /etc/profile，需要手动注入环境变量
    SANDBOX_PATH = (
        "/opt/skills-venv/bin:"
        "/opt/python/versions/cpython-3.11.14-linux-x86_64-gnu/bin:"
        "/opt/go/1.25.5/bin:"
        "/opt/node/v22.2.0/bin:"
        "/usr/lib/jvm/java-21-openjdk-amd64/bin:"
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    )

    def execute(
            self,
            command: str,
            *,
            timeout: int | None = None,
    ) -> ExecuteResponse:
        """在沙盒内部执行一条 Shell 命令。

        Args：
            command：要执行的 Shell 命令字符串。
            timeout：等待命令完成的最大时间（秒）。
                如果为 None，则使用后端默认的超时时间。
        """
        effective_timeout = timeout if timeout is not None else self._default_timeout

        # P0-2：供应链防线——pip install 白名单外的包直接拦截（不下发沙箱）。
        # 这是确定性代码护栏：模型"可能被注入诱导装恶意包"的场景一律代码兜底。
        bad_pkg = _pip_violation(command)
        if bad_pkg is not None:
            logger.warning("SUPPLY_CHAIN_BLOCK 拦截白名单外的 pip 安装: %s", bad_pkg)
            return ExecuteResponse(
                output=(
                    f"pip install 被安全策略拦截：包 '{bad_pkg}' 不在允许清单内"
                    f"（{sorted(_PIP_PACKAGE_WHITELIST)}）。\n"
                    '[错误处理指引] {"error_type": "permanent"}\n'
                    "供应链防线：沙箱只允许安装白名单内的常用数据分析包，"
                    "重试无效。若任务确需该包，如实向用户说明包名与用途，"
                    "由用户决定是否扩充白名单——不擅自绕过、不换渠道安装。"
                ),
                exit_code=1,
                truncated=False,
            )

        # 非交互式 shell 不会 source /etc/profile，需要注入 PATH 确保 pip/python 可用
        wrapped = f'export PATH="{self.SANDBOX_PATH}:$PATH" && {command}'
        logger.debug(f"准备执行命令：{command[:100]}...（超时时间={effective_timeout}秒）")
        return self._execute_command(wrapped, timeout=effective_timeout)

    def _execute_command(
            self,
            command: str,
            *,
            timeout: int,
    ) -> ExecuteResponse:
        """使用 OpenSandbox 的 API 执行命令。"""
        try:
            logger.debug(f"通过 OpenSandbox API 执行命令：{command}")
            result = self._sandbox.commands.run(command)
            logger.debug(f"命令执行完成，退出码：{result.exit_code}")

            # 提取标准输出与标准错误
            stdout = ""
            stderr = ""

            if result.logs.stdout:
                stdout = "\n".join([log.text for log in result.logs.stdout])
                logger.debug(f"命令标准输出长度：{len(stdout)} 字符")

            if result.logs.stderr:
                stderr = "\n".join([log.text for log in result.logs.stderr])
                logger.debug(f"命令标准错误长度：{len(stderr)} 字符")

            # 合并输出
            output = stdout
            if stderr and stderr.strip():
                output += f"\n<stderr>{stderr.strip()}</stderr>"

            # loop 改造 C：命令失败时的结构化重试指引。
            # 注意只对"真实错误签名"（traceback/异常/超时）追加，不污染
            # grep 无匹配这类正常的非零退出——指引要出现在模型需要它的时刻。
            exit_code = result.exit_code or 0
            if exit_code != 0:
                low = output.lower()
                if exit_code == 124 or "timeout" in low or "timed out" in low:
                    output += ('\n[错误处理指引] {"error_type": "transient", "retry_budget": 1}\n'
                               '命令超时：可原样重试一次；仍超时则缩小数据量或分步执行。')
                elif "traceback" in low or "error" in low or "exception" in low:
                    output += ('\n[错误处理指引] {"error_type": "permanent"}\n'
                               '命令执行失败：读完整 traceback 定位原因（缺包→pip install 后重跑；'
                               '语法/名字错→修复代码；数据为空→回上游重新查），'
                               '同类错误连续 2 次未解决就停止重试并如实报告。')

            logger.info(f"命令执行成功，退出码：{exit_code}")
            return ExecuteResponse(
                output=output,
                exit_code=exit_code,
                truncated=False,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"执行命令时发生错误：{error_msg}", exc_info=True)

            if "timeout" in error_msg.lower():
                logger.warning(f"命令在 {timeout} 秒后超时")
                return ExecuteResponse(
                    output=(f"命令在 {timeout} 秒后超时"
                            f'\n[错误处理指引] {{"error_type": "transient", "retry_budget": 1}}'
                            f"\n超时：可原样重试一次；仍超时则缩小数据量或分步执行。"),
                    exit_code=124,
                    truncated=False,
                )

            return ExecuteResponse(
                output=(f"执行命令时出错：{error_msg}"
                        f'\n[错误处理指引] {{"error_type": "transient", "retry_budget": 1}}'
                        f"\n基础设施层异常：等待 2 秒后原样重试一次；"
                        f"连续失败则停止重试并如实报告。"),
                exit_code=1,
                truncated=False,
            )

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """从沙箱下载指定文件。

        Args:
            paths: 沙箱中的绝对文件路径列表。

        Returns:
            与 paths 顺序对应的响应列表，包含文件内容或错误信息。
        """
        responses: list[FileDownloadResponse] = []

        for path in paths:
            if not path.startswith("/"):
                responses.append(
                    FileDownloadResponse(path=path, content=None, error="invalid_path")
                )
                continue
            try:
                content = self._sandbox.files.read_file(path)
                # 统一转为 bytes
                content_bytes = content.encode("utf-8") if isinstance(content, str) else content
                responses.append(
                    FileDownloadResponse(path=path, content=content_bytes, error=None)
                )
            except Exception:
                responses.append(
                    FileDownloadResponse(path=path, content=None, error="file_not_found")
                )

        return responses

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """上传文件到沙箱。

        Args:
            files: 每个元素为 (绝对路径, 文件内容字节) 的元组列表。

        Returns:
            与 files 顺序对应的响应列表，包含操作错误信息（成功时为 None）。
        """
        responses: list[FileUploadResponse] = []
        upload_entries: list[WriteEntry] = []

        for path, content in files:
            if not path.startswith("/"):
                responses.append(FileUploadResponse(path=path, error="invalid_path"))
                continue
            try:
                # 将 bytes 转换为字符串用于写入
                if isinstance(content, bytes):
                    try:
                        content_str = content.decode("utf-8")
                    except UnicodeDecodeError:
                        content_str = content.decode("latin-1")
                else:
                    content_str = str(content)
                upload_entries.append(WriteEntry(path=path, data=content_str, mode=0o644))
                responses.append(FileUploadResponse(path=path, error=None))
            except Exception as e:
                responses.append(FileUploadResponse(path=path, error=str(e)))

        if upload_entries:
            try:
                self._sandbox.files.write_files(upload_entries)
            except Exception as e:
                # 若写操作失败，将所有成功准备但未真正上传的条目标记为错误
                for resp in responses:
                    if resp.error is None:
                        resp.error = f"upload_failed: {e}"

        return responses