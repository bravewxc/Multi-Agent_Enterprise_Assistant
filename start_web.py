"""
DeepAgent Web application launcher.

Starts services in dependency order:
1. MCP Server
2. Global OpenSandbox prewarm
3. Agent Protocol server for async subagents
4. FastAPI backend
5. Vue frontend
"""

import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
AGENT_PROTOCOL_HOST = os.environ.get("ASYNC_AGENT_PROTOCOL_HOST", "127.0.0.1")
AGENT_PROTOCOL_PORT = int(os.environ.get("ASYNC_AGENT_PROTOCOL_PORT", "2024"))


def build_python_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["ASYNC_AGENT_PROTOCOL_URL"] = (
        f"http://{AGENT_PROTOCOL_HOST}:{AGENT_PROTOCOL_PORT}"
    )
    return env


def stream_process_output(proc, prefix):
    try:
        for line in proc.stdout:
            if line:
                try:
                    text = line.decode("utf-8", errors="replace").rstrip()
                except Exception:
                    text = line.decode("gbk", errors="replace").rstrip()
                print(f"[{prefix}] {text}")
    except Exception:
        pass


def start_process(name, args, cwd, env=None, shell=False):
    proc = subprocess.Popen(
        args,
        cwd=cwd,
        env=env,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    threading.Thread(
        target=stream_process_output,
        args=(proc, name),
        daemon=True,
    ).start()
    return proc


def run_mcp_server():
    print("[MCP] Starting MCP service...")
    print("[MCP] Using FastMCP at http://127.0.0.1:8000/mcp")
    return start_process(
        "MCP",
        [sys.executable, "-m", "mcp_server.server_main"],
        cwd=PROJECT_ROOT,
        env=build_python_env(),
    )


def langgraph_executable():
    scripts_dir = os.path.dirname(sys.executable)
    candidate = os.path.join(scripts_dir, "langgraph.exe")
    if os.path.exists(candidate):
        return candidate
    return "langgraph"


def run_agent_protocol_server():
    print("[AgentProtocol] Starting async subagent Agent Protocol service...")
    print(
        "[AgentProtocol] Using LangGraph at "
        f"http://{AGENT_PROTOCOL_HOST}:{AGENT_PROTOCOL_PORT}"
    )
    return start_process(
        "AgentProtocol",
        [
            langgraph_executable(),
            "dev",
            "--host",
            AGENT_PROTOCOL_HOST,
            "--port",
            str(AGENT_PROTOCOL_PORT),
            "--n-jobs-per-worker",
            "10",
            "--allow-blocking",
        ],
        cwd=PROJECT_ROOT,
        env=build_python_env(),
    )


def prewarm_global_sandbox():
    print("[Sandbox] Ensuring global OpenSandbox is ready...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "agent.backends.global_sandbox_manager",
            "--ensure",
        ],
        cwd=PROJECT_ROOT,
        env=build_python_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.rstrip())
        return False
    print("[Sandbox] Global OpenSandbox is ready!")
    return True


def check_mcp_ready(proc, max_wait=60):
    print("[System] Waiting for MCP server to be ready...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if proc.poll() is not None:
            print(f"[ERROR] MCP process exited early with code {proc.returncode}")
            return False

        try:
            with socket.create_connection(("127.0.0.1", 8000), timeout=3):
                print("[System] MCP server is ready!")
                return True
        except Exception:
            pass

        time.sleep(1)
        elapsed = int(time.time() - start_time)
        print(f"[System] Waiting for MCP... ({elapsed}s / {max_wait}s)")

    return False


def check_agent_protocol_ready(proc, max_wait=120):
    print("[System] Waiting for Agent Protocol server to be ready...")
    start_time = time.time()
    health_url = f"http://{AGENT_PROTOCOL_HOST}:{AGENT_PROTOCOL_PORT}/ok"

    while time.time() - start_time < max_wait:
        if proc.poll() is not None:
            print(
                "[ERROR] Agent Protocol process exited early "
                f"with code {proc.returncode}"
            )
            return False

        try:
            response = urllib.request.urlopen(health_url, timeout=5)
            if response.status == 200:
                print("[System] Agent Protocol server is ready!")
                return True
        except Exception:
            try:
                with socket.create_connection(
                    (AGENT_PROTOCOL_HOST, AGENT_PROTOCOL_PORT),
                    timeout=3,
                ):
                    print("[System] Agent Protocol server port is ready!")
                    return True
            except Exception:
                pass

        time.sleep(2)
        elapsed = int(time.time() - start_time)
        print(
            "[System] Waiting for Agent Protocol... "
            f"({elapsed}s / {max_wait}s)"
        )

    return False


def run_backend():
    print("[Backend] Starting FastAPI service...")
    print("[Backend] Using uvicorn at http://localhost:8090")
    return start_process(
        "Backend",
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api_view.web_main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8090",
        ],
        cwd=PROJECT_ROOT,
        env=build_python_env(),
    )


