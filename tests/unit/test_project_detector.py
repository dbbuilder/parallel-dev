"""Unit tests for ProjectDetector."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.services.project_detector import ProjectDetector


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestProjectDetector:
    """Test ProjectDetector class."""

    def test_detector_initialization(self):
        """Test that detector can be instantiated."""
        detector = ProjectDetector()
        assert detector is not None

    def test_is_project_with_requirements_file(self, temp_dir):
        """Test that directory with REQUIREMENTS.md is detected as project."""
        req_file = temp_dir / "REQUIREMENTS.md"
        req_file.write_text("# Requirements", encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_project_with_todo_file(self, temp_dir):
        """Test that directory with TODO.md is detected as project."""
        todo_file = temp_dir / "TODO.md"
        todo_file.write_text("# TODO", encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_project_with_readme_file(self, temp_dir):
        """Test that directory with README.md is detected as project."""
        readme_file = temp_dir / "README.md"
        readme_file.write_text("# Project", encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_project_with_package_json(self, temp_dir):
        """Test that directory with package.json is detected as project."""
        package_file = temp_dir / "package.json"
        package_file.write_text('{"name": "test"}', encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_project_with_pyproject_toml(self, temp_dir):
        """Test that directory with pyproject.toml is detected as project."""
        pyproject_file = temp_dir / "pyproject.toml"
        pyproject_file.write_text('[tool.poetry]', encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_project_with_cargo_toml(self, temp_dir):
        """Test that directory with Cargo.toml is detected as project."""
        cargo_file = temp_dir / "Cargo.toml"
        cargo_file.write_text('[package]', encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_project_with_git_directory(self, temp_dir):
        """Test that directory with .git is detected as project."""
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is True

    def test_is_not_project_empty_directory(self, temp_dir):
        """Test that empty directory is not detected as project."""
        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is False

    def test_is_not_project_with_only_random_files(self, temp_dir):
        """Test that directory with only random files is not a project."""
        random_file = temp_dir / "random.txt"
        random_file.write_text("random content", encoding='utf-8')

        detector = ProjectDetector()
        assert detector.is_project(temp_dir) is False

    def test_should_ignore_node_modules(self, temp_dir):
        """Test that node_modules directory is ignored."""
        detector = ProjectDetector()
        node_modules = temp_dir / "node_modules"
        node_modules.mkdir()

        assert detector.should_ignore(node_modules) is True

    def test_should_ignore_venv(self, temp_dir):
        """Test that venv directory is ignored."""
        detector = ProjectDetector()
        venv = temp_dir / "venv"
        venv.mkdir()

        assert detector.should_ignore(venv) is True

    def test_should_ignore_git(self, temp_dir):
        """Test that .git directory is ignored."""
        detector = ProjectDetector()
        git_dir = temp_dir / ".git"
        git_dir.mkdir()

        assert detector.should_ignore(git_dir) is True

    def test_should_ignore_pycache(self, temp_dir):
        """Test that __pycache__ directory is ignored."""
        detector = ProjectDetector()
        pycache = temp_dir / "__pycache__"
        pycache.mkdir()

        assert detector.should_ignore(pycache) is True

    def test_should_ignore_dist(self, temp_dir):
        """Test that dist directory is ignored."""
        detector = ProjectDetector()
        dist_dir = temp_dir / "dist"
        dist_dir.mkdir()

        assert detector.should_ignore(dist_dir) is True

    def test_should_not_ignore_normal_directory(self, temp_dir):
        """Test that normal directories are not ignored."""
        detector = ProjectDetector()
        normal_dir = temp_dir / "src"
        normal_dir.mkdir()

        assert detector.should_ignore(normal_dir) is False

    def test_get_project_name_from_directory(self, temp_dir):
        """Test extracting project name from directory name."""
        detector = ProjectDetector()
        project_dir = temp_dir / "my-awesome-project"
        project_dir.mkdir()

        name = detector.get_project_name(project_dir)
        assert name == "my-awesome-project"

    def test_get_project_name_from_package_json(self, temp_dir):
        """Test extracting project name from package.json."""
        package_file = temp_dir / "package.json"
        package_file.write_text('{"name": "my-package"}', encoding='utf-8')

        detector = ProjectDetector()
        name = detector.get_project_name(temp_dir)
        assert name == "my-package"

    def test_get_project_name_from_pyproject_toml(self, temp_dir):
        """Test extracting project name from pyproject.toml."""
        pyproject_file = temp_dir / "pyproject.toml"
        content = """[tool.poetry]
name = "my-python-project"
version = "0.1.0"
"""
        pyproject_file.write_text(content, encoding='utf-8')

        detector = ProjectDetector()
        name = detector.get_project_name(temp_dir)
        assert name == "my-python-project"

    def test_get_project_name_from_cargo_toml(self, temp_dir):
        """Test extracting project name from Cargo.toml."""
        cargo_file = temp_dir / "Cargo.toml"
        content = """[package]
name = "my-rust-project"
version = "0.1.0"
"""
        cargo_file.write_text(content, encoding='utf-8')

        detector = ProjectDetector()
        name = detector.get_project_name(temp_dir)
        assert name == "my-rust-project"

    def test_get_project_name_fallback_to_directory(self, temp_dir):
        """Test fallback to directory name when no config files exist."""
        detector = ProjectDetector()
        name = detector.get_project_name(temp_dir)
        assert name == temp_dir.name

    def test_detect_project_files(self, temp_dir):
        """Test detecting which key files are present."""
        # Create project files
        (temp_dir / "README.md").write_text("# Project", encoding='utf-8')
        (temp_dir / "TODO.md").write_text("# TODO", encoding='utf-8')

        detector = ProjectDetector()
        files = detector.detect_project_files(temp_dir)

        assert "README.md" in files
        assert "TODO.md" in files
        assert "REQUIREMENTS.md" not in files

    def test_detect_all_project_files(self, temp_dir):
        """Test detecting all possible project files."""
        # Create all files
        (temp_dir / "README.md").write_text("# README", encoding='utf-8')
        (temp_dir / "TODO.md").write_text("# TODO", encoding='utf-8')
        (temp_dir / "REQUIREMENTS.md").write_text("# REQ", encoding='utf-8')

        detector = ProjectDetector()
        files = detector.detect_project_files(temp_dir)

        assert len(files) == 3
        assert all(f in files for f in ["README.md", "TODO.md", "REQUIREMENTS.md"])
