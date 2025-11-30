Param(
    # Use -SkipFrontendBuild if you only changed backend code
    [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"

# Go to repo root (folder where this script lives)
Set-Location $PSScriptRoot

Write-Host "== [1/4] Python virtualenv =="

if (-not (Test-Path ".\venv")) {
    Write-Host "Creating virtualenv 'venv'..."
    python -m venv venv
}

Write-Host "Activating virtualenv..."
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing backend Python dependencies..."
pip install -r ".\app_backend\requirements.txt"

# Make sure Python can see src/
$env:PYTHONPATH = "$PSScriptRoot;$PSScriptRoot\src"

# ----------------- Frontend build -----------------
if (-not $SkipFrontendBuild) {
    Write-Host "== [2/4] Frontend build =="

    Push-Location ".\app_frontend"

    if (-not (Test-Path ".\node_modules")) {
        Write-Host "Running npm install (first time only)..."
        npm install
    } else {
        Write-Host "node_modules exists - skipping npm install"
    }

    Write-Host "Running npm run build..."
    npm run build

    Pop-Location
} else {
    Write-Host "Skipping frontend build (use -SkipFrontendBuild to enable this)."
}

# ----------------- Start backend -----------------
Write-Host "== [3/4] Starting backend on http://127.0.0.1:8000 =="
Start-Process "http://127.0.0.1:8000"

Write-Host "== [4/4] Launching uvicorn (Ctrl+C to stop) =="
python -m uvicorn app_backend.main:app --reload
