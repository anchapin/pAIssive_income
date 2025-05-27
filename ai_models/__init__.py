"""__init__ - Module for ai_models.__init__."""

from __future__ import annotations

# Standard library imports
import contextlib
import logging
from typing import Any

# Local imports
from .version import __version__

# Configure logging
logger = logging.getLogger(__name__)

# Third-party imports
try:
    # Try to import aiohttp
    import aiohttp
    AIOHTTP_AVAILABLE = True
    logger.info(f"aiohttp version {aiohttp.__version__} is available")
except ImportError as e:
    # If aiohttp is not available, use mock implementations
    AIOHTTP_AVAILABLE = False
    logger.warning(f"aiohttp not available: {e}. Using mock implementations")
    # Import mock_aiohttp as aiohttp
    try:
        from . import mock_aiohttp as aiohttp
        logger.info(f"Using mock aiohttp version {aiohttp.__version__}")
    except ImportError as e2:
        logger.exception(f"Failed to import mock_aiohttp: {e2}")


# Define variables that will be populated when importing adapters
OllamaAdapter: Any = None
OpenAICompatibleAdapter: Any = None
LMStudioAdapter: Any = None
TensorRTAdapter: Any = None
MCPAdapter: Any = None
AdapterError: type[Exception] = None  # type: ignore[assignment]
ModelContextProtocolError: type[Exception] = None  # type: ignore[assignment]
AdapterFactory: Any = None

# Use contextlib.suppress instead of try-except-pass
with contextlib.suppress(ImportError):
    # Import adapters
    from .adapters import AdapterError as ImportedAdapterError
    from .adapters import AdapterFactory as ImportedAdapterFactory
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
    AdapterFactory = ImportedAdapterFactory

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
