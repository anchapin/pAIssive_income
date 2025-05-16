"""Test that MCP adapter can be imported from the top-level package."""

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
        
        try:
            # Reload the modules to ensure clean imports
            import sys
            from importlib import reload
            import ai_models.adapters
            import ai_models
            reload(ai_models.adapters)
            reload(ai_models)
            
            # Now test the top-level import
            from ai_models import MCPAdapter
            
            # Check if the import succeeded
            assert MCPAdapter is not None, "MCPAdapter should not be None"
            assert MCPAdapter.__name__ == "MCPAdapter", f"Expected 'MCPAdapter', got '{MCPAdapter.__name__}'"
        except ImportError as e:
            pytest.fail(f"Failed to import MCPAdapter from ai_models: {e}")
