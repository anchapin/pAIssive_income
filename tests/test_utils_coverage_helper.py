"""Tests for utils/coverage_helper.py module."""

import os
import sys

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
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


class TestCoverageHelperFunctions:
    """Test suite for coverage helper functions."""

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
        assert subtract(0, 1) == -1
        assert subtract(5.5, 2.5) == 3.0

    def test_multiply(self):
        """Test the multiply function."""
        assert multiply(2, 3) == 6
        assert multiply(0, 5) == 0
        assert multiply(-1, -1) == 1
        assert multiply(1.5, 2) == 3.0

    def test_divide(self):
        """Test the divide function."""
        assert divide(6, 3) == 2
        assert divide(5, 2) == 2.5
        assert divide(0, 1) == 0
        assert divide(-6, 3) == -2

    def test_divide_by_zero(self):
        """Test that divide raises ValueError when dividing by zero."""
        with pytest.raises(ValueError) as excinfo:
            divide(1, 0)
        assert "Cannot divide by zero" in str(excinfo.value)

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

    def test_get_first_element_with_list(self):
        """Test the get_first_element function with a non-empty list."""
        assert get_first_element([1, 2, 3]) == 1
        assert get_first_element(["a", "b", "c"]) == "a"

    def test_get_first_element_with_empty_list(self):
        """Test the get_first_element function with an empty list."""
        assert get_first_element([]) is None
        assert get_first_element([], default="default") == "default"

    def test_format_string_valid(self):
        """Test the format_string function with valid inputs."""
        assert format_string("Hello, {name}!", name="World") == "Hello, World!"
        assert format_string("{greeting}, {name}!", greeting="Hi", name="User") == "Hi, User!"

    def test_format_string_missing_key(self):
        """Test that format_string raises ValueError when a key is missing."""
        with pytest.raises(ValueError) as excinfo:
            format_string("Hello, {name}!")
        assert "Missing required key" in str(excinfo.value)
