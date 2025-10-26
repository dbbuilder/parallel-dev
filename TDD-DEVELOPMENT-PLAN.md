# ParallelDev - Comprehensive TDD Development Plan

**Created**: 2025-10-25
**Status**: Ready for Execution
**Approach**: Test-Driven Development with Maximum Autonomy

---

## Executive Summary

This plan implements ParallelDev using **strict Test-Driven Development (TDD)** methodology, enabling autonomous development with high confidence and minimal manual intervention. The plan prioritizes:

1. **Test-First Development**: Write tests before implementation
2. **Incremental Progress**: Small, testable units of work
3. **Continuous Validation**: Every change validated by tests
4. **Autonomous Execution**: Self-contained development cycles
5. **Quality Gates**: Clear success criteria for each phase

---

## Current State Analysis

### What Exists (850 LOC)
- ✅ **Data Models**: Project, Task, Requirement (with enums)
- ✅ **Configuration**: Backend config.py (194 LOC)
- ✅ **Configuration**: Src ConfigManager (217 LOC)
- ✅ **Logging**: logger.py (99 LOC)
- ✅ **Structure**: Directory scaffolding (backend/, src/, frontend/)
- ✅ **Config Files**: config.json with comprehensive settings
- ✅ **Documentation**: README, REQUIREMENTS, TODO, ARCHITECTURE, CLAUDE.md

### What's Missing (Critical Path)
- ❌ **Tests**: Zero test files (0% coverage)
- ❌ **Database**: Schema, migrations, CRUD operations
- ❌ **Parsers**: Markdown parsing logic (TODO.md, REQUIREMENTS.md)
- ❌ **Scanner**: File system scanning service
- ❌ **Metrics**: Progress calculation engine
- ❌ **API**: Flask endpoints
- ❌ **Frontend**: Entire Vue.js application
- ❌ **Integration**: Backend ↔ Frontend communication

### Risk Assessment
- **HIGH RISK**: No tests = brittle codebase
- **MEDIUM RISK**: Dual backend pattern (backend/ + src/) could cause confusion
- **LOW RISK**: Good documentation and clear architecture

---

## TDD Development Strategy

### Core Principles

1. **Red-Green-Refactor Cycle**
   ```
   RED:      Write failing test
   GREEN:    Write minimal code to pass
   REFACTOR: Improve code quality
   REPEAT:   Next test
   ```

2. **Test Pyramid**
   ```
   E2E Tests (10%)      - Full workflows
   Integration (30%)    - Component interactions
   Unit Tests (60%)     - Individual functions
   ```

3. **Test Coverage Requirements**
   - **Minimum**: 80% line coverage
   - **Target**: 90% line coverage
   - **Critical Paths**: 100% coverage (parsers, metrics)

4. **Test Isolation**
   - Each test independent
   - No shared state between tests
   - Use fixtures and mocks liberally

### Testing Tools

```python
# requirements-dev.txt (to be created)
pytest==7.4.3                 # Test framework
pytest-cov==4.1.0             # Coverage reporting
pytest-mock==3.12.0           # Mocking utilities
pytest-asyncio==0.23.2        # Async test support
pytest-xdist==3.5.0           # Parallel test execution
faker==22.0.0                 # Test data generation
freezegun==1.4.0              # Time mocking
responses==0.24.1             # HTTP mocking
```

---

## Phase-by-Phase TDD Implementation

### Phase 0: Test Infrastructure Setup (2-3 hours)

**Goal**: Establish test environment and CI/CD foundation

#### Tasks

**0.1 Environment Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**0.2 Test Directory Structure**
```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_models.py             # Test data models
│   ├── test_config.py             # Test configuration
│   ├── test_parsers.py            # Test markdown parsers
│   ├── test_scanner.py            # Test file scanner
│   └── test_metrics.py            # Test metrics calculator
├── integration/
│   ├── __init__.py
│   ├── test_database.py           # Test DB operations
│   ├── test_api.py                # Test API endpoints
│   └── test_end_to_end.py         # Test complete workflows
├── fixtures/
│   ├── sample_requirements.md     # Sample markdown files
│   ├── sample_todo.md
│   └── sample_readme.md
└── helpers/
    ├── __init__.py
    └── test_utils.py              # Test utilities
```

