"""
Project Data Model
Represents a development project with requirements, tasks, and metrics
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from .requirement import Requirement
from .task import Task


class ProgressMetrics:
    """Calculated metrics for project progress."""
    
    def __init__(self):
        """Initialize progress metrics with default values."""
        self.total_requirements = 0
        self.completed_requirements = 0
        self.in_progress_requirements = 0
        
        self.total_tasks = 0
        self.completed_tasks = 0
        self.in_progress_tasks = 0
        
        self.completion_percentage = 0.0
        self.health_score = 0.0  # 0-1 scale
        
        self.orphaned_requirements = 0  # Requirements with no tasks
        self.orphaned_tasks = 0  # Tasks with no requirements
        
        self.last_calculated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            'total_requirements': self.total_requirements,
            'completed_requirements': self.completed_requirements,
            'in_progress_requirements': self.in_progress_requirements,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'in_progress_tasks': self.in_progress_tasks,
            'completion_percentage': self.completion_percentage,
            'health_score': self.health_score,
            'orphaned_requirements': self.orphaned_requirements,
            'orphaned_tasks': self.orphaned_tasks,
            'last_calculated': self.last_calculated.isoformat()
        }



class Project:
    """Represents a development project with all its metadata and content."""
    
    def __init__(self, path: str, name: Optional[str] = None):
        """
        Initialize a project.
        
        Args:
            path: Absolute path to the project directory
            name: Optional display name (defaults to directory name)
        """
        self.path = Path(path).resolve()
        self.name = name or self.path.name
        
        # Content from markdown files
        self.requirements: List[Requirement] = []
        self.tasks: List[Task] = []
        self.readme_content: Optional[str] = None
        
        # File metadata
        self.has_requirements_file = False
        self.has_todo_file = False
        self.has_readme_file = False
        
        self.requirements_file_path: Optional[Path] = None
        self.todo_file_path: Optional[Path] = None
        self.readme_file_path: Optional[Path] = None
        
        # Project structure
        self.sub_projects: List['Project'] = []
        self.parent_project: Optional['Project'] = None
        
        # Metrics
        self.metrics = ProgressMetrics()
        
        # Timestamps
        self.created_at = datetime.now()
        self.last_scanned = datetime.now()
        self.last_updated: Optional[datetime] = None
    
    def add_requirement(self, requirement: Requirement) -> None:
        """Add a requirement to this project."""
        self.requirements.append(requirement)
    
    def add_task(self, task: Task) -> None:
        """Add a task to this project."""
        self.tasks.append(task)
    
    def add_sub_project(self, project: 'Project') -> None:
        """
        Add a sub-project to this project.
        
        Args:
            project: The sub-project to add
        """
        project.parent_project = self
        self.sub_projects.append(project)
    
    def get_all_requirements(self, include_subprojects: bool = False) -> List[Requirement]:
        """
        Get all requirements from this project.
        
        Args:
            include_subprojects: If True, include requirements from sub-projects
            
        Returns:
            List of all requirements
        """
        reqs = self.requirements.copy()
        
        if include_subprojects:
            for sub_project in self.sub_projects:
                reqs.extend(sub_project.get_all_requirements(include_subprojects=True))
        
        return reqs
    
    def get_all_tasks(self, include_subprojects: bool = False) -> List[Task]:
        """
        Get all tasks from this project.
        
        Args:
            include_subprojects: If True, include tasks from sub-projects
            
        Returns:
            List of all tasks
        """
        tks = self.tasks.copy()
        
        if include_subprojects:
            for sub_project in self.sub_projects:
                tks.extend(sub_project.get_all_tasks(include_subprojects=True))
        
        return tks
    
    def get_depth(self) -> int:
        """
        Calculate the depth of this project in the hierarchy.

        Returns:
            Depth level (0 for root projects, 1 for direct children, etc.)
        """
        depth = 0
        current = self.parent_project
        while current is not None:
            depth += 1
            current = current.parent_project
        return depth

    def calculate_completion(self) -> float:
        """
        Calculate completion percentage based on tasks.

        Returns:
            Completion percentage (0.0 to 100.0)
        """
        total = len(self.tasks)
        if total == 0:
            return 0.0

        from .task import TaskStatus
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.DONE)
        return (completed / total) * 100.0
    
    def __repr__(self) -> str:
        """String representation of the project."""
        return (
            f"Project(name='{self.name}', "
            f"reqs={len(self.requirements)}, "
            f"tasks={len(self.tasks)}, "
            f"subs={len(self.sub_projects)})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization."""
        return {
            'name': self.name,
            'path': str(self.path),
            'requirements_count': len(self.requirements),
            'tasks_count': len(self.tasks),
            'sub_projects_count': len(self.sub_projects),
            'has_requirements_file': self.has_requirements_file,
            'has_todo_file': self.has_todo_file,
            'has_readme_file': self.has_readme_file,
            'metrics': self.metrics.to_dict(),
            'last_scanned': self.last_scanned.isoformat() if self.last_scanned else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
