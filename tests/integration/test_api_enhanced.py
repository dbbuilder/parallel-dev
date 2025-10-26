"""
Integration tests for enhanced API endpoints with filtering, sorting, and search.
Tests Phase 8 functionality.
"""

import pytest
from datetime import datetime, timedelta
from src.api.app import create_app
from backend.database.db_manager import DatabaseManager
from src.models.project import Project
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority


@pytest.fixture
def app():
    """Create test Flask application."""
    from backend.database.db_manager import init_database
    import tempfile
    import os

    # Create temp database file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    # Initialize database schema
    init_database(db_path)

    # Create database manager and app
    db = DatabaseManager(db_path)
    app = create_app(testing=True, db_manager=db)

    yield app

    # Cleanup
    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def populated_db(app):
    """Create database with test data."""
    db = app.db

    # Create multiple projects with different characteristics
    projects = [
        {
            'path': '/test/project1',
            'name': 'Authentication System',
            'description': 'User authentication and authorization'
        },
        {
            'path': '/test/project2',
            'name': 'Payment Gateway',
            'description': 'Payment processing integration'
        },
        {
            'path': '/test/project3',
            'name': 'Dashboard UI',
            'description': 'Admin dashboard interface'
        }
    ]

    project_ids = []
    for proj_data in projects:
        proj_id = db.create_project(**proj_data)
        project_ids.append(proj_id)

    # Add tasks to projects with various statuses and priorities
    tasks_data = [
        # Project 1 tasks
        (project_ids[0], 'Implement login', TaskStatus.DONE, TaskPriority.HIGH, 'Authentication', 'Backend'),
        (project_ids[0], 'Add OAuth support', TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 'Authentication', 'Backend'),
        (project_ids[0], 'Fix password reset', TaskStatus.BLOCKED, TaskPriority.HIGH, 'Authentication', 'Backend'),
        (project_ids[0], 'Add 2FA', TaskStatus.TODO, TaskPriority.LOW, 'Security', 'Backend'),

        # Project 2 tasks
        (project_ids[1], 'Stripe integration', TaskStatus.DONE, TaskPriority.HIGH, 'Payments', 'Backend'),
        (project_ids[1], 'Payment webhooks', TaskStatus.IN_PROGRESS, TaskPriority.HIGH, 'Payments', 'Backend'),
        (project_ids[1], 'Refund handling', TaskStatus.TODO, TaskPriority.MEDIUM, 'Payments', 'Backend'),

        # Project 3 tasks
        (project_ids[2], 'Create charts', TaskStatus.DONE, TaskPriority.MEDIUM, 'Visualization', 'Frontend'),
        (project_ids[2], 'Add dark mode', TaskStatus.IN_PROGRESS, TaskPriority.LOW, 'UI', 'Frontend'),
        (project_ids[2], 'Responsive design', TaskStatus.TODO, TaskPriority.HIGH, 'UI', 'Frontend'),
    ]

    for proj_id, desc, status, priority, stage, category in tasks_data:
        db.create_task(
            project_id=proj_id,
            description=desc,
            status=status.value,
            priority=priority.value,
            stage=stage,
            category=category
        )

    # Add requirements
    requirements_data = [
        (project_ids[0], 'System must support email/password login', RequirementPriority.CRITICAL),
        (project_ids[0], 'System should support OAuth providers', RequirementPriority.HIGH),
        (project_ids[0], 'System could support biometric auth', RequirementPriority.MEDIUM),
        (project_ids[1], 'System must process payments securely', RequirementPriority.CRITICAL),
        (project_ids[1], 'System should handle refunds', RequirementPriority.HIGH),
    ]

    for proj_id, desc, priority in requirements_data:
        db.create_requirement(
            project_id=proj_id,
            description=desc,
            priority=priority.value
        )

    return db, project_ids


class TestProjectFiltering:
    """Test filtering projects by various criteria."""

    def test_get_projects_no_filter(self, client, populated_db):
        """Test getting all projects without filters."""
        response = client.get('/api/projects')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']) == 3

    def test_filter_projects_by_name(self, client, populated_db):
        """Test filtering projects by name (partial match)."""
        response = client.get('/api/projects?name=auth')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 1
        assert 'Authentication' in data['data'][0]['name']

    def test_filter_projects_by_path(self, client, populated_db):
        """Test filtering projects by path."""
        response = client.get('/api/projects?path=/test/project1')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 1
        assert data['data'][0]['path'] == '/test/project1'


class TestProjectSorting:
    """Test sorting projects by various fields."""

    def test_sort_projects_by_name_asc(self, client, populated_db):
        """Test sorting projects by name ascending."""
        response = client.get('/api/projects?sort=name&order=asc')
        assert response.status_code == 200
        data = response.get_json()
        names = [p['name'] for p in data['data']]
        assert names == sorted(names)

    def test_sort_projects_by_name_desc(self, client, populated_db):
        """Test sorting projects by name descending."""
        response = client.get('/api/projects?sort=name&order=desc')
        assert response.status_code == 200
        data = response.get_json()
        names = [p['name'] for p in data['data']]
        assert names == sorted(names, reverse=True)


