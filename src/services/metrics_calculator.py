"""
Metrics Calculator
Calculates project progress metrics from tasks and requirements.
"""

from datetime import datetime
from typing import Dict
from collections import defaultdict

from src.models.project import Project, ProgressMetrics
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority


class MetricsCalculator:
    """
    Calculates comprehensive metrics for project progress tracking.

    Analyzes tasks and requirements to compute:
    - Completion percentages
    - Status counts
    - Health scores
    - Orphaned items
    - Priority distributions
    """

    def calculate(
        self,
        project: Project,
        include_subprojects: bool = False
    ) -> ProgressMetrics:
        """
        Calculate all metrics for a project.

        Args:
            project: Project to calculate metrics for
            include_subprojects: If True, include metrics from sub-projects

        Returns:
            ProgressMetrics object with calculated values
        """
        metrics = ProgressMetrics()

        # Get tasks and requirements
        tasks = project.get_all_tasks(include_subprojects=include_subprojects)
        requirements = project.get_all_requirements(include_subprojects=include_subprojects)

        # Calculate task counts
        metrics.total_tasks = len(tasks)
        metrics.completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        metrics.in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)

        # Calculate requirement counts
        metrics.total_requirements = len(requirements)
        metrics.completed_requirements = sum(
            1 for r in requirements if r.status == RequirementStatus.COMPLETED
        )
        metrics.in_progress_requirements = sum(
            1 for r in requirements if r.status == RequirementStatus.IN_PROGRESS
        )

        # Calculate completion percentage
        metrics.completion_percentage = self._calculate_completion_percentage(
            tasks, requirements
        )

        # Calculate health score
        metrics.health_score = self._calculate_health_score(tasks, requirements)

        # Calculate orphaned items
        metrics.orphaned_requirements = sum(
            1 for r in requirements if len(r.related_task_ids) == 0
        )
        metrics.orphaned_tasks = sum(
            1 for t in tasks if len(t.related_requirement_ids) == 0
        )

        # Update timestamp
        metrics.last_calculated = datetime.now()

        # Update project's metrics
        project.metrics = metrics

        return metrics

    def _calculate_completion_percentage(
        self,
        tasks: list[Task],
        requirements: list[Requirement]
    ) -> float:
        """
        Calculate overall completion percentage.

        Strategy:
        - If only tasks exist: base on task completion
        - If only requirements exist: base on requirement completion
        - If both exist: average of both percentages

        Args:
            tasks: List of tasks
            requirements: List of requirements

        Returns:
            Completion percentage (0.0 to 100.0)
        """
        task_percentage = None
        req_percentage = None

        # Calculate task completion percentage
        if len(tasks) > 0:
            completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
            task_percentage = (completed_tasks / len(tasks)) * 100.0

        # Calculate requirement completion percentage
        if len(requirements) > 0:
            completed_reqs = sum(1 for r in requirements if r.status == RequirementStatus.COMPLETED)
            req_percentage = (completed_reqs / len(requirements)) * 100.0

        # Return based on what's available
        if task_percentage is not None and req_percentage is not None:
            return (task_percentage + req_percentage) / 2.0
        elif task_percentage is not None:
            return task_percentage
        elif req_percentage is not None:
            return req_percentage
        else:
            return 0.0

    def _calculate_health_score(
        self,
        tasks: list[Task],
        requirements: list[Requirement]
    ) -> float:
        """
        Calculate project health score (0.0 to 1.0).

        Health score is based on:
        - Percentage of items that are NOT blocked
        - High score = few/no blocked items
        - Low score = many blocked items

        Args:
            tasks: List of tasks
            requirements: List of requirements

        Returns:
            Health score (0.0 to 1.0)
        """
        total_items = len(tasks) + len(requirements)

        if total_items == 0:
            return 1.0  # Empty project is "healthy"

        blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
        blocked_reqs = sum(1 for r in requirements if r.status == RequirementStatus.BLOCKED)
        blocked_items = blocked_tasks + blocked_reqs

        # Health score = percentage of non-blocked items
        return (total_items - blocked_items) / total_items

    def count_tasks_by_priority(self, project: Project) -> Dict[TaskPriority, int]:
        """
        Count tasks grouped by priority level.

        Args:
            project: Project to analyze

        Returns:
            Dictionary mapping TaskPriority to count
        """
        counts = defaultdict(int)

        # Initialize all priorities to 0
        for priority in TaskPriority:
            counts[priority] = 0

        # Count tasks
        for task in project.tasks:
            counts[task.priority] += 1

        return dict(counts)

    def count_requirements_by_priority(
        self,
        project: Project
    ) -> Dict[RequirementPriority, int]:
        """
        Count requirements grouped by priority level.

        Args:
            project: Project to analyze

        Returns:
            Dictionary mapping RequirementPriority to count
        """
        counts = defaultdict(int)

        # Initialize all priorities to 0
        for priority in RequirementPriority:
            counts[priority] = 0

        # Count requirements
        for req in project.requirements:
            counts[req.priority] += 1

        return dict(counts)

    def count_tasks_by_stage(self, project: Project) -> Dict[str, int]:
        """
        Count tasks grouped by stage.

        Args:
            project: Project to analyze

        Returns:
            Dictionary mapping stage name to count
        """
        counts = defaultdict(int)

        for task in project.tasks:
            counts[task.stage] += 1

        return dict(counts)

    def count_requirements_by_category(self, project: Project) -> Dict[str, int]:
        """
        Count requirements grouped by category.

        Args:
            project: Project to analyze

        Returns:
            Dictionary mapping category name to count
        """
        counts = defaultdict(int)

        for req in project.requirements:
            counts[req.category] += 1

        return dict(counts)
