"""Additional tests for the common_utils.string_utils module to improve coverage."""

import pytest
import re
import unicodedata
from unittest.mock import patch

from common_utils.string_utils import (
    slugify,
    camel_to_snake,
    snake_to_camel,
    truncate,
    remove_html_tags,
    format_number,
)


class TestStringUtilsAdditional:
    """Additional test suite for string utility functions to improve coverage."""

    def test_slugify_with_unicode_normalization(self):
        """Test slugify with unicode normalization."""
        # Test with a string that requires unicode normalization
        text = "Café au lait"
        result = slugify(text)
        assert result == "cafe-au-lait"
        
        # Test with a string that has combining characters
        text = "a\u0300e\u0301i\u0302o\u0303u\u0304"  # à é î õ ū
        result = slugify(text)
        assert result == "aeiou"

    def test_slugify_with_multiple_separators(self):
        """Test slugify with multiple separators in the input."""
        text = "hello--world  test"
        result = slugify(text)
        assert result == "hello-world-test"
        
        text = "hello_world-test"
        result = slugify(text)
        assert result == "hello_world-test"
        
        # Test with custom separator
        text = "hello--world  test"
        result = slugify(text, separator="_")
        assert result == "hello_world_test"

    def test_camel_to_snake_with_numbers(self):
        """Test camel_to_snake with numbers in different positions."""
        # Numbers at the beginning
        assert camel_to_snake("123Test") == "123_test"
        
        # Numbers in the middle
        assert camel_to_snake("hello123World") == "hello123_world"
        
        # Numbers at the end
        assert camel_to_snake("helloWorld123") == "hello_world123"
        
        # Multiple numbers
        assert camel_to_snake("hello123World456") == "hello123_world456"

    def test_camel_to_snake_with_consecutive_uppercase(self):
        """Test camel_to_snake with consecutive uppercase letters."""
        # Test with consecutive uppercase letters
        assert camel_to_snake("HTTPRequest") == "http_request"
        assert camel_to_snake("APIEndpoint") == "api_endpoint"
        assert camel_to_snake("JSONParser") == "json_parser"
        
        # Test with uppercase letters at the end
        assert camel_to_snake("requestJSON") == "request_json"
        assert camel_to_snake("parseHTML") == "parse_html"

    def test_snake_to_camel_with_multiple_underscores(self):
        """Test snake_to_camel with multiple consecutive underscores."""
        # Test with multiple consecutive underscores
        assert snake_to_camel("hello___world") == "helloWorld"
        assert snake_to_camel("hello___world", capitalize_first=True) == "HelloWorld"
        
        # Test with underscores at the beginning and end
        assert snake_to_camel("___hello_world___") == "HelloWorld"
        assert snake_to_camel("___hello_world___", capitalize_first=True) == "HelloWorld"

    def test_snake_to_camel_with_empty_components(self):
        """Test snake_to_camel with empty components."""
        # Test with empty components
        assert snake_to_camel("hello__world") == "helloWorld"
        assert snake_to_camel("__hello") == "Hello"
        assert snake_to_camel("hello__") == "hello"
        
        # Test with only underscores
        assert snake_to_camel("_") == ""
        assert snake_to_camel("__") == ""
        assert snake_to_camel("___") == ""

    def test_truncate_with_exact_length(self):
        """Test truncate when text length equals max_length."""
        # Test when text length equals max_length
        assert truncate("Hello", 5) == "Hello"
        assert truncate("Hello", 5, suffix="...") == "Hello"
        
        # Test when text length is one less than max_length
        assert truncate("Hell", 5) == "Hell"
        assert truncate("Hell", 5, suffix="...") == "Hell"
        
        # Test when text length is one more than max_length
        assert truncate("Hello!", 5) == "He..."
        assert truncate("Hello!", 5, suffix="!") == "Hell!"

    def test_truncate_with_very_short_max_length(self):
        """Test truncate with very short max_length."""
        # Test with max_length = 1
        assert truncate("Hello", 1) == "..."
        assert truncate("Hello", 1, suffix="!") == "!"
        
        # Test with max_length = 0
        assert truncate("Hello", 0) == "..."
        assert truncate("Hello", 0, suffix="!") == "!"
        
        # Test with negative max_length
        assert truncate("Hello", -1) == "..."
        assert truncate("Hello", -5) == "..."

    def test_remove_html_tags_with_nested_tags(self):
        """Test remove_html_tags with deeply nested tags."""
        # Test with deeply nested tags
        html = "<div><p><span><strong>Hello</strong> <em>World</em></span></p></div>"
        assert remove_html_tags(html) == "Hello World"
        
        # Test with self-closing tags
        html = "<p>Hello<br/>World<img src='test.jpg'/></p>"
        assert remove_html_tags(html) == "HelloWorld"
        
        # Test with HTML entities
        html = "<p>Hello &amp; World</p>"
        assert remove_html_tags(html) == "Hello &amp; World"

    def test_remove_html_tags_with_malformed_html(self):
        """Test remove_html_tags with malformed HTML."""
        # Test with unclosed tags
        html = "<p>Hello <strong>World"
        assert remove_html_tags(html) == "Hello World"
        
        # Test with unopened tags
        html = "Hello World</p>"
        assert remove_html_tags(html) == "Hello World"
        
        # Test with mismatched tags
        html = "<p>Hello <strong>World</p></strong>"
        assert remove_html_tags(html) == "Hello World"

    def test_format_number_with_large_values(self):
        """Test format_number with very large values."""
        # Test with large integer
        assert format_number(1000000000) == "1,000,000,000.00"
        
        # Test with large float
        assert format_number(1000000000.12345) == "1,000,000,000.12"
        
        # Test with scientific notation
        assert format_number(1e10) == "10,000,000,000.00"
        assert format_number(1.23e-5, decimal_places=7) == "0.0000123"

    def test_format_number_with_different_decimal_places(self):
        """Test format_number with different decimal places."""
        # Test with large number of decimal places
        assert format_number(1.23456789, decimal_places=8) == "1.23456789"
        
        # Test with zero decimal places
        assert format_number(1.23456789, decimal_places=0) == "1"
        assert format_number(1.5, decimal_places=0) == "2"
        assert format_number(1.4, decimal_places=0) == "1"
        
        # Test with negative decimal places (should be treated as 0)
        with pytest.raises(ValueError):
            format_number(1.23456789, decimal_places=-1)
