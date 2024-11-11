from pathlib import Path

from pydantic import BaseModel, Field

from repo2llm.constants import DEFAULT_IGNORE_PATTERNS
from repo2llm.formatters import get_formatter_for_file


class RepoConfig(BaseModel):
    """Configuration for repository processing."""

    root_dir: Path
    ignore_patterns: set[str] = Field(
        default_factory=lambda: DEFAULT_IGNORE_PATTERNS.copy()
    )
    include_patterns: set[str] | None = None

    def add_ignore_patterns(self, patterns: set[str]) -> None:
        """Add additional ignore patterns to the existing ones."""
        self.ignore_patterns.update(patterns)

    class Config:
        arbitrary_types_allowed = True


class RepoProcessor:
    """Main class for processing repository contents."""

    def __init__(self, config: RepoConfig):
        self.config = config
        # Split patterns into directory names and file patterns
        self.dir_ignores = {p for p in config.ignore_patterns if not p.startswith('*')}
        self.file_patterns = {p for p in config.ignore_patterns if p.startswith('*')}

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

    def process_repository(self) -> str:
        """
        Process the repository and return formatted contents.

        Returns:
            str: Formatted repository contents.
        """
        output: list[str] = []

        try:
            # Get all files in the repository
            for path in sorted(self.config.root_dir.rglob('*')):
                rel_path = None

                if not path.is_file() or self._should_ignore(path):
                    continue

                # If include patterns are specified, check if the file matches any
                if self.config.include_patterns:
                    rel_path = path.relative_to(self.config.root_dir)
                    if not any(
                        rel_path.match(pattern)
                        for pattern in self.config.include_patterns
                    ):
                        continue

                try:
                    # Get relative path from root directory
                    rel_path = path.relative_to(self.config.root_dir)

                    # Get appropriate formatter for file type
                    formatter = get_formatter_for_file(path)
                    if formatter is None:
                        continue

                    # Read and format file content
                    with open(path, encoding='utf-8') as f:
                        content = f.read()

                    formatted_content = formatter.format_content(
                        path=rel_path,
                        content=content,
                    )
                    output.append(formatted_content)

                except Exception as e:
                    output.append(f'\n# Error reading {rel_path}: {e!s}\n')

        except Exception as e:
            output.append(f'\n# Error processing repository: {e!s}\n')

        return '\n'.join(output)
