"""Unit tests for Requirement model."""

import pytest
from datetime import datetime
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority


class TestRequirementCreation:
    """Test suite for Requirement creation and initialization."""

    def test_requirement_creation_with_defaults(self):
        """Test creating a requirement with default values."""
        req = Requirement(description="User authentication required")

        assert req.description == "User authentication required"
        assert req.status == RequirementStatus.PLANNED
        assert req.priority == RequirementPriority.UNKNOWN
        assert req.category == "General"
        assert req.line_number == 0
        assert isinstance(req.created_at, datetime)
        assert isinstance(req.related_task_ids, list)
        assert len(req.related_task_ids) == 0

    def test_requirement_creation_with_custom_values(self):
        """Test creating a requirement with custom values."""
        req = Requirement(
            description="  MUST: Support user authentication  ",
            status=RequirementStatus.IN_PROGRESS,
            priority=RequirementPriority.CRITICAL,
            category="Security",
            line_number=15
        )

        assert req.description == "MUST: Support user authentication"  # Trimmed
        assert req.status == RequirementStatus.IN_PROGRESS
        assert req.priority == RequirementPriority.CRITICAL
        assert req.category == "Security"
        assert req.line_number == 15

    def test_requirement_description_whitespace_trimming(self):
        """Test that requirement description whitespace is trimmed."""
        req = Requirement(description="  \n  Requirement with whitespace  \n  ")
        assert req.description == "Requirement with whitespace"

    def test_requirement_with_empty_description(self):
        """Test requirement with empty description."""
        req = Requirement(description="")
        assert req.description == ""

    def test_requirement_category_default(self):
        """Test category defaults to 'General' when None."""
        req = Requirement(description="Test", category=None)
        assert req.category == "General"


class TestRequirementStatus:
    """Test suite for RequirementStatus enum."""

    def test_requirement_status_enum_values(self):
        """Test all requirement status enum values."""
        assert RequirementStatus.PLANNED.value == "planned"
        assert RequirementStatus.IN_PROGRESS.value == "in_progress"
        assert RequirementStatus.COMPLETED.value == "completed"
        assert RequirementStatus.BLOCKED.value == "blocked"

    def test_requirement_status_from_string(self):
        """Test creating RequirementStatus from string."""
        assert RequirementStatus("planned") == RequirementStatus.PLANNED
        assert RequirementStatus("in_progress") == RequirementStatus.IN_PROGRESS
        assert RequirementStatus("completed") == RequirementStatus.COMPLETED
        assert RequirementStatus("blocked") == RequirementStatus.BLOCKED

    def test_all_status_values_unique(self):
        """Test that all status values are unique."""
        values = [status.value for status in RequirementStatus]
        assert len(values) == len(set(values))


class TestRequirementPriority:
    """Test suite for RequirementPriority enum."""

    def test_requirement_priority_enum_values(self):
        """Test all requirement priority enum values."""
        assert RequirementPriority.CRITICAL.value == "critical"
        assert RequirementPriority.HIGH.value == "high"
        assert RequirementPriority.MEDIUM.value == "medium"
        assert RequirementPriority.LOW.value == "low"
        assert RequirementPriority.UNKNOWN.value == "unknown"

    def test_requirement_priority_from_string(self):
        """Test creating RequirementPriority from string."""
        assert RequirementPriority("critical") == RequirementPriority.CRITICAL
        assert RequirementPriority("high") == RequirementPriority.HIGH
        assert RequirementPriority("medium") == RequirementPriority.MEDIUM
        assert RequirementPriority("low") == RequirementPriority.LOW
        assert RequirementPriority("unknown") == RequirementPriority.UNKNOWN

    def test_all_priority_values_unique(self):
        """Test that all priority values are unique."""
        values = [priority.value for priority in RequirementPriority]
        assert len(values) == len(set(values))


class TestRequirementRelationships:
    """Test suite for requirement relationships and metadata."""

    def test_requirement_related_tasks_list(self):
        """Test related tasks list initialization and usage."""
        req = Requirement("User authentication")
        assert req.related_task_ids == []

        req.related_task_ids.append("TASK-001")
        req.related_task_ids.append("TASK-002")

        assert len(req.related_task_ids) == 2
        assert "TASK-001" in req.related_task_ids
        assert "TASK-002" in req.related_task_ids

    def test_requirement_created_at_timestamp(self):
        """Test created_at is a valid datetime."""
        req = Requirement("Test")
        assert isinstance(req.created_at, datetime)
        assert req.created_at <= datetime.now()