**0.3 pytest Configuration**
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src
    --cov=backend
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
    -n auto
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow-running tests
    parser: Parser-specific tests
    database: Database tests
```

**0.4 Continuous Integration (GitHub Actions)**
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest
      - uses: codecov/codecov-action@v3
```

**Success Criteria**:
- ✅ Virtual environment created
- ✅ Test directory structure exists
- ✅ `pytest` runs (0 tests, 0 failures)
- ✅ Coverage report generated

---

### Phase 1: Core Data Models (TDD) (4-6 hours)

**Goal**: Validate and extend existing models with comprehensive tests

#### 1.1 Test Task Model

**File**: `tests/unit/test_models.py`

```python
import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus, TaskPriority


class TestTask:
    """Test suite for Task model."""

    def test_task_creation_with_defaults(self):
        """Test creating a task with default values."""
        task = Task(description="Implement feature")

        assert task.description == "Implement feature"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.UNKNOWN
        assert task.section == "General"
        assert task.stage == "Stage 1"
        assert task.line_number == 0
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_custom_values(self):
        """Test creating a task with custom values."""
        task = Task(
            description="  High priority task  ",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            section="Database Layer",
            stage="Phase 1",
            line_number=42
        )

        assert task.description == "High priority task"  # Trimmed
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.section == "Database Layer"
        assert task.stage == "Phase 1"
        assert task.line_number == 42

    def test_task_status_enum_values(self):
        """Test all task status enum values."""
        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.DONE.value == "done"
        assert TaskStatus.BLOCKED.value == "blocked"

    def test_task_priority_enum_values(self):
        """Test all task priority enum values."""
        assert TaskPriority.CRITICAL.value == "critical"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.UNKNOWN.value == "unknown"

    def test_task_repr(self):
        """Test task string representation."""
        task = Task("Test task", priority=TaskPriority.HIGH)
        repr_str = repr(task)

        assert "Task" in repr_str
        assert "high" in repr_str
        assert "todo" in repr_str

    def test_task_related_requirements(self):
        """Test related requirements list."""
        task = Task("Implement auth")
        task.related_requirement_ids.append("REQ-001")
        task.related_requirement_ids.append("REQ-002")

        assert len(task.related_requirement_ids) == 2
        assert "REQ-001" in task.related_requirement_ids

    def test_task_estimated_effort(self):
        """Test estimated effort field."""
        task = Task("Complex task")
        task.estimated_effort = "2 days"

        assert task.estimated_effort == "2 days"
```

**Expected**: Tests PASS (models already implemented)

#### 1.2 Add Missing Model Features

**New Tests** (Red):
```python
def test_task_to_dict(self):
    """Test converting task to dictionary."""
    task = Task(
        description="Test",
        status=TaskStatus.DONE,
        priority=TaskPriority.HIGH
    )

    task_dict = task.to_dict()

    assert task_dict['description'] == "Test"
    assert task_dict['status'] == "done"
    assert task_dict['priority'] == "high"
    assert 'created_at' in task_dict

def test_task_from_dict(self):
    """Test creating task from dictionary."""
    data = {
        'description': 'Test task',
        'status': 'in_progress',
        'priority': 'high',
        'section': 'Testing'
    }

    task = Task.from_dict(data)

    assert task.description == "Test task"
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.priority == TaskPriority.HIGH
```

**Implementation** (Green):
```python
# src/models/task.py

def to_dict(self) -> Dict[str, Any]:
    """Convert task to dictionary for serialization."""
    return {
        'description': self.description,
        'status': self.status.value,
        'priority': self.priority.value,
        'section': self.section,
        'stage': self.stage,
        'line_number': self.line_number,
        'related_requirement_ids': self.related_requirement_ids,
        'estimated_effort': self.estimated_effort,
        'created_at': self.created_at.isoformat()
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Task':
    """Create task from dictionary."""
    return cls(
        description=data['description'],
        status=TaskStatus(data.get('status', 'todo')),
        priority=TaskPriority(data.get('priority', 'unknown')),
        section=data.get('section'),
        stage=data.get('stage'),
        line_number=data.get('line_number', 0)
    )
```

