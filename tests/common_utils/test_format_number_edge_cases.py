"""Tests for edge cases in the format_number function."""

import pytest

from common_utils.string_utils import format_number


class TestFormatNumberEdgeCases:
    """Test suite for format_number edge cases."""

    def test_format_number_with_non_numeric_input(self):
        """Test format_number with non-numeric input."""
        # Test with string input
        with pytest.raises(TypeError):
            format_number("1234.56")

        # Test with None input
        with pytest.raises(TypeError):
            format_number(None)

        # Note: In Python, bool is a subclass of int, so True is treated as 1
        # and False as 0, which are valid numeric inputs

        # Test with list input
        with pytest.raises(TypeError):
            format_number([1234.56])

        # Test with dict input
        with pytest.raises(TypeError):
            format_number({"value": 1234.56})

    def test_format_number_with_invalid_decimal_places(self):
        """Test format_number with invalid decimal_places parameter."""
        # Test with negative decimal places
        with pytest.raises(ValueError):
            format_number(1234.56, decimal_places=-1)

        # Test with non-integer decimal places
        with pytest.raises(TypeError):
            format_number(1234.56, decimal_places=2.5)

        # Test with string decimal places
        with pytest.raises(TypeError):
            format_number(1234.56, decimal_places="2")

        # Test with None decimal places
        with pytest.raises(TypeError):
            format_number(1234.56, decimal_places=None)

    def test_format_number_with_special_values(self):
        """Test format_number with special numeric values."""
        # Test with infinity
        assert format_number(float("inf")) == "inf"

        # Test with negative infinity
        assert format_number(float("-inf")) == "-inf"

        # Test with NaN
        assert format_number(float("nan")).lower() == "nan"

    def test_format_number_with_boolean_values(self):
        """Test format_number with boolean values (which are valid as they're a subclass of int)."""
        # Test with True (should be treated as 1)
        assert format_number(True) == "1.00"

        # Test with False (should be treated as 0)
        assert format_number(False) == "0.00"

        # Test with different decimal places
        assert format_number(True, decimal_places=0) == "1"
        assert format_number(False, decimal_places=3) == "0.000"
