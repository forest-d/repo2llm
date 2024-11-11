from collections.abc import Generator
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from repo2llm.core import RepoConfig, RepoProcessor


@pytest.fixture
def temp_repo(tmp_path) -> Generator[Path, None, None]:
    """Create a temporary repository with various file types."""
    # Create directory structure
    src = tmp_path / 'src'
    src.mkdir()
    tests = tmp_path / 'tests'
    tests.mkdir()

    # Create some Python files
    main_py = src / 'main.py'
    main_py.write_text(
        dedent("""
        def main():
            print("Hello, World!")

        if __name__ == "__main__":
            main()
    """).strip()
    )

    init_py = src / '__init__.py'
    init_py.write_text('')

    # Create some TypeScript files
    app_ts = src / 'app.ts'
    app_ts.write_text(
        dedent("""
        interface User {
            name: string;
            age: number;
        }

        const user: User = {
            name: "John",
            age: 30
        };
    """).strip()
    )

    # Create some JavaScript files
    utils_js = src / 'utils.js'
    utils_js.write_text(
        dedent("""
        function formatDate(date) {
            return new Date(date).toLocaleDateString();
        }

        module.exports = { formatDate };
    """).strip()
    )

    # Create some files that should be ignored
    (tmp_path / 'node_modules').mkdir()
    (tmp_path / 'node_modules' / 'package.json').write_text('{}')

    (tmp_path / '.git').mkdir()
    (tmp_path / '.git' / 'config').write_text('')

    yield tmp_path


def test_repo_config_validation():
    """Test RepoConfig validation."""
    # Valid configuration
    config = RepoConfig(root_dir=Path('/some/path'))
    assert isinstance(config.ignore_patterns, set)
    assert '__pycache__' in config.ignore_patterns

    # Test with custom ignore patterns
    custom_patterns = {'custom_dir', '*.txt'}
    config = RepoConfig(root_dir=Path('/some/path'))
    config.add_ignore_patterns(custom_patterns)
    assert 'custom_dir' in config.ignore_patterns
    assert '*.txt' in config.ignore_patterns
    # Should still have defaults
    assert '.git' in config.ignore_patterns


def test_repo_processor_ignore_patterns(temp_repo: Path):
    """Test that RepoProcessor correctly handles ignore patterns."""
    config = RepoConfig(root_dir=temp_repo)
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that ignored files are not included
    assert 'node_modules' not in output
    assert '.git' not in output

    # Check that non-ignored files are included
    assert 'main.py' in output
    assert 'app.ts' in output
    assert 'utils.js' in output


@patch('repo2llm.formatters.get_formatter_for_file')
def test_repo_processor_file_content(mock_get_formatter, temp_repo: Path):
    """Test that RepoProcessor correctly processes file content."""

    # Mock the formatter to use consistent path separators
    class MockFormatter:
        def format_content(self, path, content):
            path_str = str(path).replace('\\', '/')
            return f'# {path_str}\n{content}\n'

    mock_get_formatter.return_value = MockFormatter()

    config = RepoConfig(root_dir=temp_repo)
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that file contents are included with correct formatting
    assert 'def main():' in output
    assert 'print("Hello, World!")' in output

    # Check that file paths are included as comments with forward slashes
    assert '<file name="src/main.py">' in output


def test_repo_processor_error_handling(temp_repo: Path):
    """Test that RepoProcessor handles errors gracefully."""
    # Create a file that will cause a UnicodeDecodeError
    binary_file = temp_repo / 'src' / 'binary.py'
    binary_file.write_bytes(bytes([0x80, 0x81, 0x82]))

    config = RepoConfig(root_dir=temp_repo)
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    assert 'binary.py' not in output

    # Check that other files are still processed
    assert 'main.py' in output


@patch('repo2llm.formatters.get_formatter_for_file')
def test_repo_processor_nested_directories(mock_get_formatter, temp_repo: Path):
    """Test that RepoProcessor handles nested directories correctly."""

    # Mock the formatter to use consistent path separators
    class MockFormatter:
        def format_content(self, path, content):
            path_str = str(path).replace('\\', '/')
            return f'<file name="{path_str}">{content}</file>'

    mock_get_formatter.return_value = MockFormatter()

    # Create nested directory structure
    nested_dir = temp_repo / 'src' / 'nested' / 'deep'
    nested_dir.mkdir(parents=True)

    nested_file = nested_dir / 'nested.py'
    nested_file.write_text("print('I am nested!')")

    config = RepoConfig(root_dir=temp_repo)
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that nested files are included with correct paths
    assert '<file name="src/nested/deep/nested.py">' in output

    assert "print('I am nested!')" in output


def test_repo_processor_root_files(temp_repo: Path):
    """Test that RepoProcessor correctly handles files in the root directory."""
    # Create a file in the root directory
    root_file = temp_repo / 'pyproject.toml'
    root_file.write_text("[tool.poetry]\nname = 'test'\nversion = '0.1.0'\n")

    config = RepoConfig(root_dir=temp_repo)
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that root file is included
    assert 'pyproject.toml' in output
    assert '[tool.poetry]' in output
