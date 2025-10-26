@echo off
REM Start ParallelDev Frontend on port 8001

echo Starting ParallelDev Frontend on port 8001...

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo Node modules not found. Installing dependencies...
    call npm install
)

REM Start frontend dev server
echo Frontend will be available at http://localhost:8001
echo API requests will be proxied to http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

call npm run dev
