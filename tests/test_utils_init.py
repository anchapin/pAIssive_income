"""Tests for utils/__init__.py module."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
import utils


def test_utils_exports():
    """Test that the utils module exports the expected functions."""
    assert hasattr(utils, "add")
    assert hasattr(utils, "subtract")
    assert hasattr(utils, "multiply")
    assert hasattr(utils, "divide")
    assert hasattr(utils, "average")


def test_utils_all():
    """Test that __all__ contains the expected functions."""
    expected_exports = ["add", "subtract", "multiply", "divide", "average"]
    assert set(utils.__all__) == set(expected_exports)


def test_utils_functions():
    """Test that the exported functions work as expected."""
    assert utils.add(1, 2) == 3
    assert utils.subtract(5, 2) == 3
    assert utils.multiply(2, 3) == 6
    assert utils.divide(6, 2) == 3
    assert utils.average([1, 2, 3]) == 2
