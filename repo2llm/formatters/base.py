from pathlib import Path


class BaseFormatter:
    def format_content(self, path: Path, content: str) -> str:
        """Format content for a file. Filename is placed in XML tag attribute and content is enclosed in tags."""
        normalized_path = self._normalize_path(path)
        if content.strip() == "":
            return f'<file name="{normalized_path}"></file>\n'
        return f'<file name="{normalized_path}">\n\n{content}\n</file>'

    @staticmethod
    def _normalize_path(path: Path) -> str:
        """Convert path to use forward slashes for consistency."""
        return str(path).replace('\\', '/')
