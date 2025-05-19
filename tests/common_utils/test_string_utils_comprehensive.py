"""Comprehensive tests for the common_utils.string_utils module."""

import re
import unicodedata
from unittest.mock import patch

import pytest

from common_utils.string_utils import (
    slugify,
    camel_to_snake,
    snake_to_camel,
    truncate,
    remove_html_tags,
    format_number,
)


class TestStringUtilsComprehensive:
    """Comprehensive test suite for string utility functions."""

    def test_slugify_basic(self):
        """Test basic slugify functionality."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Hello, World!") == "hello-world"
        assert slugify("  Hello  -  World  !  ") == "hello-world"

    def test_slugify_special_characters(self):
        """Test slugify with special characters and accents."""
        assert slugify("Héllö Wörld") == "hello-world"
        # Special characters are removed, but underscore is kept
        assert slugify("!@#$%^&*()_+") == "_"
        assert slugify("123 456-789") == "123-456-789"

    def test_slugify_edge_cases(self):
        """Test slugify with edge cases."""
        assert slugify("") == ""
        assert slugify(None) == ""
        assert slugify(123) == "123"
        assert slugify(True) == "true"
        assert slugify(False) == "false"

    def test_slugify_custom_separator(self):
        """Test slugify with custom separator."""
        assert slugify("Hello World", separator="_") == "hello_world"
        assert slugify("Hello, World!", separator="+") == "hello+world"
        assert slugify("  Hello  -  World  !  ", separator=".") == "hello.world"

    def test_slugify_allow_unicode(self):
        """Test slugify with allow_unicode=True."""
        # With allow_unicode=False (default), accents are removed
        assert slugify("Héllö Wörld") == "hello-world"
        
        # With allow_unicode=True, accents are preserved
        assert "ö" in slugify("Héllö Wörld", allow_unicode=True)
        assert "é" in slugify("Héllö Wörld", allow_unicode=True)

    def test_camel_to_snake_basic(self):
        """Test basic camel_to_snake functionality."""
        assert camel_to_snake("helloWorld") == "hello_world"
        assert camel_to_snake("HelloWorld") == "hello_world"
        assert camel_to_snake("helloWorldAgain") == "hello_world_again"

    def test_camel_to_snake_edge_cases(self):
        """Test camel_to_snake with edge cases."""
        assert camel_to_snake("") == ""
        assert camel_to_snake("hello") == "hello"
        assert camel_to_snake("HELLO") == "hello"
        assert camel_to_snake("hello_world") == "hello_world"
        assert camel_to_snake("HelloWorldWithNumbers123") == "hello_world_with_numbers123"

    def test_camel_to_snake_acronyms(self):
        """Test camel_to_snake with acronyms."""
        assert camel_to_snake("HTTPRequest") == "http_request"
        assert camel_to_snake("APIResponse") == "api_response"
        assert camel_to_snake("JSONParser") == "json_parser"

    def test_snake_to_camel_basic(self):
        """Test basic snake_to_camel functionality."""
        assert snake_to_camel("hello_world") == "helloWorld"
        assert snake_to_camel("hello_world_again") == "helloWorldAgain"

    def test_snake_to_camel_capitalize_first(self):
        """Test snake_to_camel with capitalize_first=True."""
        assert snake_to_camel("hello_world", capitalize_first=True) == "HelloWorld"
        assert snake_to_camel("hello_world_again", capitalize_first=True) == "HelloWorldAgain"

    def test_snake_to_camel_edge_cases(self):
        """Test snake_to_camel with edge cases."""
        assert snake_to_camel("") == ""
        assert snake_to_camel("hello") == "hello"
        assert snake_to_camel("hello_") == "hello"
        assert snake_to_camel("_hello") == "Hello"
        assert snake_to_camel("__hello__world__") == "HelloWorld"

    def test_truncate_basic(self):
        """Test basic truncate functionality."""
        assert truncate("Hello World", 5) == "Hello..."
        assert truncate("Hello", 10) == "Hello"
        assert truncate("Hello World", 8) == "Hello..."

    def test_truncate_custom_suffix(self):
        """Test truncate with custom suffix."""
        assert truncate("Hello World", 5, suffix="!") == "Hello!"
        assert truncate("Hello", 10, suffix="!!!") == "Hello"
        assert truncate("Hello World", 8, suffix=" [more]") == "Hello [more]"

    def test_truncate_edge_cases(self):
        """Test truncate with edge cases."""
        assert truncate("", 5) == ""
        assert truncate("Hello", 0) == "..."
        assert truncate("Hello", -1) == "..."
        assert truncate("Hello", 5, suffix="") == "Hello"

    def test_remove_html_tags_basic(self):
        """Test basic remove_html_tags functionality."""
        assert remove_html_tags("<p>Hello World</p>") == "Hello World"
        assert remove_html_tags("<p>Hello <b>World</b></p>") == "Hello World"
        assert remove_html_tags("<p>Hello<br>World</p>") == "HelloWorld"

    def test_remove_html_tags_with_attributes(self):
        """Test remove_html_tags with HTML attributes."""
        assert remove_html_tags('<p class="test">Hello World</p>') == "Hello World"
        assert remove_html_tags('<a href="https://example.com">Link</a>') == "Link"
        assert remove_html_tags('<img src="image.jpg" alt="Image">') == ""

    def test_remove_html_tags_nested(self):
        """Test remove_html_tags with nested tags."""
        html = '<div><p>Hello <span style="color:red">World</span></p></div>'
        assert remove_html_tags(html) == "Hello World"

    def test_remove_html_tags_edge_cases(self):
        """Test remove_html_tags with edge cases."""
        assert remove_html_tags("") == ""
        assert remove_html_tags("Hello World") == "Hello World"
        assert remove_html_tags("<>Hello World</>") == "Hello World"
        assert remove_html_tags("< >Hello World</ >") == "Hello World"

    def test_format_number_basic(self):
        """Test basic format_number functionality."""
        assert format_number(1234.5678) == "1,234.57"
        assert format_number(1234) == "1,234.00"
        assert format_number(1234.5678, decimal_places=3) == "1,234.568"

    def test_format_number_decimal_places(self):
        """Test format_number with different decimal places."""
        assert format_number(1234.5678, decimal_places=0) == "1,235"
        assert format_number(1234.5678, decimal_places=1) == "1,234.6"
        assert format_number(1234.5678, decimal_places=4) == "1,234.5678"

    def test_format_number_edge_cases(self):
        """Test format_number with edge cases."""
        assert format_number(0) == "0.00"
        assert format_number(-1234.5678) == "-1,234.57"
        assert format_number(0.1234, decimal_places=4) == "0.1234"
        assert format_number(1e6) == "1,000,000.00"
