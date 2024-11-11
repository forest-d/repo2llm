from pathlib import Path

from pydantic import BaseModel, Field

from repo2llm.constants import DEFAULT_IGNORE_PATTERNS
from repo2llm.formatters import get_formatter_for_file


class RepoConfig(BaseModel):
    """Configuration for repository processing."""

    root_dir: Path
    ignore_patterns: set[str] = Field(default_factory=lambda: DEFAULT_IGNORE_PATTERNS.copy())

    def add_ignore_patterns(self, patterns: set[str]) -> None:
        """Add additional ignore patterns to the existing ones."""
        self.ignore_patterns.update(patterns)


class RepoProcessor:
    """Main class for processing repository contents."""

    def __init__(self, config: RepoConfig):
        self.config = config

        # Split patterns into directory names and file patterns
        self.dir_ignores = {p for p in config.ignore_patterns if not p.startswith('*')}
        self.file_patterns = {p for p in config.ignore_patterns if p.startswith('*')}

        self.processed_files_count = 0

    def _should_ignore(self, path: Path) -> bool:
        """
        Determine if a file should be ignored using pathlib patterns.

        Args:
            path (Path): Path to check

        Returns:
            bool: True if the file should be ignored
        """
        try:
            # If the path is the same as root_dir, ignore it
            if path == self.config.root_dir:
                return True

            # Get relative path - if path is inside root_dir, this will work
            rel_path = path.relative_to(self.config.root_dir)

            # Check if any parent directory matches ignore patterns
            for part in rel_path.parts:
                if part in self.dir_ignores:
                    return True

            # Check file patterns (*.ext)
            for pattern in self.file_patterns:
                if rel_path.match(pattern):
                    return True

            return False

        except ValueError:
            # Path is outside root_dir
            return True

    def process_repository(self) -> tuple[str, int]:
        """
        Process the repository and return formatted contents.

        Returns:
            str: Formatted repository contents.
        """
        output: list[str] = []
        self.processed_files_count = 0

        try:
            # Get all files in the repository
            for path in sorted(self.config.root_dir.rglob('*')):
                rel_path = None
                if not path.is_file() or self._should_ignore(path):
                    continue

                try:
                    # Get relative path from root directory
                    rel_path = path.relative_to(self.config.root_dir)

                    # Get appropriate formatter for file type
                    formatter = get_formatter_for_file(path)
                    if formatter is None:
                        continue

                    # Try to read the file content
                    try:
                        with open(path, encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        continue
                    except Exception:
                        continue

                    formatted_content = formatter.format_content(
                        path=rel_path,
                        content=content,
                    )
                    output.append(formatted_content)
                    self.processed_files_count += 1

                except Exception as e:
                    print(f'{rel_path} error: {e!s}')

        except Exception:
            raise

        return '\n\n'.join(output), self.processed_files_count
