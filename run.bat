@echo off
title Language Translation Application
echo ========================================================
echo Starting Language Translation Application Local Server...
echo ========================================================
cd /d "%~dp0"

IF NOT EXIST ".venv\Scripts\streamlit.exe" (
    echo Virtual environment not found or incomplete.
    echo Creating virtual environment and installing dependencies...
    py -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

echo.
echo Launching Streamlit on http://localhost:8501 ...
echo Press Ctrl+C in this terminal window to stop the server.
echo.
.\.venv\Scripts\streamlit.exe run app.py
pause
