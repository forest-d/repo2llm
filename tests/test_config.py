import pytest

from repo2llm.config import ConfigFileSettings, find_config_file, load_config_file


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config file."""
    config_file = tmp_path / '.repo2llm'
    config_file.write_text(
        """
# Ignore directories
.github/
.vscode/
node_modules/
__pycache__/

# Ignore files
*.pyc
*.log
*.tmp

# Empty lines and comments are ignored

""",
        encoding='utf-8',
    )
    return config_file


def test_find_config_file(tmp_path):
    """Test finding config file in directory hierarchy."""
    # Create nested directory structure
    deep_dir = tmp_path / 'a' / 'b' / 'c'
    deep_dir.mkdir(parents=True)

    # Create config file in root
    config_file = tmp_path / '.repo2llm'
    config_file.write_text('*.tmp', encoding='utf-8')

    # Should find config from any level
    assert find_config_file(deep_dir) == config_file
    assert find_config_file(tmp_path / 'a') == config_file
    assert find_config_file(tmp_path) == config_file

    # Should return None if no config found
    other_dir = tmp_path.parent / 'other'
    assert find_config_file(other_dir) is None


def test_load_config_file(temp_config):
    """Test loading and parsing config file."""
    config = load_config_file(temp_config)

    assert isinstance(config, ConfigFileSettings)
    assert isinstance(config.ignore, set)

    # Check if expected patterns are present
    assert '.github/' in config.ignore
    assert '.vscode/' in config.ignore
    assert 'node_modules/' in config.ignore
    assert '__pycache__/' in config.ignore
    assert '*.pyc' in config.ignore
    assert '*.log' in config.ignore
    assert '*.tmp' in config.ignore


def test_config_with_comments_and_empty_lines(tmp_path):
    """Test that comments and empty lines are handled correctly."""
    config_file = tmp_path / '.repo2llm'
    config_file.write_text(
        """
# This is a comment
*.tmp

# Another comment
temp/


node_modules/
""",
        encoding='utf-8',
    )

    config = load_config_file(config_file)
    assert len(config.ignore) == 3
    assert '*.tmp' in config.ignore
    assert 'temp/' in config.ignore
    assert 'node_modules/' in config.ignore


def test_config_file_utf8(tmp_path):
    """Test handling of UTF-8 characters in config."""
    config_file = tmp_path / '.repo2llm'
    config_file.write_text(
        """
# UTF-8 characters in comments: 你好
résumé.doc
お気に入り/
""",
        encoding='utf-8',
    )

    config = load_config_file(config_file)
    assert 'résumé.doc' in config.ignore
    assert 'お気に入り/' in config.ignore
