from repo2llm.formatters.base import BaseFormatter


class GenericTextFormatter(BaseFormatter):
    """Generic formatter for text files."""

    @staticmethod
    def is_text_file(content: str) -> bool:
        """
        Determine if content appears to be text by checking for common binary file markers.

        Args:
            content (str): File content to check

        Returns:
            bool: True if content appears to be text
        """
        # Check for null bytes which typically indicate binary content
        if '\x00' in content:
            return False

        # Check if content is largely printable ASCII
        printable_ratio = sum(1 for c in content[:1024] if 32 <= ord(c) <= 126 or c in '\n\r\t') / min(
            len(content), 1024
        )
        return printable_ratio > 0.8  # At least 80% should be printable characters
