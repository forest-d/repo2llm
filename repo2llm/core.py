from fnmatch import fnmatch
from importlib import metadata
from pathlib import Path

from pydantic import BaseModel, Field

from repo2llm.constants import DEFAULT_IGNORE_PATTERNS
from repo2llm.formatters import get_formatter_for_file


def get_version() -> str:
    """Get the current version of repo2llm."""
    try:
        return metadata.version('repo2llm')
    except metadata.PackageNotFoundError:
        return 'unknown'


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
        self.processed_files_count = 0

    def _should_ignore(self, path: Path) -> bool:
        """
        Determine if a file should be ignored based on path matching including wildcards.
        Supports glob-style patterns with * and ** wildcards.
        """
        try:
            if path == self.config.root_dir:
                return True

            rel_path = path.relative_to(self.config.root_dir)
            rel_path_str = str(rel_path).replace('\\', '/')

            for pattern in self.config.ignore_patterns:
                # Skip empty patterns
                if not pattern:
                    continue

                # Handle directory pattern (ending with /)
                if pattern.endswith('/'):
                    pattern_without_slash = pattern[:-1]

                    # Case 1: Path is at the root level matching the pattern
                    # e.g., pattern="build/" should match path="build/file.txt"
                    if rel_path_str.startswith(pattern):
                        return True

                    # Case 2: Path contains a directory segment matching the pattern
                    # e.g., pattern="build/" should match path="src/build/output/file.txt"
                    path_parts = rel_path_str.split('/')
                    for i in range(len(path_parts) - 1):  # -1 because we don't check the filename
                        if path_parts[i] == pattern_without_slash:
                            # Make sure it's used as a directory (has something after it)
                            if i < len(path_parts) - 1:
                                return True

                    continue

                # Case 3: Exact path match
                if rel_path_str == pattern:
                    return True

                # Case 4: Path is subdirectory/file of a directory specified without trailing slash
                # e.g., pattern="src/nested" should match path="src/nested/test.py"
                if '/' in pattern and not pattern.endswith('*'):  # Looks like a directory path
                    if rel_path_str.startswith(pattern + '/'):
                        return True

                    # Handle parent directories specified as patterns
                    # Build up path segments and compare
                    segments = rel_path_str.split('/')
                    current = ''
                    for i, seg in enumerate(segments):
                        if i > 0:
                            current += '/'
                        current += seg

                        # Check if current segment matches the pattern
                        if current == pattern:
                            return True

                # Case 5: Wildcard pattern matching
                if fnmatch(rel_path_str, pattern):
                    return True

            return False

        except ValueError:
            return True
        except ZeroDivisionError:
            return True
        except Exception:
            return True

    def process_repository(self) -> tuple[str, int]:
        """Process the repository and return formatted contents."""
        output: list[str] = []
        self.processed_files_count = 0

        try:
            for path in sorted(self.config.root_dir.rglob('*')):
                rel_path = None
                if not path.is_file() or self._should_ignore(path):
                    continue

                try:
                    rel_path = path.relative_to(self.config.root_dir)
                    formatter = get_formatter_for_file(path)
                    if formatter is None:
                        continue

                    try:
                        with open(path, encoding='utf-8') as f:
                            content = f.read()
                    except (UnicodeDecodeError, Exception):
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
