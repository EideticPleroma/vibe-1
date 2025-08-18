@echo off
REM Verify and switch to root workspace directory
set ROOT=%~dp0
cd /d %ROOT%
if not %errorlevel%==0 (
    echo Error: Could not switch to the script's directory: %ROOT%. Please check the path.
    pause
    exit /b
)
echo In root workspace: %CD%

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/ and ensure it's added to PATH.
    pause
    exit /b
)

REM Check if Node.js is installed
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH.
    echo Please install Node.js 16 or higher from https://nodejs.org/ and ensure it's added to PATH.
    pause
    exit /b
)

REM Check if npm is installed (comes with Node.js)
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed or not in PATH. This usually comes with Node.js.
    echo Please reinstall Node.js from https://nodejs.org/.
    pause
    exit /b
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if not %errorlevel%==0 (
    echo Error: Failed to activate venv. Ensure venv exists and is set up properly.
    echo If venv doesn't exist, create it manually as per README instructions.
    echo Also ensure Python is correctly installed.
    pause
    exit /b
)

REM Start backend in a new window
start "Backend Server" cmd /k "cd backend && python app.py"

REM Start frontend in a new window (give backend a moment to start)
timeout /t 2 /nobreak >nul
start "Frontend App" cmd /k "cd frontend && npm start"

echo Servers started! Backend on http://localhost:5000, Frontend on http://localhost:3000.

echo WARNING: If this is your first run, the frontend may need to install dependencies. Watch the "Frontend App" window for progress.
echo It may take a few minutes to compile. Look for "Compiled successfully!" message.

echo Next steps:
echo 1. Check the "Backend Server" window for "Running on http://127.0.0.1:5000"
echo 2. Check the "Frontend App" window for "Local: http://localhost:3000"
echo 3. Once both are ready, open your browser to http://localhost:3000
echo 4. If errors occur, check the terminal windows and ensure Python and Node.js are installed.

pause

