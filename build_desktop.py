#!/usr/bin/env python3
"""
CineMatrix Studio — Production Desktop Build & Distribution Pipeline
Packages CineMatrix Studio into a standalone desktop application release.
Author: Kirk LaSalle & Antigravity AI
"""

import sys
import os
import subprocess
import shutil
import json
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
FRONTEND_DIST = os.path.join(FRONTEND_DIR, "dist")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
DIST_RELEASE_DIR = os.path.join(ROOT_DIR, "dist_release")

def log(step: str, msg: str):
    print(f"\n[BUILD {step}] {msg}")

def check_environment():
    log("1/4", "Checking build prerequisites...")
    # Check Python
    print(f"  • Python: {sys.version.split()[0]}")
    # Check Node / npm
    npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_cmd:
        print("  ✖ Error: npm not found in system PATH.")
        sys.exit(1)
    npm_ver = subprocess.check_output([npm_cmd, "--version"], text=True).strip()
    print(f"  • npm:    {npm_ver}")
    print("  ✔ Prerequisites satisfied.")

def build_frontend():
    log("2/4", "Compiling React 18 / Vite production bundle...")
    npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
    cmd = [npm_cmd, "run", "build"]
    p = subprocess.run(cmd, cwd=FRONTEND_DIR, text=True)
    if p.returncode != 0:
        print("  ✖ Error: Frontend build failed.")
        sys.exit(1)
    
    if not os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        print("  ✖ Error: frontend/dist/index.html not found after build.")
        sys.exit(1)
    
    dist_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(FRONTEND_DIST)
        for filename in filenames
    )
    print(f"  ✔ Frontend production bundle compiled ({dist_size / 1024:.1f} KB).")

def verify_backend_integrity():
    log("3/4", "Verifying backend dependencies and schemas...")
    cmd = [sys.executable, "-c", "import fastapi, uvicorn, pydantic, sqlite3; print('  ✔ Backend core libraries verified.')"]
    p = subprocess.run(cmd, cwd=BACKEND_DIR)
    if p.returncode != 0:
        print("  ✖ Warning: Backend verification returned non-zero code.")

def assemble_release_package():
    log("4/4", "Assembling desktop distribution bundle in dist_release/...")
    if os.path.exists(DIST_RELEASE_DIR):
        shutil.rmtree(DIST_RELEASE_DIR)
    os.makedirs(DIST_RELEASE_DIR, exist_ok=True)

    # 1. Copy Frontend Dist
    target_frontend = os.path.join(DIST_RELEASE_DIR, "frontend_dist")
    shutil.copytree(FRONTEND_DIST, target_frontend)

    # 2. Copy Backend Core (excluding pycache and large logs)
    target_backend = os.path.join(DIST_RELEASE_DIR, "backend")
    shutil.copytree(
        BACKEND_DIR, 
        target_backend, 
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.log", "static/videos/*", ".pytest_cache")
    )

    # 3. Copy Launchers and Documentation
    shutil.copy2(os.path.join(ROOT_DIR, "desktop_launcher.py"), DIST_RELEASE_DIR)
    shutil.copy2(os.path.join(ROOT_DIR, "start_cinematrix.bat"), DIST_RELEASE_DIR)
    if os.path.exists(os.path.join(ROOT_DIR, "SCREENWRITER_ONBOARDING_GUIDE.md")):
        shutil.copy2(os.path.join(ROOT_DIR, "SCREENWRITER_ONBOARDING_GUIDE.md"), DIST_RELEASE_DIR)

    # 4. Write manifest
    manifest = {
        "product_name": "CineMatrix Studio",
        "version": "3.2.0",
        "channel": "Early Adopter Creator Desktop Release",
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "founder": "Kirk LaSalle",
        "nle_standards": ["Avid Media Composer", "Adobe Premiere Pro", "DaVinci Resolve"],
        "governance": "Kirk LaSalle Permanent Active Directives"
    }
    with open(os.path.join(DIST_RELEASE_DIR, "version_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"  ✔ Release package assembled successfully at: {DIST_RELEASE_DIR}")

def main():
    print("=" * 70)
    print("       CINEMATRIX STUDIO — DESKTOP PRODUCTION BUNDLE BUILDER")
    print("=" * 70)
    start_time = time.time()
    check_environment()
    build_frontend()
    verify_backend_integrity()
    assemble_release_package()
    duration = time.time() - start_time
    print()
    print("=" * 70)
    print(f"BUILD COMPLETE: CineMatrix Studio v3.2 packaged in {duration:.1f}s!")
    print("=" * 70)

if __name__ == "__main__":
    main()
