"""Test module for mock_crewai module."""

import os
import sys
import importlib
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the mock_crewai module directly
mock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai")
if os.path.exists(mock_dir):
    sys.path.insert(0, os.path.dirname(mock_dir))

import mock_crewai as crewai


class TestCrewAIMock:
    """Test suite for mock_crewai module."""

    def test_version_attribute(self):
        """Test that the __version__ attribute is defined."""
        assert hasattr(crewai, "__version__")
        assert isinstance(crewai.__version__, str)
        assert crewai.__version__ == "0.120.0"
        
    def test_version_attribute_in_init(self):
        """Test that the __version__ attribute is defined in __init__.py."""
        # Import the module directly to check its attributes
        import mock_crewai
        assert hasattr(mock_crewai, "__version__")
        assert isinstance(mock_crewai.__version__, str)
        assert mock_crewai.__version__ == "0.120.0"
        
    def test_version_attribute_import(self):
        """Test that the __version__ attribute can be imported directly."""
        # Test direct import of __version__
        from mock_crewai import __version__
        assert __version__ == "0.120.0"