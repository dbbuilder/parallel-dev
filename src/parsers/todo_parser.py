"""
TODO.md Parser
Parses TODO markdown files to extract tasks with status, priority, and hierarchy.
"""

import re
from pathlib import Path
from typing import List

from src.parsers.base_parser import BaseParser
from src.models.task import Task, TaskStatus, TaskPriority


class TodoParser(BaseParser):
    """
    Parser for TODO.md files.

    Extracts tasks with:
    - Status: [ ] (todo), [x] (done), [~] (in progress)
    - Priority: Critical, High, Medium, Low (prefix before description)
    - Stage: Extracted from ## headers
    - Section: Extracted from ### headers
    - Line numbers for reference
    """

    # Regex patterns
    TASK_PATTERN = re.compile(r'^\s*-\s*\[([x~\s])\]\s*(.+)$', re.IGNORECASE)
    PRIORITY_PATTERN = re.compile(r'^(critical|high|medium|low):\s*(.+)$', re.IGNORECASE)
    STAGE_PATTERN = re.compile(r'^##\s+(.+)$')
    SECTION_PATTERN = re.compile(r'^###\s+(.+)$')

    def __init__(self):
        """Initialize the TODO parser."""
        self.current_stage = "Stage 1"  # Default stage
        self.current_section = "General"  # Default section

    def parse(self, file_path: Path | str) -> List[Task]:
        """
        Parse a TODO.md file and return list of Task objects.

        Args:
            file_path: Path to TODO.md file

        Returns:
            List of Task objects

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        content = self._read_file(file_path)
        lines = self._split_into_lines(content)

        tasks = []
        self.current_stage = "Stage 1"
        self.current_section = "General"

        for line_num, line in lines:
            # Check for stage header (##)
            stage_match = self.STAGE_PATTERN.match(line)
            if stage_match:
                self.current_stage = stage_match.group(1).strip()
                continue

            # Check for section header (###)
            section_match = self.SECTION_PATTERN.match(line)
            if section_match:
                self.current_section = section_match.group(1).strip()
                continue

            # Check for task line
            task_match = self.TASK_PATTERN.match(line)
            if task_match:
                status_char = task_match.group(1)
                task_text = task_match.group(2).strip()

                # Parse status
                status = self._parse_status(status_char)

                # Parse priority and description
                priority, description = self._parse_priority_and_description(task_text)

                # Create task
                task = Task(
                    description=description,
                    status=status,
                    priority=priority,
                    section=self.current_section,
                    stage=self.current_stage,
                    line_number=line_num
                )

                tasks.append(task)

        return tasks

    def _parse_status(self, status_char: str) -> TaskStatus:
        """
        Parse status character to TaskStatus enum.

        Args:
            status_char: Character inside brackets (x, ~, or space)

        Returns:
            TaskStatus enum value
        """
        status_char = status_char.strip().lower()

        if status_char == 'x':
            return TaskStatus.DONE
        elif status_char == '~':
            return TaskStatus.IN_PROGRESS
        else:
            return TaskStatus.TODO

    def _parse_priority_and_description(self, task_text: str) -> tuple[TaskPriority, str]:
        """
        Extract priority and description from task text.

        Priority format: "Priority: Description"
        Example: "High: Implement feature X"

        Args:
            task_text: Full task text

        Returns:
            Tuple of (priority, description)
        """
        priority_match = self.PRIORITY_PATTERN.match(task_text)

        if priority_match:
            priority_str = priority_match.group(1).strip().lower()
            description = priority_match.group(2).strip()

            # Map string to enum
            priority_map = {
                'critical': TaskPriority.CRITICAL,
                'high': TaskPriority.HIGH,
                'medium': TaskPriority.MEDIUM,
                'low': TaskPriority.LOW
            }

            priority = priority_map.get(priority_str, TaskPriority.UNKNOWN)
            return priority, description
        else:
            # No priority prefix found
            return TaskPriority.UNKNOWN, task_text.strip()
