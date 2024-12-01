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


def test_repo_processor_ignore_explicit_files(temp_repo: Path):
    """Test that RepoProcessor correctly handles explicit file ignores."""
    config = RepoConfig(root_dir=temp_repo)
    config.add_ignore_patterns({'src/main.py'})  # Ignore specific file
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that explicitly ignored file is not included
    assert 'src/main.py' not in output
    # But other files should be included
    assert 'app.ts' in output
    assert 'utils.js' in output


def test_repo_processor_ignore_directories(temp_repo: Path):
    """Test that RepoProcessor correctly handles directory ignores."""
    # Create nested structure
    nested_dir = temp_repo / 'src' / 'nested'
    nested_dir.mkdir()
    test_file = nested_dir / 'test.py'
    test_file.write_text("print('test')")

    config = RepoConfig(root_dir=temp_repo)
    config.add_ignore_patterns({'src/nested'})  # Ignore specific directory
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that files in ignored directory are not included
    assert 'src/nested/test.py' not in output
    # But other files should be included
    assert 'src/main.py' in output


def test_repo_processor_ignore_with_trailing_slash(temp_repo: Path):
    """Test that RepoProcessor handles directory patterns with trailing slashes."""
    config = RepoConfig(root_dir=temp_repo)
    config.add_ignore_patterns({'src/'})  # Ignore with trailing slash
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that all files in src/ are ignored
    assert 'src/main.py' not in output
    assert 'src/app.ts' not in output
    assert 'src/utils.js' not in output


def test_repo_processor_ignore_case_sensitive(temp_repo: Path):
    """Test that ignore patterns are case-sensitive."""
    # Create test files with different cases
    (temp_repo / 'src' / 'Test.py').write_text("print('Test')")
    (temp_repo / 'src' / 'test.py').write_text("print('test')")

    config = RepoConfig(root_dir=temp_repo)
    config.add_ignore_patterns({'src/Test.py'})  # Ignore specific case
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Check that only exact case match is ignored
    assert 'src/Test.py' not in output
    assert 'src/test.py' in output


def test_repo_processor_ignore_patterns(temp_repo: Path):
    """Test that RepoProcessor correctly handles file and directory ignores."""
    # Create nested test structure
    nested_dir = temp_repo / 'src' / 'nested'
    nested_dir.mkdir()
    test_file = nested_dir / 'test.py'
    test_file.write_text("print('test')")

    config = RepoConfig(root_dir=temp_repo)
    # Test both file and directory ignores
    config.add_ignore_patterns({'src/main.py', 'src/nested'})
    processor = RepoProcessor(config)

    output, count = processor.process_repository()

    # Verify ignored files aren't included
    assert 'src/main.py' not in output
    assert 'src/nested/test.py' not in output
    # Verify other files are included
    assert 'src/app.ts' in output


def test_repo_processor_wildcard_ignores(temp_repo: Path):
    """Test that RepoProcessor correctly handles wildcard patterns."""
    # Create test files
    (temp_repo / 'src' / 'test1.py').write_text("print('test1')")
    (temp_repo / 'src' / 'test2.py').write_text("print('test2')")
    (temp_repo / 'src' / 'other.txt').write_text('other')
    nested = temp_repo / 'src' / 'nested'
    nested.mkdir()
    (nested / 'test3.py').write_text("print('test3')")

    config = RepoConfig(root_dir=temp_repo)

    # Test different wildcard patterns
    config.add_ignore_patterns(
        {
            '*.py',  # All Python files
            'src/t*.py',  # Python files starting with t in src/
            '**/nested/*.py',  # Any Python file in a nested directory
        }
    )

    processor = RepoProcessor(config)
    output, count = processor.process_repository()

    # Verify ignored files aren't included
    assert 'test1.py' not in output
    assert 'test2.py' not in output
    assert 'test3.py' not in output
    # Verify non-ignored files are included
    assert 'other.txt' in output


def test_repo_processor_directory_wildcard(temp_repo: Path):
    """Test that RepoProcessor handles directory wildcards correctly."""
    # Create nested test structure
    nested = temp_repo / 'src' / 'nested'
    nested.mkdir()
    (nested / 'test.py').write_text("print('test')")
    (nested / 'deep').mkdir()
    (nested / 'deep' / 'test.py').write_text("print('deep')")

    config = RepoConfig(root_dir=temp_repo)
    config.add_ignore_patterns({'**/nested/**'})  # Ignore nested directory and all subdirs

    processor = RepoProcessor(config)
    output, count = processor.process_repository()

    # Verify all files in nested directories are ignored
    assert 'nested/test.py' not in output
    assert 'nested/deep/test.py' not in output
    # Verify other files still included
    assert 'src/main.py' in output
