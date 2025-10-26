"""
Task Data Model
Represents a single task from TODO.md
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class TaskStatus(Enum):
    """Status values for tasks."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Task:
    """Represents a single task with status and priority tracking."""
    
    def __init__(
        self,
        description: str,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.UNKNOWN,
        section: Optional[str] = None,
        stage: Optional[str] = None,
        line_number: int = 0
    ):
        """
        Initialize a task.
        
        Args:
            description: Text description of the task
            status: Current status of the task
            priority: Priority level of the task
            section: Optional section name within the TODO
            stage: Optional stage or phase name
            line_number: Line number in the source file (for reference)
        """
        self.description = description.strip()
        self.status = status
        self.priority = priority
        self.section = section or "General"
        self.stage = stage or "Stage 1"
        self.line_number = line_number
        self.related_requirement_ids: List[str] = []  # IDs of related requirements
        self.estimated_effort: Optional[str] = None  # e.g., "2 hours", "1 day"
        self.created_at = datetime.now()
    
    def __repr__(self) -> str:
        """String representation of the task."""
        return f"Task({self.priority.value}, {self.status.value}: {self.description[:50]}...)"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary for serialization.

        Returns:
            Dictionary containing all task attributes
        """
        return {
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'section': self.section,
            'stage': self.stage,
            'line_number': self.line_number,
            'related_requirement_ids': self.related_requirement_ids.copy(),
            'estimated_effort': self.estimated_effort,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create task from dictionary.

        Args:
            data: Dictionary containing task attributes

        Returns:
            Task instance
        """
        task = cls(
            description=data['description'],
            status=TaskStatus(data.get('status', 'todo')),
            priority=TaskPriority(data.get('priority', 'unknown')),
            section=data.get('section'),
            stage=data.get('stage'),
            line_number=data.get('line_number', 0)
        )

        # Set optional fields if present
        if 'estimated_effort' in data:
            task.estimated_effort = data['estimated_effort']
        if 'related_requirement_ids' in data:
            task.related_requirement_ids = data['related_requirement_ids'].copy()

        return task
