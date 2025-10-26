"""
Requirement Data Model
Represents a single requirement from REQUIREMENTS.md
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class RequirementStatus(Enum):
    """Status values for requirements."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class RequirementPriority(Enum):
    """Priority levels for requirements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Requirement:
    """Represents a single requirement with status and priority tracking."""
    
    def __init__(
        self,
        description: str,
        status: RequirementStatus = RequirementStatus.PLANNED,
        priority: RequirementPriority = RequirementPriority.UNKNOWN,
        category: Optional[str] = None,
        line_number: int = 0
    ):
        """
        Initialize a requirement.
        
        Args:
            description: Text description of the requirement
            status: Current status of the requirement
            priority: Priority level of the requirement
            category: Optional category or section name
            line_number: Line number in the source file (for reference)
        """
        self.description = description.strip()
        self.status = status
        self.priority = priority
        self.category = category or "General"
        self.line_number = line_number
        self.related_task_ids: List[str] = []  # IDs of related tasks
        self.created_at = datetime.now()
    
    def __repr__(self) -> str:
        """String representation of the requirement."""
        return f"Requirement({self.priority.value}, {self.status.value}: {self.description[:50]}...)"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert requirement to dictionary for serialization.

        Returns:
            Dictionary containing all requirement attributes
        """
        return {
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'category': self.category,
            'line_number': self.line_number,
            'related_task_ids': self.related_task_ids.copy(),
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        """
        Create requirement from dictionary.

        Args:
            data: Dictionary containing requirement attributes

        Returns:
            Requirement instance
        """
        req = cls(
            description=data['description'],
            status=RequirementStatus(data.get('status', 'planned')),
            priority=RequirementPriority(data.get('priority', 'unknown')),
            category=data.get('category'),
            line_number=data.get('line_number', 0)
        )

        # Set optional fields if present
        if 'related_task_ids' in data:
            req.related_task_ids = data['related_task_ids'].copy()

        return req
