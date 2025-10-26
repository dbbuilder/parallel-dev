@echo off
REM Start ParallelDev Backend API on port 8000

echo Starting ParallelDev Backend API on port 8000...
echo.

REM Check for virtual environment
if not exist venv (
    echo Virtual environment not found. Creating it now...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        echo Make sure Python 3.9+ is installed and in your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment activation script not found.
    echo Trying to recreate virtual environment...
    rmdir /s /q venv
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install dependencies if needed
echo Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Flask not found. Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
    echo.
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
