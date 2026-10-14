#!/usr/bin/env python3
"""
CineMatrix Studio — Standalone Desktop Application Launcher
Oscar-Tier Generative Pre-Visualization & Animatics Platform
Author: Kirk LaSalle & Antigravity AI

The launcher detects how it is being run:

* development — from a source checkout containing ``frontend/package.json``;
  starts the Vite dev server with ``npm run dev``.
* bundled     — from a ``dist_release/`` package containing ``frontend_dist/``;
  serves the prebuilt interface itself, so end users need Python only
  (no Node.js / npm).

Flags:
  --no-window   start the services without opening an app window
  --smoke-test  start the services, verify the API and UI end to end, then exit
"""

import argparse
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")
BUNDLED_FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend_dist")

API_URL = "http://127.0.0.1:8000"
DEV_APP_URL = "http://localhost:5173"
BUNDLED_HOST = "127.0.0.1"
BUNDLED_PORT = 5173
BUNDLED_APP_URL = f"http://{BUNDLED_HOST}:{BUNDLED_PORT}"

BACKEND_STARTUP_TIMEOUT = 45.0
FRONTEND_STARTUP_TIMEOUT = 15.0
BROWSER_PROFILE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
    "CineMatrixStudio",
    "browser-profile",
)

processes = []
servers = []


def read_app_version() -> str:
    """Single-source the version from backend/main.py's APP_VERSION (same contract as build_desktop.py)."""
    try:
        with open(os.path.join(BACKEND_DIR, "main.py"), "r", encoding="utf-8") as handle:
            match = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', handle.read(), re.MULTILINE)
    except OSError:
        match = None
    return match.group(1) if match else "unknown"


APP_VERSION = read_app_version()
USER_AGENT = f"CineMatrixDesktop/{APP_VERSION}"


def log(msg: str):
    print(f"[CineMatrix Desktop] {msg}", flush=True)


def http_get(url: str, headers: dict | None = None, timeout: float = 5.0):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.headers, resp.read()


def is_server_online(url: str, timeout: float = 1.0) -> bool:
    try:
        status, _, _ = http_get(url, timeout=timeout)
        return status in (200, 304)
    except Exception:
        return False


def ensure_backend_running(timeout: float = BACKEND_STARTUP_TIMEOUT):
    if is_server_online(f"{API_URL}/health", timeout=0.8):
        log("Backend API is already running.")
        return None

    log("Starting FastAPI backend server on 127.0.0.1:8000...")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload-exclude",
        "*database*",
    ]
    p = subprocess.Popen(cmd, cwd=BACKEND_DIR)
    processes.append(p)

    # Wait for the backend to become healthy; first start imports heavy libraries.
    deadline = time.time() + timeout
    while time.time() < deadline:
        if p.poll() is not None:
            log(
                f"Error: Backend exited during startup (code {p.returncode}). "
                "On a fresh install, run start_cinematrix.bat so dependencies are installed."
            )
            return p
        if is_server_online(f"{API_URL}/health", timeout=0.5):
            log("Backend API initialized successfully.")
            return p
        time.sleep(0.5)

    log("Warning: Backend took longer than expected to initialize.")
    return p


def detect_frontend_mode(root_dir: str = ROOT_DIR) -> str | None:
    """Return 'development', 'bundled', or None when no frontend is present."""
    if os.path.isfile(os.path.join(root_dir, "frontend", "package.json")):
        return "development"
    if os.path.isfile(os.path.join(root_dir, "frontend_dist", "index.html")):
        return "bundled"
    return None


class BundledFrontendHandler(SimpleHTTPRequestHandler):
    """Serves the prebuilt Vite bundle with pinned MIME types and an SPA fallback.

    Windows can map ``.js`` to ``text/plain`` through the registry, which makes
    browsers refuse to execute ES module scripts, so the types are fixed here.
    """

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".wasm": "application/wasm",
        ".webmanifest": "application/manifest+json",
    }

    def send_head(self):
        request_path = urllib.parse.urlsplit(self.path).path
        has_extension = bool(os.path.splitext(request_path)[1])
        if not has_extension and not os.path.exists(self.translate_path(self.path)):
            # Client-side route: hand it to the SPA. Missing assets still 404.
            self.path = "/index.html"
        return super().send_head()

    def end_headers(self):
        # index.html must be revalidated so a new release's hashed assets are picked up.
        if urllib.parse.urlsplit(self.path).path in ("/", "/index.html"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, format, *args):  # noqa: A002 - signature defined by BaseHTTPRequestHandler
        pass


