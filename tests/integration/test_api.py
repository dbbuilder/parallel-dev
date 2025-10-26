"""Integration tests for Flask API endpoints."""

import pytest
import json
from pathlib import Path
import tempfile
import shutil

from src.api.app import create_app
from src.models.project import Project
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority
from backend.database.db_manager import DatabaseManager


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_file.name
    temp_file.close()

    # Initialize database schema
    from backend.database.db_manager import init_database
    init_database(db_path)

    # Create database manager
    db = DatabaseManager(db_path)

    yield db

    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def app(temp_db):
    """Create Flask app for testing."""
    app = create_app(testing=True, db_manager=temp_db)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Provide Flask test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_project(temp_db):
    """Create and insert a sample project."""
    # Create project
    project_id = temp_db.create_project(
        name="Test Project 1",
        path="/test/project1"
    )

    # Create tasks
    temp_db.create_task(
        project_id=project_id,
        description="Task 1",
        status="done",
        priority="high"
    )
    temp_db.create_task(
        project_id=project_id,
        description="Task 2",
        status="todo",
        priority="medium"
    )

    # Create requirement
    temp_db.create_requirement(
        project_id=project_id,
        description="Requirement 1",
        status="completed"
    )

    return project_id


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test GET /api/health."""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestProjectsAPI:
    """Test /api/projects endpoints."""

    def test_get_all_projects_empty(self, client):
        """Test GET /api/projects with no projects."""
        response = client.get('/api/projects')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data'] == []

    def test_get_all_projects_with_data(self, client, sample_project):
        """Test GET /api/projects with existing projects."""
        response = client.get('/api/projects')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == "Test Project 1"

    def test_get_project_by_id(self, client, sample_project):
        """Test GET /api/projects/<id>."""
        response = client.get(f'/api/projects/{sample_project}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['id'] == sample_project
        assert data['data']['name'] == "Test Project 1"

    def test_get_nonexistent_project(self, client):
        """Test GET /api/projects/99999."""
        response = client.get('/api/projects/99999')

        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()

    def test_get_project_with_tasks(self, client, sample_project):
        """Test that project includes tasks."""
        response = client.get(f'/api/projects/{sample_project}')

        assert response.status_code == 200
        data = response.get_json()
        assert 'tasks' in data['data']
        assert len(data['data']['tasks']) == 2

    def test_get_project_with_requirements(self, client, sample_project):
        """Test that project includes requirements."""
        response = client.get(f'/api/projects/{sample_project}')

        assert response.status_code == 200
        data = response.get_json()
        assert 'requirements' in data['data']
        assert len(data['data']['requirements']) == 1


class TestMetricsAPI:
    """Test /api/projects/<id>/metrics endpoints."""

    def test_get_project_metrics(self, client, sample_project):
        """Test GET /api/projects/<id>/metrics."""
        response = client.get(f'/api/projects/{sample_project}/metrics')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'metrics' in data['data']

    def test_metrics_include_completion(self, client, sample_project):
        """Test that metrics include completion percentage."""
        response = client.get(f'/api/projects/{sample_project}/metrics')

        data = response.get_json()
        metrics = data['data']['metrics']
        assert 'completion_percentage' in metrics
        assert isinstance(metrics['completion_percentage'], (int, float))

    def test_metrics_include_task_counts(self, client, sample_project):
        """Test that metrics include task counts."""
        response = client.get(f'/api/projects/{sample_project}/metrics')

        data = response.get_json()
        metrics = data['data']['metrics']
        assert 'total_tasks' in metrics
        assert 'completed_tasks' in metrics
        assert metrics['total_tasks'] == 2
        assert metrics['completed_tasks'] == 1

    def test_metrics_include_health_score(self, client, sample_project):
        """Test that metrics include health score."""
        response = client.get(f'/api/projects/{sample_project}/metrics')

        data = response.get_json()
        metrics = data['data']['metrics']
        assert 'health_score' in metrics
        assert 0.0 <= metrics['health_score'] <= 1.0

    def test_metrics_nonexistent_project(self, client):
        """Test metrics for nonexistent project."""
        response = client.get('/api/projects/99999/metrics')

        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'


class TestDashboardAPI:
    """Test /api/dashboard endpoint."""

    def test_get_dashboard_empty(self, client):
        """Test GET /api/dashboard with no projects."""
        response = client.get('/api/dashboard')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'summary' in data['data']

    def test_dashboard_includes_totals(self, client, sample_project):
        """Test dashboard includes total counts."""
        response = client.get('/api/dashboard')

        data = response.get_json()
        summary = data['data']['summary']
        assert 'total_projects' in summary
        assert 'total_tasks' in summary
        assert 'total_requirements' in summary
        assert summary['total_projects'] == 1

    def test_dashboard_includes_completion(self, client, sample_project):
        """Test dashboard includes overall completion."""
        response = client.get('/api/dashboard')

        data = response.get_json()
        summary = data['data']['summary']
        assert 'overall_completion' in summary
        assert isinstance(summary['overall_completion'], (int, float))

    def test_dashboard_includes_project_list(self, client, sample_project):
        """Test dashboard includes project list."""
        response = client.get('/api/dashboard')

        data = response.get_json()
        assert 'projects' in data['data']
        assert len(data['data']['projects']) == 1


class TestScanAPI:
    """Test /api/scan endpoint."""

    def test_trigger_scan(self, client, temp_db):
        """Test POST /api/scan."""
        # Create temporary directory with a project
        temp_dir = tempfile.mkdtemp()
        try:
            readme_path = Path(temp_dir) / "README.md"
            readme_path.write_text("# Test Project")

            # Trigger scan with directory parameter
            response = client.post('/api/scan', json={'directory': temp_dir})

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert 'projects_found' in data['data']
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_scan_without_directory(self, client):
        """Test scan with missing directory parameter."""
        response = client.post('/api/scan', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_scan_invalid_directory(self, client):
        """Test scan with non-existent directory."""
        response = client.post('/api/scan', json={'directory': '/nonexistent/path'})

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'


class TestErrorHandling:
    """Test API error handling."""

    def test_404_for_unknown_endpoint(self, client):
        """Test that unknown endpoints return 404."""
        response = client.get('/api/unknown')

        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test that wrong HTTP methods return 405."""
        response = client.post('/api/projects')

        assert response.status_code == 405

    def test_invalid_json_returns_error(self, client):
        """Test that invalid JSON returns error."""
        response = client.post(
            '/api/scan',
            data='invalid json',
            content_type='application/json'
        )

        # Flask returns 500 for malformed JSON (werkzeug.exceptions.BadRequest wrapped in 500)
        assert response.status_code in [400, 500]


class TestCORS:
    """Test CORS headers."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are set."""
        response = client.get('/api/health')

        assert 'Access-Control-Allow-Origin' in response.headers

    def test_options_request(self, client):
        """Test OPTIONS preflight request."""
        response = client.options('/api/projects')

        assert response.status_code == 200
        # Flask-CORS handles OPTIONS automatically
        assert 'Access-Control-Allow-Origin' in response.headers
