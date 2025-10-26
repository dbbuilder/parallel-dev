# ParallelDev - Parallel Development Manager

## Overview

ParallelDev is a comprehensive project management and visualization system designed to monitor and analyze multiple software development projects simultaneously. The system automatically scans project directories, parses documentation files (REQUIREMENTS.md, TODO.md, README.md), calculates progress metrics, and provides an interactive web-based dashboard for tracking development status across numerous concurrent projects.

This tool serves as the foundation for future AI-powered development orchestration, where multiple AI agents can work on different projects in parallel while maintaining coordinated progress tracking and context management.

## Development Status

**Current Phase**: Phase 7 - Frontend (Vue.js) ✅ **COMPLETE**

### Completed Phases:
- ✅ **Phase 1: Core Data Models** - 76 tests, 100% coverage
  - Task, Requirement, Project models with full serialization
- ✅ **Phase 2: Database Layer** - 85 tests, 87% coverage
  - DatabaseManager with CRUD operations for all entities
  - SQLite schema with 9 tables, 2 views, 5 triggers
- ✅ **Phase 3: Markdown Parsers** - 38 tests, 100% coverage
  - TODO.md parser with status/priority extraction
  - REQUIREMENTS.md parser with MoSCoW priorities
- ✅ **Phase 4: File Scanner** - 38 tests, 85-94% coverage
  - ProjectDetector with intelligent project identification
  - DirectoryScanner with recursive traversal
- ✅ **Phase 5: Metrics Calculator** - 18 tests, 100% coverage
  - Completion percentage calculation (tasks & requirements)
  - Health score based on blocked items
  - Orphaned task/requirement detection
  - Priority, stage, and category breakdowns
- ✅ **Phase 6: Flask API** - 24 tests, 100% passing
  - RESTful API with JSON responses
  - Project list and detail endpoints
  - Metrics endpoint with live calculations
  - Dashboard aggregation endpoint
  - Directory scan trigger endpoint
  - CORS support for frontend integration
  - Comprehensive error handling
- ✅ **Phase 7: Frontend (Vue.js)** - Initial implementation
  - Vue.js 3 with Composition API
  - Vite build system
  - Dashboard component with live data
  - API client service with comprehensive tests
  - Vitest testing framework configured
  - Responsive UI with modern design

### Overall Statistics:
- ✅ **279 Backend Tests Passing** (100% success rate)
- ✅ **49% Backend Coverage** (1,064 statements, 522 covered)
- ✅ **Frontend API Tests**: 6 test suites (getProjects, getProject, getMetrics, getDashboard, triggerScan, getHealth)
- ✅ **TDD Methodology** - All code developed test-first
- ✅ **Full Stack Complete** - Backend + Frontend MVP ready

See [TDD-DEVELOPMENT-PLAN.md](TDD-DEVELOPMENT-PLAN.md) for detailed roadmap.

## Key Features

### Current Capabilities (MVP)
- **Automated Project Discovery**: Recursively scans configured directories to identify and catalog projects
- **Intelligent Parsing**: Extracts structured information from REQUIREMENTS.md, TODO.md, and README.md files
- **Progress Metrics**: Calculates completion percentages, task counts, and requirement coverage
- **Visual Dashboard**: Interactive web interface with treeview accordion for project navigation
- **Real-time Monitoring**: File change detection with automatic status updates
- **Historical Tracking**: Stores metrics over time for trend analysis and velocity calculations
- **RESTful API**: Comprehensive API for accessing project data and metrics

### Future Capabilities (Planned)
- **AI Agent Orchestration**: Spawn and manage Claude Code agents for automated development
- **Context Engineering**: Intelligent prompt generation with managed context windows
- **Gap Analysis**: AI-powered comparison of requirements vs implementation
- **Multi-Provider AI Integration**: Support for Claude, OpenAI, and OpenRouter APIs
- **Write Operations**: Task creation, status updates, and requirement management via UI
- **Predictive Analytics**: Project completion estimation and dependency analysis

## Architecture

### Technology Stack

#### Backend
- **Language**: Python 3.9+
- **Web Framework**: Flask (RESTful API)
- **Database**: SQLite (with future support for PostgreSQL)
- **Markdown Parsing**: python-markdown / markdown2
- **File Monitoring**: watchdog
- **Environment Management**: python-dotenv
- **Logging**: Python logging module with structured output

#### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Charting**: Chart.js with vue-chartjs
- **Routing**: Vue Router

### Project Structure

