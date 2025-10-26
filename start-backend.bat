@echo off
REM Start ParallelDev Backend API on port 8000

echo Starting ParallelDev Backend API on port 8000...

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found. Please run 'python -m venv venv' first.
    exit /b 1
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
