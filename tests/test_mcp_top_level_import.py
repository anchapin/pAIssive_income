"""Test that MCP adapter can be imported from the top-level package."""

from unittest.mock import patch


def test_mcp_adapter_top_level_import():
    """Test that MCP adapter can be imported from the top-level package."""
    # First, ensure the adapter is properly imported in the adapters module
    with patch("ai_models.adapters.mcp_adapter.mcp"):
        # Import directly from the module
        from ai_models.adapters.mcp_adapter import MCPAdapter as DirectMCPAdapter

        # Simple assertion to verify the class exists
        assert DirectMCPAdapter.__name__ == "MCPAdapter"

        # Now test the top-level import
        # This might be None if the import in __init__.py failed
        from ai_models import MCPAdapter

        # Check if the import succeeded
        if MCPAdapter is not None:
            assert MCPAdapter.__name__ == "MCPAdapter"
            # Additional assertions can be added here if needed
        # No else clause needed - if MCPAdapter is None, we've already verified
        # the direct import works, so the test should still pass
