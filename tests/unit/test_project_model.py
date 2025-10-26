"""Unit tests for Project model."""

import pytest
from pathlib import Path
from datetime import datetime
from src.models.project import Project, ProgressMetrics
from src.models.task import Task, TaskStatus
from src.models.requirement import Requirement


class TestProjectCreation:
    """Test suite for Project creation and initialization."""

    def test_project_creation_with_path_only(self):
        """Test creating a project with just a path."""
        project = Project(path="/test/project")

        assert project.path == Path("/test/project").resolve()
        assert project.name == "project"  # Derived from path
        assert isinstance(project.requirements, list)
        assert isinstance(project.tasks, list)
        assert isinstance(project.sub_projects, list)
        assert project.parent_project is None
        assert isinstance(project.metrics, ProgressMetrics)
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.last_scanned, datetime)

    def test_project_creation_with_custom_name(self):
        """Test creating a project with custom name."""
        project = Project(path="/test/my_project", name="Custom Name")

        assert project.name == "Custom Name"
        assert project.path == Path("/test/my_project").resolve()

    def test_project_path_resolution(self):
        """Test that project path is resolved to absolute path."""
        project = Project(path="relative/path")

        assert project.path.is_absolute()

    def test_project_empty_lists_on_creation(self):
        """Test that all lists are empty on creation."""
        project = Project(path="/test")

        assert len(project.requirements) == 0
        assert len(project.tasks) == 0
        assert len(project.sub_projects) == 0


class TestProgressMetrics:
    """Test suite for ProgressMetrics."""

    def test_metrics_initialization(self):
        """Test metrics are initialized with default values."""
        metrics = ProgressMetrics()

        assert metrics.total_requirements == 0
        assert metrics.completed_requirements == 0
        assert metrics.in_progress_requirements == 0
        assert metrics.total_tasks == 0
        assert metrics.completed_tasks == 0
        assert metrics.in_progress_tasks == 0
        assert metrics.completion_percentage == 0.0
        assert metrics.health_score == 0.0
        assert metrics.orphaned_requirements == 0
        assert metrics.orphaned_tasks == 0
        assert isinstance(metrics.last_calculated, datetime)

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = ProgressMetrics()
        metrics.total_tasks = 10
        metrics.completed_tasks = 5
        metrics.completion_percentage = 50.0

        metrics_dict = metrics.to_dict()

        assert metrics_dict['total_tasks'] == 10
        assert metrics_dict['completed_tasks'] == 5
        assert metrics_dict['completion_percentage'] == 50.0
        assert 'last_calculated' in metrics_dict


