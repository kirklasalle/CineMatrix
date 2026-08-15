@echo off
TITLE Storyboard AI — Oscar Prestige Master Launcher
COLOR 0B

echo ===============================================================================
echo                     STORYBOARD AI -- MASTER DESKTOP LAUNCHER
echo              Governed by PRISM Sacred Covenant and The 10 Laws
echo ===============================================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and re-run.
    pause
    exit /b 1
)

:: 2. Check Node
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH.
    echo Please install Node.js 18+ and re-run.
    pause
    exit /b 1
)

echo [1/3] Launching FastAPI Backend Server on http://127.0.0.1:8000...
start "Storyboard AI - Backend Server" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Launching Vite React Frontend on http://localhost:5173...
start "Storyboard AI - Frontend Client" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo [3/3] Waiting for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening Storyboard AI Studio in default browser...
start http://localhost:5173

echo.
echo ===============================================================================
echo  Storyboard AI is active!
echo  - Frontend: http://localhost:5173
echo  - Backend API: http://127.0.0.1:8000
echo  - API Docs: http://127.0.0.1:8000/docs
echo ===============================================================================
echo.
echo Keep the backend and frontend terminal windows open while using Storyboard AI.
pause
