@echo off
TITLE Storyboard AI — Test Suite Runner
COLOR 0A

echo ===============================================================================
echo                 STORYBOARD AI — COMPLETE TEST SUITE RUNNER
echo ===============================================================================
echo.

echo [1/2] Running Backend Pytest Suite...
python -m pytest backend/tests/ -v
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend tests failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Frontend TypeScript & Vite Production Build...
cd /d %~dp0frontend
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend build failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ===============================================================================
echo  ALL TESTS PASSED WITH 100%% SUCCESS RATE!
echo ===============================================================================
pause
