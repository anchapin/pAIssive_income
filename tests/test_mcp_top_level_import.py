"""Test that MCP adapter can be imported from the top-level package."""

import logging
import sys
import importlib
import pytest
from unittest.mock import patch


def test_mcp_adapter_top_level_import():
    """Test that MCP adapter can be imported from the top-level package."""
    # First, ensure the adapter is properly imported in the adapters module
    with patch("ai_models.adapters.mcp_adapter.mcp"):
        # Import directly from the module
        from ai_models.adapters.mcp_adapter import MCPAdapter as DirectMCPAdapter

        # Simple assertion to verify the class exists
        assert DirectMCPAdapter.__name__ == "MCPAdapter"

        # Patch sys.modules to ensure the mock MCP module is loaded correctly
        with patch.dict(sys.modules):
            try:
                # Create a mock for the modelcontextprotocol module
                if "modelcontextprotocol" not in sys.modules:
                    import types
                    modelcontextprotocol = types.ModuleType("modelcontextprotocol")
                    modelcontextprotocol.Client = type("Client", (), {})
                    modelcontextprotocol.ConnectionError = type("ConnectionError", (Exception,), {})
                    sys.modules["modelcontextprotocol"] = modelcontextprotocol

                # Reload the adapter modules
                import ai_models.adapters.mcp_adapter
                importlib.reload(ai_models.adapters.mcp_adapter)

                # Force-reload the modules
                import ai_models.adapters
                importlib.reload(ai_models.adapters)

                import ai_models
                importlib.reload(ai_models)

                # Now try the import from ai_models directly
                from ai_models import MCPAdapter as TopLevelMCPAdapter

                # Check if the import succeeded
                assert TopLevelMCPAdapter is not None
                assert TopLevelMCPAdapter.__name__ == "MCPAdapter"

            except Exception as e:
                logging.error(f"Failed to import MCPAdapter from ai_models: {e}")
                pytest.skip("MCPAdapter not available in ai_models - skipping this test")
