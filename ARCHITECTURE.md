# ParallelDev - System Architecture

## Document Overview

This document provides a comprehensive architectural overview of the ParallelDev system, including design decisions, technology stack, component interactions, and architectural patterns. It incorporates modern best practices from 2025 research on project management dashboards, real-time monitoring, markdown parsing, and AI agent orchestration.

**Last Updated**: 2025-10-25
**Version**: 0.1.0 (Early Development)
**Status**: Architecture defined, implementation in Phase 1

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Principles](#architectural-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Technology Stack](#technology-stack)
5. [Component Architecture](#component-architecture)
6. [Data Architecture](#data-architecture)
7. [API Architecture](#api-architecture)
8. [Real-Time Monitoring Architecture](#real-time-monitoring-architecture)
9. [Markdown Parsing Architecture](#markdown-parsing-architecture)
10. [AI Agent Orchestration Architecture](#ai-agent-orchestration-architecture)
11. [Security Architecture](#security-architecture)
12. [Deployment Architecture](#deployment-architecture)
13. [Performance Considerations](#performance-considerations)
14. [Future Architecture Evolution](#future-architecture-evolution)

---

## System Overview

### Purpose

ParallelDev is a comprehensive project management and visualization system designed to:
- Monitor and analyze multiple software development projects in parallel
- Parse project documentation (REQUIREMENTS.md, TODO.md, README.md)
- Calculate progress metrics and health indicators
- Provide real-time visual dashboards for tracking development status
- **Future**: Orchestrate AI agents for automated development tasks

### Core Value Proposition

1. **Unified Monitoring**: Single dashboard for tracking 100+ concurrent projects
2. **Automated Analysis**: Intelligent parsing and metrics calculation without manual input
3. **Real-Time Updates**: File watching with automatic status refresh
4. **AI-Ready Foundation**: Architecture designed for future AI agent integration
5. **Zero Configuration**: Works with existing project structures without modification

### Design Philosophy

- **Read-Only First**: MVP operates in read-only mode to ensure safety
- **Minimal Coupling**: Core library (`src/`) independent of web framework (`backend/`)
- **Progressive Enhancement**: Start simple, add complexity incrementally
- **Future-Proof**: Architecture supports planned AI orchestration features

---

## Architectural Principles

### 1. Separation of Concerns

**Dual Backend Pattern**: The system employs a unique dual-backend architecture:

```
src/              # Core library (domain logic, models, parsers)
├── models/       # Data models (Project, Task, Requirement)
├── core/         # Core services (ConfigManager)
├── parsers/      # Markdown parsing logic (future)
├── metrics/      # Metrics calculation (future)
└── scanners/     # File system scanning (future)

backend/          # Flask API server (presentation layer)
├── api.py        # REST endpoints
├── main.py       # Flask application
└── services/     # API-specific services
```

**Benefits**:
- Core library can be used standalone (CLI, scripts)
- Backend can be swapped (Flask → FastAPI/GraphQL)
- Testing isolation
- Multiple deployment modes (web, CLI, embedded)

### 2. Domain-Driven Design

**Core Domain Models**:
- **Project**: Aggregate root representing a development project
- **Task**: Entity representing actionable TODO items
- **Requirement**: Entity representing functional/technical requirements
- **ProgressMetrics**: Value object for calculated metrics

**Domain Boundaries**:
- Scanning domain: File discovery and monitoring
- Parsing domain: Markdown analysis and extraction
- Metrics domain: Progress calculation and analytics
- Orchestration domain: AI agent management (future)

### 3. Event-Driven Architecture

**Event Sources**:
- File system changes (watchdog events)
- Scheduled scans (periodic polling)
- Manual triggers (API requests)
- Agent activities (future)

**Event Flow**:
```
File Change → Watchdog → Parser → Metrics Calculator → Database → WebSocket → Frontend
```

### 4. Plugin Architecture (Future)

**Extensibility Points**:
- Custom parsers for different markdown formats
- Custom metrics calculators
- AI provider adapters (Claude, OpenAI, OpenRouter)
- Visualization renderers

### 5. Fail-Safe Operation

**Graceful Degradation**:
- Individual project parsing failures don't crash the system
- Missing markdown files don't prevent project detection
- Database connection failures log errors but don't block scans
- Configuration errors fall back to sensible defaults

---

## High-Level Architecture

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Environment                        │
│                                                              │
│  ┌──────────────┐                  ┌──────────────┐         │
│  │   Projects   │                  │   Browser    │         │
│  │   (d:\dev2)  │                  │  (Dashboard) │         │
│  └──────┬───────┘                  └──────┬───────┘         │
│         │                                  │                 │
└─────────┼──────────────────────────────────┼─────────────────┘
          │                                  │
          │ File System                      │ HTTP/WS
          │                                  │
┌─────────▼──────────────────────────────────▼─────────────────┐
│                    ParallelDev System                         │
│                                                              │
│  ┌────────────────┐      ┌────────────────┐                │
│  │  File Watcher  │      │   Flask API    │                │
│  │   (watchdog)   │      │   (Backend)    │                │
│  └────────┬───────┘      └────────┬───────┘                │
│           │                       │                          │
│           │                       │                          │
│  ┌────────▼───────────────────────▼───────┐                │
│  │         Core Library (src/)            │                │
│  │  ┌──────────┐  ┌──────────┐           │                │
│  │  │ Scanner  │  │  Parser  │           │                │
│  │  └────┬─────┘  └────┬─────┘           │                │
│  │       │             │                  │                │
│  │  ┌────▼─────────────▼─────┐           │                │
│  │  │   Metrics Calculator   │           │                │
│  │  └────────────┬────────────┘           │                │
│  └───────────────┼────────────────────────┘                │
│                  │                                          │
│         ┌────────▼────────┐                                │
│         │  SQLite Database │                                │
│         └─────────────────┘                                │
└───────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
1. File System Scan:
   User Projects → Scanner → Parser → Metrics → Database

2. Real-Time Updates:
   File Change → Watchdog → Scanner → Parser → Metrics → Database → WebSocket → Frontend

3. API Request:
   Browser → Flask API → Core Library → Database → JSON Response → Browser

4. Dashboard Load:
   Browser → API (GET /projects) → Database → Tree Data → Vue.js Rendering
```

---

## Technology Stack

### Backend (Python)

#### Core Framework
- **Flask 3.x**: Lightweight web framework for RESTful API
  - **Why Flask**: Simple, minimal overhead, easy to understand
  - **Alternatives Considered**: FastAPI (async), Django (too heavy)

#### Data Persistence
- **SQLite**: Embedded relational database
  - **Why SQLite**: Zero configuration, file-based, sufficient for MVP
  - **Future Migration**: PostgreSQL for enterprise scale

#### Markdown Parsing
- **Planned Libraries** (based on 2025 research):
  - **mistletoe**: Fast, spec-compliant, AST-based parsing
  - **commonmark**: Pure Python CommonMark implementation
  - **Alternatives**: markdown-it-py, python-markdown

**Selection Criteria**:
```python
# mistletoe provides AST for structured parsing
import mistletoe
from mistletoe.ast_renderer import ASTRenderer

# Two-step parsing: Markdown → AST → Custom extraction
with open('TODO.md') as f:
    doc = mistletoe.Document(f)
    ast = ASTRenderer().render(doc)
    tasks = extract_tasks_from_ast(ast)  # Custom logic
```

**Why AST-based**: Enables precise extraction of task hierarchies, status markers, and metadata without regex brittleness.

#### File Monitoring
- **watchdog 6.0+**: Cross-platform file system event monitoring
  - **Pattern**: Observer pattern with event handlers
  - **Scalability Note**: kqueue (macOS/BSD) requires increased file descriptor limits for large projects

```python
# Debounced file watching pattern
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class DebounceHandler(PatternMatchingEventHandler):
    def __init__(self, debounce_seconds=2):
        super().__init__(patterns=['*.md'])
        self.debounce_seconds = debounce_seconds
        self.pending_events = {}

    def on_modified(self, event):
        # Debounce rapid changes
        self.schedule_update(event.src_path)
```

#### Configuration Management
- **JSON-based**: `config.json` with schema validation
- **ConfigManager**: Dot notation access, defaults, validation

#### Logging
- **Python logging**: Structured logging with rotation
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output**: Both file and console with configurable formats

### Frontend (Vue.js)

#### Framework
- **Vue.js 3**: Progressive JavaScript framework
  - **Composition API**: Modern, reactive, TypeScript-friendly
  - **Why Vue**: Gentle learning curve, excellent docs, reactive

#### Build Tool
- **Vite 5.x**: Fast build tool and dev server
  - **Why Vite**: Lightning-fast HMR, native ESM, optimized builds

#### Styling
- **Tailwind CSS 3.x**: Utility-first CSS framework
  - **Why Tailwind**: Rapid UI development, consistent design system

#### State Management
- **Pinia**: Official Vue state management
  - **Why Pinia**: Vue 3 native, TypeScript support, simpler than Vuex

#### HTTP Client
- **Axios**: Promise-based HTTP client
  - **Features**: Interceptors, request cancellation, automatic JSON

#### Visualization
- **Chart.js 4.x**: Canvas-based charting
  - **vue-chartjs**: Vue 3 wrapper for Chart.js
  - **Chart Types**: Line (progress), Bar (tasks), Donut (completion)

---

## Component Architecture

### Backend Components

#### 1. Scanner Service

**Responsibility**: Discover and catalog projects from file system

```python
class ProjectScanner:
    """
    Recursively scans directories to discover projects.

    Detection Logic:
    - Project identified by presence of REQUIREMENTS.md, TODO.md, or README.md
    - Supports nested projects (projects within projects)
    - Respects ignore list (node_modules, .git, etc.)
    """

    def scan(self, root_path: str) -> List[Project]:
        """
        Performance Target: 100 projects in <30 seconds
        Scalability: Handles up to 500 projects
        """
        pass
```

**Optimization**:
- Parallel scanning with multiprocessing
- Ignore list filtering early (before recursion)
- Incremental scanning (only changed projects)

#### 2. Parser Service

**Responsibility**: Extract structured data from markdown files

**Architecture Pattern**: Strategy Pattern for different markdown types

```python
class MarkdownParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> Any:
        pass

class TodoParser(MarkdownParser):
    """
    Extracts tasks from TODO.md

    Parsing Strategy:
    1. AST parsing with mistletoe
    2. Identify list items
    3. Extract status markers: [ ], [x], [~]
    4. Parse hierarchy: stage → section → task
    5. Extract priorities: High, Medium, Low
    """

    def parse(self, content: str) -> List[Task]:
        # AST-based parsing
        doc = mistletoe.Document(content)
        return self._extract_tasks(doc)

class RequirementsParser(MarkdownParser):
    """
    Extracts requirements from REQUIREMENTS.md

    MoSCoW Detection:
    - MUST: Required features
    - SHOULD: Important features
    - COULD: Nice-to-have features
    - WON'T: Out of scope
    """
    pass

class ReadmeParser(MarkdownParser):
    """
    Extracts project metadata from README.md

    Extraction:
    - Project title (first H1)
    - Description (first paragraph)
    - Technology stack (keywords)
    """
    pass
```

#### 3. Metrics Calculator

**Responsibility**: Compute progress metrics and health scores

```python
class MetricsCalculator:
    """
    Calculates project metrics.

    Metrics:
    - Completion percentage: (completed_tasks / total_tasks) * 100
    - Health score: Multi-factor calculation
    - Velocity: Tasks completed per time period
    - Gap analysis: Requirements without tasks
    """

    def calculate_completion(self, project: Project) -> float:
        """Performance: O(n) where n = task count"""
        pass

    def calculate_health_score(self, project: Project) -> float:
        """
        Health Score Formula:
        - Completion rate: 40%
        - Recent activity: 30%
        - Requirement coverage: 20%
        - Blockers/issues: 10%

        Range: 0.0 to 1.0
        """
        pass

    def detect_gaps(self, project: Project) -> Dict[str, int]:
        """
        Gap Analysis:
        - Orphaned requirements: Requirements with no tasks
        - Orphaned tasks: Tasks with no requirements

        Uses fuzzy matching (rapidfuzz) for semantic linking
        """
        pass
```

#### 4. File Watcher Service

**Responsibility**: Monitor file system for changes

**Pattern**: Observer pattern with debouncing

```python
class FileWatcherService:
    """
    Real-time file monitoring with watchdog.

    Debouncing Strategy:
    - Wait 2 seconds after last change before triggering update
    - Prevents excessive updates during bulk edits

    Scalability Considerations:
    - kqueue (macOS): Increase ulimit -n (file descriptors)
    - inotify (Linux): Increase fs.inotify.max_user_watches
    - Windows: Uses ReadDirectoryChangesW (no limits)
    """

    def __init__(self, debounce_seconds: int = 2):
        self.observer = Observer()
        self.debounce_seconds = debounce_seconds

    def watch(self, path: str, callback: Callable):
        """Start watching directory for changes"""
        pass
```

### Frontend Components

#### 1. Dashboard View

**Component Hierarchy**:
```
Dashboard.vue
├── ProjectTreePanel.vue
│   └── ProjectTreeNode.vue (recursive)
├── ProjectDetailPanel.vue
│   ├── ProjectHeader.vue
│   ├── TaskList.vue
│   └── RequirementsList.vue
└── MetricsPanel.vue
    ├── ProgressChart.vue
    ├── TaskChart.vue
    └── CompletionDonut.vue
```

#### 2. State Management (Pinia)

```javascript
// stores/projects.js
export const useProjectsStore = defineStore('projects', {
  state: () => ({
    projects: [],
    selectedProjectId: null,
    loading: false,
    error: null
  }),

  getters: {
    projectTree: (state) => {
      // Transform flat list to hierarchical tree
      return buildTree(state.projects)
    },

    selectedProject: (state) => {
      return state.projects.find(p => p.id === state.selectedProjectId)
    }
  },

  actions: {
    async fetchProjects() {
      this.loading = true
      try {
        const response = await api.getProjects()
        this.projects = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  }
})
```

---

## Data Architecture

### Database Schema (SQLite)

```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT UNIQUE NOT NULL,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scanned TIMESTAMP,
    last_updated TIMESTAMP,

    -- File flags
    has_requirements_file BOOLEAN DEFAULT 0,
    has_todo_file BOOLEAN DEFAULT 0,
    has_readme_file BOOLEAN DEFAULT 0,

    -- File paths
    requirements_file_path TEXT,
    todo_file_path TEXT,
    readme_file_path TEXT,

    -- Metadata
    readme_content TEXT,

    FOREIGN KEY (parent_id) REFERENCES projects(id)
);

-- Requirements table
CREATE TABLE requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('MUST', 'SHOULD', 'COULD', 'WONT')),
    category TEXT,  -- functional, technical, performance, etc.
    section TEXT,   -- Section heading in REQUIREMENTS.md
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed')),
    priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
    stage TEXT,     -- Phase or stage in TODO.md
    section TEXT,   -- Section within stage
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Metrics history table
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Task metrics
    total_tasks INTEGER,
    completed_tasks INTEGER,
    in_progress_tasks INTEGER,

    -- Requirement metrics
    total_requirements INTEGER,
    completed_requirements INTEGER,

    -- Calculated metrics
    completion_percentage REAL,
    health_score REAL,

    -- Gap analysis
    orphaned_requirements INTEGER,
    orphaned_tasks INTEGER,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_projects_parent ON projects(parent_id);
CREATE INDEX idx_projects_path ON projects(path);
CREATE INDEX idx_requirements_project ON requirements(project_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(project_id, status);
CREATE INDEX idx_metrics_project_time ON metrics(project_id, timestamp DESC);
```

### Data Models (Python)

**Design Pattern**: Rich domain models with behavior

```python
# src/models/project.py
@dataclass
class Project:
    """
    Rich domain model for projects.

    Responsibilities:
    - Aggregate root for requirements and tasks
    - Parent-child project relationships
    - Metrics calculation coordination
    """

    path: Path
    name: str
    requirements: List[Requirement] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    sub_projects: List['Project'] = field(default_factory=list)
    parent_project: Optional['Project'] = None
    metrics: ProgressMetrics = field(default_factory=ProgressMetrics)

    def add_requirement(self, requirement: Requirement) -> None:
        """Add requirement and recalculate metrics"""
        self.requirements.append(requirement)
        self.metrics = self._calculate_metrics()

    def get_all_tasks(self, include_subprojects: bool = False) -> List[Task]:
        """Get tasks with optional subproject aggregation"""
        tasks = self.tasks.copy()
        if include_subprojects:
            for sub in self.sub_projects:
                tasks.extend(sub.get_all_tasks(include_subprojects=True))
        return tasks

    def calculate_completion(self) -> float:
        """Calculate completion percentage"""
        total = len(self.tasks)
        if total == 0:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return (completed / total) * 100.0
```

---

## API Architecture

### RESTful API Design

**Principles**:
- Resource-based URLs
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response format
- HATEOAS for discoverability (future)
- Versioning in URL (`/api/v1/...`)

### Endpoint Design

```
GET    /api/projects                 # List all projects
GET    /api/projects/{id}             # Get project details
GET    /api/projects/{id}/tasks       # Get project tasks
GET    /api/projects/{id}/requirements # Get project requirements
GET    /api/projects/{id}/metrics     # Get historical metrics
GET    /api/projects/{id}/metrics/latest # Get current metrics

GET    /api/dashboard                 # Aggregated statistics
POST   /api/scan                      # Trigger manual scan
GET    /api/config                    # Get configuration

# Future write operations
POST   /api/projects/{id}/tasks       # Create task
PATCH  /api/tasks/{id}                # Update task status
```

### Response Format

```json
{
  "status": "success",
  "data": {
    "project": {
      "id": 1,
      "name": "ParallelDev",
      "path": "/d/dev2/parallel-dev",
      "completion_percentage": 25.5,
      "health_score": 0.75,
      "metrics": {
        "total_tasks": 150,
        "completed_tasks": 38,
        "in_progress_tasks": 5,
        "total_requirements": 100,
        "orphaned_requirements": 12
      },
      "last_scanned": "2025-10-25T16:30:00Z"
    }
  },
  "meta": {
    "timestamp": "2025-10-25T16:31:00Z",
    "version": "0.1.0"
  }
}
```

### Error Handling

```json
{
  "status": "error",
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project with ID 999 not found",
    "details": {
      "requested_id": 999
    }
  },
  "meta": {
    "timestamp": "2025-10-25T16:31:00Z",
    "request_id": "abc-123-def"
  }
}
```

### CORS Configuration

```python
# backend/main.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative port
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## Real-Time Monitoring Architecture

### Dashboard Architecture Pattern

**Based on 2025 Research**: Modern dashboards implement a three-tier architecture:
1. **Operational Dashboard**: Real-time task progress, team performance
2. **Tactical Dashboard**: Resource utilization, cost management
3. **Strategic Dashboard**: High-level portfolio overview

ParallelDev implements the **Operational Dashboard** pattern with hierarchical project trees and real-time metrics.

### Real-Time Update Mechanisms

**Option 1: WebSocket (Future)**
```javascript
// Frontend WebSocket connection
const ws = new WebSocket('ws://localhost:5000/ws')

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  if (update.type === 'PROJECT_UPDATED') {
    projectsStore.updateProject(update.project)
  }
}
```

**Option 2: Short Polling (Current)**
```javascript
// Poll every 30 seconds
setInterval(() => {
  projectsStore.fetchProjects()
}, 30000)
```

**Option 3: Server-Sent Events (Alternative)**
```python
@app.route('/api/events')
def events():
    def generate():
        while True:
            # Check for updates
            if updates_available():
                yield f"data: {json.dumps(get_updates())}\n\n"
            time.sleep(5)
    return Response(generate(), mimetype='text/event-stream')
```

### File Change Propagation

```
File Modified
    ↓
Watchdog Event
    ↓
Debounce (2 seconds)
    ↓
Trigger Re-Parse
    ↓
Update Database
    ↓
Broadcast to Clients (WebSocket/SSE)
    ↓
Frontend Update
```

---

## Markdown Parsing Architecture

### AST-Based Parsing Pattern

**Research Finding (2025)**: Two-step parsing process is industry best practice:
1. **Markdown → AST**: Parse markdown into abstract syntax tree
2. **AST → Domain Objects**: Extract structured data from AST

**Library Selection**: **mistletoe** for ParallelDev

```python
import mistletoe
from mistletoe.ast_renderer import ASTRenderer

class TodoParser:
    """
    AST-based TODO.md parser.

    Advantages over Regex:
    - Handles nested lists correctly
    - Respects markdown structure
    - Extensible for custom syntax
    - Robust to formatting variations
    """

    def parse(self, content: str) -> List[Task]:
        # Parse markdown to AST
        doc = mistletoe.Document(content)
        ast = ASTRenderer().render(doc)

        # Extract tasks from AST
        return self._extract_tasks_from_ast(ast)

    def _extract_tasks_from_ast(self, ast: dict) -> List[Task]:
        """
        Traverse AST to find list items with checkboxes.

        AST Structure for Tasks:
        {
            "type": "List",
            "children": [
                {
                    "type": "ListItem",
                    "children": [
                        {
                            "type": "RawText",
                            "content": "[ ] High: Implement feature"
                        }
                    ]
                }
            ]
        }
        """
        tasks = []
        current_stage = None
        current_section = None

        for node in self._traverse_ast(ast):
            if node['type'] == 'Heading':
                if node['level'] == 2:
                    current_stage = node['content']
                elif node['level'] == 3:
                    current_section = node['content']

            elif node['type'] == 'ListItem':
                task = self._parse_task_item(node, current_stage, current_section)
                if task:
                    tasks.append(task)

        return tasks

    def _parse_task_item(self, node: dict, stage: str, section: str) -> Optional[Task]:
        """
        Parse task from list item node.

        Expected formats:
        - [ ] High: Implement feature
        - [x] Medium: Complete feature
        - [~] Low: In progress
        """
        text = node.get('content', '')

        # Extract status
        status = TaskStatus.NOT_STARTED
        if text.startswith('[x]'):
            status = TaskStatus.COMPLETED
        elif text.startswith('[~]'):
            status = TaskStatus.IN_PROGRESS

        # Extract priority
        priority = self._extract_priority(text)

        # Extract task text
        task_text = self._clean_task_text(text)

        return Task(
            text=task_text,
            status=status,
            priority=priority,
            stage=stage,
            section=section
        )
```

### Requirement Parsing with MoSCoW

```python
class RequirementsParser:
    """
    Parse REQUIREMENTS.md with MoSCoW prioritization.

    MoSCoW Method:
    - MUST: Critical requirements
    - SHOULD: Important requirements
    - COULD: Nice-to-have requirements
    - WON'T: Out of scope
    """

    PRIORITY_PATTERNS = {
        'MUST': r'(?i)\b(MUST|must have|required|critical)\b',
        'SHOULD': r'(?i)\b(SHOULD|should have|important)\b',
        'COULD': r'(?i)\b(COULD|could have|nice to have|optional)\b',
        'WONT': r'(?i)\b(WON\'T|won\'t have|will not have)\b'
    }

    def parse(self, content: str) -> List[Requirement]:
        doc = mistletoe.Document(content)
        requirements = []
        current_category = None

        for node in self._traverse_ast(doc):
            if node['type'] == 'Heading' and node['level'] == 2:
                current_category = node['content']

            elif node['type'] == 'ListItem':
                req = self._parse_requirement(node, current_category)
                if req:
                    requirements.append(req)

        return requirements

    def _parse_requirement(self, node: dict, category: str) -> Optional[Requirement]:
        text = node.get('content', '')
        priority = self._detect_priority(text)

        return Requirement(
            text=text,
            priority=priority,
            category=category
        )

    def _detect_priority(self, text: str) -> str:
        """Detect MoSCoW priority from requirement text"""
        for priority, pattern in self.PRIORITY_PATTERNS.items():
            if re.search(pattern, text):
                return priority
        return 'SHOULD'  # Default
```

---

## AI Agent Orchestration Architecture

### Multi-Agent Patterns (2025 Research)

ParallelDev is designed to support five orchestration patterns:

#### 1. Sequential Orchestration
```
Agent 1 (Requirements Analysis)
    ↓
Agent 2 (Task Breakdown)
    ↓
Agent 3 (Code Generation)
    ↓
Agent 4 (Testing)
```

#### 2. Parallel Orchestration
```
                    ┌─→ Agent 1 (Frontend)
                    │
Coordinator Agent ──┼─→ Agent 2 (Backend)
                    │
                    └─→ Agent 3 (Tests)
```

#### 3. Hierarchical Orchestration
```
Meta-Agent (Project Manager)
    ├─→ Sub-Agent 1 (Feature A)
    │       ├─→ Worker 1 (Components)
    │       └─→ Worker 2 (Tests)
    └─→ Sub-Agent 2 (Feature B)
            ├─→ Worker 3 (API)
            └─→ Worker 4 (Docs)
```

#### 4. Event-Driven Orchestration
```
File Change Event → Agent spawned dynamically
Test Failure Event → Debug Agent triggered
Requirement Added → Analysis Agent activated
```

#### 5. Collaborative Orchestration
```
Agent 1 ←→ Agent 2 ←→ Agent 3
(Shared context, message passing, consensus)
```

### Claude Code Integration

**Based on 2025 Research**: Claude Code supports up to 10 parallel tasks

```python
class ClaudeAgentOrchestrator:
    """
    Orchestrate multiple Claude Code agents.

    Capabilities:
    - Spawn up to 10 parallel agents
    - Task queue for >10 tasks (batch processing)
    - Resource management (CPU, memory limits)
    - Parent-child communication (when supported)
    """

    def __init__(self, max_parallel_agents: int = 10):
        self.max_parallel_agents = max_parallel_agents
        self.active_agents = {}
        self.task_queue = []

    async def spawn_agent(self, task: AgentTask) -> str:
        """
        Spawn a Claude Code agent via Task tool.

        Args:
            task: Structured task with prompt and context

        Returns:
            agent_id for tracking
        """
        if len(self.active_agents) >= self.max_parallel_agents:
            # Queue for batch execution
            self.task_queue.append(task)
            return None

        # Spawn agent using Task tool
        agent_id = await self._spawn_claude_agent(task)
        self.active_agents[agent_id] = task
        return agent_id

    async def _spawn_claude_agent(self, task: AgentTask) -> str:
        """
        Use Claude Code Task tool to spawn subagent.

        Prompt Engineering:
        - Clear task description
        - Explicit steps
        - Expected deliverables
        - Success criteria
        """
        prompt = self._build_agent_prompt(task)

        # Task tool invocation (pseudo-code)
        agent_id = await claude_task_tool.invoke({
            "prompt": prompt,
            "description": task.description,
            "subagent_type": task.agent_type
        })

        return agent_id

    def _build_agent_prompt(self, task: AgentTask) -> str:
        """
        Build optimized prompt for agent.

        Research Finding: Explicit steps increase parallelism usage
        """
        return f"""
        Task: {task.description}

        Steps to complete:
        {chr(10).join(f'{i+1}. {step}' for i, step in enumerate(task.steps))}

        Context:
        {task.context}

        Expected Deliverables:
        {chr(10).join(f'- {d}' for d in task.deliverables)}

        Success Criteria:
        {chr(10).join(f'- {c}' for c in task.success_criteria)}
        """
```

### 7-Agent Feature Pattern

**Research Finding**: This pattern delivers 5x faster feature implementation

```python
async def implement_feature_with_agents(feature_spec: dict):
    """
    Spawn 7 specialized agents for feature implementation.

    Agents:
    1. Component Creator
    2. Styles/CSS
    3. Tests
    4. Type Definitions
    5. Documentation
    6. Configuration Updates
    7. Integration & Validation
    """

    agents = [
        AgentTask("component", "Create Vue components", steps=[...]),
        AgentTask("styles", "Implement Tailwind CSS styles", steps=[...]),
        AgentTask("tests", "Write unit and integration tests", steps=[...]),
        AgentTask("types", "Define TypeScript interfaces", steps=[...]),
        AgentTask("docs", "Generate documentation", steps=[...]),
        AgentTask("config", "Update configuration files", steps=[...]),
        AgentTask("integration", "Integrate and validate", steps=[...]),
    ]

    # Spawn all agents in parallel
    agent_ids = await asyncio.gather(*[
        orchestrator.spawn_agent(agent) for agent in agents
    ])

    # Wait for completion
    results = await orchestrator.wait_for_completion(agent_ids)

    return results
```

### AI Provider Abstraction

```python
class AIProviderAdapter(ABC):
    """Abstract interface for AI providers"""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def spawn_agent(self, task: AgentTask) -> str:
        pass

class ClaudeProvider(AIProviderAdapter):
    """Anthropic Claude integration"""

    async def complete(self, prompt: str, **kwargs) -> str:
        # Use Anthropic API
        pass

class OpenAIProvider(AIProviderAdapter):
    """OpenAI GPT integration"""

    async def complete(self, prompt: str, **kwargs) -> str:
        # Use OpenAI API
        pass

class OpenRouterProvider(AIProviderAdapter):
    """OpenRouter multi-model integration"""

    async def complete(self, prompt: str, **kwargs) -> str:
        # Use OpenRouter API
        pass
```

---

## Security Architecture

### Current Security (MVP - Read-Only)

**Threat Model**:
- **Low Risk**: Read-only operation limits attack surface
- **File System Access**: Limited to configured scan directory
- **No User Input**: No write operations reduce injection risks

**Security Measures**:
- Input validation for file paths (prevent directory traversal)
- Configuration validation
- SQL parameterized queries (prevent SQL injection)
- CORS restrictions on API

### Future Security (Write Operations)

**Authentication**:
- JWT-based authentication
- OAuth 2.0 / SAML for enterprise SSO

**Authorization**:
- Role-based access control (RBAC)
- Project-level permissions

**Data Protection**:
- Encryption at rest (database encryption)
- Encryption in transit (HTTPS/TLS)
- API key secure storage (environment variables, secrets manager)

**Audit Logging**:
- All write operations logged
- User action tracking
- Change history

---

## Deployment Architecture

### Development Deployment

```
┌─────────────────┐         ┌─────────────────┐
│  Flask Backend  │         │   Vite Dev      │
│  localhost:5000 │ ←─────→ │  localhost:5173 │
└────────┬────────┘         └─────────────────┘
         │
         ↓
┌─────────────────┐
│ SQLite Database │
│  data/db.sqlite │
└─────────────────┘
```

### Production Deployment (Future)

```
                    ┌─────────────┐
                    │   Nginx     │
                    │ (Reverse    │
                    │  Proxy)     │
                    └──────┬──────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
    ┌──────▼──────┐               ┌───────▼────────┐
    │   Static    │               │  Flask App     │
    │   Files     │               │  (Gunicorn)    │
    │  (Vue.js)   │               │  Multiple      │
    └─────────────┘               │  Workers       │
                                  └───────┬────────┘
                                          │
                                  ┌───────▼────────┐
                                  │  PostgreSQL    │
                                  │  Database      │
                                  └────────────────┘
```

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.main:app"]

# Frontend Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

---

## Performance Considerations

### Scalability Targets

| Metric | MVP Target | Future Target |
|--------|------------|---------------|
| Projects | 100 | 500+ |
| Initial Scan Time | <30 seconds | <60 seconds |
| API Response Time | <500ms | <200ms |
| Dashboard Load Time | <3 seconds | <1 second |
| Concurrent Users | 1 | 100+ |

### Optimization Strategies

#### Database Optimization
- **Indexing**: Strategic indexes on foreign keys and query columns
- **Query Optimization**: Use EXPLAIN to analyze slow queries
- **Connection Pooling**: Reuse database connections
- **Caching**: Redis cache for frequently accessed data (future)

#### File System Scanning
- **Parallel Scanning**: Use multiprocessing for directory traversal
- **Incremental Updates**: Only re-scan changed projects
- **Ignore List Optimization**: Filter ignored directories early

#### API Performance
- **Pagination**: Limit result sets (default 20 items)
- **Field Filtering**: Return only requested fields
- **Compression**: GZIP response compression
- **HTTP/2**: Support multiplexing (future)

#### Frontend Performance
- **Code Splitting**: Lazy load routes and components
- **Tree Shaking**: Remove unused code with Vite
- **Asset Optimization**: Compress images and fonts
- **Virtual Scrolling**: For large project lists

---

## Future Architecture Evolution

### Phase 1: Current (MVP)
- Read-only monitoring
- Single-user desktop application
- SQLite database
- Basic dashboard

### Phase 2: Enhanced Dashboard (3-6 months)
- Advanced visualizations (Gantt charts, dependency graphs)
- Real-time updates via WebSocket
- Enhanced filtering and search

### Phase 3: Write Operations (6-9 months)
- Task creation and updates via UI
- Requirement management
- Change tracking and audit logs
- Multi-user authentication

### Phase 4: AI Integration (9-12 months)
- AI-powered gap analysis
- Automated task suggestions
- Natural language queries
- Code analysis integration

### Phase 5: Agent Orchestration (12-18 months)
- Multi-agent collaboration
- Automated development workflows
- Agent specialization
- Cost optimization

### Phase 6: Enterprise Features (18+ months)
- Multi-tenant support
- Advanced RBAC
- High availability deployment
- PostgreSQL/microservices migration

---

## Conclusion

ParallelDev's architecture is designed with a clear progression from a simple read-only monitoring tool to a sophisticated AI-powered development orchestration platform. The dual-backend pattern, domain-driven design, and plugin architecture provide the flexibility needed to evolve the system while maintaining stability and performance.

The architecture incorporates modern best practices from 2025 research:
- **Dashboard Design**: Operational dashboard pattern with real-time updates
- **Markdown Parsing**: AST-based parsing with mistletoe
- **File Monitoring**: Debounced watchdog with scalability considerations
- **AI Orchestration**: Multi-agent patterns with Claude Code integration

This foundation supports the ambitious long-term vision of autonomous project management while delivering immediate value through comprehensive project monitoring and analytics.
