from pathlib import Path

from repo2llm.formatters.base import BaseFormatter
from repo2llm.formatters.generic import GenericTextFormatter
from repo2llm.formatters.javascript import JavaScriptFormatter
from repo2llm.formatters.json import JSONFormatter
from repo2llm.formatters.markdown import MarkdownFormatter
from repo2llm.formatters.python import PythonFormatter
from repo2llm.formatters.toml import TOMLFormatter
from repo2llm.formatters.typescript import TypeScriptFormatter
from repo2llm.formatters.yaml import YAMLFormatter

# Extensions that should be ignored even with fallback
BINARY_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.pyd',  # Python bytecode
    '.so',
    '.dll',
    '.dylib',  # Shared libraries
    '.exe',
    '.bin',  # Executables
    '.zip',
    '.tar',
    '.gz',
    '.bz2',
    '.7z',
    '.rar',  # Archives
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.bmp',
    '.ico',  # Images
    '.mp3',
    '.wav',
    '.ogg',  # Audio
    '.mp4',
    '.avi',
    '.mov',  # Video
    '.pdf',
    '.doc',
    '.docx',
    '.xls',
    '.xlsx',  # Documents
    '.db',
    '.sqlite',
    '.sqlite3',  # Databases
}

# Mapping of file extensions to formatters
FORMATTERS = {
    '.py': PythonFormatter(),
    '.js': JavaScriptFormatter(),
    '.jsx': JavaScriptFormatter(),
    '.ts': TypeScriptFormatter(),
    '.tsx': TypeScriptFormatter(),
    '.json': JSONFormatter(),
    '.toml': TOMLFormatter(),
    '.yaml': YAMLFormatter(),
    '.yml': YAMLFormatter(),
    '.md': MarkdownFormatter(),
}

# Generic formatter for fallback
GENERIC_FORMATTER = GenericTextFormatter()


def get_formatter_for_file(path: Path) -> BaseFormatter | None:
    """
    Get the appropriate formatter for a given file path.
    Falls back to generic text formatter for unknown extensions
    if the file appears to be text.

    Args:
        path (Path): Path to the file

    Returns:
        Optional[BaseFormatter]: Formatter instance or None if file should be ignored
    """
    # First check if it's a known binary extension
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return None

    # Use specific formatter if available
    if path.suffix.lower() in FORMATTERS:
        return FORMATTERS[path.suffix.lower()]

    # Try to read the start of the file to check if it's text
    try:
        # Read first 1024 bytes to check content type
        with open(path, encoding='utf-8') as f:
            content_sample = f.read(1024)

        # If it appears to be text, use generic formatter
        if GENERIC_FORMATTER.is_text_file(content_sample):
            return GENERIC_FORMATTER

    except (OSError, UnicodeDecodeError):
        # If we can't read it as text, ignore it
        return None

    return None
