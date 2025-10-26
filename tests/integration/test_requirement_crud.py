"""Integration tests for Requirement CRUD operations."""

import pytest
from datetime import datetime
from pathlib import Path

from backend.database.db_manager import DatabaseManager, init_database


@pytest.fixture
def test_db_path(tmp_path):
    """Provide temporary database path for testing."""
    return tmp_path / "test_requirement_crud.db"


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
    """Create a sample project for requirement testing."""
    project_id = db_manager.create_project(
        name="Test Project",
        path="/test/path"
    )
    return project_id


class TestRequirementCRUD:
    """Test Requirement CRUD operations."""

    def test_create_requirement_minimal(self, db_manager, sample_project):
        """Test creating a requirement with minimal required fields."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="System must support user authentication"
        )

        assert req_id is not None
        assert req_id > 0

    def test_create_requirement_full(self, db_manager, sample_project):
        """Test creating a requirement with all fields."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="Full requirement description",
            category="Functional Requirements",
            priority="critical",
            status="in_progress",
            requirement_number=1,
            line_number=42
        )

        assert req_id is not None
        assert req_id > 0

    def test_get_requirement_by_id(self, db_manager, sample_project):
        """Test retrieving a requirement by ID."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="Test requirement",
            priority="high",
            status="planned"
        )

        requirement = db_manager.get_requirement(req_id)

        assert requirement is not None
        assert requirement['id'] == req_id
        assert requirement['description'] == "Test requirement"
        assert requirement['project_id'] == sample_project
        assert requirement['priority'] == "high"
        assert requirement['status'] == "planned"
        assert requirement['created_at'] is not None

    def test_get_nonexistent_requirement(self, db_manager):
        """Test retrieving a requirement that doesn't exist."""
        requirement = db_manager.get_requirement(99999)

        assert requirement is None

    def test_update_requirement_status(self, db_manager, sample_project):
        """Test updating a requirement's status."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="Test requirement",
            status="planned"
        )

        result = db_manager.update_requirement(
            req_id,
            status="completed"
        )

        assert result is True

        requirement = db_manager.get_requirement(req_id)
        assert requirement['status'] == "completed"

    def test_update_requirement_priority(self, db_manager, sample_project):
        """Test updating a requirement's priority."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="Test requirement",
            priority="low"
        )

        result = db_manager.update_requirement(
            req_id,
            priority="critical"
        )

        assert result is True

        requirement = db_manager.get_requirement(req_id)
        assert requirement['priority'] == "critical"

    def test_update_requirement_multiple_fields(self, db_manager, sample_project):
        """Test updating multiple fields at once."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="Original requirement"
        )

        result = db_manager.update_requirement(
            req_id,
            description="Updated requirement",
            status="in_progress",
            priority="high",
            category="Technical Requirements"
        )

        assert result is True

        requirement = db_manager.get_requirement(req_id)
        assert requirement['description'] == "Updated requirement"
        assert requirement['status'] == "in_progress"
        assert requirement['priority'] == "high"
        assert requirement['category'] == "Technical Requirements"

    def test_update_nonexistent_requirement(self, db_manager):
        """Test updating a requirement that doesn't exist."""
        result = db_manager.update_requirement(
            99999,
            description="Updated"
        )

        assert result is False

    def test_delete_requirement(self, db_manager, sample_project):
        """Test deleting a requirement."""
        req_id = db_manager.create_requirement(
            project_id=sample_project,
            description="Test requirement"
        )

        result = db_manager.delete_requirement(req_id)

        assert result is True

        # Verify requirement is gone
        requirement = db_manager.get_requirement(req_id)
        assert requirement is None

    def test_delete_nonexistent_requirement(self, db_manager):
        """Test deleting a requirement that doesn't exist."""
        result = db_manager.delete_requirement(99999)

        assert result is False

    def test_list_requirements_empty(self, db_manager):
        """Test listing requirements when none exist."""
        requirements = db_manager.list_requirements()

        assert requirements == []

    def test_list_requirements_all(self, db_manager, sample_project):
        """Test listing all requirements."""
        # Create multiple requirements
        db_manager.create_requirement(sample_project, description="Req 1")
        db_manager.create_requirement(sample_project, description="Req 2")
        db_manager.create_requirement(sample_project, description="Req 3")

        requirements = db_manager.list_requirements()

        assert len(requirements) == 3
        assert all('id' in r for r in requirements)
        assert all('description' in r for r in requirements)

    def test_list_requirements_by_project(self, db_manager, sample_project):
        """Test listing requirements filtered by project."""
        # Create another project
        project2 = db_manager.create_project(name="Project 2", path="/project2")

        # Create requirements in different projects
        db_manager.create_requirement(sample_project, description="Req 1")
        db_manager.create_requirement(sample_project, description="Req 2")
        db_manager.create_requirement(project2, description="Req 3")

        # Filter by project
        project1_reqs = db_manager.list_requirements(project_id=sample_project)
        project2_reqs = db_manager.list_requirements(project_id=project2)

        assert len(project1_reqs) == 2
        assert len(project2_reqs) == 1
        assert all(r['project_id'] == sample_project for r in project1_reqs)
        assert project2_reqs[0]['description'] == "Req 3"

    def test_list_requirements_by_status(self, db_manager, sample_project):
        """Test listing requirements filtered by status."""
        # Create requirements with different statuses
        id1 = db_manager.create_requirement(sample_project, description="Req 1", status="planned")
        id2 = db_manager.create_requirement(sample_project, description="Req 2", status="in_progress")
        id3 = db_manager.create_requirement(sample_project, description="Req 3", status="completed")

        # Filter by status
        planned_reqs = db_manager.list_requirements(status="planned")
        in_progress_reqs = db_manager.list_requirements(status="in_progress")
        completed_reqs = db_manager.list_requirements(status="completed")

        assert len(planned_reqs) == 1
        assert len(in_progress_reqs) == 1
        assert len(completed_reqs) == 1
        assert planned_reqs[0]['description'] == "Req 1"
        assert in_progress_reqs[0]['description'] == "Req 2"
        assert completed_reqs[0]['description'] == "Req 3"

    def test_list_requirements_by_priority(self, db_manager, sample_project):
        """Test listing requirements filtered by priority."""
        # Create requirements with different priorities
        db_manager.create_requirement(sample_project, description="Req 1", priority="critical")
        db_manager.create_requirement(sample_project, description="Req 2", priority="high")
        db_manager.create_requirement(sample_project, description="Req 3", priority="low")

        # Filter by priority
        critical_reqs = db_manager.list_requirements(priority="critical")
        high_reqs = db_manager.list_requirements(priority="high")

        assert len(critical_reqs) == 1
        assert len(high_reqs) == 1
        assert critical_reqs[0]['description'] == "Req 1"
        assert high_reqs[0]['description'] == "Req 2"

    def test_list_requirements_by_category(self, db_manager, sample_project):
        """Test listing requirements filtered by category."""
        # Create requirements with different categories
        db_manager.create_requirement(sample_project, description="Req 1", category="Functional Requirements")
        db_manager.create_requirement(sample_project, description="Req 2", category="Technical Requirements")
        db_manager.create_requirement(sample_project, description="Req 3", category="Functional Requirements")

        # Filter by category
        functional_reqs = db_manager.list_requirements(category="Functional Requirements")
        technical_reqs = db_manager.list_requirements(category="Technical Requirements")

        assert len(functional_reqs) == 2
        assert len(technical_reqs) == 1
        assert all(r['category'] == "Functional Requirements" for r in functional_reqs)
        assert technical_reqs[0]['description'] == "Req 2"

    def test_cascade_delete_project_requirements(self, db_manager, sample_project):
        """Test that deleting a project deletes all its requirements."""
        # Create requirements for project
        req1_id = db_manager.create_requirement(sample_project, description="Req 1")
        req2_id = db_manager.create_requirement(sample_project, description="Req 2")

        # Delete project
        db_manager.delete_project(sample_project)

        # Verify requirements are gone
        assert db_manager.get_requirement(req1_id) is None
        assert db_manager.get_requirement(req2_id) is None

    def test_requirement_priority_check_constraint(self, db_manager, sample_project):
        """Test that requirement priority must be valid enum value."""
        # Valid priorities
        valid_priorities = ['critical', 'high', 'medium', 'low', 'unknown']
        for priority in valid_priorities:
            req_id = db_manager.create_requirement(
                sample_project,
                description=f"Req {priority}",
                priority=priority
            )
            assert req_id > 0

        # Invalid priority should fail
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            db_manager.create_requirement(
                sample_project,
                description="Invalid requirement",
                priority="invalid_priority"
            )

    def test_requirement_status_check_constraint(self, db_manager, sample_project):
        """Test that requirement status must be valid enum value."""
        # Valid statuses
        valid_statuses = ['planned', 'in_progress', 'completed', 'blocked']
        for status in valid_statuses:
            req_id = db_manager.create_requirement(
                sample_project,
                description=f"Req {status}",
                status=status
            )
            assert req_id > 0

        # Invalid status should fail
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            db_manager.create_requirement(
                sample_project,
                description="Invalid requirement",
                status="invalid_status"
            )
