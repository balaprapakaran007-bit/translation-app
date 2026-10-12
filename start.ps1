# Language Translation Application - Local Server Launcher
Set-Location $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Language Translation Application Local Server..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if (-not (Test-Path ".\.venv\Scripts\streamlit.exe")) {
    Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
    py -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt
}

Write-Host "Opening Streamlit app at http://localhost:8501..." -ForegroundColor Green
.\.venv\Scripts\streamlit.exe run app.py
