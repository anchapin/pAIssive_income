"""Test that MCP adapter can be imported."""

import logging
from unittest.mock import patch


def test_mcp_adapter_import():
    """Test that MCP adapter can be imported."""
    with patch("ai_models.adapters.mcp_adapter.mcp"):
        # Import should succeed with the mock
        from ai_models.adapters.mcp_adapter import MCPAdapter

        # Simple assertion to verify the class exists
        assert MCPAdapter.__name__ == "MCPAdapter"
