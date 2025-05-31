"""Tests for the utils.math_utils module."""

import pytest

from utils.math_utils import add, average, divide, multiply, subtract


class TestMathUtils:
    """Test cases for math utility functions."""

    def test_add(self):
        """Test add function."""
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
        assert add(2.5, 3.5) == 6.0

    def test_subtract(self):
        """Test subtract function."""
        assert subtract(5, 3) == 2
        assert subtract(1, 1) == 0
        assert subtract(0, 5) == -5
        assert subtract(5.5, 2.5) == 3.0

    def test_multiply(self):
        """Test multiply function."""
        assert multiply(2, 3) == 6
        assert multiply(-2, 3) == -6
        assert multiply(0, 5) == 0
        assert multiply(2.5, 2) == 5.0

    def test_divide(self):
        """Test divide function."""
        assert divide(6, 3) == 2
        assert divide(5, 2) == 2.5
        assert divide(0, 5) == 0
        assert divide(10, 4) == 2.5

    def test_divide_by_zero(self):
        """Test divide by zero raises ZeroDivisionError."""
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_average(self):
        """Test average function."""
        assert average([1, 2, 3, 4, 5]) == 3
        assert average([0, 10]) == 5
        assert average([5]) == 5
        assert average([1.5, 2.5, 3.5]) == 2.5

    def test_average_empty_list(self):
        """Test average with empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            average([])
