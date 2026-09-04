"""
SandboxBackendProxy — 稳定句柄，内部 backend 可热替换。

显式代理 SandboxBackendProtocol 全部 18 个方法 + id property，
确保 Python MRO 不会找到协议层的 NotImplementedError 默认实现。
"""
from __future__ import annotations

from deepagents.backends.protocol import (
    EditResult,
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
    SandboxBackendProtocol,
    WriteResult,
)


class SandboxBackendProxy(SandboxBackendProtocol):
    """代理所有 SandboxBackendProtocol 方法到内部 backend，支持热替换。"""

    def __init__(self, backend: SandboxBackendProtocol) -> None:
        self._backend = backend

    @property
    def id(self) -> str:
        return self._backend.id

    def replace_backend(self, backend: SandboxBackendProtocol) -> None:
        self._backend = backend

    # ---- 同步方法 ----

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        return self._backend.execute(command, timeout=timeout)

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        return self._backend.read(file_path, offset, limit)

    def write(self, file_path: str, content: str) -> WriteResult:
        return self._backend.write(file_path, content)

    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> EditResult:
        return self._backend.edit(file_path, old_string, new_string, replace_all)

    # 新版文件列举 API（deepagents >= 0.5）。必须显式转发，否则协议层
    # BackendProtocol.ls() 默认实现会因本类重写了 ls_info 而走 deprecated
    # 分支，在底层 ls() 返回 error（如目录不存在）时抛
    # NotImplementedError("This behavior is only available via the new `ls` API.")
    def ls(self, path: str):
        return self._backend.ls(path)

    def glob(self, pattern: str, path: str = "/"):
        return self._backend.glob(pattern, path)

    def ls_info(self, path: str) -> list:
        return self._backend.ls(path).entries or []

    def glob_info(self, pattern: str, path: str = "/") -> list:
        return self._backend.glob(pattern, path).matches or []

    def grep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> list | str:
        return self._backend.grep_raw(pattern, path, glob)

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        return self._backend.upload_files(files)

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        return self._backend.download_files(paths)

    # ---- 异步方法 ----

    async def aexecute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        return await self._backend.aexecute(command, timeout=timeout)

    async def aread(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        return await self._backend.aread(file_path, offset, limit)

    async def awrite(self, file_path: str, content: str) -> WriteResult:
        return await self._backend.awrite(file_path, content)

    async def aedit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> EditResult:
        return await self._backend.aedit(file_path, old_string, new_string, replace_all)

    async def als_info(self, path: str) -> list:
        return (await self._backend.als(path)).entries or []

    async def aglob_info(self, pattern: str, path: str = "/") -> list:
        return (await self._backend.aglob(pattern, path)).matches or []

    async def agrep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> list | str:
        return await self._backend.agrep_raw(pattern, path, glob)

    async def aupload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        return await self._backend.aupload_files(files)

    async def adownload_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        return await self._backend.adownload_files(paths)

    # ---- fallback：未来新增的方法 ----

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._backend, name)
