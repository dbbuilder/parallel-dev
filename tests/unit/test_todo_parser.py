"""Unit tests for TODO.md parser."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.parsers.todo_parser import TodoParser
from src.models.task import Task, TaskStatus, TaskPriority


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_todo_file(temp_dir):
    """Create sample TODO.md file."""
    todo_path = temp_dir / "TODO.md"
    content = """# Project TODO

## Phase 1: Setup

### Database
- [ ] High: Create database schema
- [x] Medium: Implement connection pooling
- [~] Low: Add query logging

### Models
- [x] Critical: Create base models
- [ ] High: Add validation methods
"""
    todo_path.write_text(content, encoding='utf-8')
    return todo_path


class TestTodoParser:
    """Test TodoParser class."""

    def test_parser_initialization(self):
        """Test that parser can be instantiated."""
        parser = TodoParser()
        assert parser is not None

    def test_parse_empty_file(self, temp_dir):
        """Test parsing an empty file."""
        empty_file = temp_dir / "empty.md"
        empty_file.write_text("", encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(empty_file)

        assert tasks == []

    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error."""
        parser = TodoParser()

        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.md")

    def test_parse_simple_todo_item(self, temp_dir):
        """Test parsing a single todo item."""
        todo_file = temp_dir / "simple.md"
        todo_file.write_text("- [ ] Implement feature X", encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 1
        assert tasks[0].description == "Implement feature X"
        assert tasks[0].status == TaskStatus.TODO

    def test_parse_completed_task(self, temp_dir):
        """Test parsing completed task with [x]."""
        todo_file = temp_dir / "completed.md"
        todo_file.write_text("- [x] Completed task", encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 1
        assert tasks[0].status == TaskStatus.DONE

    def test_parse_in_progress_task(self, temp_dir):
        """Test parsing in-progress task with [~]."""
        todo_file = temp_dir / "in_progress.md"
        todo_file.write_text("- [~] Work in progress", encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 1
        assert tasks[0].status == TaskStatus.IN_PROGRESS

    def test_parse_task_with_priority(self, temp_dir):
        """Test parsing task with priority prefix."""
        todo_file = temp_dir / "priority.md"
        todo_file.write_text("- [ ] High: Important task", encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 1
        assert tasks[0].priority == TaskPriority.HIGH
        assert tasks[0].description == "Important task"

    def test_parse_all_priority_levels(self, temp_dir):
        """Test parsing all priority levels."""
        todo_file = temp_dir / "priorities.md"
        content = """
- [ ] Critical: Urgent task
- [ ] High: Important task
- [ ] Medium: Normal task
- [ ] Low: Nice to have
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 4
        assert tasks[0].priority == TaskPriority.CRITICAL
        assert tasks[1].priority == TaskPriority.HIGH
        assert tasks[2].priority == TaskPriority.MEDIUM
        assert tasks[3].priority == TaskPriority.LOW

    def test_parse_task_without_priority(self, temp_dir):
        """Test that task without priority gets UNKNOWN."""
        todo_file = temp_dir / "no_priority.md"
        todo_file.write_text("- [ ] Task without priority", encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 1
        assert tasks[0].priority == TaskPriority.UNKNOWN

    def test_parse_with_stage_header(self, temp_dir):
        """Test parsing tasks under stage headers (##)."""
        todo_file = temp_dir / "stages.md"
        content = """
## Phase 1: Setup
- [ ] Task 1

## Phase 2: Development
- [ ] Task 2
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 2
        assert tasks[0].stage == "Phase 1: Setup"
        assert tasks[0].description == "Task 1"
        assert tasks[1].stage == "Phase 2: Development"
        assert tasks[1].description == "Task 2"

    def test_parse_with_section_header(self, temp_dir):
        """Test parsing tasks under section headers (###)."""
        todo_file = temp_dir / "sections.md"
        content = """
## Phase 1
### Database
- [ ] Task 1

### API
- [ ] Task 2
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 2
        assert tasks[0].section == "Database"
        assert tasks[0].stage == "Phase 1"
        assert tasks[1].section == "API"
        assert tasks[1].stage == "Phase 1"

    def test_parse_line_numbers(self, temp_dir):
        """Test that line numbers are captured."""
        todo_file = temp_dir / "line_numbers.md"
        content = """# Header

- [ ] Task on line 3
- [ ] Task on line 4
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 2
        assert tasks[0].line_number == 3
        assert tasks[1].line_number == 4

    def test_parse_ignore_non_task_lines(self, temp_dir):
        """Test that non-task lines are ignored."""
        todo_file = temp_dir / "mixed.md"
        content = """# TODO

Some paragraph text.

- [ ] Actual task
- Not a checkbox item
* [ ] Different bullet style

1. Numbered list
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        # Should only parse the one valid checkbox task
        assert len(tasks) == 1
        assert tasks[0].description == "Actual task"

    def test_parse_sample_fixture_file(self):
        """Test parsing the actual sample_todo.md fixture."""
        fixture_path = Path("tests/fixtures/sample_todo.md")

        parser = TodoParser()
        tasks = parser.parse(fixture_path)

        # Verify we got tasks
        assert len(tasks) > 0

        # Check for specific tasks
        descriptions = [t.description for t in tasks]
        assert "Create database schema SQL file" in descriptions
        assert "Implement db_manager.py with connection management" in descriptions

        # Check status mix
        statuses = [t.status for t in tasks]
        assert TaskStatus.TODO in statuses
        assert TaskStatus.DONE in statuses
        assert TaskStatus.IN_PROGRESS in statuses

    def test_parse_multiple_stages_and_sections(self, sample_todo_file):
        """Test parsing file with multiple stages and sections."""
        parser = TodoParser()
        tasks = parser.parse(sample_todo_file)

        assert len(tasks) > 0

        # Check that stages are assigned
        stages = {t.stage for t in tasks}
        assert "Phase 1: Setup" in stages

        # Check that sections are assigned
        sections = {t.section for t in tasks}
        assert "Database" in sections
        assert "Models" in sections

    def test_parse_returns_task_objects(self, sample_todo_file):
        """Test that parser returns Task model instances."""
        parser = TodoParser()
        tasks = parser.parse(sample_todo_file)

        assert len(tasks) > 0
        assert all(isinstance(task, Task) for task in tasks)

    def test_whitespace_handling(self, temp_dir):
        """Test that extra whitespace is handled correctly."""
        todo_file = temp_dir / "whitespace.md"
        content = """
-  [x]  High:   Task with extra spaces

-[ ] Medium:No space after dash
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 2
        # Whitespace should be trimmed
        assert tasks[0].description == "Task with extra spaces"
        assert tasks[0].priority == TaskPriority.HIGH

    def test_case_insensitive_priority(self, temp_dir):
        """Test that priority matching is case-insensitive."""
        todo_file = temp_dir / "case.md"
        content = """
- [ ] HIGH: Uppercase priority
- [ ] high: Lowercase priority
- [ ] High: Mixed case priority
"""
        todo_file.write_text(content, encoding='utf-8')

        parser = TodoParser()
        tasks = parser.parse(todo_file)

        assert len(tasks) == 3
        assert all(t.priority == TaskPriority.HIGH for t in tasks)
