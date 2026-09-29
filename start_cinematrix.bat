@echo off
TITLE CineMatrix Studio — Master Desktop Launcher
COLOR 0B

echo ===============================================================================
echo                   CINEMATRIX STUDIO v3.2 — DESKTOP LAUNCHER
echo          Oscar-Tier Pre-Visualization, Animatics & Graphic Novel Suite
echo                 Governed by Kirk LaSalle Permanent Directives
echo ===============================================================================
echo.

:: 1. Verify Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and re-run.
    pause
    exit /b 1
)

:: 2. Verify Node.js / npm
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH.
    echo Please install Node.js 18+ and re-run.
    pause
    exit /b 1
)

:: 3. Launch via Python Desktop Orchestrator
echo [1/2] Checking system dependencies and ports...
cd /d "%~dp0"

echo [2/2] Launching CineMatrix Desktop Suite...
python desktop_launcher.py

echo.
echo CineMatrix Studio session ended.
pause
