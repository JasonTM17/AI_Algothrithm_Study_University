"""Desktop launcher for the 15-Puzzle AI Streamlit dashboard."""

from __future__ import annotations

import os
import argparse
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import webbrowser
from pathlib import Path


APP_TITLE = "15-Puzzle AI Algorithm Study"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8520
SERVER_START_TIMEOUT = 45.0


def app_root() -> Path:
    """Return the source root in development or the PyInstaller bundle root."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent


def app_file() -> Path:
    """Return the Streamlit app file inside the current runtime root."""
    return app_root() / "app.py"


def app_log_file() -> Path:
    """Return a stable local log file for desktop launcher diagnostics."""
    log_dir = Path(tempfile.gettempdir()) / "15-puzzle-ai"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "streamlit-server.log"


def find_free_port(start: int = DEFAULT_PORT, attempts: int = 40) -> int:
    """Return a free local port near the app-mode default range."""
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((DEFAULT_HOST, port)) != 0:
                return port
    raise RuntimeError("No free local port found for the desktop launcher.")


def build_streamlit_command(port: int) -> list[str]:
    """Build the Streamlit command without starting the process."""
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file()),
        "--server.address",
        DEFAULT_HOST,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.fileWatcherType",
        "none",
        "--server.runOnSave",
        "false",
        "--client.toolbarMode",
        "minimal",
    ]


def streamlit_options(port: int) -> dict[str, object]:
    """Return shared Streamlit server options for CLI and bundled modes."""
    return {
        "server.address": DEFAULT_HOST,
        "server.port": port,
        "server.headless": True,
        "browser.gatherUsageStats": False,
        "server.fileWatcherType": "none",
        "server.runOnSave": False,
        "client.toolbarMode": "minimal",
    }


def parse_serve_port(args: list[str]) -> int:
    """Read the bundled server port from launcher arguments."""
    if "--port" not in args:
        raise RuntimeError("Missing --port for bundled Streamlit server mode.")
    index = args.index("--port")
    try:
        return int(args[index + 1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError("Invalid --port value for bundled Streamlit server mode.") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse launcher arguments for app, browser, and bundled server modes."""
    parser = argparse.ArgumentParser(description="Launch the 15-Puzzle AI desktop app.")
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, default=None, help="Preferred local port.")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Open in the default browser instead of a native app window.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Start the local server without opening a window. Useful for smoke tests.",
    )
    return parser.parse_args(argv)


def wait_for_server(url: str, timeout: float = SERVER_START_TIMEOUT) -> None:
    """Wait until Streamlit responds or raise a timeout error."""
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001 - keep launcher resilient.
            last_error = exc
            time.sleep(0.35)
    raise RuntimeError(f"Streamlit did not start at {url}: {last_error}")


def hold_server_session(url: str) -> None:
    """Keep the server process alive without opening a UI window."""
    print(f"15-Puzzle AI is running at: {url}")
    print(f"Server log: {app_log_file()}")
    print("Press Ctrl+C to stop the local app server.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return


def hold_browser_session(url: str) -> None:
    """Open the browser fallback and keep the local server alive."""
    webbrowser.open(url)
    print(f"Opened in your browser: {url}")
    print("Close this terminal window to stop the local app server.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return


def open_app_window(url: str, *, force_browser: bool = False) -> None:
    """Open the app in a native window when pywebview is available."""
    if force_browser:
        hold_browser_session(url)
        return

    try:
        import webview  # type: ignore
    except Exception:  # noqa: BLE001 - browser fallback keeps launcher usable.
        hold_browser_session(url)
        return

    webview.create_window(APP_TITLE, url, width=1280, height=860, min_size=(1024, 720))
    webview.start()


def serve_streamlit(port: int) -> int:
    """Run Streamlit in the foreground for the packaged child process."""
    from streamlit import config
    from streamlit.web import bootstrap

    for key, value in streamlit_options(port).items():
        config.set_option(key, value, "desktop launcher")

    bootstrap.run(str(app_file()), False, [], {})
    return 0


def start_streamlit_bundle_process(port: int) -> subprocess.Popen:
    """Start the packaged executable as a local Streamlit server child."""
    log = app_log_file().open("w", encoding="utf-8")
    return subprocess.Popen(
        [sys.executable, "--serve", "--port", str(port)],
        cwd=Path(sys.executable).resolve().parent,
        stdout=log,
        stderr=subprocess.STDOUT,
    )


def start_streamlit_process(port: int) -> subprocess.Popen:
    """Start Streamlit as a subprocess during source-tree development."""
    log = app_log_file().open("w", encoding="utf-8")
    return subprocess.Popen(
        build_streamlit_command(port),
        cwd=Path(__file__).resolve().parent,
        stdout=log,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    """Start Streamlit and open the lecturer-friendly app window."""
    args = parse_args(sys.argv[1:])
    if args.serve:
        if args.port is None:
            return serve_streamlit(parse_serve_port(sys.argv[1:]))
        return serve_streamlit(args.port)

    port = args.port if args.port is not None else find_free_port()
    url = f"http://{DEFAULT_HOST}:{port}"
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    if getattr(sys, "frozen", False):
        process = start_streamlit_bundle_process(port)
    else:
        process = start_streamlit_process(port)

    try:
        wait_for_server(url)
        if args.no_wait:
            hold_server_session(url)
        else:
            open_app_window(url, force_browser=args.browser)
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
