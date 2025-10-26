"""Unit tests for DirectoryScanner."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.services.directory_scanner import DirectoryScanner
from src.services.project_detector import ProjectDetector


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def nested_projects(temp_dir):
    """Create nested project structure for testing."""
    # Root project
    (temp_dir / "README.md").write_text("# Root", encoding='utf-8')

    # Subdirectory project
    sub1 = temp_dir / "project1"
    sub1.mkdir()
    (sub1 / "TODO.md").write_text("# Project 1", encoding='utf-8')

    # Nested project
    sub2 = temp_dir / "project1" / "nested"
    sub2.mkdir()
    (sub2 / "REQUIREMENTS.md").write_text("# Nested", encoding='utf-8')

    # Not a project
    sub3 = temp_dir / "not-project"
    sub3.mkdir()
    (sub3 / "random.txt").write_text("random", encoding='utf-8')

    # Ignored directory
    node_modules = temp_dir / "node_modules"
    node_modules.mkdir()
    (node_modules / "README.md").write_text("# Should be ignored", encoding='utf-8')

    return temp_dir


class TestDirectoryScanner:
    """Test DirectoryScanner class."""

    def test_scanner_initialization(self):
        """Test that scanner can be instantiated."""
        scanner = DirectoryScanner()
        assert scanner is not None

    def test_scanner_with_custom_detector(self):
        """Test that scanner accepts custom detector."""
        detector = ProjectDetector()
        scanner = DirectoryScanner(detector=detector)
        assert scanner.detector is detector

    def test_scan_empty_directory(self, temp_dir):
        """Test scanning an empty directory."""
        scanner = DirectoryScanner()
        projects = scanner.scan(temp_dir)

        assert projects == []

    def test_scan_single_project(self, temp_dir):
        """Test scanning directory with single project."""
        (temp_dir / "README.md").write_text("# Project", encoding='utf-8')

        scanner = DirectoryScanner()
        projects = scanner.scan(temp_dir)

        assert len(projects) == 1
        assert projects[0] == temp_dir

    def test_scan_nested_projects(self, nested_projects):
        """Test scanning directory with nested projects."""
        scanner = DirectoryScanner()
        projects = scanner.scan(nested_projects)

        # Should find root, project1, and nested (3 projects)
        assert len(projects) == 3

        paths = [str(p) for p in projects]
        assert str(nested_projects) in paths
        assert str(nested_projects / "project1") in paths
        assert str(nested_projects / "project1" / "nested") in paths

    def test_scan_ignores_node_modules(self, nested_projects):
        """Test that node_modules is ignored."""
        scanner = DirectoryScanner()
        projects = scanner.scan(nested_projects)

        # Should not find project in node_modules
        paths = [str(p) for p in projects]
        assert not any("node_modules" in p for p in paths)

    def test_scan_ignores_not_projects(self, nested_projects):
        """Test that non-project directories are not included."""
        scanner = DirectoryScanner()
        projects = scanner.scan(nested_projects)

        # Should not find "not-project" directory
        paths = [str(p) for p in projects]
        assert not any("not-project" in p for p in paths)

    def test_scan_with_max_depth(self, nested_projects):
        """Test scanning with depth limit."""
        scanner = DirectoryScanner(max_depth=1)
        projects = scanner.scan(nested_projects)

        # Should only find root and project1 (depth 0 and 1)
        assert len(projects) <= 2

    def test_scan_returns_paths(self, temp_dir):
        """Test that scan returns Path objects."""
        (temp_dir / "README.md").write_text("# Project", encoding='utf-8')

        scanner = DirectoryScanner()
        projects = scanner.scan(temp_dir)

        assert len(projects) == 1
        assert isinstance(projects[0], Path)

    def test_scan_non_existent_directory(self):
        """Test scanning non-existent directory raises error."""
        scanner = DirectoryScanner()

        with pytest.raises(FileNotFoundError):
            scanner.scan("/nonexistent/path")

    def test_scan_file_instead_of_directory(self, temp_dir):
        """Test scanning a file instead of directory raises error."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("content", encoding='utf-8')

        scanner = DirectoryScanner()

        with pytest.raises(ValueError, match="not a directory"):
            scanner.scan(file_path)

    def test_scan_returns_sorted_paths(self, nested_projects):
        """Test that scan returns paths in sorted order."""
        scanner = DirectoryScanner()
        projects = scanner.scan(nested_projects)

        # Paths should be sorted
        assert projects == sorted(projects)

    def test_scan_with_callback(self, nested_projects):
        """Test scanning with progress callback."""
        scanned_dirs = []

        def callback(directory: Path):
            scanned_dirs.append(directory)

        scanner = DirectoryScanner()
        projects = scanner.scan(nested_projects, callback=callback)

        # Callback should have been called for each scanned directory
        assert len(scanned_dirs) > 0

    def test_get_project_info(self, temp_dir):
        """Test getting project info for a directory."""
        (temp_dir / "README.md").write_text("# My Project", encoding='utf-8')
        (temp_dir / "TODO.md").write_text("# TODO", encoding='utf-8')

        scanner = DirectoryScanner()
        info = scanner.get_project_info(temp_dir)

        assert info['path'] == str(temp_dir)
        assert info['name'] == temp_dir.name
        assert 'README.md' in info['files']
        assert 'TODO.md' in info['files']

    def test_get_project_info_with_package_json(self, temp_dir):
        """Test getting project info extracts name from package.json."""
        (temp_dir / "package.json").write_text('{"name": "my-package"}', encoding='utf-8')

        scanner = DirectoryScanner()
        info = scanner.get_project_info(temp_dir)

        assert info['name'] == "my-package"
