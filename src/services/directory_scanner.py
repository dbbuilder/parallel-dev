"""
Directory Scanner
Recursively scans directories to find projects.
"""

from pathlib import Path
from typing import List, Callable, Optional, Dict, Any

from src.services.project_detector import ProjectDetector


class DirectoryScanner:
    """
    Recursively scans directories to find software projects.

    Uses ProjectDetector to identify projects and respects
    ignore rules to skip certain directories (node_modules, venv, etc.).
    """

    def __init__(self, detector: Optional[ProjectDetector] = None, max_depth: Optional[int] = None):
        """
        Initialize the directory scanner.

        Args:
            detector: ProjectDetector instance (creates default if None)
            max_depth: Maximum recursion depth (None for unlimited)
        """
        self.detector = detector or ProjectDetector()
        self.max_depth = max_depth

    def scan(
        self,
        root_directory: Path | str,
        callback: Optional[Callable[[Path], None]] = None
    ) -> List[Path]:
        """
        Scan a directory tree and return all project directories.

        Args:
            root_directory: Root directory to start scanning
            callback: Optional callback function called for each scanned directory

        Returns:
            List of Path objects to project directories (sorted)

        Raises:
            FileNotFoundError: If root_directory doesn't exist
            ValueError: If root_directory is not a directory
        """
        root_path = Path(root_directory)

        if not root_path.exists():
            raise FileNotFoundError(f"Directory not found: {root_directory}")

        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_directory}")

        projects = []
        self._scan_recursive(root_path, projects, callback, depth=0)

        # Return sorted list
        return sorted(projects)

    def _scan_recursive(
        self,
        directory: Path,
        projects: List[Path],
        callback: Optional[Callable[[Path], None]],
        depth: int
    ) -> None:
        """
        Recursively scan a directory.

        Args:
            directory: Current directory to scan
            projects: List to accumulate found projects
            callback: Optional callback function
            depth: Current recursion depth
        """
        # Check max depth
        if self.max_depth is not None and depth > self.max_depth:
            return

        # Call callback if provided
        if callback:
            callback(directory)

        # Check if this directory is a project
        if self.detector.is_project(directory):
            projects.append(directory)

        # Scan subdirectories
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    # Skip ignored directories
                    if self.detector.should_ignore(item):
                        continue

                    # Recurse into subdirectory
                    self._scan_recursive(item, projects, callback, depth + 1)

        except PermissionError:
            # Skip directories we can't access
            pass

    def get_project_info(self, directory: Path | str) -> Dict[str, Any]:
        """
        Get information about a project directory.

        Args:
            directory: Path to project directory

        Returns:
            Dictionary with project information:
            - path: Full path as string
            - name: Project name
            - files: List of documentation files present
        """
        path = Path(directory)

        return {
            'path': str(path),
            'name': self.detector.get_project_name(path),
            'files': self.detector.detect_project_files(path)
        }
