"""Shared pytest fixtures for all tests."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add src and backend to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_project_structure(temp_dir):
    """Create a sample project directory structure for testing."""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()

    # Create sample markdown files
    (project_dir / "README.md").write_text("""# Test Project

This is a test project for unit testing.

## Technology Stack
- Python 3.11
- Flask
- Vue.js
""")

    (project_dir / "TODO.md").write_text("""# TODO List

## Phase 1: Foundation

### Database Layer
- [ ] High: Create database schema
- [x] Medium: Implement CRUD operations
- [~] Low: Add database migrations

### Testing
- [ ] High: Write unit tests
- [ ] Medium: Write integration tests
""")

    (project_dir / "REQUIREMENTS.md").write_text("""# Requirements

## Functional Requirements
1. MUST: System shall support user authentication
2. SHOULD: System should log all operations
3. COULD: System could support multi-language

## Technical Requirements
1. MUST: Use Python 3.11+
2. SHOULD: Follow PEP 8 guidelines
""")

    return project_dir


@pytest.fixture
def sample_todo_content():
    """Provide sample TODO.md content."""
    return """# Project Tasks

## Phase 1: Setup

### Environment
- [ ] High: Install Python 3.11
- [x] Medium: Create virtual environment
- [~] Low: Configure IDE

## Phase 2: Development

### Backend
- [ ] Critical: Implement authentication
- [ ] High: Create database models
- [ ] Medium: Write API endpoints
"""


@pytest.fixture
def sample_requirements_content():
    """Provide sample REQUIREMENTS.md content."""
    return """# System Requirements

## Functional Requirements

### Core Features
1. MUST: User authentication and authorization
2. MUST: Data persistence with SQLite
3. SHOULD: Real-time updates via WebSocket
4. COULD: Export data to CSV
5. WON'T: Support for IE11

## Technical Requirements

### Performance
1. MUST: Page load time < 3 seconds
2. SHOULD: Support 100+ concurrent users
3. COULD: Support 1000+ concurrent users

### Security
1. MUST: Encrypt sensitive data
2. MUST: Implement CSRF protection
"""


@pytest.fixture
def mock_timestamp(monkeypatch):
    """Provide a consistent timestamp for testing."""
    fixed_time = datetime(2025, 10, 25, 12, 0, 0)

    class MockDatetime:
        @classmethod
        def now(cls):
            return fixed_time

    monkeypatch.setattr("datetime.datetime", MockDatetime)
    return fixed_time
