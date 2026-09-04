"""Global OpenSandbox manager shared by FastAPI and Agent Protocol processes.

The project runs the main agent in FastAPI and the async analyst graph in a
separate Agent Protocol process. Python objects cannot be shared across those
processes, so this module persists the single global sandbox id to disk and
lets each process reconnect to the same sandbox.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from opensandbox import SandboxSync
from opensandbox.config import ConnectionConfigSync

from agent.backends.custom_opensandbox import OpenSandboxBackend
from agent.backends.sandbox_proxy import SandboxBackendProxy
from agent.env_utils import SANDBOX_DOMAIN

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"
STATE_DIR = PROJECT_ROOT / ".langgraph_api"
STATE_FILE = STATE_DIR / "global_sandbox.json"

LOCAL_SKILLS_DIR = SRC_DIR / "skills"
LOCAL_AGENTS_MD = SRC_DIR / "agent" / "memory" / "AGENTS.md"
AGENTS_MD_FILENAME = "/AGENTS.md"
SANDBOX_SKILLS_ROOT = "/skills"

SANDBOX_IMAGE = (
    "sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/"
    "code-interpreter:v1.0.2"
)

SANDBOX_CONFIG = ConnectionConfigSync(
    domain=SANDBOX_DOMAIN,
    use_server_proxy=True,
    request_timeout=timedelta(seconds=60),
    transport=httpx.HTTPTransport(limits=httpx.Limits(max_connections=20)),
)

_lock = threading.RLock()
_proxy: SandboxBackendProxy | None = None


def _read_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("Failed to read global sandbox state", exc_info=True)
        return {}


def _write_state(sandbox_id: str) -> None:
    """把沙箱的当前状态写入本地文件，采用临时文件 + 原子替换的方式保证写入安全。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "sandbox_id": sandbox_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


def _connect_sandbox(sandbox_id: str) -> OpenSandboxBackend:
    sandbox = SandboxSync.connect(sandbox_id, connection_config=SANDBOX_CONFIG)
    backend = OpenSandboxBackend(sandbox=sandbox)
    _ping_backend(backend)
    _ensure_sandbox_ready(backend)
    return backend


def _create_sandbox() -> OpenSandboxBackend:
    sandbox = SandboxSync.create(
        SANDBOX_IMAGE,
        entrypoint=["/opt/opensandbox/code-interpreter.sh"],
        env={"PYTHON_VERSION": "3.11"},
        resource={"cpu": "1", "memory": "2Gi"},
        # timeout 是沙箱的"最大存活时长"（TTL，SDK 文档：Maximum sandbox lifetime），
        # 不是创建等待时间。原 10 分钟过短——沙箱每 10 分钟到期被服务端销毁，
        # 下一个请求就会撞上 404（日志刷 "Sandbox ... not found"）并触发 ~20s 重建。
        # 改为 23 小时，覆盖整个开发日；须小于服务端上限
        # max_sandbox_timeout_seconds=86400（24h，见 .sandbox.toml [server]）。
        # OpenSandbox 服务端重启导致的沙箱丢失仍由 get_global_sandbox_sync 自愈兜底。
        timeout=timedelta(hours=23),
        # code-interpreter 镜像启动时需安装多语言内核（首次 >30s），
        # SDK 默认 ready_timeout=30s 过短会导致健康检查超时
        ready_timeout=timedelta(minutes=5),
        connection_config=SANDBOX_CONFIG,
    )
    backend = OpenSandboxBackend(sandbox=sandbox)
    _ensure_sandbox_ready(backend)
    _write_state(backend.id)
    return backend


def _ping_backend(backend: OpenSandboxBackend | SandboxBackendProxy) -> None:
    result = backend.execute("echo ok", timeout=30)
    if result.exit_code != 0:
        raise RuntimeError(f"Sandbox health check failed: {result.output[:500]}")


def _ensure_sandbox_ready(backend: OpenSandboxBackend | SandboxBackendProxy) -> None:
    backend.execute("mkdir -p /analysis/temp")
    backend.execute("python3 -m venv /opt/skills-venv", timeout=120)
    sentinel = "/tmp/.global_sandbox_packages_installed"
    if backend.execute(f"test -f {sentinel}").exit_code != 0:
        result = backend.execute(
            "/opt/skills-venv/bin/pip install requests beautifulsoup4 "
            "-i https://mirrors.aliyun.com/pypi/simple/ --default-timeout=60 --no-input -q",
            timeout=300,
        )
        if result.exit_code == 0:
            backend.execute(f"touch {sentinel}")
    _seed_files(backend)


def _seed_files(backend: OpenSandboxBackend | SandboxBackendProxy) -> None:
    uploads: list[tuple[str, bytes]] = []
    if LOCAL_AGENTS_MD.exists():
        uploads.append((AGENTS_MD_FILENAME, LOCAL_AGENTS_MD.read_bytes()))

    if LOCAL_SKILLS_DIR.exists():
        for local_file in LOCAL_SKILLS_DIR.rglob("*"):
            if local_file.is_file():
                rel = local_file.relative_to(LOCAL_SKILLS_DIR).as_posix()
                uploads.append((f"{SANDBOX_SKILLS_ROOT}/{rel}", local_file.read_bytes()))

    if uploads:
        backend.upload_files(uploads)


def get_global_sandbox_sync() -> SandboxBackendProxy:
    """Return the shared global sandbox, reconnecting or recreating if needed."""
    global _proxy
    with _lock:
        if _proxy is not None:
            try:
                _ping_backend(_proxy)
                return _proxy
            except Exception:
                logger.warning("Cached global sandbox is unhealthy; recreating", exc_info=True)

        state = _read_state()
        sandbox_id = state.get("sandbox_id")
        if sandbox_id:
            try:
                backend = _connect_sandbox(sandbox_id)
                _proxy = SandboxBackendProxy(backend)
                return _proxy
            except Exception:
                logger.warning("Failed to reconnect global sandbox %s", sandbox_id, exc_info=True)

        backend = _create_sandbox()
        _proxy = SandboxBackendProxy(backend)
        return _proxy


async def ensure_global_sandbox() -> SandboxBackendProxy:
    """Async wrapper for FastAPI startup/request paths."""
    return await asyncio.to_thread(get_global_sandbox_sync)


async def ping_global_sandbox() -> bool:
    try:
        backend = await ensure_global_sandbox()
        await asyncio.to_thread(_ping_backend, backend)
        return True
    except Exception:
        return False


async def recreate_global_sandbox() -> SandboxBackendProxy:
    global _proxy
    def _recreate() -> SandboxBackendProxy:
        global _proxy
        with _lock:
            backend = _create_sandbox()
            if _proxy is None:
                _proxy = SandboxBackendProxy(backend)
            else:
                _proxy.replace_backend(backend)
            return _proxy

    return await asyncio.to_thread(_recreate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ensure", action="store_true", help="Create or reconnect the global sandbox.")
    args = parser.parse_args()
    if args.ensure:
        backend = get_global_sandbox_sync()
        print(f"Global sandbox ready: {backend.id}")


if __name__ == "__main__":
    main()
