"""Integration tests for database operations."""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

# Database will be implemented in backend.database.db_manager
from backend.database.db_manager import DatabaseManager, init_database


@pytest.fixture
def test_db_path(tmp_path):
    """Provide temporary database path for testing."""
    return tmp_path / "test_paralleldev.db"


@pytest.fixture
def db_manager(test_db_path):
    """
    Provide initialized database manager.

    This fixture:
    1. Creates a temporary database
    2. Initializes schema
    3. Returns manager instance
    4. Cleans up after test
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


class TestDatabaseInitialization:
    """Test database initialization and schema creation."""

    def test_database_file_created(self, test_db_path):
        """Test that database file is created."""
        init_database(test_db_path)
        assert test_db_path.exists()
        assert test_db_path.is_file()

    def test_database_connection(self, test_db_path):
        """Test that database can be connected to."""
        init_database(test_db_path)
        conn = sqlite3.connect(test_db_path)
        assert conn is not None
        conn.close()

    def test_foreign_keys_enabled(self, db_manager):
        """Test that foreign keys are enabled."""
        assert db_manager.foreign_keys_enabled() == True

    def test_all_tables_created(self, db_manager):
        """Test that all required tables are created."""
        tables = db_manager.get_tables()

        required_tables = [
            'projects',
            'requirements',
            'tasks',
            'metrics',
            'scan_history',
            'file_changes',
            'ai_agent_sessions',
            'configuration',
            'schema_version'
        ]

        for table in required_tables:
            assert table in tables, f"Table '{table}' not found in database"

    def test_all_views_created(self, db_manager):
        """Test that all views are created."""
        views = db_manager.get_views()

        required_views = [
            'vw_project_summary',
            'vw_recent_metrics'
        ]

        for view in required_views:
            assert view in views, f"View '{view}' not found in database"

    def test_all_indexes_created(self, db_manager):
        """Test that indexes are created."""
        indexes = db_manager.get_indexes()

        # Sample of important indexes
        assert 'idx_projects_parent_id' in indexes
        assert 'idx_projects_path' in indexes
        assert 'idx_tasks_project_id' in indexes
        assert 'idx_requirements_project_id' in indexes

    def test_configuration_defaults_inserted(self, db_manager):
        """Test that default configuration is inserted."""
        config = db_manager.get_all_configuration()

        assert len(config) >= 4
        assert any(c['key'] == 'scan_interval_seconds' for c in config)
        assert any(c['key'] == 'file_watch_enabled' for c in config)
        assert any(c['key'] == 'metrics_history_days' for c in config)
        assert any(c['key'] == 'ai_enabled' for c in config)

    def test_schema_version_recorded(self, db_manager):
        """Test that schema version is recorded."""
        version = db_manager.get_schema_version()
        assert version == 1


class TestDatabaseManager:
    """Test DatabaseManager utility methods."""

    def test_get_tables(self, db_manager):
        """Test getting list of tables."""
        tables = db_manager.get_tables()
        assert isinstance(tables, list)
        assert len(tables) > 0
        assert 'projects' in tables

    def test_get_views(self, db_manager):
        """Test getting list of views."""
        views = db_manager.get_views()
        assert isinstance(views, list)
        assert 'vw_project_summary' in views

    def test_get_indexes(self, db_manager):
        """Test getting list of indexes."""
        indexes = db_manager.get_indexes()
        assert isinstance(indexes, list)
        assert len(indexes) > 0

    def test_get_columns_for_table(self, db_manager):
        """Test getting columns for a specific table."""
        columns = db_manager.get_columns('projects')

        assert 'id' in columns
        assert 'path' in columns
        assert 'name' in columns
        assert 'parent_id' in columns
        assert 'created_at' in columns

    def test_table_exists(self, db_manager):
        """Test checking if table exists."""
        assert db_manager.table_exists('projects') == True
        assert db_manager.table_exists('nonexistent_table') == False

    def test_execute_query(self, db_manager):
        """Test executing raw SQL query."""
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM projects")
        assert result is not None
        assert len(result) == 1
        assert 'count' in result[0]

    def test_execute_many(self, db_manager):
        """Test batch insert operations."""
        # This will be used for bulk operations
        data = [
            ("Test1", "/path/1"),
            ("Test2", "/path/2"),
        ]

        count = db_manager.execute_many(
            "INSERT INTO projects (name, path) VALUES (?, ?)",
            data
        )

        assert count == 2


class TestProjectsTable:
    """Test projects table structure and constraints."""

    def test_projects_table_columns(self, db_manager):
        """Test that projects table has correct columns."""
        columns = db_manager.get_columns('projects')

        expected_columns = [
            'id', 'path', 'name', 'parent_id', 'description',
            'requirements_content', 'todo_content', 'readme_content',
            'status', 'created_at', 'last_scanned', 'last_modified'
        ]

        for col in expected_columns:
            assert col in columns, f"Column '{col}' missing from projects table"

    def test_projects_unique_path_constraint(self, db_manager):
        """Test that path must be unique."""
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test', '/test/path')"
        )

        # Attempting to insert duplicate path should fail
        with pytest.raises(sqlite3.IntegrityError):
            db_manager.execute_query(
                "INSERT INTO projects (name, path) VALUES ('Test2', '/test/path')"
            )

    def test_projects_foreign_key_constraint(self, db_manager):
        """Test foreign key constraint on parent_id."""
        # Attempting to insert with invalid parent_id should fail
        with pytest.raises(sqlite3.IntegrityError):
            db_manager.execute_query(
                "INSERT INTO projects (name, path, parent_id) VALUES ('Test', '/test', 999)"
            )


class TestTasksTable:
    """Test tasks table structure and constraints."""

    def test_tasks_table_columns(self, db_manager):
        """Test that tasks table has correct columns."""
        columns = db_manager.get_columns('tasks')

        expected_columns = [
            'id', 'project_id', 'section', 'stage', 'description',
            'priority', 'status', 'order_number', 'line_number',
            'parent_task_id', 'estimated_effort', 'created_at',
            'updated_at', 'completed_at'
        ]

        for col in expected_columns:
            assert col in columns, f"Column '{col}' missing from tasks table"

    def test_tasks_status_check_constraint(self, db_manager):
        """Test that task status must be valid enum value."""
        # First create a project
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test', '/test')"
        )

        # Valid status should work
        db_manager.execute_query(
            "INSERT INTO tasks (project_id, description, status) "
            "VALUES (1, 'Test task', 'todo')"
        )

        # Invalid status should fail
        with pytest.raises(sqlite3.IntegrityError):
            db_manager.execute_query(
                "INSERT INTO tasks (project_id, description, status) "
                "VALUES (1, 'Test task', 'invalid_status')"
            )

    def test_tasks_priority_check_constraint(self, db_manager):
        """Test that task priority must be valid enum value."""
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test', '/test')"
        )

        # Valid priorities
        valid_priorities = ['critical', 'high', 'medium', 'low', 'unknown']
        for priority in valid_priorities:
            db_manager.execute_query(
                f"INSERT INTO tasks (project_id, description, priority) "
                f"VALUES (1, 'Test {priority}', '{priority}')"
            )

        # Invalid priority should fail
        with pytest.raises(sqlite3.IntegrityError):
            db_manager.execute_query(
                "INSERT INTO tasks (project_id, description, priority) "
                "VALUES (1, 'Test', 'invalid_priority')"
            )


class TestRequirementsTable:
    """Test requirements table structure and constraints."""

    def test_requirements_table_columns(self, db_manager):
        """Test that requirements table has correct columns."""
        columns = db_manager.get_columns('requirements')

        expected_columns = [
            'id', 'project_id', 'category', 'description',
            'priority', 'status', 'requirement_number',
            'line_number', 'created_at', 'updated_at'
        ]

        for col in expected_columns:
            assert col in columns, f"Column '{col}' missing from requirements table"

    def test_requirements_priority_check_constraint(self, db_manager):
        """Test that requirement priority must be valid enum value."""
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test', '/test')"
        )

        # Valid priorities
        valid_priorities = ['critical', 'high', 'medium', 'low', 'unknown']
        for priority in valid_priorities:
            db_manager.execute_query(
                f"INSERT INTO requirements (project_id, description, priority) "
                f"VALUES (1, 'Test {priority}', '{priority}')"
            )

        # Invalid priority should fail
        with pytest.raises(sqlite3.IntegrityError):
            db_manager.execute_query(
                "INSERT INTO requirements (project_id, description, priority) "
                "VALUES (1, 'Test', 'must')"  # Old enum value, should fail
            )


class TestTriggers:
    """Test database triggers."""

    def test_project_timestamp_trigger(self, db_manager):
        """Test that last_modified is updated on project update."""
        # Insert project
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test', '/test')"
        )

        # Get initial timestamp
        result = db_manager.execute_query(
            "SELECT last_modified FROM projects WHERE id = 1"
        )
        initial_timestamp = result[0]['last_modified']

        # Update project
        import time
        time.sleep(1.1)  # Ensure timestamp difference (SQLite has 1-second precision)
        db_manager.execute_query(
            "UPDATE projects SET name = 'Updated' WHERE id = 1"
        )

        # Get new timestamp
        result = db_manager.execute_query(
            "SELECT last_modified FROM projects WHERE id = 1"
        )
        new_timestamp = result[0]['last_modified']

        # Timestamp should be different
        assert new_timestamp != initial_timestamp

    def test_task_completed_at_trigger(self, db_manager):
        """Test that completed_at is set when task is marked done."""
        # Create project and task
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test', '/test')"
        )
        db_manager.execute_query(
            "INSERT INTO tasks (project_id, description, status) "
            "VALUES (1, 'Test task', 'todo')"
        )

        # completed_at should be NULL initially
        result = db_manager.execute_query(
            "SELECT completed_at FROM tasks WHERE id = 1"
        )
        assert result[0]['completed_at'] is None

        # Mark task as done
        db_manager.execute_query(
            "UPDATE tasks SET status = 'done' WHERE id = 1"
        )

        # completed_at should now be set
        result = db_manager.execute_query(
            "SELECT completed_at FROM tasks WHERE id = 1"
        )
        assert result[0]['completed_at'] is not None


class TestViews:
    """Test database views."""

    def test_project_summary_view(self, db_manager):
        """Test that project summary view works correctly."""
        # Create test data
        db_manager.execute_query(
            "INSERT INTO projects (name, path) VALUES ('Test Project', '/test')"
        )
        db_manager.execute_query(
            "INSERT INTO tasks (project_id, description, status) VALUES (1, 'Task 1', 'done')"
        )
        db_manager.execute_query(
            "INSERT INTO tasks (project_id, description, status) VALUES (1, 'Task 2', 'todo')"
        )

        # Query view
        result = db_manager.execute_query(
            "SELECT * FROM vw_project_summary WHERE id = 1"
        )

        assert len(result) == 1
        assert result[0]['name'] == 'Test Project'
        assert result[0]['total_tasks'] == 2
        assert result[0]['completed_tasks'] == 1
        assert result[0]['completion_percentage'] == 50.0
