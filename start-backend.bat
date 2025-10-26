@echo off
REM Start ParallelDev Backend API on port 8000

echo Starting ParallelDev Backend API on port 8000...

REM Check for virtual environment
if not exist venv (
    echo Virtual environment not found. Creating it now...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

REM Install dependencies if needed
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Check if database exists, initialize if not
if not exist data\projects.db (
    echo Database not found. Initializing...
    if not exist data mkdir data
    python -c "from backend.database.db_manager import init_database; init_database('data/projects.db')"
)

REM Set port and start backend
set PORT=8000
echo Backend API will be available at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python src\api\app.py