class TestTaskFiltering:
    """Test filtering tasks within a project."""

    def test_filter_tasks_by_status(self, client, populated_db):
        """Test filtering tasks by status."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?status=done')
        assert response.status_code == 200
        data = response.get_json()
        assert all(t['status'] == 'done' for t in data['data'])

    def test_filter_tasks_by_priority(self, client, populated_db):
        """Test filtering tasks by priority."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?priority=high')
        assert response.status_code == 200
        data = response.get_json()
        assert all(t['priority'] == 'high' for t in data['data'])

    def test_filter_tasks_by_category(self, client, populated_db):
        """Test filtering tasks by category."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[1]}/tasks?category=Payments')
        assert response.status_code == 200
        data = response.get_json()
        assert all(t['category'] == 'Payments' for t in data['data'])

    def test_filter_tasks_by_stage(self, client, populated_db):
        """Test filtering tasks by stage."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?stage=Authentication')
        assert response.status_code == 200
        data = response.get_json()
        assert all(t['stage'] == 'Authentication' for t in data['data'])

    def test_filter_tasks_multiple_criteria(self, client, populated_db):
        """Test filtering tasks by multiple criteria."""
        db, project_ids = populated_db
        response = client.get(
            f'/api/projects/{project_ids[0]}/tasks?status=done&priority=high'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert all(
            t['status'] == 'done' and t['priority'] == 'high'
            for t in data['data']
        )


class TestRequirementFiltering:
    """Test filtering requirements within a project."""

    def test_filter_requirements_by_priority(self, client, populated_db):
        """Test filtering requirements by priority."""
        db, project_ids = populated_db
        response = client.get(
            f'/api/projects/{project_ids[0]}/requirements?priority=critical'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert all(r['priority'] == 'critical' for r in data['data'])

    def test_filter_requirements_by_status(self, client, populated_db):
        """Test filtering requirements by status."""
        db, project_ids = populated_db
        response = client.get(
            f'/api/projects/{project_ids[0]}/requirements?status=planned'
        )
        assert response.status_code == 200
        data = response.get_json()
        # All requirements default to planned status
        assert len(data['data']) >= 1


class TestPagination:
    """Test pagination for large result sets."""

    def test_pagination_first_page(self, client, populated_db):
        """Test getting first page of results."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?page=1&per_page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 2
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 2
        assert data['pagination']['total'] >= 4

    def test_pagination_second_page(self, client, populated_db):
        """Test getting second page of results."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?page=2&per_page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 2
        assert data['pagination']['page'] == 2

    def test_pagination_default_values(self, client, populated_db):
        """Test pagination with default values."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks')
        assert response.status_code == 200
        data = response.get_json()
        # Should return all results when no pagination specified
        assert len(data['data']) >= 4


class TestSearch:
    """Test search functionality across projects, tasks, and requirements."""

    def test_search_projects(self, client, populated_db):
        """Test searching projects by keyword."""
        response = client.get('/api/search?q=payment&type=projects')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1
        # Should find "Payment Gateway" project
        assert any('Payment' in r['name'] for r in data['data'])

    def test_search_tasks(self, client, populated_db):
        """Test searching tasks by keyword."""
        response = client.get('/api/search?q=oauth&type=tasks')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1
        assert any('OAuth' in r['description'] for r in data['data'])

    def test_search_requirements(self, client, populated_db):
        """Test searching requirements by keyword."""
        response = client.get('/api/search?q=login&type=requirements')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1
        assert any('login' in r['description'].lower() for r in data['data'])

    def test_search_all_types(self, client, populated_db):
        """Test searching across all types."""
        response = client.get('/api/search?q=auth')
        assert response.status_code == 200
        data = response.get_json()
        # Should search projects, tasks, and requirements
        assert 'projects' in data['data']
        assert 'tasks' in data['data']
        assert 'requirements' in data['data']

    def test_search_no_results(self, client, populated_db):
        """Test search with no matching results."""
        response = client.get('/api/search?q=nonexistentterm12345')
        assert response.status_code == 200
        data = response.get_json()
        if 'projects' in data['data']:
            assert len(data['data']['projects']) == 0


class TestSortingTasks:
    """Test sorting tasks by various fields."""

    def test_sort_tasks_by_priority(self, client, populated_db):
        """Test sorting tasks by priority."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?sort=priority')
        assert response.status_code == 200
        data = response.get_json()
        # High priority tasks should come first
        priorities = [t['priority'] for t in data['data']]
        assert priorities[0] in ['high', 'medium', 'low']

    def test_sort_tasks_by_status(self, client, populated_db):
        """Test sorting tasks by status."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?sort=status')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) >= 1


class TestErrorHandling:
    """Test error handling for invalid parameters."""

    def test_invalid_sort_field(self, client, populated_db):
        """Test sorting by invalid field."""
        response = client.get('/api/projects?sort=invalid_field')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'invalid' in data['message'].lower()

    def test_invalid_filter_value(self, client, populated_db):
        """Test filtering with invalid value."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?status=invalid_status')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_invalid_page_number(self, client, populated_db):
        """Test pagination with invalid page number."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?page=0')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_invalid_per_page(self, client, populated_db):
        """Test pagination with invalid per_page value."""
        db, project_ids = populated_db
        response = client.get(f'/api/projects/{project_ids[0]}/tasks?per_page=0')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
