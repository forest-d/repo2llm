from pathlib import Path

import pytest

from repo2llm.formatters.generic import GenericTextFormatter


@pytest.fixture
def formatter():
    """Create a GenericTextFormatter instance."""
    return GenericTextFormatter()


def test_format_content(formatter):
    """Test basic content formatting."""
    path = Path('test.txt')
    content = 'Hello, World!'

    formatted = formatter.format_content(path, content)

    assert formatted == '<file name="test.txt">\n\nHello, World!\n</file>'


def test_format_empty_content(formatter):
    """Test formatting empty content."""
    path = Path('empty.txt')
    content = ''

    formatted = formatter.format_content(path, content)

    assert formatted == '<file name="empty.txt"></file>\n'


def test_format_whitespace_only_content(formatter):
    """Test formatting whitespace-only content."""
    path = Path('whitespace.txt')
    content = '   \n  \t  \n'

    formatted = formatter.format_content(path, content)

    assert formatted == '<file name="whitespace.txt"></file>\n'


def test_is_text_file_with_text_content(formatter):
    """Test text file detection with valid text content."""
    content = 'This is a regular text file\nwith multiple lines\nand some special chars: !@#$%'

    assert formatter.is_text_file(content) is True


def test_is_text_file_with_binary_content(formatter):
    """Test text file detection with binary content."""
    # Create content with null bytes (typical in binary files)
    content = 'Some text\x00with null\x00bytes'

    assert formatter.is_text_file(content) is False


def test_is_text_file_with_high_non_ascii_ratio(formatter):
    """Test text file detection with high ratio of non-ASCII characters."""
    # Create content with lots of non-printable characters
    content = ''.join(chr(i) for i in range(0, 32)) * 10

    assert formatter.is_text_file(content) is False


def test_is_text_file_with_mixed_content(formatter):
    """Test text file detection with mixed content."""
    # Content that's mostly text but has some binary-like parts
    # Using a shorter sample since the formatter only checks first 1024 bytes
    content = 'Regular text\n' * 50

    assert formatter.is_text_file(content) is True

    # Content with null bytes should be rejected
    content_with_nulls = content + '\x00\x01\x02\x03'
    assert formatter.is_text_file(content_with_nulls) is False


def test_format_path_with_backslashes(formatter):
    """Test path normalization with backslashes."""
    path = Path('nested\\folder\\test.txt')
    content = 'Test content'

    formatted = formatter.format_content(path, content)

    assert 'nested/folder/test.txt' in formatted
    assert '\\' not in formatted


def test_is_text_file_with_utf8_content(formatter):
    """Test text file detection with UTF-8 content."""
    # Mix of ASCII and common Latin-1 characters that should be accepted
    content = """Hello World!
    étude café
    über größer
    señor niño
    """
    assert formatter.is_text_file(content) is True


def test_is_text_file_with_control_characters(formatter):
    """Test text file detection with some control characters."""
    # Content with common control characters (newlines, tabs, etc)
    content = 'Line 1\nLine 2\tTabbed\rCarriage return'

    assert formatter.is_text_file(content) is True


def test_is_text_file_short_content(formatter):
    """Test text file detection with very short content."""
    content = 'Short'

    assert formatter.is_text_file(content) is True
