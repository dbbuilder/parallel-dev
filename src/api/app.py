"""
Flask Application Factory
Creates and configures the Flask API application.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.database.db_manager import DatabaseManager
from src.services.directory_scanner import DirectoryScanner
from src.services.project_detector import ProjectDetector
from src.services.metrics_calculator import MetricsCalculator
from src.parsers.todo_parser import TodoParser
from src.parsers.requirements_parser import RequirementsParser
from src.api.query_parser import QueryParser, QueryParseError


def create_app(testing: bool = False, db_manager: Optional[DatabaseManager] = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        testing: If True, configure for testing mode
        db_manager: Optional DatabaseManager instance (for testing)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Configuration
    app.config['TESTING'] = testing
    app.config['JSON_SORT_KEYS'] = False

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database
    if db_manager:
        app.db = db_manager
    else:
        db_path = "./data/projects.db"
        if not Path(db_path).exists():
            from backend.database.db_manager import init_database
            init_database(db_path)
        app.db = DatabaseManager(db_path)

    # Initialize services
    app.scanner = DirectoryScanner(ProjectDetector())
    app.calculator = MetricsCalculator()
    app.todo_parser = TodoParser()
    app.requirements_parser = RequirementsParser()

    # ==================== ROUTES ====================

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/projects', methods=['GET'])
    def get_all_projects():
        """Get all projects with optional filtering, sorting, and pagination."""
        try:
            # Parse query parameters
            filters = QueryParser.parse_filters('projects')
            sorting = QueryParser.parse_sorting('projects')
            pagination = QueryParser.parse_pagination()

            # Get projects from database
            projects = app.db.list_projects()

            # Apply filters
            projects = QueryParser.apply_filters(projects, filters)

            # Apply sorting
            projects = QueryParser.apply_sorting(
                projects,
                sorting['sort'],
                sorting['order']
            )

            # Apply pagination
            projects, page_meta = QueryParser.apply_pagination(
                projects,
                pagination['page'],
                pagination['per_page']
            )

            response = {
                'status': 'success',
                'data': projects
            }

            # Add pagination metadata if applicable
            if page_meta:
                response['pagination'] = page_meta

            return jsonify(response)

        except QueryParseError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/projects/<int:project_id>', methods=['GET'])
    def get_project(project_id: int):
        """Get single project by ID."""
        try:
            project = app.db.get_project(project_id)

            if not project:
                return jsonify({
                    'status': 'error',
                    'message': f'Project {project_id} not found'
                }), 404

            # Get tasks and requirements
            tasks = app.db.list_tasks(project_id=project_id)
            requirements = app.db.list_requirements(project_id=project_id)

            # Build response
            project_data = dict(project)
            project_data['tasks'] = tasks
            project_data['requirements'] = requirements

            return jsonify({
                'status': 'success',
                'data': project_data
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/projects/<int:project_id>/metrics', methods=['GET'])
    def get_project_metrics(project_id: int):
        """Get metrics for a specific project."""
        try:
            project_dict = app.db.get_project(project_id)

            if not project_dict:
                return jsonify({
                    'status': 'error',
                    'message': f'Project {project_id} not found'
                }), 404

            # Create Project object from dict
            from src.models.project import Project
            from src.models.task import Task, TaskStatus, TaskPriority
            from src.models.requirement import Requirement, RequirementStatus, RequirementPriority

            project = Project(path=project_dict['path'], name=project_dict['name'])

            # Load tasks
            tasks_data = app.db.list_tasks(project_id=project_id)
            for task_dict in tasks_data:
                task = Task(
                    description=task_dict['description'],
                    status=TaskStatus(task_dict.get('status', 'todo')),
                    priority=TaskPriority(task_dict.get('priority', 'unknown'))
                )
                project.add_task(task)

            # Load requirements
            reqs_data = app.db.list_requirements(project_id=project_id)
            for req_dict in reqs_data:
                req = Requirement(
                    description=req_dict['description'],
                    status=RequirementStatus(req_dict.get('status', 'planned')),
                    priority=RequirementPriority(req_dict.get('priority', 'unknown'))
                )
                project.add_requirement(req)

            # Calculate metrics
            metrics = app.calculator.calculate(project)

            return jsonify({
                'status': 'success',
                'data': {
                    'project_id': project_id,
                    'metrics': metrics.to_dict()
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
    def get_project_tasks(project_id: int):
        """Get tasks for a specific project with filtering, sorting, and pagination."""
        try:
            # Verify project exists
            project_dict = app.db.get_project(project_id)
            if not project_dict:
                return jsonify({
                    'status': 'error',
                    'message': f'Project {project_id} not found'
                }), 404

            # Parse query parameters
            filters = QueryParser.parse_filters('tasks')
            sorting = QueryParser.parse_sorting('tasks')
            pagination = QueryParser.parse_pagination()

            # Get tasks from database
            tasks = app.db.list_tasks(project_id=project_id)

            # Apply filters
            tasks = QueryParser.apply_filters(tasks, filters)

            # Apply sorting
            tasks = QueryParser.apply_sorting(
                tasks,
                sorting['sort'],
                sorting['order']
            )

            # Apply pagination
            tasks, page_meta = QueryParser.apply_pagination(
                tasks,
                pagination['page'],
                pagination['per_page']
            )

            response = {
                'status': 'success',
                'data': tasks
            }

            # Add pagination metadata if applicable
            if page_meta:
                response['pagination'] = page_meta

            return jsonify(response)

        except QueryParseError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/projects/<int:project_id>/requirements', methods=['GET'])
    def get_project_requirements(project_id: int):
        """Get requirements for a specific project with filtering, sorting, and pagination."""
        try:
            # Verify project exists
            project_dict = app.db.get_project(project_id)
            if not project_dict:
                return jsonify({
                    'status': 'error',
                    'message': f'Project {project_id} not found'
                }), 404

            # Parse query parameters
            filters = QueryParser.parse_filters('requirements')
            sorting = QueryParser.parse_sorting('requirements')
            pagination = QueryParser.parse_pagination()

            # Get requirements from database
            requirements = app.db.list_requirements(project_id=project_id)

            # Apply filters
            requirements = QueryParser.apply_filters(requirements, filters)

            # Apply sorting
            requirements = QueryParser.apply_sorting(
                requirements,
                sorting['sort'],
                sorting['order']
            )

            # Apply pagination
            requirements, page_meta = QueryParser.apply_pagination(
                requirements,
                pagination['page'],
                pagination['per_page']
            )

            response = {
                'status': 'success',
                'data': requirements
            }

            # Add pagination metadata if applicable
            if page_meta:
                response['pagination'] = page_meta

            return jsonify(response)

        except QueryParseError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/search', methods=['GET'])
    def search():
        """Search across projects, tasks, and requirements."""
        try:
            # Parse search parameters
            search_params = QueryParser.parse_search()
            query = search_params['query'].lower()
            search_type = search_params['type']

            results = {}

            # Search projects
            if search_type in ['all', 'projects']:
                projects = app.db.list_projects()
                matching_projects = [
                    p for p in projects
                    if query in p.get('name', '').lower()
                    or query in p.get('description', '').lower()
                    or query in p.get('path', '').lower()
                ]
                results['projects'] = matching_projects if search_type == 'all' else results

            # Search tasks
            if search_type in ['all', 'tasks']:
                tasks = app.db.list_tasks()
                matching_tasks = [
                    t for t in tasks
                    if query in t.get('description', '').lower()
                    or query in t.get('category', '').lower()
                    or query in t.get('stage', '').lower()
                ]
                if search_type == 'all':
                    results['tasks'] = matching_tasks
                else:
                    results = matching_tasks

            # Search requirements
            if search_type in ['all', 'requirements']:
                requirements = app.db.list_requirements()
                matching_requirements = [
                    r for r in requirements
                    if query in r.get('description', '').lower()
                ]
                if search_type == 'all':
                    results['requirements'] = matching_requirements
                else:
                    results = matching_requirements

            # For specific type searches, return the list directly
            if search_type != 'all':
                return jsonify({
                    'status': 'success',
                    'data': results
                })

            # For 'all' type searches, return categorized results
            return jsonify({
                'status': 'success',
                'data': results
            })

        except QueryParseError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/dashboard', methods=['GET'])
    def get_dashboard():
        """Get dashboard summary data."""
        try:
            projects = app.db.list_projects()

            # Calculate aggregated metrics
            total_projects = len(projects)
            total_tasks = 0
            total_requirements = 0
            all_tasks = app.db.list_tasks()
            all_requirements = app.db.list_requirements()

            # Count totals
            total_tasks = len(all_tasks)
            total_requirements = len(all_requirements)

            # Count completed
            completed_tasks = sum(1 for t in all_tasks if t.get('status') == 'done')
            completed_requirements = sum(1 for r in all_requirements if r.get('status') == 'completed')

            # Calculate overall completion
            total_items = total_tasks + total_requirements
            completed_items = completed_tasks + completed_requirements
            overall_completion = (completed_items / total_items * 100.0) if total_items > 0 else 0.0

            return jsonify({
                'status': 'success',
                'data': {
                    'summary': {
                        'total_projects': total_projects,
                        'total_tasks': total_tasks,
                        'total_requirements': total_requirements,
                        'overall_completion': overall_completion
                    },
                    'projects': projects
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @app.route('/api/scan', methods=['POST'])
    def trigger_scan():
        """Trigger directory scan for projects."""
        try:
            # Get directory from request
            data = request.get_json()

            if not data or 'directory' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing required parameter: directory'
                }), 400

            directory = data['directory']
            directory_path = Path(directory)

            # Validate directory exists
            if not directory_path.exists():
                return jsonify({
                    'status': 'error',
                    'message': f'Directory does not exist: {directory}'
                }), 400

            if not directory_path.is_dir():
                return jsonify({
                    'status': 'error',
                    'message': f'Path is not a directory: {directory}'
                }), 400

            # Scan for projects
            project_paths = app.scanner.scan(directory_path)

            projects_added = 0

            # Process each project
            for project_path in project_paths:
                # Get project info
                info = app.scanner.get_project_info(project_path)

                # Create project object
                from src.models.project import Project
                project = Project(path=str(project_path), name=info['name'])

                # Parse TODO.md if exists
                todo_path = project_path / "TODO.md"
                if todo_path.exists():
                    tasks = app.todo_parser.parse(todo_path)
                    for task in tasks:
                        project.add_task(task)
                    project.has_todo_file = True
                    project.todo_file_path = todo_path

                # Parse REQUIREMENTS.md if exists
                req_path = project_path / "REQUIREMENTS.md"
                if req_path.exists():
                    requirements = app.requirements_parser.parse(req_path)
                    for req in requirements:
                        project.add_requirement(req)
                    project.has_requirements_file = True
                    project.requirements_file_path = req_path

                # Check README.md
                readme_path = project_path / "README.md"
                if readme_path.exists():
                    project.has_readme_file = True
                    project.readme_file_path = readme_path

                # Insert into database
                project_id = app.db.create_project(
                    name=info['name'],
                    path=str(project_path)
                )

                # Insert tasks
                for task in project.tasks:
                    app.db.create_task(
                        project_id=project_id,
                        description=task.description,
                        status=task.status.value,
                        priority=task.priority.value
                    )

                # Insert requirements
                for req in project.requirements:
                    app.db.create_requirement(
                        project_id=project_id,
                        description=req.description,
                        status=req.status.value,
                        priority=req.priority.value
                    )

                projects_added += 1

            return jsonify({
                'status': 'success',
                'data': {
                    'projects_found': len(project_paths),
                    'projects_added': projects_added
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    # ==================== ERROR HANDLERS ====================

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors."""
        return jsonify({
            'status': 'error',
            'message': 'Bad request'
        }), 400

    return app


if __name__ == '__main__':
    import os
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