def check_backend_ready(proc, max_wait=180):
    print("[System] Waiting for backend to be ready...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if proc.poll() is not None:
            print(f"[ERROR] Backend process exited early with code {proc.returncode}")
            return False

        try:
            req = urllib.request.Request("http://localhost:8090/health")
            response = urllib.request.urlopen(req, timeout=5)
            if response.status == 200:
                data = response.read().decode("utf-8")
                if "healthy" in data:
                    print("[System] Backend is ready!")
                    return True
        except Exception:
            pass

        time.sleep(2)
        elapsed = int(time.time() - start_time)
        print(f"[System] Waiting for backend... ({elapsed}s / {max_wait}s)")

    return False


def run_frontend():
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("[Frontend] Installing dependencies...")
        result = subprocess.run(
            "npm install",
            cwd=FRONTEND_DIR,
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("[Frontend] Dependency installation failed:")
            print(result.stderr)
            return None
        print("[Frontend] Dependencies installed")

    print("[Frontend] Starting Vue dev server...")
    print("[Frontend] Using Vite at http://localhost:3000")
    return start_process(
        "Frontend",
        "npm run dev",
        cwd=FRONTEND_DIR,
        shell=True,
    )


def stop_process(name, proc):
    if not proc:
        return

    print(f"[System] Stopping {name}...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


def main():
    print("=" * 60)
    print("         DeepAgent Web Application Launcher")
    print("=" * 60)
    print()
    print("NOTE: Agent initialization takes 30-60 seconds")
    print("      Please wait patiently for the service to be ready")
    print()

    mcp_proc = None
    agent_protocol_proc = None
    backend_proc = None
    frontend_proc = None

    def cleanup():
        print("\n\n[System] Stopping services...")
        stop_process("Frontend", frontend_proc)
        stop_process("Backend", backend_proc)
        stop_process("AgentProtocol", agent_protocol_proc)
        stop_process("MCP", mcp_proc)
        print("[System] All services stopped")

    def signal_handler(sig, frame):
        cleanup()
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except Exception:
        pass

    try:
        mcp_proc = run_mcp_server()
        if not check_mcp_ready(mcp_proc, max_wait=60):
            print("[ERROR] MCP server failed to start within 60 seconds")
            print("[ERROR] Please check the logs above for errors")
            cleanup()
            return

        if not prewarm_global_sandbox():
            print("[ERROR] Global OpenSandbox prewarm failed")
            print("[ERROR] Please check the logs above for errors")
            cleanup()
            return

        agent_protocol_proc = run_agent_protocol_server()
        if not check_agent_protocol_ready(agent_protocol_proc, max_wait=120):
            print("[ERROR] Agent Protocol server failed to start within 120 seconds")
            print("[ERROR] Please check the logs above for errors")
            cleanup()
            return

        backend_proc = run_backend()
        if not check_backend_ready(backend_proc, max_wait=180):
            print("[ERROR] Backend failed to start within 180 seconds")
            print("[ERROR] Please check the logs above for errors")
            cleanup()
            return

        frontend_proc = run_frontend()

        print()
        print("=" * 60)
        print("  All services started successfully!")
        print("=" * 60)
        print()
        print("  Please access:")
        print("    - MCP Server: http://127.0.0.1:8000/mcp")
        print(
            "    - Agent Protocol: "
            f"http://{AGENT_PROTOCOL_HOST}:{AGENT_PROTOCOL_PORT}"
        )
        print("    - Frontend: http://localhost:3000")
        print("    - API docs: http://localhost:8090/docs")
        print()
        print("  Press Ctrl+C to stop all services")
        print("=" * 60)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        cleanup()


if __name__ == "__main__":
    main()
