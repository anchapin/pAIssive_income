"""__init__ - Module for ai_models/adapters.__init__."""

# Standard library imports
from __future__ import annotations

import importlib.util
from typing import Any

# Third-party imports
# Local imports
# Export the exception classes first (these should always be available)
from .exceptions import AdapterError, ModelContextProtocolError

# Define adapter classes as optional
# We'll try to import them, but if they're not available, they'll remain None
OllamaAdapter: Any | None = None
OpenAICompatibleAdapter: Any | None = None
LMStudioAdapter: Any | None = None
TensorRTAdapter: Any | None = None
MCPAdapter: Any | None = None


# Helper function to safely import an adapter
def _safe_import(module_name: str, class_name: str) -> object | None:
    """
    Safely import a class from a module.

    Args:
        module_name: The name of the module to import from
        class_name: The name of the class to import

    Returns:
        The imported class or None if import failed

    """
    try:
        # Check if the module can be imported
        if importlib.util.find_spec(f"ai_models.adapters.{module_name}"):
            # Import the module
            module = importlib.import_module(
                f".{module_name}", package="ai_models.adapters"
            )
            # Get the class from the module
            return getattr(module, class_name, None)
    except (ImportError, AttributeError):
        pass

    # Return None if any of the above fails
    return None


# Import adapters safely
OllamaAdapter = _safe_import("ollama_adapter", "OllamaAdapter")
OpenAICompatibleAdapter = _safe_import(
    "openai_compatible_adapter", "OpenAICompatibleAdapter"
)
LMStudioAdapter = _safe_import("lmstudio_adapter", "LMStudioAdapter")
TensorRTAdapter = _safe_import("tensorrt_adapter", "TensorRTAdapter")
MCPAdapter = _safe_import("mcp_adapter", "MCPAdapter")