#### 1.3 Repeat for Requirement and Project Models

Similar TDD cycles for:
- `test_requirement.py`
- `test_project.py`

**Time Estimate**: 4-6 hours
**Success Criteria**:
- ✅ 30+ model tests passing
- ✅ 100% model coverage
- ✅ Serialization/deserialization working

---

### Phase 2: Database Layer (TDD) (8-10 hours)

**Goal**: Implement SQLite database with full CRUD operations

#### 2.1 Database Schema (Test-First)

**Test**: `tests/unit/test_database.py`

```python
import pytest
import sqlite3
from pathlib import Path
from backend.database.db_manager import DatabaseManager, init_database


@pytest.fixture
def test_db_path(tmp_path):
    """Provide temporary database path."""
    return tmp_path / "test.db"


@pytest.fixture
def db_manager(test_db_path):
    """Provide initialized database manager."""
    init_database(test_db_path)
    manager = DatabaseManager(test_db_path)
    yield manager
    manager.close()


class TestDatabaseSchema:
    """Test database schema creation."""

    def test_database_initialization(self, test_db_path):
        """Test database file is created."""
        init_database(test_db_path)
        assert test_db_path.exists()

    def test_projects_table_exists(self, db_manager):
        """Test projects table is created."""
        tables = db_manager.get_tables()
        assert 'projects' in tables

    def test_projects_table_schema(self, db_manager):
        """Test projects table has correct columns."""
        columns = db_manager.get_columns('projects')

        assert 'id' in columns
        assert 'name' in columns
        assert 'path' in columns
        assert 'parent_id' in columns
        assert 'has_requirements_file' in columns
        assert 'created_at' in columns

    def test_tasks_table_exists(self, db_manager):
        """Test tasks table is created."""
        tables = db_manager.get_tables()
        assert 'tasks' in tables

    def test_requirements_table_exists(self, db_manager):
        """Test requirements table is created."""
        tables = db_manager.get_tables()
        assert 'requirements' in tables

    def test_metrics_table_exists(self, db_manager):
        """Test metrics table is created."""
        tables = db_manager.get_tables()
        assert 'metrics' in tables

    def test_foreign_key_constraints(self, db_manager):
        """Test foreign key constraints are enabled."""
        assert db_manager.foreign_keys_enabled()
```

**Implementation**: `backend/database/db_manager.py`

```python
"""Database Manager for ParallelDev."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional


def init_database(db_path: str) -> None:
    """
    Initialize database with schema.

    Args:
        db_path: Path to SQLite database file
    """
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r') as f:
        schema = f.read()

    cursor.executescript(schema)
    conn.commit()
    conn.close()


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, db_path: str):
        """Initialize database manager."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def get_tables(self) -> List[str]:
        """Get list of all tables."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_columns(self, table_name: str) -> List[str]:
        """Get list of columns for a table."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]

    def foreign_keys_enabled(self) -> bool:
        """Check if foreign keys are enabled."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        return cursor.fetchone()[0] == 1

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
```

**Schema**: `backend/database/schema.sql`

```sql
-- Projects table
CREATE TABLE IF NOT EXISTS projects (
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

    FOREIGN KEY (parent_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Requirements table
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('MUST', 'SHOULD', 'COULD', 'WONT')),
    category TEXT,
    section TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    status TEXT CHECK(status IN ('todo', 'in_progress', 'done', 'blocked')),
    priority TEXT CHECK(priority IN ('critical', 'high', 'medium', 'low', 'unknown')),
    stage TEXT,
    section TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    in_progress_tasks INTEGER DEFAULT 0,

    total_requirements INTEGER DEFAULT 0,
    completed_requirements INTEGER DEFAULT 0,

    completion_percentage REAL DEFAULT 0.0,
    health_score REAL DEFAULT 0.0,

    orphaned_requirements INTEGER DEFAULT 0,
    orphaned_tasks INTEGER DEFAULT 0,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_parent ON projects(parent_id);
CREATE INDEX IF NOT EXISTS idx_projects_path ON projects(path);
CREATE INDEX IF NOT EXISTS idx_requirements_project ON requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(project_id, status);
CREATE INDEX IF NOT EXISTS idx_metrics_project_time ON metrics(project_id, timestamp DESC);
```

