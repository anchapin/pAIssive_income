"""__init__ - Module for ai_models.__init__."""

# Standard library imports
import contextlib
import logging
from typing import Any, Optional, Type

# Third-party imports
try:
    # Try to import aiohttp
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    # If aiohttp is not available, use mock implementations
    AIOHTTP_AVAILABLE = False
    logging.warning("aiohttp not available, using mock implementations")

# Local imports

# Define variables that will be populated when importing adapters
BaseModelAdapter: Optional[Any] = None
OllamaAdapter: Optional[Any] = None
OpenAICompatibleAdapter: Optional[Any] = None
LMStudioAdapter: Optional[Any] = None
TensorRTAdapter: Optional[Any] = None
MCPAdapter: Optional[Any] = None
AdapterFactory: Optional[Any] = None
AdapterError: Optional[Type[Exception]] = None
ModelContextProtocolError: Optional[Type[Exception]] = None

# Check if aiohttp is available before importing adapters
if AIOHTTP_AVAILABLE:
    # Use contextlib.suppress instead of try-except-pass
    with contextlib.suppress(ImportError):
        # Import adapters
        from .adapters import (
            BaseModelAdapter,
            OllamaAdapter,
            OpenAICompatibleAdapter,
            LMStudioAdapter,
            TensorRTAdapter,
            MCPAdapter,
            AdapterFactory,
            AdapterError,
            ModelContextProtocolError,
        )
else:
    # Log warning about using mock implementations
    logging.warning("Using mock adapters due to missing aiohttp")
    # Import mock adapters
    with contextlib.suppress(ImportError):
        from .mock_adapters import (
            MockBaseModelAdapter as BaseModelAdapter,
            MockOllamaAdapter as OllamaAdapter,
            MockLMStudioAdapter as LMStudioAdapter,
            MockOpenAICompatibleAdapter as OpenAICompatibleAdapter,
            MockAdapterFactory as AdapterFactory,
        )

# Version information
from .version import __version__

# Define what should be exported
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
    "__version__",
]
