@echo off
TITLE Storyboard AI - Launch Orchestrator
SETLOCAL EnableDelayedExpansion

:: --- Configuration ---
SET BACKEND_DIR=%~dp0backend
SET FRONTEND_DIR=%~dp0frontend
SET BROWSER_URL=http://localhost:5173

echo.
echo ============================================================
echo      Storyboard AI - Professional Startup Sequence
echo ============================================================
echo.

:: 1. Run Health Checks
echo [1/3] Running System Health Checks...
cd /d "%BACKEND_DIR%"
python check_environment.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] WARNING: Health checks failed or returned warnings.
    echo [?] Press any key to attempt launch anyway, or Ctrl+C to abort.
    pause > nul
)

:: 2. Launch Backend
echo.
echo [2/3] Launching FastAPI Backend...
start "Storyboard Backend" cmd /k "cd /d %BACKEND_DIR% && python -m uvicorn main:app --reload --reload-exclude "*database*" --host 127.0.0.1 --port 8000"

:: 3. Launch Frontend
echo.
echo [3/3] Launching Vite Frontend...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [!] node_modules missing. Installing dependencies...
    start /wait "Frontend Install" cmd /c "cd /d %FRONTEND_DIR% && npm install"
)
start "Storyboard Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

:: 4. Finalizing
echo.
echo ============================================================
echo   Application is launching in separate windows.
echo   - Backend: http://localhost:8000
echo   - Frontend: %BROWSER_URL%
echo ============================================================
echo.

:: Wait a moment for Vite to warm up
timeout /t 5 /nobreak > nul

echo [!] Opening default browser...
start %BROWSER_URL%

echo.
echo [✓] Done! Keep this window open if you want to monitor the launcher.
echo     Press any key to exit this launcher window (services will stay running).
pause > nul
