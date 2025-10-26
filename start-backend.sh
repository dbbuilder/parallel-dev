#!/bin/bash
# Start ParallelDev Backend API on port 8000

echo "Starting ParallelDev Backend API on port 8000..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run 'python -m venv venv' first."
    exit 1
fi

# Check if database exists, initialize if not
if [ ! -f "data/projects.db" ]; then
    echo "Database not found. Initializing..."
    mkdir -p data
    python -c "from backend.database.db_manager import init_database; init_database('data/projects.db')"
fi

# Set port and start backend
export PORT=8000
echo "Backend API will be available at http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python src/api/app.py