#### 2.2 CRUD Operations (TDD)

**Tests**: Create, Read, Update, Delete for each entity

```python
class TestProjectCRUD:
    """Test project CRUD operations."""

    def test_create_project(self, db_manager):
        """Test creating a new project."""
        project_id = db_manager.create_project(
            name="TestProject",
            path="/path/to/project"
        )

        assert project_id is not None
        assert project_id > 0

    def test_get_project_by_id(self, db_manager):
        """Test retrieving project by ID."""
        project_id = db_manager.create_project(
            name="TestProject",
            path="/path/to/project"
        )

        project = db_manager.get_project(project_id)

        assert project is not None
        assert project['name'] == "TestProject"
        assert project['path'] == "/path/to/project"

    def test_update_project(self, db_manager):
        """Test updating project."""
        project_id = db_manager.create_project(
            name="OldName",
            path="/path"
        )

        db_manager.update_project(project_id, name="NewName")
        project = db_manager.get_project(project_id)

        assert project['name'] == "NewName"

    def test_delete_project(self, db_manager):
        """Test deleting project."""
        project_id = db_manager.create_project(
            name="ToDelete",
            path="/path"
        )

        db_manager.delete_project(project_id)
        project = db_manager.get_project(project_id)

        assert project is None

    def test_list_all_projects(self, db_manager):
        """Test listing all projects."""
        db_manager.create_project("Project1", "/path1")
        db_manager.create_project("Project2", "/path2")

        projects = db_manager.list_projects()

        assert len(projects) >= 2
```

**Time Estimate**: 8-10 hours
**Success Criteria**:
- ✅ 50+ database tests passing
- ✅ Full CRUD for all entities
- ✅ Foreign key constraints working
- ✅ 90%+ database code coverage

---

### Phase 3: Markdown Parsers (TDD) (10-12 hours)

**Goal**: Parse TODO.md and REQUIREMENTS.md with high accuracy

#### 3.1 TODO Parser (TDD)

**Test Fixtures**: `tests/fixtures/sample_todo.md`

```markdown
# Sample TODO

## Phase 1: Foundation

### Database Layer
- [ ] High: Create database schema
- [x] Medium: Implement CRUD operations
- [~] Low: Add database migrations

### Parsing
- [ ] High: Implement TODO parser
- [ ] Medium: Implement REQUIREMENTS parser
```

**Tests**: `tests/unit/test_parsers.py`

```python
import pytest
from pathlib import Path
from src.parsers.todo_parser import TodoParser
from src.models.task import Task, TaskStatus, TaskPriority


@pytest.fixture
def sample_todo_file(tmp_path):
    """Create sample TODO.md file."""
    content = """# Sample TODO

## Phase 1: Foundation

### Database Layer
- [ ] High: Create database schema
- [x] Medium: Implement CRUD operations
- [~] Low: Add database migrations
"""
    file_path = tmp_path / "TODO.md"
    file_path.write_text(content)
    return file_path


class TestTodoParser:
    """Test TODO.md parser."""

    def test_parser_initialization(self):
        """Test parser can be initialized."""
        parser = TodoParser()
        assert parser is not None

    def test_parse_file(self, sample_todo_file):
        """Test parsing TODO file."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        assert len(tasks) == 3

    def test_parse_task_status_not_started(self, sample_todo_file):
        """Test parsing not started tasks."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        not_started = [t for t in tasks if t.status == TaskStatus.TODO]
        assert len(not_started) == 1
        assert "Create database schema" in not_started[0].description

    def test_parse_task_status_completed(self, sample_todo_file):
        """Test parsing completed tasks."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        completed = [t for t in tasks if t.status == TaskStatus.DONE]
        assert len(completed) == 1
        assert "Implement CRUD operations" in completed[0].description

    def test_parse_task_status_in_progress(self, sample_todo_file):
        """Test parsing in-progress tasks."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        assert len(in_progress) == 1
        assert "Add database migrations" in in_progress[0].description

    def test_parse_task_priority(self, sample_todo_file):
        """Test parsing task priority."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        high_priority = [t for t in tasks if t.priority == TaskPriority.HIGH]
        assert len(high_priority) == 1

    def test_parse_task_hierarchy(self, sample_todo_file):
        """Test parsing stage and section hierarchy."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        for task in tasks:
            assert task.stage == "Phase 1: Foundation"
            assert task.section == "Database Layer"

    def test_parse_line_numbers(self, sample_todo_file):
        """Test line number tracking."""
        parser = TodoParser()
        tasks = parser.parse_file(sample_todo_file)

        for task in tasks:
            assert task.line_number > 0
```

