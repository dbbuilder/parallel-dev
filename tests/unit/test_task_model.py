"""Unit tests for Task model."""

import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus, TaskPriority


class TestTaskCreation:
    """Test suite for Task creation and initialization."""

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
        assert isinstance(task.related_requirement_ids, list)
        assert len(task.related_requirement_ids) == 0

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

        assert task.description == "High priority task"  # Should be trimmed
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.section == "Database Layer"
        assert task.stage == "Phase 1"
        assert task.line_number == 42

    def test_task_description_whitespace_trimming(self):
        """Test that task description whitespace is trimmed."""
        task = Task(description="  \n  Task with whitespace  \n  ")
        assert task.description == "Task with whitespace"

    def test_task_with_empty_description(self):
        """Test task with empty description."""
        task = Task(description="")
        assert task.description == ""

    def test_task_section_default(self):
        """Test section defaults to 'General' when None."""
        task = Task(description="Test", section=None)
        assert task.section == "General"

    def test_task_stage_default(self):
        """Test stage defaults to 'Stage 1' when None."""
        task = Task(description="Test", stage=None)
        assert task.stage == "Stage 1"


class TestTaskStatus:
    """Test suite for TaskStatus enum."""

    def test_task_status_enum_values(self):
        """Test all task status enum values."""
        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.DONE.value == "done"
        assert TaskStatus.BLOCKED.value == "blocked"

    def test_task_status_from_string(self):
        """Test creating TaskStatus from string."""
        assert TaskStatus("todo") == TaskStatus.TODO
        assert TaskStatus("in_progress") == TaskStatus.IN_PROGRESS
        assert TaskStatus("done") == TaskStatus.DONE
        assert TaskStatus("blocked") == TaskStatus.BLOCKED

    def test_all_status_values_unique(self):
        """Test that all status values are unique."""
        values = [status.value for status in TaskStatus]
        assert len(values) == len(set(values))


class TestTaskPriority:
    """Test suite for TaskPriority enum."""

    def test_task_priority_enum_values(self):
        """Test all task priority enum values."""
        assert TaskPriority.CRITICAL.value == "critical"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.UNKNOWN.value == "unknown"

    def test_task_priority_from_string(self):
        """Test creating TaskPriority from string."""
        assert TaskPriority("critical") == TaskPriority.CRITICAL
        assert TaskPriority("high") == TaskPriority.HIGH
        assert TaskPriority("medium") == TaskPriority.MEDIUM
        assert TaskPriority("low") == TaskPriority.LOW
        assert TaskPriority("unknown") == TaskPriority.UNKNOWN

    def test_all_priority_values_unique(self):
        """Test that all priority values are unique."""
        values = [priority.value for priority in TaskPriority]
        assert len(values) == len(set(values))


class TestTaskRelationships:
    """Test suite for task relationships and metadata."""

    def test_task_related_requirements_list(self):
        """Test related requirements list initialization and usage."""
        task = Task("Implement auth")
        assert task.related_requirement_ids == []

        task.related_requirement_ids.append("REQ-001")
        task.related_requirement_ids.append("REQ-002")

        assert len(task.related_requirement_ids) == 2
        assert "REQ-001" in task.related_requirement_ids
        assert "REQ-002" in task.related_requirement_ids

    def test_task_estimated_effort_none_by_default(self):
        """Test estimated effort is None by default."""
        task = Task("Complex task")
        assert task.estimated_effort is None

    def test_task_estimated_effort_can_be_set(self):
        """Test estimated effort can be set."""
        task = Task("Complex task")
        task.estimated_effort = "2 days"
        assert task.estimated_effort == "2 days"

    def test_task_created_at_timestamp(self):
        """Test created_at is a valid datetime."""
        task = Task("Test")
        assert isinstance(task.created_at, datetime)
        assert task.created_at <= datetime.now()


class TestTaskRepresentation:
    """Test suite for task string representation."""

    def test_task_repr_contains_key_info(self):
        """Test task __repr__ contains key information."""
        task = Task(
            "Test task with long description that should be truncated",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )
        repr_str = repr(task)

        assert "Task" in repr_str
        assert "high" in repr_str
        assert "in_progress" in repr_str

    def test_task_repr_for_each_status(self):
        """Test __repr__ for each status type."""
        for status in TaskStatus:
            task = Task("Test", status=status)
            repr_str = repr(task)
            assert status.value in repr_str

    def test_task_repr_for_each_priority(self):
        """Test __repr__ for each priority type."""
        for priority in TaskPriority:
            task = Task("Test", priority=priority)
            repr_str = repr(task)
            assert priority.value in repr_str


class TestTaskSerialization:
    """Test suite for task serialization."""

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            description="Test task",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            section="Testing",
            stage="Phase 1",
            line_number=42
        )
        task.estimated_effort = "1 hour"
        task.related_requirement_ids = ["REQ-001"]

        task_dict = task.to_dict()

        assert task_dict['description'] == "Test task"
        assert task_dict['status'] == "done"
        assert task_dict['priority'] == "high"
        assert task_dict['section'] == "Testing"
        assert task_dict['stage'] == "Phase 1"
        assert task_dict['line_number'] == 42
        assert task_dict['estimated_effort'] == "1 hour"
        assert task_dict['related_requirement_ids'] == ["REQ-001"]
        assert 'created_at' in task_dict

    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        data = {
            'description': 'Test task',
            'status': 'in_progress',
            'priority': 'high',
            'section': 'Testing',
            'stage': 'Phase 1',
            'line_number': 42
        }

        task = Task.from_dict(data)

        assert task.description == "Test task"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.section == "Testing"
        assert task.stage == "Phase 1"
        assert task.line_number == 42

    def test_task_from_dict_with_defaults(self):
        """Test creating task from minimal dictionary."""
        data = {'description': 'Minimal task'}

        task = Task.from_dict(data)

        assert task.description == "Minimal task"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.UNKNOWN

    def test_task_serialization_roundtrip(self):
        """Test task can be serialized and deserialized."""
        original = Task(
            description="Roundtrip test",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.CRITICAL,
            section="Testing",
            stage="Phase 2"
        )

        task_dict = original.to_dict()
        restored = Task.from_dict(task_dict)

        assert restored.description == original.description
        assert restored.status == original.status
        assert restored.priority == original.priority
        assert restored.section == original.section
        assert restored.stage == original.stage
