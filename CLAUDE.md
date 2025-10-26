# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ParallelDev is a comprehensive project management and visualization system designed to monitor and analyze multiple software development projects in parallel. The system scans project directories, parses documentation files (REQUIREMENTS.md, TODO.md, README.md), calculates progress metrics, and provides a visual dashboard for tracking development status across numerous concurrent projects.

**Current Status**: Early development phase (Phase 1 - Core Foundation at 0% completion). The system is being designed for future AI-powered development orchestration where multiple AI agents can work on different projects in parallel while maintaining coordinated progress tracking and context management.

## Architecture

### Dual Backend Structure

This project has **two parallel backend implementations** being developed:

1. **`backend/`** - Flask-based RESTful API server (Python)
   - Intended for production web-based dashboard
   - Provides API endpoints for frontend consumption
   - Implements file watching and real-time updates

2. **`src/`** - Core Python library/CLI implementation
   - Shared data models and business logic
   - Can be used independently or integrated with Flask backend
   - Contains the core scanning, parsing, and metrics calculation logic

**Key Point**: Both `backend/` and `src/` contain Python modules. The `src/` directory provides the core library that the `backend/` Flask app will consume.

### Technology Stack

**Backend**:
- Python 3.9+
- Flask (RESTful API)
- SQLite database (planned)
- watchdog (file monitoring)
- markdown/markdown2 (parsing)

**Frontend** (Planned):
- Vue.js 3 with Composition API
- Vite build tool
- Tailwind CSS
- Pinia (state management)
- Axios (HTTP client)
- Chart.js (visualization)

### Data Models

Core models are defined in `src/models/`:
- **Project** (`project.py`): Represents a development project with requirements, tasks, metrics, and sub-projects
- **Task** (`task.py`): Individual TODO items with status (not started, in progress, completed)
- **Requirement** (`requirement.py`): Requirements with MoSCoW priorities (MUST, SHOULD, COULD, WON'T)
- **ProgressMetrics** (`project.py`): Calculated metrics including completion percentage, health score, orphaned items

Projects support hierarchical structure with parent/child relationships.

### Configuration

Configuration is managed via `config.json` at the project root. Key settings:
- **Scanning**: `scan_directory` (default: `d:\dev2`), `ignored_directories`, `project_indicators`
- **Database**: `path` for SQLite database location
- **Parsing**: Task status markers, priority keywords, requirement priorities
- **AI Providers**: Claude, OpenAI, OpenRouter (future use, currently disabled)
- **Features**: Toggles for file_watching, periodic_scanning, write_operations, etc.

The `ConfigManager` class (`src/core/config_manager.py`) provides:
- Nested key access with dot notation (e.g., `config.get('logging.level')`)
- Default fallback values
- Configuration validation
- JSON-based persistence

### Markdown Parsing Conventions

ParallelDev expects projects to follow these markdown file conventions:

**REQUIREMENTS.md**:
```markdown
## Functional Requirements
1. MUST: System shall do X
2. SHOULD: System should do Y
3. COULD: System could do Z
```

**TODO.md**:
```markdown
## Stage 1: Foundation
### Core Services
- [ ] High: Implement feature A
- [x] Medium: Complete feature B
- [~] Low: In progress on feature C
```

Task status markers: `[ ]` (not started), `[x]` (completed), `[~]` (in progress)

## Common Development Tasks

### Running the Application

**Backend Server** (when implemented):
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run Flask server
python backend/main.py
```

**Frontend** (when implemented):
```bash
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=backend --cov=src tests/
```

### Installing Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies (when available)
cd frontend
npm install
```

### Database Operations

```bash
# Initialize database (when db_manager.py is implemented)
python backend/database/db_manager.py --init

# Backup database
# See config.json for backup settings
```

## Development Workflow

### Current Development Phase

The project is in **Phase 1: Core Foundation** with 0% completion. Priority tasks:
1. Database layer implementation (schema, CRUD operations)
2. Data models completion
3. Project scanner service
4. File parsers (TODO.md, REQUIREMENTS.md, README.md)
5. Metrics calculator
6. Configuration management (partially complete)

See `TODO.md` for the complete task breakdown across 6 phases.

### Coding Standards

**Python**:
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Include docstrings for all classes and functions
- Implement comprehensive error handling with try/except blocks
- Log all important operations and errors
- Comment complex logic and business rules

**Future Frontend** (JavaScript/Vue.js):
- Use Composition API for Vue components
- Follow Vue.js style guide
- Use async/await for asynchronous operations
- Add JSDoc comments for functions
- Use Tailwind CSS utility classes for styling

### Project Structure

```
parallel-dev/
├── backend/              # Flask API server (future)
│   ├── models/          # Database models
│   ├── services/        # Business logic services
│   ├── database/        # Database management
│   ├── utils/           # Utility functions
│   ├── main.py          # Flask application entry (to be created)
│   ├── api.py           # API endpoints (to be created)
│   └── config.py        # Configuration loading
├── src/                 # Core Python library
│   ├── core/           # Core functionality (ConfigManager)
│   ├── models/         # Data models (Project, Task, Requirement)
│   ├── future/         # Future AI integration code
│   ├── ui/             # UI-related code
│   └── visualization/  # Visualization utilities
├── frontend/            # Vue.js frontend (future)
│   ├── src/
│   │   ├── components/ # Vue components
│   │   ├── services/   # API client
│   │   └── main.js     # Entry point
│   └── package.json
├── data/                # SQLite database location
├── logs/                # Application logs
├── tests/               # Test files
├── config.json          # Application configuration
├── requirements.txt     # Python dependencies
├── REQUIREMENTS.md      # System requirements specification
├── TODO.md              # Development task list
└── README.md            # Project documentation
```

## Important Constraints

1. **Read-Only Operation (MVP)**: Initial version operates in read-only mode - no file modifications during scanning or analysis
2. **No Write Operations**: Do not implement task creation or modification via UI in initial phases
3. **Environment**: System must operate on Windows environment initially (configured for `d:\dev2`)
4. **Performance**: Initial scan of up to 100 projects must complete within 30 seconds
5. **Future Features**: AI integration (Claude, OpenAI, OpenRouter) and agent orchestration are planned but NOT yet implemented

## Key Design Decisions

1. **Dual Backend Approach**: Separation of core library (`src/`) and web API (`backend/`) allows for flexible deployment
2. **Hierarchical Projects**: Projects can contain sub-projects, enabling complex organizational structures
3. **Gap Analysis**: System tracks "orphaned" requirements (no tasks) and "orphaned" tasks (no requirements)
4. **Metrics-Driven**: Progress metrics calculated automatically including completion percentage and health score
5. **Configuration-Based**: Highly configurable via JSON to support different project structures and workflows

## Future Capabilities (Not Yet Implemented)

- AI Agent Orchestration: Spawn and manage Claude Code agents for automated development
- Context Engineering: Intelligent prompt generation with managed context windows
- Gap Analysis: AI-powered comparison of requirements vs implementation
- Write Operations: Task creation, status updates, and requirement management via UI
- Predictive Analytics: Project completion estimation and dependency analysis
