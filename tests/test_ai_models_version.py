"""Tests for ai_models/version.py module."""

import os
import re
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
from ai_models.version import __version__


def test_version_exists():
    """Test that the __version__ attribute exists."""
    assert __version__ is not None


def test_version_is_string():
    """Test that the __version__ attribute is a string."""
    assert isinstance(__version__, str)


def test_version_format():
    """Test that the __version__ attribute follows semantic versioning."""
    # Semantic versioning pattern: MAJOR.MINOR.PATCH
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, __version__) is not None
