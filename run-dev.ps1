# run-dev.ps1 - Start backend_v2 (Postgres) + frontend + open browser

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$backendPath   = Join-Path $root "backend_v2"
$venvActivate  = Join-Path $root "app_backend\venv\Scripts\Activate.ps1"
$frontendPath  = Join-Path $root "app_frontend"

Write-Host "=== Starting Full SCV Dev Environment ===" -ForegroundColor Cyan

# -------------------------------
# Start backend_v2 (Postgres API)
# -------------------------------
Write-Host "`nStarting backend_v2..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    @"
cd `"$backendPath`"
& `"$venvActivate`"
python -m uvicorn app.main:app --reload --port 8000
"@
)

# -------------------------------
# Start frontend
# -------------------------------
Write-Host "`nStarting frontend..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    @"
cd `"$frontendPath`"
npm run dev
"@
)

# -------------------------------
# Open browser automatically
# -------------------------------
Start-Sleep -Seconds 2  # small delay so Vite starts
Write-Host "`nOpening browser to http://localhost:5173 ..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "`n=== Dev Environment Launched ===" -ForegroundColor Green