```
d:\dev2\parallel-dev\
├── backend\
│   ├── models\              # Data models (Project, Task, Metric, Requirement)
│   ├── services\            # Business logic (scanners, parsers, calculators)
│   ├── database\            # Database management and schema
│   ├── utils\               # Utility functions (logging, markdown helpers)
│   ├── main.py              # Flask application entry point
│   ├── api.py               # API endpoint definitions
│   └── config.py            # Configuration management
├── frontend\
│   ├── public\              # Static assets
│   ├── src\
│   │   ├── components\      # Vue components (Dashboard, ProjectTree, etc.)
│   │   ├── services\        # API client and utilities
│   │   ├── App.vue          # Root Vue component
│   │   └── main.js          # Application entry point
│   ├── package.json         # Frontend dependencies
│   └── vite.config.js       # Vite configuration
├── data\
│   └── projects.db          # SQLite database
├── logs\                    # Application logs
├── config.json              # Application configuration
├── requirements.txt         # Python dependencies
├── REQUIREMENTS.md          # System requirements specification
├── README.md                # This file
├── TODO.md                  # Development task list
└── FUTURE.md                # Future enhancements and roadmap
```

## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn package manager
- Git (for cloning and version control)

### Backend Setup

1. **Navigate to project directory**:
```bash
cd d:\dev2\parallel-dev
```

2. **Create Python virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure application**:
Edit `config.json` to set your scan directory and preferences:
```json
{
  "scan_directory": "d:\\dev2",
  "database_path": "./data/projects.db",
  "scan_interval_seconds": 300,
  "file_watch_enabled": true
}
```

5. **Initialize database**:
```bash
python backend/database/db_manager.py --init
```

6. **Run backend server**:
```bash
python backend/main.py
```
Backend will be available at http://localhost:5000

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install Node.js dependencies**:
```bash
npm install
```

