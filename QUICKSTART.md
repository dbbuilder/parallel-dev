# ParallelDev - Quick Start Guide

Get ParallelDev up and running in minutes!

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **Git** (for cloning)

## Quick Start (3 Steps)

### 1. Clone and Setup

```bash
git clone https://github.com/dbbuilder/parallel-dev.git
cd parallel-dev

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Launch the Application

**Option A: Launch Both Services (Recommended)**

Linux/Mac:
```bash
./start-all.sh
```

Windows:
```bash
# Open two terminal windows:

# Terminal 1 - Backend:
start-backend.bat

# Terminal 2 - Frontend:
start-frontend.bat
```

**Option B: Launch Individually**

Backend only:
```bash
./start-backend.sh       # Linux/Mac
start-backend.bat        # Windows
```

Frontend only:
```bash
./start-frontend.sh      # Linux/Mac
start-frontend.bat       # Windows
```

### 3. Access the Application

- **Frontend UI**: http://localhost:8001
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health

## Default Ports

- Backend API: **8000**
- Frontend UI: **8001**

The frontend automatically proxies `/api` requests to the backend.

## First Time Setup

The backend will automatically:
1. Create the `data/` directory
2. Initialize the SQLite database
3. Set up the schema with tables and triggers

## Testing the Application

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T..."
}
```

### 2. Scan a Directory for Projects

```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"directory": "/path/to/your/projects"}'
```

### 3. View Dashboard

Open your browser to http://localhost:8001 and you should see:
- Project summary statistics
- List of scanned projects
- Completion metrics

## Running Tests

### Backend Tests

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov=backend
```

Expected: 279 tests passing

### Frontend Tests

```bash
cd frontend
npm run test
```

Expected: 6 API service test suites passing

## Troubleshooting

### Backend won't start

**Problem**: Port 8000 already in use

**Solution**: Change the port
```bash
export PORT=8002  # Linux/Mac
set PORT=8002     # Windows
python src/api/app.py
```

### Frontend won't start

**Problem**: Port 8001 already in use

**Solution**: Edit `frontend/vite.config.js` and change the port:
```javascript
server: {
  port: 8002,  // Change this
  ...
}
```

### Database errors

**Problem**: Database file corrupt or missing

**Solution**: Delete and reinitialize
```bash
rm data/projects.db
python -c "from backend.database.db_manager import init_database; init_database('data/projects.db')"
```

### Frontend can't connect to backend

**Problem**: CORS or proxy issues

**Solution**:
1. Ensure backend is running on port 8000
2. Check `frontend/vite.config.js` proxy settings
3. Clear browser cache
4. Try accessing backend directly at http://localhost:8000/api/health

## Project Structure

```
parallel-dev/
├── backend/              # Backend Python code
│   ├── database/         # Database management
│   └── ...
├── src/                  # Source code
│   ├── api/              # Flask API
│   ├── models/           # Data models
│   ├── parsers/          # Markdown parsers
│   └── services/         # Business logic
├── frontend/             # Vue.js frontend
│   ├── src/
│   │   ├── components/   # Vue components
│   │   └── services/     # API client
│   └── ...
├── tests/                # Backend tests
├── data/                 # SQLite database (auto-created)
└── start-*.sh/.bat       # Launch scripts
```

## Next Steps

1. **Scan Your Projects**: Use the API or UI to scan directories
2. **View Metrics**: Check project completion statistics
3. **Explore API**: Visit http://localhost:8000/api/projects
4. **Customize**: Edit config files to match your setup

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/projects` - List all projects
- `GET /api/projects/:id` - Get project details
- `GET /api/projects/:id/metrics` - Get project metrics
- `GET /api/dashboard` - Dashboard summary
- `POST /api/scan` - Trigger directory scan

## Configuration

### Backend
Edit `src/api/app.py` or set environment variables:
- `PORT` - Server port (default: 8000)

### Frontend
Edit `frontend/vite.config.js`:
- `server.port` - Frontend port (default: 8001)
- `server.proxy['/api'].target` - Backend URL

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [TDD-DEVELOPMENT-PLAN.md](TDD-DEVELOPMENT-PLAN.md)
- Open an issue on GitHub

## Quick Commands Reference

```bash
# Backend
./start-backend.sh              # Start backend (Linux/Mac)
start-backend.bat               # Start backend (Windows)
python src/api/app.py           # Direct launch
pytest tests/                   # Run tests

# Frontend
./start-frontend.sh             # Start frontend (Linux/Mac)
start-frontend.bat              # Start frontend (Windows)
cd frontend && npm run dev      # Direct launch
cd frontend && npm run test     # Run tests

# Both
./start-all.sh                  # Start both (Linux/Mac only)
```

That's it! You're ready to use ParallelDev! 🎉
