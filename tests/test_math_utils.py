"""Tests for the math_utils module."""

import pytest

from utils.math_utils import add, average, divide, multiply, subtract

# Constants for test values
EXPECTED_SUM_1_2 = 3
EXPECTED_SUM_1_5_2_5 = 4.0
EXPECTED_DIFF_3_1 = 2
EXPECTED_DIFF_0_5 = -5
EXPECTED_DIFF_5_5_2_5 = 3.0
EXPECTED_PRODUCT_2_3 = 6
EXPECTED_PRODUCT_NEG_2_3 = -6
EXPECTED_PRODUCT_2_5_2 = 5.0
EXPECTED_QUOTIENT_6_3 = 2
EXPECTED_QUOTIENT_5_2 = 2.5
EXPECTED_QUOTIENT_NEG_6_3 = -2
EXPECTED_AVG_1_TO_5 = 3
EXPECTED_AVG_1_5_2_5_3_5 = 2.5


class TestMathUtils:
    """Test class for math_utils module."""

    def test_add(self):
        """Test the add function."""
        assert add(1, 2) == EXPECTED_SUM_1_2
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
        assert add(1.5, 2.5) == EXPECTED_SUM_1_5_2_5

    def test_subtract(self):
        """Test the subtract function."""
        assert subtract(3, 1) == EXPECTED_DIFF_3_1
        assert subtract(1, 1) == 0
        assert subtract(0, 5) == EXPECTED_DIFF_0_5
        assert subtract(5.5, 2.5) == EXPECTED_DIFF_5_5_2_5

    def test_multiply(self):
        """Test the multiply function."""
        assert multiply(2, 3) == EXPECTED_PRODUCT_2_3
        assert multiply(-2, 3) == EXPECTED_PRODUCT_NEG_2_3
        assert multiply(0, 5) == 0
        assert multiply(2.5, 2) == EXPECTED_PRODUCT_2_5_2

    def test_divide(self):
        """Test the divide function."""
        assert divide(6, 3) == EXPECTED_QUOTIENT_6_3
        assert divide(5, 2) == EXPECTED_QUOTIENT_5_2
        assert divide(0, 5) == 0
        assert divide(-6, 3) == EXPECTED_QUOTIENT_NEG_6_3

    def test_divide_by_zero(self):
        """Test that divide raises ZeroDivisionError when dividing by zero."""
        with pytest.raises(ZeroDivisionError):
            divide(5, 0)

    def test_average(self):
        """Test the average function."""
        assert average([1, 2, 3, 4, 5]) == EXPECTED_AVG_1_TO_5
        assert average([0, 0, 0]) == 0
        assert average([1]) == 1
        assert average([1.5, 2.5, 3.5]) == EXPECTED_AVG_1_5_2_5_3_5

    def test_average_empty_list(self):
        """Test that average raises ValueError when given an empty list."""
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            average([])
