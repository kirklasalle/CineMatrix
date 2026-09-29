#!/usr/bin/env python3
"""
CineMatrix Studio — Standalone Desktop Application Launcher
Oscar-Tier Generative Pre-Visualization & Animatics Platform
Author: Kirk LaSalle & Antigravity AI
"""

import sys
import os
import time
import subprocess
import threading
import urllib.request
import urllib.error
import json
import shutil
import signal

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")
API_URL = "http://127.0.0.1:8000"
APP_URL = "http://localhost:5173"

processes = []

def log(msg: str):
    print(f"[CineMatrix Desktop] {msg}")

def is_server_online(url: str, timeout: float = 1.0) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CineMatrixDesktop/3.2"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 304)
    except Exception:
        return False

def ensure_backend_running():
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

    # Wait up to 10 seconds for backend to become healthy
    for _ in range(20):
        if is_server_online(f"{API_URL}/health", timeout=0.5):
            log("Backend API initialized successfully.")
            return p
        time.sleep(0.5)

    log("Warning: Backend took longer than expected to initialize.")
    return p

def ensure_frontend_running():
    if is_server_online(APP_URL, timeout=0.8):
        log("Frontend dev server is already running.")
        return None

    # Check if npm is installed
    npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_cmd:
        log("Error: npm not found in system PATH.")
        return None

    log("Starting Vite frontend server on http://localhost:5173...")
    p = subprocess.Popen([npm_cmd, "run", "dev"], cwd=FRONTEND_DIR)
    processes.append(p)

    # Wait up to 12 seconds for frontend to become available
    for _ in range(24):
        if is_server_online(APP_URL, timeout=0.5):
            log("Frontend client initialized successfully.")
            return p
        time.sleep(0.5)

    log("Warning: Frontend server took longer than expected to respond.")
    return p

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

    # Option 2: Microsoft Edge / Chrome in App Mode (Dedicated window without browser tabs)
    browser_exe = find_browser_app_executable()
    if browser_exe:
        log(f"Launching standalone app window via {os.path.basename(browser_exe)}...")
        app_flags = [
            browser_exe,
            f"--app={target_url}",
            "--window-size=1440,900",
            "--window-position=100,50",
            "--name=CineMatrixStudio",
        ]
        proc = subprocess.Popen(app_flags)
        proc.wait()
        return

    # Option 3: Fallback to default browser
    log("Opening in default browser...")
    import webbrowser
    webbrowser.open(target_url)

def cleanup():
    log("Shutting down background services...")
    for p in processes:
        if p and p.poll() is None:
            try:
                p.terminate()
                p.wait(timeout=2)
            except Exception:
                p.kill()

def main():
    print("=" * 70)
    print("      CINEMATRIX STUDIO v3.2 — STANDALONE DESKTOP LAUNCHER")
    print("   Oscar-Tier Screenplay Pre-Visualization & Animatics Platform")
    print("=" * 70)
    print()

    ensure_backend_running()
    ensure_frontend_running()

    print()
    log("CineMatrix Studio is ready.")
    log(f"Backend API:  {API_URL}")
    log(f"Frontend App: {APP_URL}")
    print()

    try:
        launch_desktop_window(APP_URL)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main()
