"""
conftest - Module for tests.ai_models.adapters.conftest.

This conftest file is specific to the MCP adapter tests and avoids loading the main conftest.py
which has dependencies on Flask and other components not needed for these tests.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_mcp():
    """Mock the modelcontextprotocol module."""
    with patch("ai_models.adapters.mcp_adapter.mcp") as mock_mcp:
        mock_client = MagicMock()
        mock_mcp.Client.return_value = mock_client
        mock_mcp.__version__ = "0.1.0-mock"
        yield mock_mcp


@pytest.fixture
def mock_logger():
    """Mock the logger."""
    with patch("ai_models.adapters.mcp_adapter.logger") as mock_logger:
        yield mock_logger
