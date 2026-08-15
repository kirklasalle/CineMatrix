# Storyboard AI — Master PowerShell Launcher
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "                    STORYBOARD AI — MASTER LAUNCHER (PS1)                     " -ForegroundColor White
Write-Host "             Governed by PRISM Sacred Covenant & The 10 Laws                  " -ForegroundColor DarkGray
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in new process
Write-Host "[1/3] Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\backend'; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

# 2. Start Frontend in new process
Write-Host "[2/3] Launching Vite React Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\frontend'; npm run dev"

# 3. Wait and open browser
Write-Host "[3/3] Waiting for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "`nStoryboard AI is active!" -ForegroundColor Green
Write-Host "Frontend:    http://localhost:5173"
Write-Host "Backend API: http://127.0.0.1:8000"
Write-Host "API Docs:    http://127.0.0.1:8000/docs`n"
