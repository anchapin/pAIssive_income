"""__init__ - Module for ai_models.__init__."""

# Standard library imports
import contextlib
from typing import Any, Optional, Type

# Third-party imports

# Local imports

# Define variables that will be populated when importing adapters
OllamaAdapter: Optional[Any] = None
OpenAICompatibleAdapter: Optional[Any] = None
LMStudioAdapter: Optional[Any] = None
TensorRTAdapter: Optional[Any] = None
MCPAdapter: Optional[Any] = None
AdapterError: Optional[Type[Exception]] = None
ModelContextProtocolError: Optional[Type[Exception]] = None

# Use contextlib.suppress instead of try-except-pass
with contextlib.suppress(ImportError):
    # Import adapters
    from .adapters import (
        OllamaAdapter,
        OpenAICompatibleAdapter,
        LMStudioAdapter,
        TensorRTAdapter,
        MCPAdapter,
        AdapterError,
        ModelContextProtocolError,
    )

# Version information
from .version import __version__

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