class _FrontendServer(ThreadingHTTPServer):
    # On Windows SO_REUSEADDR lets a second process bind an occupied port; refuse instead.
    allow_reuse_address = os.name != "nt"
    daemon_threads = True


def serve_bundled_frontend(dist_dir: str, host: str = BUNDLED_HOST, port: int = BUNDLED_PORT):
    handler = functools.partial(BundledFrontendHandler, directory=dist_dir)
    server = _FrontendServer((host, port), handler)
    threading.Thread(target=server.serve_forever, name="cinematrix-frontend", daemon=True).start()
    servers.append(server)
    return server


def ensure_frontend_running() -> str | None:
    """Start the interface for the detected mode and return its URL, or None on failure."""
    mode = detect_frontend_mode()

    if mode == "bundled":
        if is_server_online(BUNDLED_APP_URL, timeout=0.8):
            log(f"Interface is already being served at {BUNDLED_APP_URL}.")
            return BUNDLED_APP_URL
        log(f"Serving bundled CineMatrix interface on {BUNDLED_APP_URL}...")
        try:
            serve_bundled_frontend(BUNDLED_FRONTEND_DIST)
        except OSError as exc:
            log(f"Error: could not bind {BUNDLED_APP_URL} ({exc}). Close the program using port {BUNDLED_PORT} and retry.")
            return None
        log("Frontend client initialized successfully.")
        return BUNDLED_APP_URL

    if mode == "development":
        if is_server_online(DEV_APP_URL, timeout=0.8):
            log("Frontend dev server is already running.")
            return DEV_APP_URL

        # Check if npm is installed
        npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
        if not npm_cmd:
            log("Error: npm not found in system PATH.")
            return None

        log(f"Starting Vite frontend server on {DEV_APP_URL}...")
        p = subprocess.Popen([npm_cmd, "run", "dev"], cwd=FRONTEND_DIR)
        processes.append(p)

        deadline = time.time() + FRONTEND_STARTUP_TIMEOUT
        while time.time() < deadline:
            if is_server_online(DEV_APP_URL, timeout=0.5):
                log("Frontend client initialized successfully.")
                return DEV_APP_URL
            time.sleep(0.5)

        log("Warning: Frontend server took longer than expected to respond.")
        return DEV_APP_URL

    log("Error: no interface found. Expected frontend/ (source checkout) or frontend_dist/ (release bundle).")
    return None


