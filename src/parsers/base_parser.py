"""
Base Parser Interface
Defines the contract for all markdown parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any


class BaseParser(ABC):
    """
    Abstract base class for markdown file parsers.

    All parsers must implement the parse() method which reads
    a markdown file and returns structured data.
    """

    @abstractmethod
    def parse(self, file_path: Path | str) -> List[Any]:
        """
        Parse a markdown file and return structured data.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of parsed objects (Task, Requirement, etc.)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file content is invalid
        """
        pass

    def _read_file(self, file_path: Path | str) -> str:
        """
        Read file contents safely.

        Args:
            file_path: Path to file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _split_into_lines(self, content: str) -> List[tuple[int, str]]:
        """
        Split content into numbered lines.

        Args:
            content: File content

        Returns:
            List of (line_number, line_text) tuples (1-indexed)
        """
        return [(i + 1, line) for i, line in enumerate(content.split('\n'))]