**Implementation**: Use **mistletoe** (AST-based parsing)

```python
# src/parsers/todo_parser.py

"""TODO.md Parser using AST approach."""

import re
from pathlib import Path
from typing import List
import mistletoe
from mistletoe.ast_renderer import ASTRenderer

from src.models.task import Task, TaskStatus, TaskPriority


class TodoParser:
    """Parse TODO.md files into Task objects."""

    STATUS_MARKERS = {
        '[ ]': TaskStatus.TODO,
        '[x]': TaskStatus.DONE,
        '[~]': TaskStatus.IN_PROGRESS,
    }

    PRIORITY_PATTERN = re.compile(r'\b(Critical|High|Medium|Low)\b:', re.IGNORECASE)

    def parse_file(self, file_path: Path) -> List[Task]:
        """
        Parse TODO.md file and extract tasks.

        Args:
            file_path: Path to TODO.md file

        Returns:
            List of Task objects
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse(content)

    def parse(self, content: str) -> List[Task]:
        """Parse markdown content into tasks."""
        # Parse to AST
        doc = mistletoe.Document(content)

        tasks = []
        current_stage = None
        current_section = None

        # Traverse AST
        for child in doc.children:
            if isinstance(child, mistletoe.block_token.Heading):
                if child.level == 2:
                    current_stage = self._extract_text(child)
                elif child.level == 3:
                    current_section = self._extract_text(child)

            elif isinstance(child, mistletoe.block_token.List):
                for item in child.children:
                    task = self._parse_list_item(
                        item,
                        current_stage,
                        current_section
                    )
                    if task:
                        tasks.append(task)

        return tasks

    def _parse_list_item(self, item, stage, section) -> Optional[Task]:
        """Parse a list item into a Task."""
        text = self._extract_text(item)

        # Extract status
        status = TaskStatus.TODO
        for marker, status_value in self.STATUS_MARKERS.items():
            if text.startswith(marker):
                status = status_value
                text = text[len(marker):].strip()
                break

        # Extract priority
        priority = TaskPriority.UNKNOWN
        match = self.PRIORITY_PATTERN.search(text)
        if match:
            priority_str = match.group(1).upper()
            priority = TaskPriority[priority_str]
            # Remove priority from description
            text = self.PRIORITY_PATTERN.sub('', text, count=1).strip()

        return Task(
            description=text,
            status=status,
            priority=priority,
            stage=stage,
            section=section
        )

    def _extract_text(self, node) -> str:
        """Extract text from AST node."""
        # Simplified - full implementation would recursively extract text
        if hasattr(node, 'children'):
            return ''.join(self._extract_text(child) for child in node.children)
        elif hasattr(node, 'content'):
            return node.content
        return ''
```

#### 3.2 Requirements Parser (TDD)

Similar approach for REQUIREMENTS.md with MoSCoW parsing.

**Time Estimate**: 10-12 hours
**Success Criteria**:
- ✅ 40+ parser tests passing
- ✅ Accurate task/requirement extraction
- ✅ Proper hierarchy parsing
- ✅ 95%+ parser coverage

---

### Phase 4: File Scanner (TDD) (6-8 hours)

**Goal**: Recursively scan directories and discover projects

#### 4.1 Scanner Tests

