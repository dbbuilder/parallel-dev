"""Integration tests for Task CRUD operations."""

import pytest
from datetime import datetime
from pathlib import Path

from backend.database.db_manager import DatabaseManager, init_database


@pytest.fixture
def test_db_path(tmp_path):
    """Provide temporary database path for testing."""
    return tmp_path / "test_task_crud.db"


@pytest.fixture
def db_manager(test_db_path):
    """
    Provide initialized database manager.
    """
    # Initialize database with schema
    init_database(test_db_path)

    # Create manager instance
    manager = DatabaseManager(test_db_path)

    yield manager

    # Cleanup
    manager.close()
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def sample_project(db_manager):
    """Create a sample project for task testing."""
    project_id = db_manager.create_project(
        name="Test Project",
        path="/test/path"
    )
    return project_id


class TestTaskCRUD:
    """Test Task CRUD operations."""

    def test_create_task_minimal(self, db_manager, sample_project):
        """Test creating a task with minimal required fields."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Implement feature X"
        )

        assert task_id is not None
        assert task_id > 0

    def test_create_task_full(self, db_manager, sample_project):
        """Test creating a task with all fields."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Full task description",
            section="Core Services",
            stage="Phase 1",
            priority="high",
            status="in_progress",
            order_number=1,
            line_number=42,
            estimated_effort="2 hours"
        )

        assert task_id is not None
        assert task_id > 0

    def test_create_task_with_parent(self, db_manager, sample_project):
        """Test creating a subtask with parent."""
        # Create parent task
        parent_id = db_manager.create_task(
            project_id=sample_project,
            description="Parent task"
        )

        # Create child task
        child_id = db_manager.create_task(
            project_id=sample_project,
            description="Child task",
            parent_task_id=parent_id
        )

        assert child_id > parent_id

    def test_get_task_by_id(self, db_manager, sample_project):
        """Test retrieving a task by ID."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Test task",
            priority="high",
            status="in_progress"
        )

        task = db_manager.get_task(task_id)

        assert task is not None
        assert task['id'] == task_id
        assert task['description'] == "Test task"
        assert task['project_id'] == sample_project
        assert task['priority'] == "high"
        assert task['status'] == "in_progress"
        assert task['created_at'] is not None

    def test_get_nonexistent_task(self, db_manager):
        """Test retrieving a task that doesn't exist."""
        task = db_manager.get_task(99999)

        assert task is None

    def test_update_task_status(self, db_manager, sample_project):
        """Test updating a task's status."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Test task",
            status="todo"
        )

        result = db_manager.update_task(
            task_id,
            status="done"
        )

        assert result is True

        task = db_manager.get_task(task_id)
        assert task['status'] == "done"
        # completed_at should be set by trigger
        assert task['completed_at'] is not None

    def test_update_task_priority(self, db_manager, sample_project):
        """Test updating a task's priority."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Test task",
            priority="low"
        )

        result = db_manager.update_task(
            task_id,
            priority="critical"
        )

        assert result is True

        task = db_manager.get_task(task_id)
        assert task['priority'] == "critical"

    def test_update_task_multiple_fields(self, db_manager, sample_project):
        """Test updating multiple fields at once."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Original task"
        )

        result = db_manager.update_task(
            task_id,
            description="Updated task",
            status="in_progress",
            priority="high",
            estimated_effort="4 hours"
        )

        assert result is True

        task = db_manager.get_task(task_id)
        assert task['description'] == "Updated task"
        assert task['status'] == "in_progress"
        assert task['priority'] == "high"
        assert task['estimated_effort'] == "4 hours"

    def test_update_nonexistent_task(self, db_manager):
        """Test updating a task that doesn't exist."""
        result = db_manager.update_task(
            99999,
            description="Updated"
        )

        assert result is False

    def test_delete_task(self, db_manager, sample_project):
        """Test deleting a task."""
        task_id = db_manager.create_task(
            project_id=sample_project,
            description="Test task"
        )

        result = db_manager.delete_task(task_id)

        assert result is True

        # Verify task is gone
        task = db_manager.get_task(task_id)
        assert task is None

    def test_delete_nonexistent_task(self, db_manager):
        """Test deleting a task that doesn't exist."""
        result = db_manager.delete_task(99999)

        assert result is False

    def test_list_tasks_empty(self, db_manager):
        """Test listing tasks when none exist."""
        tasks = db_manager.list_tasks()

        assert tasks == []

    def test_list_tasks_all(self, db_manager, sample_project):
        """Test listing all tasks."""
        # Create multiple tasks
        db_manager.create_task(sample_project, description="Task 1")
        db_manager.create_task(sample_project, description="Task 2")
        db_manager.create_task(sample_project, description="Task 3")

        tasks = db_manager.list_tasks()

        assert len(tasks) == 3
        assert all('id' in t for t in tasks)
        assert all('description' in t for t in tasks)

    def test_list_tasks_by_project(self, db_manager, sample_project):
        """Test listing tasks filtered by project."""
        # Create another project
        project2 = db_manager.create_project(name="Project 2", path="/project2")

        # Create tasks in different projects
        db_manager.create_task(sample_project, description="Task 1")
        db_manager.create_task(sample_project, description="Task 2")
        db_manager.create_task(project2, description="Task 3")

        # Filter by project
        project1_tasks = db_manager.list_tasks(project_id=sample_project)
        project2_tasks = db_manager.list_tasks(project_id=project2)

        assert len(project1_tasks) == 2
        assert len(project2_tasks) == 1
        assert all(t['project_id'] == sample_project for t in project1_tasks)
        assert project2_tasks[0]['description'] == "Task 3"

    def test_list_tasks_by_status(self, db_manager, sample_project):
        """Test listing tasks filtered by status."""
        # Create tasks with different statuses
        id1 = db_manager.create_task(sample_project, description="Task 1", status="todo")
        id2 = db_manager.create_task(sample_project, description="Task 2", status="in_progress")
        id3 = db_manager.create_task(sample_project, description="Task 3", status="done")

        # Filter by status
        todo_tasks = db_manager.list_tasks(status="todo")
        in_progress_tasks = db_manager.list_tasks(status="in_progress")
        done_tasks = db_manager.list_tasks(status="done")

        assert len(todo_tasks) == 1
        assert len(in_progress_tasks) == 1
        assert len(done_tasks) == 1
        assert todo_tasks[0]['description'] == "Task 1"
        assert in_progress_tasks[0]['description'] == "Task 2"
        assert done_tasks[0]['description'] == "Task 3"

    def test_list_tasks_by_priority(self, db_manager, sample_project):
        """Test listing tasks filtered by priority."""
        # Create tasks with different priorities
        db_manager.create_task(sample_project, description="Task 1", priority="critical")
        db_manager.create_task(sample_project, description="Task 2", priority="high")
        db_manager.create_task(sample_project, description="Task 3", priority="low")

        # Filter by priority
        critical_tasks = db_manager.list_tasks(priority="critical")
        high_tasks = db_manager.list_tasks(priority="high")

        assert len(critical_tasks) == 1
        assert len(high_tasks) == 1
        assert critical_tasks[0]['description'] == "Task 1"
        assert high_tasks[0]['description'] == "Task 2"

    def test_list_tasks_by_parent_id(self, db_manager, sample_project):
        """Test listing subtasks."""
        # Create parent and children
        parent_id = db_manager.create_task(sample_project, description="Parent")
        db_manager.create_task(sample_project, description="Child 1", parent_task_id=parent_id)
        db_manager.create_task(sample_project, description="Child 2", parent_task_id=parent_id)
        db_manager.create_task(sample_project, description="Other")

        # List children of parent
        children = db_manager.list_tasks(parent_task_id=parent_id)

        assert len(children) == 2
        assert all(t['parent_task_id'] == parent_id for t in children)

    def test_cascade_delete_children(self, db_manager, sample_project):
        """Test that deleting a parent deletes children (CASCADE)."""
        # Create parent and child
        parent_id = db_manager.create_task(sample_project, description="Parent")
        child_id = db_manager.create_task(sample_project, description="Child", parent_task_id=parent_id)

        # Delete parent
        db_manager.delete_task(parent_id)

        # Verify both are gone
        assert db_manager.get_task(parent_id) is None
        assert db_manager.get_task(child_id) is None

    def test_cascade_delete_project_tasks(self, db_manager, sample_project):
        """Test that deleting a project deletes all its tasks."""
        # Create tasks for project
        task1_id = db_manager.create_task(sample_project, description="Task 1")
        task2_id = db_manager.create_task(sample_project, description="Task 2")

        # Delete project
        db_manager.delete_project(sample_project)

        # Verify tasks are gone
        assert db_manager.get_task(task1_id) is None
        assert db_manager.get_task(task2_id) is None

    def test_task_status_check_constraint(self, db_manager, sample_project):
        """Test that task status must be valid enum value."""
        # Valid status should work
        task_id = db_manager.create_task(
            sample_project,
            description="Valid task",
            status="todo"
        )
        assert task_id > 0

        # Invalid status should fail
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            db_manager.create_task(
                sample_project,
                description="Invalid task",
                status="invalid_status"
            )

    def test_task_priority_check_constraint(self, db_manager, sample_project):
        """Test that task priority must be valid enum value."""
        # Valid priorities
        valid_priorities = ['critical', 'high', 'medium', 'low', 'unknown']
        for priority in valid_priorities:
            task_id = db_manager.create_task(
                sample_project,
                description=f"Task {priority}",
                priority=priority
            )
            assert task_id > 0

        # Invalid priority should fail
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            db_manager.create_task(
                sample_project,
                description="Invalid task",
                priority="invalid_priority"
            )
