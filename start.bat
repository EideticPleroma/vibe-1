@echo off
REM Verify and switch to root workspace directory
cd /d D:\Projects\vibe-1
if not %errorlevel%==0 (
    echo Error: Could not switch to D:\Projects\vibe-1. Please run from there.
    pause
    exit /b
)
echo In root workspace: %CD%

REM Activate virtual environment
call venv\Scripts\activate.bat
if not %errorlevel%==0 (
    echo Error: Failed to activate venv. Ensure venv exists and is set up.
    pause
    exit /b
)

REM Start backend in a new window
start "Backend Server" cmd /k "cd backend && python app.py"

REM Start frontend in a new window (give backend a moment to start)
timeout /t 2 /nobreak >nul
start "Frontend App" cmd /k "cd frontend && npm start"

echo Servers started! Backend on http://localhost:5000, Frontend on http://localhost:3000.
pause
