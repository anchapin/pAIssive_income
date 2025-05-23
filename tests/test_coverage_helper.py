"""
Tests for the utils.coverage_helper module.
These tests ensure 100% coverage of the module.
"""

import logging
import unittest
import pytest
from utils.coverage_helper import add, subtract, multiply, divide, is_even, is_odd, get_first_element, format_string


# The CoverageHelper class has been removed, so we only test the math functions now


class TestMathFunctions:
    """Test cases for math functions."""

    def test_add(self):
        """Test add function."""
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0

    def test_subtract(self):
        """Test subtract function."""
        assert subtract(5, 3) == 2
        assert subtract(1, 1) == 0
        assert subtract(0, 5) == -5

    def test_multiply(self):
        """Test multiply function."""
        assert multiply(2, 3) == 6
        assert multiply(-2, 3) == -6
        assert multiply(0, 5) == 0

    def test_divide(self):
        """Test divide function."""
        assert divide(6, 3) == 2
        assert divide(5, 2) == 2.5
        assert divide(0, 5) == 0

    def test_divide_by_zero(self):
        """Test divide by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_is_even(self):
        """Test is_even function."""
        assert is_even(2) is True
        assert is_even(3) is False
        assert is_even(0) is True
        assert is_even(-2) is True
        assert is_even(-3) is False

    def test_is_odd(self):
        """Test is_odd function."""
        assert is_odd(3) is True
        assert is_odd(2) is False
        assert is_odd(0) is False
        assert is_odd(-3) is True
        assert is_odd(-2) is False

    def test_get_first_element(self):
        """Test get_first_element function."""
        assert get_first_element([1, 2, 3]) == 1
        assert get_first_element(["a", "b", "c"]) == "a"
        assert get_first_element([]) is None
        assert get_first_element([], "default") == "default"

    def test_format_string(self):
        """Test format_string function."""
        assert format_string("Hello, {name}!", name="World") == "Hello, World!"
        assert format_string("{greeting}, {name}!", greeting="Hi", name="User") == "Hi, User!"

    def test_format_string_error(self):
        """Test format_string raises ValueError on missing key."""
        with pytest.raises(ValueError, match="Missing required key"):
            format_string("Hello, {name}!")
