"""conftest - Module for tests.ai_models.adapters.conftest.

This conftest file is specific to the MCP adapter tests and avoids loading the main conftest.py
which has dependencies on Flask and other components not needed for these tests.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_mcp():
    """Mock the modelcontextprotocol module."""
    with patch("ai_models.adapters.mcp_adapter.mcp") as mock_mcp:
        mock_client = MagicMock()
        mock_mcp.Client.return_value = mock_client
        yield mock_mcp
