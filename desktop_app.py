"""Desktop launcher for the 15-Puzzle AI Streamlit dashboard."""

from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


APP_TITLE = "15-Puzzle AI Algorithm Study"
DEFAULT_HOST = "127.0.0.1"
APP_FILE = Path(__file__).with_name("app.py")


def find_free_port(start: int = 8520, attempts: int = 40) -> int:
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
        str(APP_FILE),
        "--server.address",
        DEFAULT_HOST,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]


def wait_for_server(url: str, timeout: float = 30.0) -> None:
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


def open_app_window(url: str) -> None:
    """Open the app in a native window when pywebview is available."""
    try:
        import webview  # type: ignore
    except Exception:  # noqa: BLE001 - browser fallback keeps launcher usable.
        webbrowser.open(url)
        print(f"Opened in your browser: {url}")
        print("Close this terminal window to stop the local app server.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return

    webview.create_window(APP_TITLE, url, width=1280, height=860, min_size=(1024, 720))
    webview.start()


def main() -> int:
    """Start Streamlit and open the lecturer-friendly app window."""
    port = find_free_port()
    url = f"http://{DEFAULT_HOST}:{port}"
    process = subprocess.Popen(
        build_streamlit_command(port),
        cwd=Path(__file__).resolve().parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_for_server(url)
        open_app_window(url)
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
