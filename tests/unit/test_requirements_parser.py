"""Unit tests for REQUIREMENTS.md parser."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.parsers.requirements_parser import RequirementsParser
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_requirements_file(temp_dir):
    """Create sample REQUIREMENTS.md file."""
    req_path = temp_dir / "REQUIREMENTS.md"
    content = """# Project Requirements

## Functional Requirements

### Core Features
1. MUST: System shall support user authentication
2. SHOULD: System should cache frequently accessed data
3. COULD: System could support dark mode
4. WON'T: System will not support IE11

## Technical Requirements

### Performance
5. MUST: API response time shall be under 200ms
6. CRITICAL: Database queries must use indexes
"""
    req_path.write_text(content, encoding='utf-8')
    return req_path


class TestRequirementsParser:
    """Test RequirementsParser class."""

    def test_parser_initialization(self):
        """Test that parser can be instantiated."""
        parser = RequirementsParser()
        assert parser is not None

    def test_parse_empty_file(self, temp_dir):
        """Test parsing an empty file."""
        empty_file = temp_dir / "empty.md"
        empty_file.write_text("", encoding='utf-8')

        parser = RequirementsParser()
        requirements = parser.parse(empty_file)

        assert requirements == []

    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error."""
        parser = RequirementsParser()

        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.md")

    def test_parse_must_priority(self, temp_dir):
        """Test parsing MUST requirement."""
        req_file = temp_dir / "must.md"
        req_file.write_text("1. MUST: System shall do X", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].description == "System shall do X"
        assert reqs[0].priority == RequirementPriority.CRITICAL

    def test_parse_should_priority(self, temp_dir):
        """Test parsing SHOULD requirement."""
        req_file = temp_dir / "should.md"
        req_file.write_text("1. SHOULD: System should do Y", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].priority == RequirementPriority.HIGH

    def test_parse_could_priority(self, temp_dir):
        """Test parsing COULD requirement."""
        req_file = temp_dir / "could.md"
        req_file.write_text("1. COULD: System could do Z", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].priority == RequirementPriority.MEDIUM

    def test_parse_wont_priority(self, temp_dir):
        """Test parsing WON'T requirement."""
        req_file = temp_dir / "wont.md"
        req_file.write_text("1. WON'T: System will not do W", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].priority == RequirementPriority.LOW

    def test_parse_critical_priority(self, temp_dir):
        """Test parsing CRITICAL priority."""
        req_file = temp_dir / "critical.md"
        req_file.write_text("1. CRITICAL: Critical requirement", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].priority == RequirementPriority.CRITICAL

    def test_parse_all_moscow_priorities(self, temp_dir):
        """Test parsing all MoSCoW priority levels."""
        req_file = temp_dir / "moscow.md"
        content = """
1. MUST: Must have feature
2. SHOULD: Should have feature
3. COULD: Could have feature
4. WON'T: Won't have feature
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 4
        assert reqs[0].priority == RequirementPriority.CRITICAL
        assert reqs[1].priority == RequirementPriority.HIGH
        assert reqs[2].priority == RequirementPriority.MEDIUM
        assert reqs[3].priority == RequirementPriority.LOW

    def test_parse_multiple_numbered_requirements(self, temp_dir):
        """Test that multiple numbered requirements are parsed."""
        req_file = temp_dir / "numbers.md"
        content = """
1. MUST: First requirement
2. MUST: Second requirement
15. SHOULD: Fifteenth requirement
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 3
        assert reqs[0].description == "First requirement"
        assert reqs[1].description == "Second requirement"
        assert reqs[2].description == "Fifteenth requirement"

    def test_parse_with_category_header(self, temp_dir):
        """Test parsing requirements under category headers (##)."""
        req_file = temp_dir / "categories.md"
        content = """
## Functional Requirements
1. MUST: Functional req 1

## Technical Requirements
2. MUST: Technical req 2
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 2
        assert reqs[0].category == "Functional Requirements"
        assert reqs[1].category == "Technical Requirements"

    def test_parse_line_numbers(self, temp_dir):
        """Test that line numbers are captured."""
        req_file = temp_dir / "lines.md"
        content = """# Header

1. MUST: Req on line 3
2. SHOULD: Req on line 4
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 2
        assert reqs[0].line_number == 3
        assert reqs[1].line_number == 4

    def test_parse_ignore_non_requirement_lines(self, temp_dir):
        """Test that non-requirement lines are ignored."""
        req_file = temp_dir / "mixed.md"
        content = """# Requirements

Some paragraph text.

1. MUST: Valid requirement
- Not a numbered item
* Bullet point

Regular text line
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        # Should only parse the one valid requirement
        assert len(reqs) == 1
        assert reqs[0].description == "Valid requirement"

    def test_parse_sample_fixture_file(self):
        """Test parsing the actual sample_requirements.md fixture."""
        fixture_path = Path("tests/fixtures/sample_requirements.md")

        parser = RequirementsParser()
        reqs = parser.parse(fixture_path)

        # Verify we got requirements
        assert len(reqs) > 0

        # Check for specific requirements
        descriptions = [r.description for r in reqs]
        assert "System shall recursively scan configured directories" in descriptions

        # Check priority mix
        priorities = [r.priority for r in reqs]
        assert RequirementPriority.CRITICAL in priorities
        assert RequirementPriority.HIGH in priorities
        assert RequirementPriority.MEDIUM in priorities
        assert RequirementPriority.LOW in priorities

    def test_parse_multiple_categories(self, sample_requirements_file):
        """Test parsing file with multiple categories."""
        parser = RequirementsParser()
        reqs = parser.parse(sample_requirements_file)

        assert len(reqs) > 0

        # Check that categories are assigned
        categories = {r.category for r in reqs}
        assert "Functional Requirements" in categories
        assert "Technical Requirements" in categories

    def test_parse_returns_requirement_objects(self, sample_requirements_file):
        """Test that parser returns Requirement model instances."""
        parser = RequirementsParser()
        reqs = parser.parse(sample_requirements_file)

        assert len(reqs) > 0
        assert all(isinstance(req, Requirement) for req in reqs)

    def test_whitespace_handling(self, temp_dir):
        """Test that extra whitespace is handled correctly."""
        req_file = temp_dir / "whitespace.md"
        content = """
1.  MUST:   Requirement with extra spaces

2. SHOULD: Normal spacing requirement
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 2
        # Whitespace should be trimmed
        assert reqs[0].description == "Requirement with extra spaces"
        assert reqs[1].description == "Normal spacing requirement"

    def test_case_insensitive_priority(self, temp_dir):
        """Test that priority matching is case-insensitive."""
        req_file = temp_dir / "case.md"
        content = """
1. MUST: Uppercase priority
2. must: Lowercase priority
3. Must: Mixed case priority
"""
        req_file.write_text(content, encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 3
        assert all(r.priority == RequirementPriority.CRITICAL for r in reqs)

    def test_default_status_is_planned(self, temp_dir):
        """Test that requirements default to PLANNED status."""
        req_file = temp_dir / "status.md"
        req_file.write_text("1. MUST: New requirement", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].status == RequirementStatus.PLANNED

    def test_requirement_without_priority_prefix(self, temp_dir):
        """Test parsing requirement without priority prefix gets UNKNOWN."""
        req_file = temp_dir / "no_priority.md"
        req_file.write_text("1. Requirement without priority", encoding='utf-8')

        parser = RequirementsParser()
        reqs = parser.parse(req_file)

        assert len(reqs) == 1
        assert reqs[0].priority == RequirementPriority.UNKNOWN
        assert reqs[0].description == "Requirement without priority"
