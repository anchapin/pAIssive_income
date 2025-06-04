"""__init__ - Module for ai_models.__init__."""

from __future__ import annotations

# Standard library imports
import contextlib
from typing import Any

# Local imports
from .version import __version__

# Third-party imports


# Define variables that will be populated when importing adapters
OllamaAdapter: Any = None
OpenAICompatibleAdapter: Any = None
LMStudioAdapter: Any = None
TensorRTAdapter: Any = None
MCPAdapter: Any = None
# The type: ignore is required for conditional import patterns and dynamic assignment of exception types.
# This is safe because the variable is always set to a valid Exception type or None.
AdapterError: type[Exception] = None  # type: ignore[assignment]
# The type: ignore is required for conditional import patterns and dynamic assignment of exception types.
# This is safe because the variable is always set to a valid Exception type or None.
ModelContextProtocolError: type[Exception] = None  # type: ignore[assignment]

# Use contextlib.suppress instead of try-except-pass
with contextlib.suppress(ImportError):
    # Import adapters
    from .adapters import AdapterError as ImportedAdapterError
    from .adapters import LMStudioAdapter as ImportedLMStudioAdapter
    from .adapters import MCPAdapter as ImportedMCPAdapter
    from .adapters import ModelContextProtocolError as ImportedModelContextProtocolError
    from .adapters import OllamaAdapter as ImportedOllamaAdapter
    from .adapters import OpenAICompatibleAdapter as ImportedOpenAICompatibleAdapter
    from .adapters import TensorRTAdapter as ImportedTensorRTAdapter

    # Update the module variables with the imported values
    OllamaAdapter = ImportedOllamaAdapter
    OpenAICompatibleAdapter = ImportedOpenAICompatibleAdapter
    LMStudioAdapter = ImportedLMStudioAdapter
    TensorRTAdapter = ImportedTensorRTAdapter
    MCPAdapter = ImportedMCPAdapter
    AdapterError = ImportedAdapterError
    ModelContextProtocolError = ImportedModelContextProtocolError

# Define what should be exported
__all__ = [
    "AdapterError",
    "LMStudioAdapter",
    "MCPAdapter",
    "ModelContextProtocolError",
    "OllamaAdapter",
    "OpenAICompatibleAdapter",
    "TensorRTAdapter",
    "__version__",
]
