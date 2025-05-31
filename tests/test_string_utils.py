"""Tests for the common_utils.string_utils module."""

import pytest

from common_utils.string_utils import (
    camel_to_snake,
    format_number,
    remove_html_tags,
    slugify,
    snake_to_camel,
    truncate,
)


class TestStringUtils:
    """Test suite for string utility functions."""

    def test_slugify(self):
        """Test the slugify function."""
        # Test basic slugify
        assert slugify("Hello World") == "hello-world"

        # Test with special characters
        assert slugify("Hello, World!") == "hello-world"

        # Test with accents
        assert slugify("Héllö Wörld") == "hello-world"

        # Test with custom separator
        assert slugify("Hello World", separator="_") == "hello_world"

        # Test with multiple spaces and special characters
        assert slugify("  Hello  -  World  !  ") == "hello-world"

        # Test with numbers
        assert slugify("Hello 123 World") == "hello-123-world"

        # Test with empty string
        assert slugify("") == ""

    def test_camel_to_snake(self):
        """Test the camel_to_snake function."""
        # Test basic camelCase
        assert camel_to_snake("helloWorld") == "hello_world"

        # Test PascalCase
        assert camel_to_snake("HelloWorld") == "hello_world"

        # Test with numbers
        assert camel_to_snake("hello123World") == "hello123_world"

        # Test with acronyms
        assert camel_to_snake("APIResponse") == "api_response"
        assert camel_to_snake("HTTPRequest") == "http_request"

        # Test with already snake_case
        assert camel_to_snake("hello_world") == "hello_world"

        # Test with empty string
        assert camel_to_snake("") == ""

    def test_snake_to_camel(self):
        """Test the snake_to_camel function."""
        # Test basic snake_case to camelCase
        assert snake_to_camel("hello_world") == "helloWorld"

        # Test snake_case to PascalCase
        assert snake_to_camel("hello_world", capitalize_first=True) == "HelloWorld"

        # Test with numbers
        assert snake_to_camel("hello_123_world") == "hello123World"

        # Test with multiple underscores
        assert snake_to_camel("hello__world") == "helloWorld"

        # Test with already camelCase
        assert snake_to_camel("helloWorld") == "helloWorld"

        # Test with empty string
        assert snake_to_camel("") == ""

        # Test with single word
        assert snake_to_camel("hello") == "hello"
        assert snake_to_camel("hello", capitalize_first=True) == "Hello"

    def test_truncate(self):
        """Test the truncate function."""
        # Test basic truncation
        assert truncate("Hello World", 8) == "Hello..."

        # Test with no truncation needed
        assert truncate("Hello", 10) == "Hello"

        # Test with exact length
        assert truncate("Hello", 5) == "Hello"

        # Test with custom suffix - when text is shorter than max_length, it's not truncated
        assert truncate("Hello World", 15, suffix="...more") == "Hello World"

        # Test with empty string
        assert truncate("", 5) == ""

        # Test with length less than suffix length
        assert truncate("Hello", 2, suffix="...") == "..."

        # Test with just enough space for 2 characters plus suffix
        assert truncate("Hello World", 5) == "He..."

        # Test with exact length of text
        assert truncate("Hello World", 11) == "Hello World"

    def test_remove_html_tags(self):
        """Test the remove_html_tags function."""
        # Test basic HTML removal
        assert remove_html_tags("<p>Hello World</p>") == "Hello World"

        # Test with nested tags
        assert remove_html_tags("<div><p>Hello <b>World</b></p></div>") == "Hello World"

        # Test with attributes
        assert remove_html_tags('<a href="https://example.com">Link</a>') == "Link"

        # Test with self-closing tags
        assert remove_html_tags("Hello<br/>World") == "HelloWorld"

        # Test with no tags
        assert remove_html_tags("Hello World") == "Hello World"

        # Test with empty string
        assert remove_html_tags("") == ""

    def test_format_number(self):
        """Test the format_number function."""
        # Test basic formatting
        assert format_number(1234.5678) == "1,234.57"

        # Test with different decimal places
        assert format_number(1234.5678, decimal_places=0) == "1,235"  # Rounds to nearest integer
        assert format_number(1234.5678, decimal_places=3) == "1,234.568"

        # Test with negative numbers
        assert format_number(-1234.5678) == "-1,234.57"

        # Test with zero
        assert format_number(0) == "0.00"

        # Test with large numbers
        assert format_number(1234567.89) == "1,234,567.89"

        # Test with small numbers
        assert format_number(0.12345) == "0.12"

        # Test with exact integer
        assert format_number(1234, decimal_places=0) == "1,234"
