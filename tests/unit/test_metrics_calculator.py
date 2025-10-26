"""Unit tests for MetricsCalculator."""

import pytest
from datetime import datetime

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority
from src.models.project import Project, ProgressMetrics
from src.services.metrics_calculator import MetricsCalculator


class TestMetricsCalculator:
    """Test MetricsCalculator class."""

    def test_calculator_initialization(self):
        """Test that calculator can be instantiated."""
        calculator = MetricsCalculator()
        assert calculator is not None

    def test_calculate_empty_project(self):
        """Test calculating metrics for empty project."""
        project = Project(path="/test/project")
        calculator = MetricsCalculator()

        metrics = calculator.calculate(project)

        assert metrics.total_requirements == 0
        assert metrics.total_tasks == 0
        assert metrics.completion_percentage == 0.0
        assert metrics.completed_requirements == 0
        assert metrics.completed_tasks == 0

    def test_calculate_task_counts(self):
        """Test counting tasks by status."""
        project = Project(path="/test/project")
        project.add_task(Task("Task 1", status=TaskStatus.TODO))
        project.add_task(Task("Task 2", status=TaskStatus.DONE))
        project.add_task(Task("Task 3", status=TaskStatus.IN_PROGRESS))
        project.add_task(Task("Task 4", status=TaskStatus.DONE))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        assert metrics.total_tasks == 4
        assert metrics.completed_tasks == 2
        assert metrics.in_progress_tasks == 1

    def test_calculate_requirement_counts(self):
        """Test counting requirements by status."""
        project = Project(path="/test/project")
        project.add_requirement(Requirement("Req 1", status=RequirementStatus.PLANNED))
        project.add_requirement(Requirement("Req 2", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 3", status=RequirementStatus.IN_PROGRESS))
        project.add_requirement(Requirement("Req 4", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 5", status=RequirementStatus.COMPLETED))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        assert metrics.total_requirements == 5
        assert metrics.completed_requirements == 3
        assert metrics.in_progress_requirements == 1

    def test_calculate_completion_percentage_tasks_only(self):
        """Test completion percentage calculation based on tasks."""
        project = Project(path="/test/project")
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.DONE))
        project.add_task(Task("Task 3", status=TaskStatus.TODO))
        project.add_task(Task("Task 4", status=TaskStatus.IN_PROGRESS))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        # 2 done out of 4 = 50%
        assert metrics.completion_percentage == 50.0

    def test_calculate_completion_percentage_requirements_only(self):
        """Test completion percentage when only requirements exist."""
        project = Project(path="/test/project")
        project.add_requirement(Requirement("Req 1", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 2", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 3", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 4", status=RequirementStatus.PLANNED))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        # 3 done out of 4 = 75%
        assert metrics.completion_percentage == 75.0

    def test_calculate_completion_percentage_both(self):
        """Test completion percentage with both tasks and requirements."""
        project = Project(path="/test/project")

        # 2 done out of 4 tasks = 50%
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.DONE))
        project.add_task(Task("Task 3", status=TaskStatus.TODO))
        project.add_task(Task("Task 4", status=TaskStatus.TODO))

        # 3 done out of 4 requirements = 75%
        project.add_requirement(Requirement("Req 1", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 2", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 3", status=RequirementStatus.COMPLETED))
        project.add_requirement(Requirement("Req 4", status=RequirementStatus.PLANNED))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        # Average of 50% and 75% = 62.5%
        assert metrics.completion_percentage == 62.5

    def test_calculate_health_score(self):
        """Test health score calculation."""
        project = Project(path="/test/project")

        # Healthy project: no blocked items
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.IN_PROGRESS))
        project.add_requirement(Requirement("Req 1", status=RequirementStatus.COMPLETED))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        # Health score should be high (0.0-1.0 scale)
        assert 0.0 <= metrics.health_score <= 1.0
        assert metrics.health_score > 0.5  # No blocked items

    def test_calculate_health_score_with_blocked_items(self):
        """Test health score with blocked tasks/requirements."""
        project = Project(path="/test/project")

        project.add_task(Task("Task 1", status=TaskStatus.BLOCKED))
        project.add_task(Task("Task 2", status=TaskStatus.TODO))
        project.add_requirement(Requirement("Req 1", status=RequirementStatus.BLOCKED))
        project.add_requirement(Requirement("Req 2", status=RequirementStatus.PLANNED))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        # Health score should be lower due to blocked items
        assert metrics.health_score < 1.0

    def test_calculate_orphaned_requirements(self):
        """Test detection of requirements with no related tasks."""
        project = Project(path="/test/project")

        req1 = Requirement("Req with task")
        req1.related_task_ids = ["task-1"]
        project.add_requirement(req1)

        req2 = Requirement("Req without task")
        project.add_requirement(req2)

        req3 = Requirement("Another req without task")
        project.add_requirement(req3)

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        assert metrics.orphaned_requirements == 2

    def test_calculate_orphaned_tasks(self):
        """Test detection of tasks with no related requirements."""
        project = Project(path="/test/project")

        task1 = Task("Task with requirement")
        task1.related_requirement_ids = ["req-1"]
        project.add_task(task1)

        task2 = Task("Task without requirement")
        project.add_task(task2)

        task3 = Task("Another task without requirement")
        project.add_task(task3)

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        assert metrics.orphaned_tasks == 2

    def test_calculate_updates_last_calculated(self):
        """Test that last_calculated timestamp is updated."""
        project = Project(path="/test/project")
        calculator = MetricsCalculator()

        before = datetime.now()
        metrics = calculator.calculate(project)
        after = datetime.now()

        assert before <= metrics.last_calculated <= after

    def test_calculate_by_priority(self):
        """Test counting tasks by priority."""
        project = Project(path="/test/project")
        project.add_task(Task("Task 1", priority=TaskPriority.CRITICAL))
        project.add_task(Task("Task 2", priority=TaskPriority.HIGH))
        project.add_task(Task("Task 3", priority=TaskPriority.HIGH))
        project.add_task(Task("Task 4", priority=TaskPriority.LOW))

        calculator = MetricsCalculator()
        priority_counts = calculator.count_tasks_by_priority(project)

        assert priority_counts[TaskPriority.CRITICAL] == 1
        assert priority_counts[TaskPriority.HIGH] == 2
        assert priority_counts[TaskPriority.MEDIUM] == 0
        assert priority_counts[TaskPriority.LOW] == 1

    def test_count_requirements_by_priority(self):
        """Test counting requirements by priority."""
        project = Project(path="/test/project")
        project.add_requirement(Requirement("Req 1", priority=RequirementPriority.CRITICAL))
        project.add_requirement(Requirement("Req 2", priority=RequirementPriority.CRITICAL))
        project.add_requirement(Requirement("Req 3", priority=RequirementPriority.MEDIUM))

        calculator = MetricsCalculator()
        priority_counts = calculator.count_requirements_by_priority(project)

        assert priority_counts[RequirementPriority.CRITICAL] == 2
        assert priority_counts[RequirementPriority.HIGH] == 0
        assert priority_counts[RequirementPriority.MEDIUM] == 1
        assert priority_counts[RequirementPriority.LOW] == 0

    def test_calculate_updates_project_metrics(self):
        """Test that calculate() updates the project's metrics attribute."""
        project = Project(path="/test/project")
        project.add_task(Task("Task 1", status=TaskStatus.DONE))
        project.add_task(Task("Task 2", status=TaskStatus.TODO))

        calculator = MetricsCalculator()
        metrics = calculator.calculate(project)

        # Should update project's metrics
        assert project.metrics == metrics
        assert project.metrics.total_tasks == 2
        assert project.metrics.completed_tasks == 1

    def test_calculate_with_subprojects(self):
        """Test that calculate can optionally include subprojects."""
        parent = Project(path="/test/parent")
        parent.add_task(Task("Parent task", status=TaskStatus.DONE))

        child = Project(path="/test/parent/child")
        child.add_task(Task("Child task 1", status=TaskStatus.DONE))
        child.add_task(Task("Child task 2", status=TaskStatus.TODO))
        parent.add_sub_project(child)

        calculator = MetricsCalculator()

        # Without subprojects
        metrics_only_parent = calculator.calculate(parent, include_subprojects=False)
        assert metrics_only_parent.total_tasks == 1

        # With subprojects
        metrics_with_subs = calculator.calculate(parent, include_subprojects=True)
        assert metrics_with_subs.total_tasks == 3
        assert metrics_with_subs.completed_tasks == 2

    def test_calculate_stage_breakdown(self):
        """Test counting tasks by stage."""
        project = Project(path="/test/project")
        project.add_task(Task("Task 1", stage="Stage 1"))
        project.add_task(Task("Task 2", stage="Stage 1"))
        project.add_task(Task("Task 3", stage="Stage 2"))
        project.add_task(Task("Task 4", stage="Stage 3"))
        project.add_task(Task("Task 5", stage="Stage 3"))
        project.add_task(Task("Task 6", stage="Stage 3"))

        calculator = MetricsCalculator()
        stage_counts = calculator.count_tasks_by_stage(project)

        assert stage_counts["Stage 1"] == 2
        assert stage_counts["Stage 2"] == 1
        assert stage_counts["Stage 3"] == 3

    def test_calculate_category_breakdown(self):
        """Test counting requirements by category."""
        project = Project(path="/test/project")
        project.add_requirement(Requirement("Req 1", category="Functional"))
        project.add_requirement(Requirement("Req 2", category="Functional"))
        project.add_requirement(Requirement("Req 3", category="Technical"))
        project.add_requirement(Requirement("Req 4", category="Performance"))

        calculator = MetricsCalculator()
        category_counts = calculator.count_requirements_by_category(project)

        assert category_counts["Functional"] == 2
        assert category_counts["Technical"] == 1
        assert category_counts["Performance"] == 1
