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