class TestRequirementRepresentation:
    """Test suite for requirement string representation."""

    def test_requirement_repr_contains_key_info(self):
        """Test requirement __repr__ contains key information."""
        req = Requirement(
            "MUST: Implement authentication with OAuth2 and JWT tokens",
            priority=RequirementPriority.CRITICAL,
            status=RequirementStatus.IN_PROGRESS
        )
        repr_str = repr(req)

        assert "Requirement" in repr_str
        assert "critical" in repr_str
        assert "in_progress" in repr_str

    def test_requirement_repr_for_each_status(self):
        """Test __repr__ for each status type."""
        for status in RequirementStatus:
            req = Requirement("Test", status=status)
            repr_str = repr(req)
            assert status.value in repr_str

    def test_requirement_repr_for_each_priority(self):
        """Test __repr__ for each priority type."""
        for priority in RequirementPriority:
            req = Requirement("Test", priority=priority)
            repr_str = repr(req)
            assert priority.value in repr_str


class TestRequirementSerialization:
    """Test suite for requirement serialization."""

    def test_requirement_to_dict(self):
        """Test converting requirement to dictionary."""
        req = Requirement(
            description="MUST: User authentication",
            status=RequirementStatus.COMPLETED,
            priority=RequirementPriority.CRITICAL,
            category="Security",
            line_number=25
        )
        req.related_task_ids = ["TASK-001", "TASK-002"]

        req_dict = req.to_dict()

        assert req_dict['description'] == "MUST: User authentication"
        assert req_dict['status'] == "completed"
        assert req_dict['priority'] == "critical"
        assert req_dict['category'] == "Security"
        assert req_dict['line_number'] == 25
        assert req_dict['related_task_ids'] == ["TASK-001", "TASK-002"]
        assert 'created_at' in req_dict

    def test_requirement_from_dict(self):
        """Test creating requirement from dictionary."""
        data = {
            'description': 'SHOULD: Support multi-language',
            'status': 'in_progress',
            'priority': 'high',
            'category': 'Features',
            'line_number': 42
        }

        req = Requirement.from_dict(data)

        assert req.description == "SHOULD: Support multi-language"
        assert req.status == RequirementStatus.IN_PROGRESS
        assert req.priority == RequirementPriority.HIGH
        assert req.category == "Features"
        assert req.line_number == 42

    def test_requirement_from_dict_with_defaults(self):
        """Test creating requirement from minimal dictionary."""
        data = {'description': 'Minimal requirement'}

        req = Requirement.from_dict(data)

        assert req.description == "Minimal requirement"
        assert req.status == RequirementStatus.PLANNED
        assert req.priority == RequirementPriority.UNKNOWN

    def test_requirement_serialization_roundtrip(self):
        """Test requirement can be serialized and deserialized."""
        original = Requirement(
            description="MUST: Data encryption",
            status=RequirementStatus.IN_PROGRESS,
            priority=RequirementPriority.CRITICAL,
            category="Security"
        )
        original.related_task_ids = ["TASK-003"]

        req_dict = original.to_dict()
        restored = Requirement.from_dict(req_dict)

        assert restored.description == original.description
        assert restored.status == original.status
        assert restored.priority == original.priority
        assert restored.category == original.category
        assert len(restored.related_task_ids) == 1
        assert restored.related_task_ids[0] == "TASK-003"


class TestRequirementMoSCoW:
    """Test suite for MoSCoW priority parsing (future enhancement)."""

    def test_moscow_must_detection(self):
        """Test MUST requirements can be identified."""
        req = Requirement("MUST: User authentication required")
        # Future: auto-detect priority from description
        assert "MUST" in req.description

    def test_moscow_should_detection(self):
        """Test SHOULD requirements can be identified."""
        req = Requirement("SHOULD: Support export to CSV")
        assert "SHOULD" in req.description

    def test_moscow_could_detection(self):
        """Test COULD requirements can be identified."""
        req = Requirement("COULD: Add dark mode theme")
        assert "COULD" in req.description

    def test_moscow_wont_detection(self):
        """Test WON'T requirements can be identified."""
        req = Requirement("WON'T: Support Internet Explorer 11")
        assert "WON'T" in req.description
