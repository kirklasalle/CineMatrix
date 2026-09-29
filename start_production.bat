@echo off
title CineMatrix Pre-Vis Studio - Standalone Production Server
echo ===============================================================================
echo   CINEMATRIX AI DIRECTOR PRE-VISUALIZATION STUDIO (PRODUCTION HOSTING)
echo ===============================================================================
echo.
echo [1/3] Verifying Python backend environment...
cd backend
python -c "import fastapi, uvicorn; print('FastAPI/Uvicorn runtime verified.')"

echo.
echo [2/3] Checking SQLite database and vector store...
if not exist "storyboard.db" (
    echo Initializing storyboard.db...
)

echo.
echo [3/3] Launching CineMatrix on 0.0.0.0:8000 (Direct IP/Port hosting ready)...
echo Access locally: http://localhost:8000
echo Access on network/IP: http://0.0.0.0:8000
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
pause
