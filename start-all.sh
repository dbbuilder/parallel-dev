#!/bin/bash
# Start both ParallelDev Backend and Frontend

echo "========================================="
echo "Starting ParallelDev Full Stack"
echo "========================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo "Starting backend..."
./start-backend.sh > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend..."
./start-frontend.sh > frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "Both servers started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  Backend: tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
