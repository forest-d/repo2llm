from unittest.mock import patch

import pytest
from click.testing import CliRunner

from repo2llm.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_pyperclip():
    """Mock pyperclip to prevent actual clipboard operations."""
    with patch('repo2llm.cli.pyperclip') as mock:
        yield mock


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository with various file types."""
    # Create some files
    src = tmp_path / 'src'
    src.mkdir()

    main_py = src / 'main.py'
    main_py.write_text("print('Hello, World!')")

    app_ts = src / 'app.ts'
    for line in range(20):
        app_ts.write_text(f"console.log('TypeScript line {line}');")

    return tmp_path


def test_cli_default_behavior(runner, mock_pyperclip, temp_repo):
    """Test CLI with default options."""
    with runner.isolated_filesystem():
        result = runner.invoke(main, [str(temp_repo)])

        assert result.exit_code == 0
        assert 'copied to clipboard!' in result.output
        assert mock_pyperclip.copy.called


def test_cli_no_preview(runner, mock_pyperclip, temp_repo):
    """Test CLI with preview disabled."""
    result = runner.invoke(main, [str(temp_repo), '--no-preview'])

    assert result.exit_code == 0
    assert 'copied to clipboard!' in result.output
    assert 'Preview of copied content:' not in result.output


def test_cli_custom_preview_length(runner, mock_pyperclip, temp_repo):
    """Test CLI with custom preview length."""
    result = runner.invoke(main, [str(temp_repo), '--preview-length', '10', '--preview'])

    assert result.exit_code == 0
    assert 'Preview of copied content:' in result.output

    assert len(result.output.split()) <= 10 + 11  # +11 to account for rich formatting


def test_cli_ignore_pattern(runner, mock_pyperclip, temp_repo):
    """Test CLI with custom ignore pattern."""
    result = runner.invoke(main, [str(temp_repo), '--ignore', '*.ts', '--preview'])

    assert result.exit_code == 0
    copied_content = mock_pyperclip.copy.call_args[0][0]

    # TypeScript file should be ignored
    assert 'app.ts' not in copied_content
    # Python file should still be included
    assert 'main.py' in copied_content


def test_cli_nonexistent_directory(runner):
    """Test CLI with nonexistent directory."""
    result = runner.invoke(main, ['nonexistent_directory'])

    assert result.exit_code != 0
    assert 'Error' in result.output


@patch('repo2llm.cli.console.print')
def test_cli_error_handling(mock_print, runner, temp_repo):
    """Test CLI error handling."""

    def raise_error(*args, **kwargs):
        raise PermissionError('Access denied')

    with patch('repo2llm.core.RepoProcessor.process_repository', side_effect=raise_error):
        result = runner.invoke(main, [str(temp_repo)])
        assert result.exit_code != 0
        # Check that error message is printed
        assert any('Error' in str(call) for call in mock_print.call_args_list)