class TestProjectTaskManagement:
    """Test suite for project task management."""

    def test_add_task_to_project(self):
        """Test adding a task to a project."""
        project = Project(path="/test")
        task = Task("Implement feature")

        project.add_task(task)

        assert len(project.tasks) == 1
        assert project.tasks[0] == task

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks."""
        project = Project(path="/test")

        project.add_task(Task("Task 1"))
        project.add_task(Task("Task 2"))
        project.add_task(Task("Task 3"))

        assert len(project.tasks) == 3

    def test_get_all_tasks_without_subprojects(self):
        """Test getting tasks without including subprojects."""
        project = Project(path="/test")
        project.add_task(Task("Task 1"))
        project.add_task(Task("Task 2"))

        tasks = project.get_all_tasks(include_subprojects=False)

        assert len(tasks) == 2

    def test_get_all_tasks_with_subprojects(self):
        """Test getting tasks including subprojects."""
        parent = Project(path="/parent")
        parent.add_task(Task("Parent task"))

        child = Project(path="/parent/child")
        child.add_task(Task("Child task 1"))
        child.add_task(Task("Child task 2"))

        parent.add_sub_project(child)

        all_tasks = parent.get_all_tasks(include_subprojects=True)

        assert len(all_tasks) == 3  # 1 parent + 2 child


class TestProjectRequirementManagement:
    """Test suite for project requirement management."""

    def test_add_requirement_to_project(self):
        """Test adding a requirement to a project."""
        project = Project(path="/test")
        req = Requirement("User authentication")

        project.add_requirement(req)

        assert len(project.requirements) == 1
        assert project.requirements[0] == req

    def test_add_multiple_requirements(self):
        """Test adding multiple requirements."""
        project = Project(path="/test")

        project.add_requirement(Requirement("Req 1"))
        project.add_requirement(Requirement("Req 2"))

        assert len(project.requirements) == 2

    def test_get_all_requirements_without_subprojects(self):
        """Test getting requirements without subprojects."""
        project = Project(path="/test")
        project.add_requirement(Requirement("Req 1"))

        reqs = project.get_all_requirements(include_subprojects=False)

        assert len(reqs) == 1

    def test_get_all_requirements_with_subprojects(self):
        """Test getting requirements including subprojects."""
        parent = Project(path="/parent")
        parent.add_requirement(Requirement("Parent req"))

        child = Project(path="/parent/child")
        child.add_requirement(Requirement("Child req 1"))
        child.add_requirement(Requirement("Child req 2"))

        parent.add_sub_project(child)

        all_reqs = parent.get_all_requirements(include_subprojects=True)

        assert len(all_reqs) == 3


class TestProjectHierarchy:
    """Test suite for project hierarchy management."""

    def test_add_sub_project(self):
        """Test adding a sub-project."""
        parent = Project(path="/parent")
        child = Project(path="/parent/child")

        parent.add_sub_project(child)

        assert len(parent.sub_projects) == 1
        assert parent.sub_projects[0] == child
        assert child.parent_project == parent

    def test_add_multiple_sub_projects(self):
        """Test adding multiple sub-projects."""
        parent = Project(path="/parent")
        child1 = Project(path="/parent/child1")
        child2 = Project(path="/parent/child2")

        parent.add_sub_project(child1)
        parent.add_sub_project(child2)

        assert len(parent.sub_projects) == 2
        assert child1.parent_project == parent
        assert child2.parent_project == parent

    def test_get_depth_root_project(self):
        """Test depth calculation for root project."""
        root = Project(path="/root")

        assert root.get_depth() == 0

    def test_get_depth_nested_projects(self):
        """Test depth calculation for nested projects."""
        root = Project(path="/root")
        level1 = Project(path="/root/level1")
        level2 = Project(path="/root/level1/level2")
        level3 = Project(path="/root/level1/level2/level3")

        root.add_sub_project(level1)
        level1.add_sub_project(level2)
        level2.add_sub_project(level3)

        assert root.get_depth() == 0
        assert level1.get_depth() == 1
        assert level2.get_depth() == 2
        assert level3.get_depth() == 3


class TestProjectCompletion:
    """Test suite for project completion calculations."""

    def test_calculate_completion_no_tasks(self):
        """Test completion calculation with no tasks."""
        project = Project(path="/test")

        completion = project.calculate_completion()

        assert completion == 0.0

    def test_calculate_completion_all_done(self):
        """Test completion with all tasks completed."""
        project = Project(path="/test")
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.DONE))

        completion = project.calculate_completion()

        assert completion == 100.0

    def test_calculate_completion_partial(self):
        """Test completion with partial completion."""
        project = Project(path="/test")
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.DONE))
        project.add_task(Task("Task 3", status=TaskStatus.TODO))
        project.add_task(Task("Task 4", status=TaskStatus.TODO))

        completion = project.calculate_completion()

        assert completion == 50.0

    def test_calculate_completion_in_progress_not_counted(self):
        """Test that in-progress tasks are not counted as completed."""
        project = Project(path="/test")
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.IN_PROGRESS))

        completion = project.calculate_completion()

        assert completion == 50.0


class TestProjectRepresentation:
    """Test suite for project string representation."""

    def test_project_repr(self):
        """Test project __repr__."""
        project = Project(path="/test/myproject")
        project.add_requirement(Requirement("Req 1"))
        project.add_task(Task("Task 1"))
        project.add_sub_project(Project(path="/test/myproject/sub"))

        repr_str = repr(project)

        assert "Project" in repr_str
        assert "myproject" in repr_str
        assert "reqs=1" in repr_str
        assert "tasks=1" in repr_str
        assert "subs=1" in repr_str


class TestProjectSerialization:
    """Test suite for project serialization."""

    def test_project_to_dict(self):
        """Test converting project to dictionary."""
        project = Project(path="/test/project", name="Test Project")
        project.add_task(Task("Task 1"))
        project.add_task(Task("Task 2"))
        project.add_requirement(Requirement("Req 1"))

        project_dict = project.to_dict()

        assert project_dict['name'] == "Test Project"
        assert 'path' in project_dict
        assert project_dict['requirements_count'] == 1
        assert project_dict['tasks_count'] == 2
        assert project_dict['sub_projects_count'] == 0
        assert 'metrics' in project_dict
        assert 'last_scanned' in project_dict

    def test_project_to_dict_with_file_flags(self):
        """Test to_dict includes file flags."""
        project = Project(path="/test")
        project.has_requirements_file = True
        project.has_todo_file = True
        project.has_readme_file = False

        project_dict = project.to_dict()

        assert project_dict['has_requirements_file'] == True
        assert project_dict['has_todo_file'] == True
        assert project_dict['has_readme_file'] == False


class TestProjectFileMetadata:
    """Test suite for project file metadata."""

    def test_project_file_flags_default_false(self):
        """Test file flags default to False."""
        project = Project(path="/test")

        assert project.has_requirements_file == False
        assert project.has_todo_file == False
        assert project.has_readme_file == False

    def test_project_file_paths_default_none(self):
        """Test file paths default to None."""
        project = Project(path="/test")

        assert project.requirements_file_path is None
        assert project.todo_file_path is None
        assert project.readme_file_path is None

    def test_project_readme_content_default_none(self):
        """Test readme content defaults to None."""
        project = Project(path="/test")

        assert project.readme_content is None

    def test_set_file_metadata(self):
        """Test setting file metadata."""
        project = Project(path="/test")

        project.has_requirements_file = True
        project.requirements_file_path = Path("/test/REQUIREMENTS.md")
        project.has_todo_file = True
        project.todo_file_path = Path("/test/TODO.md")
        project.readme_content = "# Test Project"

        assert project.has_requirements_file == True
        assert project.requirements_file_path == Path("/test/REQUIREMENTS.md")
        assert project.readme_content == "# Test Project"