def find_browser_app_executable():
    """Finds Edge or Chrome executable for frameless desktop app mode."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def wait_for_interrupt(reason: str = ""):
    if reason:
        log(reason)
    log("CineMatrix Studio is running. Press Ctrl+C in this window to stop it.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def launch_desktop_window(target_url: str):
    """Launches app in standalone desktop app window or default browser."""
    # Option 1: pywebview if available
    try:
        import webview
        log("Launching native window via pywebview...")
        webview.create_window(
            title="CineMatrix Studio — Oscar Prestige Pre-Visualization",
            url=target_url,
            width=1440,
            height=900,
            min_size=(1024, 700),
            background_color="#020617",
        )
        webview.start()
        return
    except ImportError:
        pass

    # Option 2: Microsoft Edge / Chrome in App Mode (Dedicated window without browser tabs).
    # A dedicated profile forces a separate browser process, so closing the window
    # ends the session instead of the launch being handed to an already-running browser.
    browser_exe = find_browser_app_executable()
    if browser_exe:
        log(f"Launching standalone app window via {os.path.basename(browser_exe)}...")
        app_flags = [
            browser_exe,
            f"--app={target_url}",
            "--window-size=1440,900",
            "--window-position=100,50",
            "--name=CineMatrixStudio",
            f"--user-data-dir={BROWSER_PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        started = time.time()
        proc = subprocess.Popen(app_flags)
        proc.wait()
        if time.time() - started < 5:
            wait_for_interrupt("The app window was handed to an existing browser session.")
        return

    # Option 3: Fallback to default browser
    log("Opening in default browser...")
    import webbrowser
    webbrowser.open(target_url)
    wait_for_interrupt()


def cleanup():
    log("Shutting down background services...")
    for server in servers:
        try:
            server.shutdown()
            server.server_close()
        except Exception:
            pass
    servers.clear()
    for p in processes:
        if p and p.poll() is None:
            try:
                p.terminate()
                p.wait(timeout=5)
            except Exception:
                p.kill()
    processes.clear()


def run_smoke_test() -> int:
    """Start both services from this directory, verify them end to end, then shut down."""
    mode = detect_frontend_mode()
    expected_app_url = BUNDLED_APP_URL if mode == "bundled" else DEV_APP_URL
    for url in (f"{API_URL}/health", expected_app_url):
        if is_server_online(url, timeout=0.8):
            log(f"Smoke test needs free ports, but {url} is already serving. Stop it and retry.")
            return 1

    failures = []
    log(f"Smoke test: frontend mode = {mode}")
    try:
        ensure_backend_running()
        app_url = ensure_frontend_running()

        try:
            status, _, body = http_get(f"{API_URL}/health")
            reported = json.loads(body).get("version")
            if status != 200:
                failures.append(f"backend /health returned HTTP {status}")
            if reported != APP_VERSION:
                failures.append(f"backend /health reports version {reported!r}, expected {APP_VERSION!r}")
        except Exception as exc:
            failures.append(f"backend /health unreachable: {exc}")

        if not app_url:
            failures.append("frontend did not start")
        else:
            try:
                status, _, body = http_get(app_url)
                html = body.decode("utf-8", "replace")
                if status != 200 or '<div id="root"' not in html:
                    failures.append(f"interface root returned HTTP {status} without the app mount point")

                assets = re.findall(r'(?:src|href)="(/assets/[^"]+\.(?:js|css))"', html)
                if mode == "bundled" and not assets:
                    failures.append("interface HTML references no /assets/*.js or *.css files")
                for asset in assets:
                    a_status, a_headers, _ = http_get(app_url + asset)
                    ctype = a_headers.get("Content-Type", "")
                    expected = "javascript" if asset.endswith(".js") else "css"
                    if a_status != 200 or expected not in ctype:
                        failures.append(f"{asset}: HTTP {a_status}, Content-Type {ctype!r}")

                route_status, _, route_body = http_get(f"{app_url}/some/client/route")
                if route_status != 200 or b'id="root"' not in route_body:
                    failures.append("client-side routes do not fall back to index.html")

                _, cors_headers, _ = http_get(f"{API_URL}/health", headers={"Origin": app_url})
                allowed = cors_headers.get("Access-Control-Allow-Origin")
                if allowed not in (app_url, "*"):
                    failures.append(f"backend CORS does not allow {app_url} (got {allowed!r})")
            except Exception as exc:
                failures.append(f"interface check failed: {exc}")
    finally:
        cleanup()

    print()
    if failures:
        log("SMOKE TEST FAILED:")
        for failure in failures:
            log(f"  - {failure}")
        return 1
    log(f"SMOKE TEST PASSED: API and interface are serving CineMatrix Studio v{APP_VERSION}.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="CineMatrix Studio desktop launcher")
    parser.add_argument("--no-window", action="store_true", help="start the services without opening an app window")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="start the services, verify the API and interface respond, then exit (non-zero on failure)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"      CINEMATRIX STUDIO v{APP_VERSION} — STANDALONE DESKTOP LAUNCHER")
    print("   Oscar-Tier Screenplay Pre-Visualization & Animatics Platform")
    print("=" * 70)
    print()

    if args.smoke_test:
        sys.exit(run_smoke_test())

    backend = ensure_backend_running()
    app_url = ensure_frontend_running()
    if app_url is None or (backend is not None and backend.poll() is not None):
        cleanup()
        sys.exit(1)

    print()
    log("CineMatrix Studio is ready.")
    log(f"Backend API:  {API_URL}")
    log(f"Frontend App: {app_url}")
    print()

    try:
        if args.no_window:
            wait_for_interrupt()
        else:
            launch_desktop_window(app_url)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main()
