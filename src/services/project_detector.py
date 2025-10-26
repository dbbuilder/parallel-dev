"""
Project Detector
Identifies directories that contain software projects.
"""

import json
import tomllib
from pathlib import Path
from typing import List, Set


class ProjectDetector:
    """
    Detects if a directory contains a software project.

    A project is identified by the presence of:
    - Documentation files: README.md, TODO.md, REQUIREMENTS.md
    - Config files: package.json, pyproject.toml, Cargo.toml, composer.json
    - Version control: .git directory
    """

    # Files that indicate a project
    PROJECT_INDICATORS = {
        'README.md',
        'TODO.md',
        'REQUIREMENTS.md',
        'package.json',
        'pyproject.toml',
        'Cargo.toml',
        'composer.json',
        'go.mod',
        'pom.xml',
        'build.gradle',
        '.git'
    }

    # Directories to ignore during scanning
    IGNORED_DIRECTORIES = {
        'node_modules',
        'venv',
        '.venv',
        'env',
        '.env',
        '__pycache__',
        '.git',
        '.svn',
        '.hg',
        'dist',
        'build',
        'target',
        '.idea',
        '.vscode',
        'htmlcov',
        '.pytest_cache',
        '.mypy_cache',
        'coverage'
    }

    def is_project(self, directory: Path | str) -> bool:
        """
        Check if a directory contains a project.

        Args:
            directory: Path to directory to check

        Returns:
            True if directory contains project indicators
        """
        path = Path(directory)

        if not path.exists() or not path.is_dir():
            return False

        # Check for any project indicator files/directories
        for indicator in self.PROJECT_INDICATORS:
            if (path / indicator).exists():
                return True

        return False

    def should_ignore(self, directory: Path | str) -> bool:
        """
        Check if a directory should be ignored during scanning.

        Args:
            directory: Path to directory to check

        Returns:
            True if directory should be ignored
        """
        path = Path(directory)
        return path.name in self.IGNORED_DIRECTORIES

    def get_project_name(self, directory: Path | str) -> str:
        """
        Extract project name from directory or config files.

        Tries in order:
        1. package.json (Node.js)
        2. pyproject.toml (Python)
        3. Cargo.toml (Rust)
        4. Directory name (fallback)

        Args:
            directory: Path to project directory

        Returns:
            Project name as string
        """
        path = Path(directory)

        # Try package.json
        package_json = path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'name' in data:
                        return data['name']
            except (json.JSONDecodeError, IOError):
                pass

        # Try pyproject.toml
        pyproject_toml = path / "pyproject.toml"
        if pyproject_toml.exists():
            try:
                with open(pyproject_toml, 'rb') as f:
                    data = tomllib.load(f)
                    if 'tool' in data and 'poetry' in data['tool']:
                        if 'name' in data['tool']['poetry']:
                            return data['tool']['poetry']['name']
                    if 'project' in data and 'name' in data['project']:
                        return data['project']['name']
            except (tomllib.TOMLDecodeError, IOError):
                pass

        # Try Cargo.toml
        cargo_toml = path / "Cargo.toml"
        if cargo_toml.exists():
            try:
                with open(cargo_toml, 'rb') as f:
                    data = tomllib.load(f)
                    if 'package' in data and 'name' in data['package']:
                        return data['package']['name']
            except (tomllib.TOMLDecodeError, IOError):
                pass

        # Fallback to directory name
        return path.name

    def detect_project_files(self, directory: Path | str) -> List[str]:
        """
        Detect which documentation files are present in the project.

        Args:
            directory: Path to project directory

        Returns:
            List of detected file names
        """
        path = Path(directory)
        found_files = []

        documentation_files = ['README.md', 'TODO.md', 'REQUIREMENTS.md']

        for filename in documentation_files:
            if (path / filename).exists():
                found_files.append(filename)

        return found_files
