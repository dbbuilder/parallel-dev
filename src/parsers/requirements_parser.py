"""
REQUIREMENTS.md Parser
Parses REQUIREMENTS markdown files to extract requirements with MoSCoW priorities.
"""

import re
from pathlib import Path
from typing import List

from src.parsers.base_parser import BaseParser
from src.models.requirement import Requirement, RequirementStatus, RequirementPriority


class RequirementsParser(BaseParser):
    """
    Parser for REQUIREMENTS.md files.

    Extracts requirements with:
    - MoSCoW Priority: MUST, SHOULD, COULD, WON'T (also supports CRITICAL, HIGH, MEDIUM, LOW)
    - Category: Extracted from ## headers
    - Requirement numbers: Extracted from numbered lists
    - Line numbers for reference
    - Default status: PLANNED
    """

    # Regex patterns
    REQUIREMENT_PATTERN = re.compile(r'^\s*(\d+)\.\s+(.+)$')
    PRIORITY_PATTERN = re.compile(
        r'^(must|should|could|won\'?t|critical|high|medium|low):\s*(.+)$',
        re.IGNORECASE
    )
    CATEGORY_PATTERN = re.compile(r'^##\s+(.+)$')

    def __init__(self):
        """Initialize the Requirements parser."""
        self.current_category = "General"  # Default category

    def parse(self, file_path: Path | str) -> List[Requirement]:
        """
        Parse a REQUIREMENTS.md file and return list of Requirement objects.

        Args:
            file_path: Path to REQUIREMENTS.md file

        Returns:
            List of Requirement objects

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        content = self._read_file(file_path)
        lines = self._split_into_lines(content)

        requirements = []
        self.current_category = "General"

        for line_num, line in lines:
            # Check for category header (##)
            category_match = self.CATEGORY_PATTERN.match(line)
            if category_match:
                self.current_category = category_match.group(1).strip()
                continue

            # Check for numbered requirement line
            req_match = self.REQUIREMENT_PATTERN.match(line)
            if req_match:
                req_number = int(req_match.group(1))
                req_text = req_match.group(2).strip()

                # Parse priority and description
                priority, description = self._parse_priority_and_description(req_text)

                # Create requirement
                requirement = Requirement(
                    description=description,
                    priority=priority,
                    status=RequirementStatus.PLANNED,  # Default status
                    category=self.current_category,
                    line_number=line_num
                )

                requirements.append(requirement)

        return requirements

    def _parse_priority_and_description(self, req_text: str) -> tuple[RequirementPriority, str]:
        """
        Extract priority and description from requirement text.

        Priority format: "PRIORITY: Description"
        Supports:
        - MoSCoW: MUST (critical), SHOULD (high), COULD (medium), WON'T (low)
        - Direct: CRITICAL, HIGH, MEDIUM, LOW

        Args:
            req_text: Full requirement text

        Returns:
            Tuple of (priority, description)
        """
        priority_match = self.PRIORITY_PATTERN.match(req_text)

        if priority_match:
            priority_str = priority_match.group(1).strip().lower().replace("'", "")
            description = priority_match.group(2).strip()

            # Map string to enum (MoSCoW + direct priorities)
            priority_map = {
                'must': RequirementPriority.CRITICAL,
                'should': RequirementPriority.HIGH,
                'could': RequirementPriority.MEDIUM,
                'wont': RequirementPriority.LOW,
                'critical': RequirementPriority.CRITICAL,
                'high': RequirementPriority.HIGH,
                'medium': RequirementPriority.MEDIUM,
                'low': RequirementPriority.LOW
            }

            priority = priority_map.get(priority_str, RequirementPriority.UNKNOWN)
            return priority, description
        else:
            # No priority prefix found
            return RequirementPriority.UNKNOWN, req_text.strip()
