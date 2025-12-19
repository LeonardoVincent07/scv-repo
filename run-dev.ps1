# run-dev.ps1 — simple, reliable dev launcher

$ErrorActionPreference = "Stop"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

$BACKEND_VENV = "$ROOT\app_backend\venv\Scripts\Activate.ps1"
$BACKEND_DIR  = "$ROOT\backend_v2"
$FRONTEND_DIR = "$ROOT\app_frontend"

Write-Host "Starting backend..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    @"
cd '$BACKEND_DIR'
& '$BACKEND_VENV'
python -m uvicorn app.main:app --reload --port 8000
"@
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    @"
cd '$FRONTEND_DIR'
npm run dev
"@
)

Start-Sleep -Seconds 2

Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"