```python
class TestProjectScanner:
    """Test project scanner."""

    def test_scan_single_project(self, tmp_path):
        """Test scanning a single project."""
        # Create project structure
        project_dir = tmp_path / "project1"
        project_dir.mkdir()
        (project_dir / "README.md").write_text("# Project")

        scanner = ProjectScanner(tmp_path)
        projects = scanner.scan()

        assert len(projects) == 1
        assert projects[0].name == "project1"

    def test_scan_nested_projects(self, tmp_path):
        """Test scanning nested projects."""
        # Create nested structure
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "README.md").write_text("# Parent")

        child = parent / "child"
        child.mkdir()
        (child / "TODO.md").write_text("# Child Tasks")

        scanner = ProjectScanner(tmp_path)
        projects = scanner.scan()

        assert len(projects) == 2

    def test_ignore_directories(self, tmp_path):
        """Test ignoring node_modules, .git, etc."""
        # Create ignored directory
        ignored = tmp_path / "node_modules"
        ignored.mkdir()
        (ignored / "README.md").write_text("# Should ignore")

        scanner = ProjectScanner(tmp_path)
        projects = scanner.scan()

        assert len(projects) == 0
```

**Time Estimate**: 6-8 hours
**Success Criteria**:
- ✅ 25+ scanner tests passing
- ✅ Recursive scanning works
- ✅ Ignore list respected
- ✅ 90%+ scanner coverage

---

### Phase 5: Metrics Calculator (TDD) (6-8 hours)

**Goal**: Calculate completion percentages, health scores, gaps

```python
class TestMetricsCalculator:
    """Test metrics calculator."""

    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        project = Project(path="/test")
        project.tasks = [
            Task("Task 1", status=TaskStatus.DONE),
            Task("Task 2", status=TaskStatus.DONE),
            Task("Task 3", status=TaskStatus.TODO),
            Task("Task 4", status=TaskStatus.TODO),
        ]

        calculator = MetricsCalculator()
        percentage = calculator.calculate_completion(project)

        assert percentage == 50.0

    def test_health_score(self):
        """Test health score calculation."""
        project = create_test_project()  # Fixture

        calculator = MetricsCalculator()
        health = calculator.calculate_health_score(project)

        assert 0.0 <= health <= 1.0

    def test_gap_detection(self):
        """Test orphaned requirement detection."""
        project = Project(path="/test")
        project.requirements = [
            Requirement("Req 1"),
            Requirement("Req 2"),
        ]
        project.tasks = [
            Task("Task 1"),  # No link to requirements
        ]

        calculator = MetricsCalculator()
        gaps = calculator.detect_gaps(project)

        assert gaps['orphaned_requirements'] == 2
        assert gaps['orphaned_tasks'] == 1
```

**Time Estimate**: 6-8 hours
**Success Criteria**:
- ✅ 30+ metrics tests passing
- ✅ Accurate calculations
- ✅ Gap detection working
- ✅ 95%+ metrics coverage

---

### Phase 6: Flask API (TDD) (10-12 hours)

**Goal**: RESTful API with full endpoint coverage

#### 6.1 API Tests

```python
import pytest
from flask import Flask
from backend.api import create_app


@pytest.fixture
def client():
    """Provide Flask test client."""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


class TestProjectsAPI:
    """Test /api/projects endpoints."""

    def test_get_all_projects(self, client):
        """Test GET /api/projects."""
        response = client.get('/api/projects')

        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'data' in data

    def test_get_project_by_id(self, client):
        """Test GET /api/projects/<id>."""
        # Create test project first
        project_id = create_test_project()

        response = client.get(f'/api/projects/{project_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['project']['id'] == project_id

    def test_get_nonexistent_project(self, client):
        """Test GET /api/projects/999."""
        response = client.get('/api/projects/999')

        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'

    def test_trigger_scan(self, client):
        """Test POST /api/scan."""
        response = client.post('/api/scan')

        assert response.status_code == 200
```

**Time Estimate**: 10-12 hours
**Success Criteria**:
- ✅ 40+ API tests passing
- ✅ All endpoints tested
- ✅ Error handling tested
- ✅ 90%+ API coverage

