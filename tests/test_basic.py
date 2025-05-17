"""Basic tests to verify that the testing framework works."""

import pytest

# Constants for test values
EXPECTED_SUM = 2
EXPECTED_DIFFERENCE = 2
EXPECTED_PRODUCT = 6
EXPECTED_QUOTIENT = 2


def test_basic_addition():
    """Test that basic addition works."""
    assert EXPECTED_SUM == 1 + 1


def test_basic_subtraction():
    """Test that basic subtraction works."""
    assert EXPECTED_DIFFERENCE == 3 - 1


def test_basic_multiplication():
    """Test that basic multiplication works."""
    assert EXPECTED_PRODUCT == 2 * 3


def test_basic_division():
    """Test that basic division works."""
    assert EXPECTED_QUOTIENT == 6 / 3


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 1, 2),
        (2, 2, 4),
        (3, 3, 6),
        (4, 4, 8),
    ],
)
def test_parametrized_addition(a, b, expected):
    """Test addition with multiple parameter sets."""
    assert a + b == expected
