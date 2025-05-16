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
    logging.info(f"aiohttp version {aiohttp.__version__} is available")
except ImportError as e:
    # If aiohttp is not available, use mock implementations
    AIOHTTP_AVAILABLE = False
    logging.warning(f"aiohttp not available: {e}. Using mock implementations")
    # Import mock_aiohttp as aiohttp
    try:
        from . import mock_aiohttp as aiohttp
        logging.info(f"Using mock aiohttp version {aiohttp.__version__}")
    except ImportError as e2:
        logging.error(f"Failed to import mock_aiohttp: {e2}")

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

# Always import exceptions first to ensure they're available
try:
    from .adapters.exceptions import AdapterError, ModelContextProtocolError
except ImportError:
    logging.warning("Failed to import adapter exceptions")
    AdapterError = type("AdapterError", (Exception,), {})
    ModelContextProtocolError = type("ModelContextProtocolError", (AdapterError,), {})

# Check if aiohttp is available before importing adapters
if AIOHTTP_AVAILABLE:
    try:
        # Import adapters
        from .adapters import (
            BaseModelAdapter,
            OllamaAdapter,
            OpenAICompatibleAdapter,
            LMStudioAdapter,
            TensorRTAdapter,
            AdapterFactory,
        )
        
        # Import MCPAdapter separately to handle possible import errors
        try:
            from .adapters.mcp_adapter import MCPAdapter
            logging.info("Successfully imported MCPAdapter")
        except ImportError as e:
            logging.warning(f"Failed to import MCPAdapter: {e}")
            MCPAdapter = None
            
        logging.info("Successfully imported real adapters")
    except ImportError as e:
        logging.warning(f"Failed to import real adapters: {e}. Falling back to mock adapters.")
        AIOHTTP_AVAILABLE = False  # Force fallback to mock adapters
else:
    logging.warning("aiohttp not available, using mock adapters")

# If aiohttp is not available or imports failed, use mock adapters
if not AIOHTTP_AVAILABLE:
    try:
        # Import mock adapters
        from .mock_adapters import (
            MockBaseModelAdapter as BaseModelAdapter,
            MockOllamaAdapter as OllamaAdapter,
            MockLMStudioAdapter as LMStudioAdapter,
            MockOpenAICompatibleAdapter as OpenAICompatibleAdapter,
            MockTensorRTAdapter as TensorRTAdapter,
            MockMCPAdapter as MCPAdapter,
            MockAdapterFactory as AdapterFactory,
        )
        logging.info("Successfully imported mock adapters")
    except ImportError as e:
        logging.error(f"Failed to import mock adapters: {e}")
        # Create minimal mock implementations if all else fails
        if "BaseModelAdapter" not in locals() or BaseModelAdapter is None:
            BaseModelAdapter = type("BaseModelAdapter", (), {"__init__": lambda self, **kwargs: None})
        if "AdapterFactory" not in locals() or AdapterFactory is None:
            AdapterFactory = type("AdapterFactory", (), {"create_adapter": staticmethod(lambda *args, **kwargs: None)})

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
