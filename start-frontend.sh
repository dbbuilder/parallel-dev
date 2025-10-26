#!/bin/bash
# Start ParallelDev Frontend on port 8001

echo "Starting ParallelDev Frontend on port 8001..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Node modules not found. Installing dependencies..."
    npm install
fi

# Start frontend dev server
echo "Frontend will be available at http://localhost:8001"
echo "API requests will be proxied to http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
