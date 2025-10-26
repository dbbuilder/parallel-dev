"""Integration tests for Project CRUD operations."""

import pytest
from datetime import datetime
from pathlib import Path

from backend.database.db_manager import DatabaseManager, init_database


@pytest.fixture
def test_db_path(tmp_path):
    """Provide temporary database path for testing."""
    return tmp_path / "test_project_crud.db"


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


class TestProjectCRUD:
    """Test Project CRUD operations."""

    def test_create_project_minimal(self, db_manager):
        """Test creating a project with minimal required fields."""
        project_id = db_manager.create_project(
            name="Test Project",
            path="/test/path"
        )

        assert project_id is not None
        assert project_id > 0

    def test_create_project_full(self, db_manager):
        """Test creating a project with all fields."""
        project_id = db_manager.create_project(
            name="Full Project",
            path="/full/path",
            description="A test project",
            parent_id=None,
            status="not_started",
            requirements_content="# Requirements",
            todo_content="# TODO",
            readme_content="# README"
        )

        assert project_id is not None
        assert project_id > 0

    def test_create_project_with_parent(self, db_manager):
        """Test creating a project with a parent."""
        # Create parent
        parent_id = db_manager.create_project(
            name="Parent Project",
            path="/parent"
        )

        # Create child
        child_id = db_manager.create_project(
            name="Child Project",
            path="/parent/child",
            parent_id=parent_id
        )

        assert child_id > parent_id

    def test_get_project_by_id(self, db_manager):
        """Test retrieving a project by ID."""
        project_id = db_manager.create_project(
            name="Test Project",
            path="/test/path",
            description="Test description"
        )

        project = db_manager.get_project(project_id)

        assert project is not None
        assert project['id'] == project_id
        assert project['name'] == "Test Project"
        assert project['path'] == "/test/path"
        assert project['description'] == "Test description"
        assert project['status'] == "not_started"
        assert project['created_at'] is not None

    def test_get_nonexistent_project(self, db_manager):
        """Test retrieving a project that doesn't exist."""
        project = db_manager.get_project(99999)

        assert project is None

    def test_update_project_name(self, db_manager):
        """Test updating a project's name."""
        project_id = db_manager.create_project(
            name="Original Name",
            path="/test/path"
        )

        result = db_manager.update_project(
            project_id,
            name="Updated Name"
        )

        assert result is True

        project = db_manager.get_project(project_id)
        assert project['name'] == "Updated Name"

    def test_update_project_status(self, db_manager):
        """Test updating a project's status."""
        project_id = db_manager.create_project(
            name="Test Project",
            path="/test/path"
        )

        result = db_manager.update_project(
            project_id,
            status="in_progress"
        )

        assert result is True

        project = db_manager.get_project(project_id)
        assert project['status'] == "in_progress"

    def test_update_project_multiple_fields(self, db_manager):
        """Test updating multiple fields at once."""
        project_id = db_manager.create_project(
            name="Test Project",
            path="/test/path"
        )

        result = db_manager.update_project(
            project_id,
            name="Updated Name",
            description="New description",
            status="in_progress"
        )

        assert result is True

        project = db_manager.get_project(project_id)
        assert project['name'] == "Updated Name"
        assert project['description'] == "New description"
        assert project['status'] == "in_progress"

    def test_update_nonexistent_project(self, db_manager):
        """Test updating a project that doesn't exist."""
        result = db_manager.update_project(
            99999,
            name="Updated Name"
        )

        assert result is False

    def test_delete_project(self, db_manager):
        """Test deleting a project."""
        project_id = db_manager.create_project(
            name="Test Project",
            path="/test/path"
        )

        result = db_manager.delete_project(project_id)

        assert result is True

        # Verify project is gone
        project = db_manager.get_project(project_id)
        assert project is None

    def test_delete_nonexistent_project(self, db_manager):
        """Test deleting a project that doesn't exist."""
        result = db_manager.delete_project(99999)

        assert result is False

    def test_list_projects_empty(self, db_manager):
        """Test listing projects when none exist."""
        projects = db_manager.list_projects()

        assert projects == []

    def test_list_projects_all(self, db_manager):
        """Test listing all projects."""
        # Create multiple projects
        db_manager.create_project(name="Project 1", path="/path1")
        db_manager.create_project(name="Project 2", path="/path2")
        db_manager.create_project(name="Project 3", path="/path3")

        projects = db_manager.list_projects()

        assert len(projects) == 3
        assert all('id' in p for p in projects)
        assert all('name' in p for p in projects)

    def test_list_projects_by_status(self, db_manager):
        """Test listing projects filtered by status."""
        # Create projects with different statuses
        id1 = db_manager.create_project(name="Project 1", path="/path1")
        id2 = db_manager.create_project(name="Project 2", path="/path2")
        id3 = db_manager.create_project(name="Project 3", path="/path3")

        db_manager.update_project(id2, status="in_progress")
        db_manager.update_project(id3, status="completed")

        # Filter by status
        not_started = db_manager.list_projects(status="not_started")
        in_progress = db_manager.list_projects(status="in_progress")
        completed = db_manager.list_projects(status="completed")

        assert len(not_started) == 1
        assert len(in_progress) == 1
        assert len(completed) == 1
        assert not_started[0]['name'] == "Project 1"
        assert in_progress[0]['name'] == "Project 2"
        assert completed[0]['name'] == "Project 3"

    def test_list_projects_by_parent_id(self, db_manager):
        """Test listing child projects."""
        # Create parent and children
        parent_id = db_manager.create_project(name="Parent", path="/parent")
        db_manager.create_project(name="Child 1", path="/parent/child1", parent_id=parent_id)
        db_manager.create_project(name="Child 2", path="/parent/child2", parent_id=parent_id)
        db_manager.create_project(name="Other", path="/other")

        # List children of parent
        children = db_manager.list_projects(parent_id=parent_id)

        assert len(children) == 2
        assert all(p['parent_id'] == parent_id for p in children)

    def test_cascade_delete_children(self, db_manager):
        """Test that deleting a parent deletes children (CASCADE)."""
        # Create parent and child
        parent_id = db_manager.create_project(name="Parent", path="/parent")
        child_id = db_manager.create_project(name="Child", path="/parent/child", parent_id=parent_id)

        # Delete parent
        db_manager.delete_project(parent_id)

        # Verify both are gone
        assert db_manager.get_project(parent_id) is None
        assert db_manager.get_project(child_id) is None

    def test_unique_path_constraint(self, db_manager):
        """Test that project paths must be unique."""
        db_manager.create_project(name="Project 1", path="/test/path")

        # Attempting to create with duplicate path should raise error
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            db_manager.create_project(name="Project 2", path="/test/path")

    def test_get_project_by_path(self, db_manager):
        """Test retrieving a project by path."""
        project_id = db_manager.create_project(
            name="Test Project",
            path="/unique/test/path"
        )

        project = db_manager.get_project_by_path("/unique/test/path")

        assert project is not None
        assert project['id'] == project_id
        assert project['name'] == "Test Project"

    def test_get_project_by_nonexistent_path(self, db_manager):
        """Test retrieving a project by a path that doesn't exist."""
        project = db_manager.get_project_by_path("/nonexistent/path")

        assert project is None
