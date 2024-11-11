from pathlib import Path

from pydantic import BaseModel


class ConfigFileSettings(BaseModel):
    """Settings from .repo2llm config file."""

    ignore: set[str] = set()


def find_config_file(start_path: Path) -> Path | None:
    """
    Look for .repo2llm config file in the given directory and its parents.

    Args:
        start_path (Path): Directory to start searching from

    Returns:
        Optional[Path]: Path to config file if found, None otherwise
    """
    current = start_path.absolute()
    while current != current.parent:
        config_file = current / '.repo2llm'
        if config_file.is_file():
            return config_file
        current = current.parent
    return None


def load_config_file(config_path: Path) -> ConfigFileSettings:
    """
    Load and parse the .repo2llm config file.
    The file format is simple, one pattern per line:
    - Lines starting with # are comments
    - Empty lines are ignored
    - Each non-empty line is treated as a path or pattern to ignore

    Example config file:
    # Development directories
    .github/
    .vscode/
    node_modules/

    # Build artifacts
    dist/
    build/
    *.pyc
    __pycache__/

    Args:
        config_path (Path): Path to config file

    Returns:
        ConfigFileSettings: Parsed config settings

    Raises:
        ValueError: If config file has invalid format
        FileNotFoundError: If config file doesn't exist
    """
    settings = ConfigFileSettings()

    try:
        with open(config_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                settings.ignore.add(line)
        return settings

    except UnicodeDecodeError as e:
        raise ValueError(f'Config file {config_path} must be a valid UTF-8 text file') from e
