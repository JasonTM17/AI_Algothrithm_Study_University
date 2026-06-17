@echo off
setlocal
cd /d "%~dp0"
python desktop_app.py
if errorlevel 1 (
    echo.
    echo Failed to start 15-Puzzle AI. Make sure Python is installed and run:
    echo pip install -r requirements.txt
    pause
)