3. **Configure API endpoint** (if needed):
Edit `frontend/src/services/api.js` to set backend URL (default: http://localhost:5000)

4. **Run development server**:
```bash
npm run dev
```
Frontend will be available at http://localhost:5173

5. **Build for production**:
```bash
npm run build
```

## Usage

### Basic Workflow

1. **Start the backend server** to begin scanning and monitoring projects
2. **Open the dashboard** in your web browser at http://localhost:5173
3. **Navigate the project tree** to view project details
4. **Click on any project** to see detailed metrics, requirements, and tasks
5. **Monitor progress** through charts and visualization panels

### Dashboard Components

#### Project Tree (Left Panel)
- Hierarchical accordion view of all projects
- Color-coded status indicators:
  - 🟢 Green: Completed (100% tasks done)
  - 🟡 Yellow: In Progress (tasks in progress or partially complete)
  - 🔴 Red: Blocked or issues detected
  - ⚪ Gray: Not started
- Expandable/collapsible nodes for nested projects
- Click to select and view details

#### Project Detail Panel (Right Panel)
- Project name, path, and description
- Completion percentage and progress bars
- Task list with status indicators
- Requirements list with coverage metrics
- Last updated timestamp

#### Metrics and Charts (Bottom Panel)
- Line chart: Progress over time
- Bar chart: Task completion by section
- Donut chart: Overall completion percentage
- Statistics cards: Total tasks, completed tasks, requirements coverage

### API Endpoints

The backend provides a RESTful API for programmatic access:

#### Projects
- `GET /api/projects` - List all projects with summary metrics
- `GET /api/projects/{id}` - Get detailed project information
- `GET /api/projects/{id}/metrics` - Get historical metrics for charting
- `GET /api/projects/{id}/tasks` - Get all tasks for a project

#### Dashboard
- `GET /api/dashboard` - Get aggregated statistics for dashboard

#### Scanning
- `POST /api/scan` - Trigger manual scan of projects directory

#### Configuration
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration (future feature)

## Configuration

### config.json

```json
{
  "scan_directory": "d:\\dev2",
  "database_path": "./data/projects.db",
  "scan_interval_seconds": 300,
  "file_watch_enabled": true,
  "ignored_directories": [
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "dist",
    "build"
  ],
  "ai_providers": {
    "claude": {
      "api_key_env": "CLAUDE_API_KEY",
      "model": "claude-sonnet-4-5-20250929",
      "max_tokens": 4000
    },
    "openai": {
      "api_key_env": "OPENAI_API_KEY",
      "model": "gpt-4-turbo",
      "max_tokens": 4000
    },
    "openrouter": {
      "api_key_env": "OPENROUTER_API_KEY",
      "base_url": "https://openrouter.ai/api/v1"
    }
  },
  "logging": {
    "level": "INFO",
    "file": "./logs/paralleldev.log",
    "max_bytes": 10485760,
    "backup_count": 5
  }
}
```

### Environment Variables

Create a `.env` file in the project root for sensitive configuration:

```env
# AI Provider API Keys (for future use)
CLAUDE_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

## Documentation Standards

ParallelDev expects projects to follow these markdown file conventions:

### REQUIREMENTS.md Format
```markdown
## Functional Requirements
1. MUST: System shall do X
2. SHOULD: System should do Y
3. COULD: System could do Z

## Technical Requirements
1. MUST: Use technology A
2. SHOULD: Support feature B
```

### TODO.md Format
```markdown
## Stage 1: Foundation
### Core Services
- [ ] High: Implement feature A
- [x] Medium: Complete feature B
- [~] Low: In progress on feature C

## Stage 2: Enhancement
### Advanced Features
- [ ] High: Add feature D
```

### README.md Format
Standard markdown with project description, setup instructions, and usage documentation.

## Development

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/your-feature-name`
2. **Implement backend changes**: Add services, models, API endpoints as needed
3. **Implement frontend changes**: Add/modify Vue components
4. **Add tests**: Write unit and integration tests
5. **Update documentation**: Modify REQUIREMENTS.md, TODO.md, README.md
6. **Submit for review**: Create pull request with detailed description

### Code Standards

#### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Include docstrings for all classes and functions
- Implement comprehensive error handling with try/except blocks
- Log all important operations and errors
- Comment complex logic and business rules

#### JavaScript/Vue.js (Frontend)
- Use Composition API for Vue components
- Follow Vue.js style guide
- Use async/await for asynchronous operations
- Implement error handling for all API calls
- Add JSDoc comments for functions
- Use Tailwind CSS utility classes for styling

### Testing

#### Backend Testing
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=backend tests/
```

#### Frontend Testing
```bash
# Run unit tests
npm run test:unit

# Run end-to-end tests
npm run test:e2e
```

## Troubleshooting

### Common Issues

#### Backend won't start
- Verify Python version: `python --version` (should be 3.9+)
- Check if virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify database file exists and is accessible
- Check logs in `./logs/paralleldev.log`

#### Frontend won't start
- Verify Node.js version: `node --version` (should be 16+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check if backend is running and accessible
- Clear browser cache and cookies
- Check browser console for errors

#### Projects not appearing in dashboard
- Verify scan directory path in config.json is correct
- Ensure projects have REQUIREMENTS.md, TODO.md, or README.md files
- Check backend logs for scanning errors
- Manually trigger scan via API: `POST http://localhost:5000/api/scan`
- Verify file permissions allow reading project directories

#### Metrics not updating
- Check if file watcher is enabled in config.json
- Verify scan interval setting is reasonable
- Check database connection and file permissions
- Review logs for parsing errors
- Manually trigger database update

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow code standards** as outlined in this document
3. **Write tests** for new functionality
4. **Update documentation** to reflect changes
5. **Submit pull request** with clear description of changes

### Commit Message Format
```
type(scope): brief description

Detailed explanation of changes made and reasoning behind them.

Fixes #issue_number
```

Types: feat, fix, docs, style, refactor, test, chore

## License

Copyright (c) 2025 DBBuilder. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is strictly prohibited.

## Support

For questions, issues, or feature requests:
- **Email**: support@dbbuilder.io
- **GitHub Issues**: https://github.com/dbbuilder/parallel-dev/issues
- **Documentation**: https://docs.dbbuilder.io/parallel-dev

## Acknowledgments

- Flask framework and ecosystem
- Vue.js and Vue community
- Tailwind CSS for beautiful UI design
- Chart.js for data visualization
- watchdog library for file monitoring
- Anthropic Claude for AI capabilities

## Version History

### v0.1.0 (Current - MVP)
- Initial release with core scanning and parsing
- Basic dashboard with project tree view
- SQLite database integration
- Real-time file monitoring
- Progress metrics calculation
- RESTful API implementation

### Future Versions
- v0.2.0: Enhanced parsing and metrics
- v0.3.0: Advanced visualization and filtering
- v0.4.0: AI integration preparation layer
- v0.5.0: AI-powered gap analysis
- v1.0.0: Full agent orchestration system
