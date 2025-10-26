#!/bin/bash
# Start ParallelDev Backend API on port 8000

echo "Starting ParallelDev Backend API on port 8000..."

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating it now..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Install dependencies if needed
if ! pip show Flask > /dev/null 2>&1; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
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
