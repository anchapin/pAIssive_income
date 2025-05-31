"""Test module for utils/coverage_helper.py."""

import pytest

from utils.coverage_helper import (
    add,
    divide,
    format_string,
    get_first_element,
    is_even,
    is_odd,
    multiply,
    subtract,
)


class TestCoverageHelper:
    """Test suite for coverage_helper module."""

    def test_add(self):
        """Test the add function."""
        assert add(1, 2) == 3
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
        assert add(1.5, 2.5) == 4.0

    def test_subtract(self):
        """Test the subtract function."""
        assert subtract(3, 2) == 1
        assert subtract(1, 1) == 0
        assert subtract(0, 5) == -5
        assert subtract(5.5, 2.5) == 3.0

    def test_multiply(self):
        """Test the multiply function."""
        assert multiply(2, 3) == 6
        assert multiply(-2, 3) == -6
        assert multiply(0, 5) == 0
        assert multiply(2.5, 2) == 5.0

    def test_divide(self):
        """Test the divide function."""
        assert divide(6, 3) == 2
        assert divide(5, 2) == 2.5
        assert divide(0, 5) == 0
        assert divide(-6, 3) == -2

    def test_divide_by_zero(self):
        """Test that divide raises ValueError when dividing by zero."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_is_even(self):
        """Test the is_even function."""
        assert is_even(2) is True
        assert is_even(0) is True
        assert is_even(-2) is True
        assert is_even(1) is False
        assert is_even(-1) is False

    def test_is_odd(self):
        """Test the is_odd function."""
        assert is_odd(1) is True
        assert is_odd(-1) is True
        assert is_odd(0) is False
        assert is_odd(2) is False
        assert is_odd(-2) is False

    def test_get_first_element(self):
        """Test the get_first_element function."""
        assert get_first_element([1, 2, 3]) == 1
        assert get_first_element(["a", "b", "c"]) == "a"
        assert get_first_element([]) is None
        assert get_first_element([], default="empty") == "empty"

    def test_format_string(self):
        """Test the format_string function."""
        assert format_string("Hello, {name}!", name="World") == "Hello, World!"
        assert format_string("{greeting}, {name}!", greeting="Hi", name="Alice") == "Hi, Alice!"
        assert format_string("No placeholders") == "No placeholders"

    def test_format_string_missing_key(self):
        """Test that format_string raises ValueError when a required key is missing."""
        with pytest.raises(ValueError, match="Missing required key: 'name'"):
            format_string("Hello, {name}!")
