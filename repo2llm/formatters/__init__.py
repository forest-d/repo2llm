from pathlib import Path

from repo2llm.formatters.base import BaseFormatter
from repo2llm.formatters.javascript import JavaScriptFormatter
from repo2llm.formatters.json import JSONFormatter
from repo2llm.formatters.markdown import MarkdownFormatter
from repo2llm.formatters.python import PythonFormatter
from repo2llm.formatters.toml import TOMLFormatter
from repo2llm.formatters.typescript import TypeScriptFormatter
from repo2llm.formatters.yaml import YAMLFormatter

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


def get_formatter_for_file(path: Path) -> BaseFormatter | None:
    """Get the appropriate formatter for a given file path."""
    return FORMATTERS.get(path.suffix)
