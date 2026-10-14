@echo off
setlocal
TITLE CineMatrix Studio - Desktop Launcher
COLOR 0B
cd /d "%~dp0"

echo ===============================================================================
echo                     CINEMATRIX STUDIO - DESKTOP LAUNCHER
echo          Oscar-Tier Pre-Visualization, Animatics ^& Graphic Novel Suite
echo                 Governed by Kirk LaSalle Permanent Directives
echo ===============================================================================
echo.

:: 1. Locate a supported Python, 3.12 through 3.14. The newest Python release can lack
::    wheels for some dependencies (onnxruntime via chromadb), so known-good versions
::    are preferred through the Windows "py" launcher before falling back to PATH.
set "CM_PY="
for %%V in (3.14 3.13 3.12) do (
    if not defined CM_PY (
        py -%%V -c "import sys" >nul 2>&1 && set "CM_PY=py -%%V"
    )
)
if not defined CM_PY (
    python -c "import sys; sys.exit(0 if (3, 12) <= sys.version_info[:2] <= (3, 14) else 1)" >nul 2>&1 && set "CM_PY=python"
)
if not defined CM_PY (
    echo [ERROR] CineMatrix Studio needs Python 3.12, 3.13, or 3.14.
    echo Install Python 3.14 from https://www.python.org/downloads/ and re-run.
    echo Python found on PATH, if any:
    python --version 2>nul
    pause
    exit /b 1
)

:: 2. First run: create a private environment so system Python stays untouched.
::    An environment built with an unsupported Python is discarded and rebuilt.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if (3, 12) <= sys.version_info[:2] <= (3, 14) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo Rebuilding .venv with a supported Python version...
        rmdir /s /q ".venv"
    )
)
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating private Python environment in .venv ...
    %CM_PY% -m venv .venv
    if errorlevel 1 goto :setup_failed
)
".venv\Scripts\python.exe" --version

:: 3. Install dependencies on first run, or again whenever requirements.txt changes
fc /b "backend\requirements.txt" ".venv\requirements.installed.txt" >nul 2>&1
if errorlevel 1 (
    echo [2/3] Installing CineMatrix dependencies - first run only, this can take a few minutes...
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r "backend\requirements.txt"
    if errorlevel 1 goto :setup_failed
    copy /y "backend\requirements.txt" ".venv\requirements.installed.txt" >nul
)

:: 4. Launch via Python Desktop Orchestrator
echo [3/3] Launching CineMatrix Desktop Suite...
".venv\Scripts\python.exe" desktop_launcher.py %*
set "CM_EXIT=%ERRORLEVEL%"

echo.
echo CineMatrix Studio session ended.
pause
exit /b %CM_EXIT%

:setup_failed
echo.
echo [ERROR] Dependency setup failed. Check your internet connection and the messages above,
echo then re-run start_cinematrix.bat. Delete the .venv folder to force a clean reinstall.
pause
exit /b 1
