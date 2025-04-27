"""
Configuration for pytest.
"""
import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Define fixtures that can be used across all tests

@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def temp_dir(tmp_path):
    """Return a temporary directory that will be cleaned up after the test."""
    return tmp_path