---

### Phase 7: Frontend (TDD with Vue Test Utils) (20-24 hours)

**Goal**: Complete Vue.js dashboard with component tests

#### 7.1 Component Tests

```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ProjectTree from '@/components/ProjectTree.vue'


describe('ProjectTree', () => {
  it('renders project tree', () => {
    const wrapper = mount(ProjectTree, {
      props: {
        projects: [
          { id: 1, name: 'Project 1', completion: 50 }
        ]
      }
    })

    expect(wrapper.text()).toContain('Project 1')
  })

  it('emits select event on click', async () => {
    const wrapper = mount(ProjectTree, {
      props: { projects: [{ id: 1, name: 'Test' }] }
    })

    await wrapper.find('.project-node').trigger('click')

    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0]).toEqual([1])
  })

  it('shows correct status color', () => {
    const wrapper = mount(ProjectTree, {
      props: {
        projects: [
          { id: 1, name: 'Done', completion: 100 }
        ]
      }
    })

    expect(wrapper.find('.status-indicator').classes()).toContain('status-completed')
  })
})
```

**Time Estimate**: 20-24 hours
**Success Criteria**:
- ✅ 60+ component tests passing
- ✅ All components tested
- ✅ E2E tests passing
- ✅ 80%+ frontend coverage

---

## Autonomous Execution Strategy

### Self-Validation Checkpoints

After each phase:

1. **Run Tests**: `pytest -v`
2. **Check Coverage**: `pytest --cov`
3. **Validate Quality**: All tests green + coverage > 80%
4. **Commit**: Git commit with descriptive message
5. **Proceed**: Move to next phase

### Automated Quality Gates

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest --cov --cov-fail-under=80
if [ $? -ne 0 ]; then
    echo "Tests failed or coverage below 80%"
    exit 1
fi
```

### Progress Tracking

Use TodoWrite tool to track:
- Current phase
- Tests written vs passing
- Coverage percentage
- Blockers/issues

---

## Success Metrics

### Overall Goals

- **Test Count**: 300+ tests total
- **Coverage**: 90%+ overall
- **Critical Path Coverage**: 100% (parsers, metrics, database)
- **Zero Manual Testing**: All validation automated
- **CI/CD Green**: All builds passing

### Phase Completion Criteria

Each phase complete when:
- ✅ All tests passing
- ✅ Coverage requirements met
- ✅ Code reviewed (self-review against architecture)
- ✅ Documentation updated
- ✅ Git committed

---

## Estimated Timeline

| Phase | Hours | Days (8h/day) |
|-------|-------|---------------|
| 0. Test Infrastructure | 3 | 0.5 |
| 1. Core Models | 6 | 0.75 |
| 2. Database Layer | 10 | 1.25 |
| 3. Parsers | 12 | 1.5 |
| 4. Scanner | 8 | 1.0 |
| 5. Metrics | 8 | 1.0 |
| 6. Flask API | 12 | 1.5 |
| 7. Frontend | 24 | 3.0 |
| **Total** | **83** | **10.5** |

**Buffer**: +20% = **~13 days total**

---

## Risk Mitigation

### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tests fail unexpectedly | Medium | High | Incremental commits, frequent validation |
| Parser edge cases | High | Medium | Comprehensive test fixtures, real-world samples |
| Frontend complexity | High | High | Start with simple components, iterate |
| Integration issues | Medium | High | Integration tests at each phase boundary |

---

## Next Immediate Actions

1. **Create `requirements-dev.txt`**
2. **Set up virtual environment**
3. **Create test directory structure**
4. **Write first test** (test_task.py)
5. **Watch it pass** (models already implemented)
6. **Begin Phase 1** (add serialization)

---

## Conclusion

This TDD plan provides:
- **Clear roadmap**: Phase-by-phase progression
- **Autonomous execution**: Self-validating checkpoints
- **High confidence**: Tests before code
- **Quality assurance**: Coverage requirements
- **Measurable progress**: Test count, coverage metrics

**Ready to execute autonomously with minimal supervision.**
