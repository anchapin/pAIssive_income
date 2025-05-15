"""__init__ - Module for ai_models.__init__."""

# Standard library imports
import logging

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
if AIOHTTP_AVAILABLE:
    try:
        from .adapters import (
            BaseModelAdapter,
            OllamaAdapter,
            LMStudioAdapter,
            OpenAICompatibleAdapter,
            AdapterFactory,
        )
    except ImportError as e:
        logging.warning(f"Error importing adapters: {e}")
        # Use mock implementations
        from .mock_adapters import (
            MockBaseModelAdapter as BaseModelAdapter,
            MockOllamaAdapter as OllamaAdapter,
            MockLMStudioAdapter as LMStudioAdapter,
            MockOpenAICompatibleAdapter as OpenAICompatibleAdapter,
            MockAdapterFactory as AdapterFactory,
        )
else:
    # Use mock implementations
    from .mock_adapters import (
        MockBaseModelAdapter as BaseModelAdapter,
        MockOllamaAdapter as OllamaAdapter,
        MockLMStudioAdapter as LMStudioAdapter,
        MockOpenAICompatibleAdapter as OpenAICompatibleAdapter,
        MockAdapterFactory as AdapterFactory,
    )

__all__ = [
    'BaseModelAdapter',
    'OllamaAdapter',
    'LMStudioAdapter',
    'OpenAICompatibleAdapter',
    'AdapterFactory',
]
