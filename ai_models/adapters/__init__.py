"""__init__ - Module for ai_models/adapters.__init__."""

# Standard library imports
import importlib
import importlib.util
import sys
from typing import Any, Optional, Type

# Third-party imports

# Local imports
# Export the exception classes first (these should always be available)
from .exceptions import (
    AdapterError,
    ModelContextProtocolError,
)

# Define adapter classes as optional
# We'll try to import them, but if they're not available, they'll remain None
BaseModelAdapter: Optional[Any] = None
OllamaAdapter: Optional[Any] = None
OpenAICompatibleAdapter: Optional[Any] = None
LMStudioAdapter: Optional[Any] = None
TensorRTAdapter: Optional[Any] = None
MCPAdapter: Optional[Any] = None
AdapterFactory: Optional[Any] = None

# Helper function to safely import an adapter
def _safe_import(module_name: str, class_name: str) -> Optional[Any]:
    """Safely import a class from a module.

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
            module = importlib.import_module(f".{module_name}", package="ai_models.adapters")
            # Get the class from the module
            return getattr(module, class_name, None)
        else:
            return None
    except (ImportError, AttributeError):
        return None

# Import adapters safely
BaseModelAdapter = _safe_import("base_adapter", "BaseModelAdapter")
OllamaAdapter = _safe_import("ollama_adapter", "OllamaAdapter")
OpenAICompatibleAdapter = _safe_import("openai_compatible_adapter", "OpenAICompatibleAdapter")
LMStudioAdapter = _safe_import("lmstudio_adapter", "LMStudioAdapter")
TensorRTAdapter = _safe_import("tensorrt_adapter", "TensorRTAdapter")
MCPAdapter = _safe_import("mcp_adapter", "MCPAdapter")
AdapterFactory = _safe_import("adapter_factory", "AdapterFactory")

__all__ = [
    "AdapterError",
    "AdapterFactory",
    "BaseModelAdapter",
    "LMStudioAdapter",
    "MCPAdapter",
    "ModelContextProtocolError",
    "OllamaAdapter",
    "OpenAICompatibleAdapter",
    "TensorRTAdapter",
]
