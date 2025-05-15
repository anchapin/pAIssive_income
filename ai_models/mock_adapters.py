"""mock_adapters - Module for ai_models.mock_adapters.

This module provides mock implementations of the adapter classes for testing.
"""

# Standard library imports
import logging
from typing import Dict, Any, List, Optional, Type

# Third-party imports

# Local imports

logger = logging.getLogger(__name__)

class MockBaseModelAdapter:
    """Mock implementation of BaseModelAdapter for testing."""

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models.

        Returns:
            List of model information dictionaries
        """
        return [
            {"name": "mock-model-1", "size": "7B"},
            {"name": "mock-model-2", "size": "13B"},
        ]

    async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the specified model.

        Args:
            model: The name of the model to use
            prompt: The input prompt
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated text
        """
        return {
            "model": model,
            "response": f"Mock response for prompt: {prompt}",
            "done": True
        }

    async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completions using the specified model.

        Args:
            model: The name of the model to use
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated chat completion
        """
        return {
            "model": model,
            "message": {
                "role": "assistant",
                "content": f"Mock chat response for {len(messages)} messages"
            }
        }

    async def close(self):
        """Close any resources."""
        pass


class MockOllamaAdapter(MockBaseModelAdapter):
    """Mock implementation of OllamaAdapter for testing."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60):
        """Initialize the mock Ollama adapter.

        Args:
            base_url: The base URL of the Ollama API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockOllamaAdapter with base_url={base_url}")


class MockLMStudioAdapter(MockBaseModelAdapter):
    """Mock implementation of LMStudioAdapter for testing."""

    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: Optional[str] = None, timeout: int = 60):
        """Initialize the mock LM Studio adapter.

        Args:
            base_url: The base URL of the LM Studio API server
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockLMStudioAdapter with base_url={base_url}")


class MockOpenAICompatibleAdapter(MockBaseModelAdapter):
    """Mock implementation of OpenAICompatibleAdapter for testing."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        """Initialize the mock OpenAI-compatible adapter.

        Args:
            base_url: The base URL of the API server
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockOpenAICompatibleAdapter with base_url={base_url}")


class MockAdapterFactory:
    """Mock factory class for creating model adapters."""

    # Registry of adapter types
    _adapter_registry = {
        "ollama": MockOllamaAdapter,
        "lmstudio": MockLMStudioAdapter,
        "openai": MockOpenAICompatibleAdapter,
    }

    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[MockBaseModelAdapter]) -> None:
        """Register a new adapter type.

        Args:
            name: The name of the adapter type
            adapter_class: The adapter class to register
        """
        cls._adapter_registry[name] = adapter_class
        logger.info(f"Registered adapter type: {name}")

    @classmethod
    def create_adapter(cls, adapter_type: str, **kwargs) -> Optional[MockBaseModelAdapter]:
        """Create an adapter of the specified type.

        Args:
            adapter_type: The type of adapter to create
            **kwargs: Additional parameters to pass to the adapter constructor

        Returns:
            An instance of the specified adapter type, or None if the type is not registered
        """
        adapter_class = cls._adapter_registry.get(adapter_type)
        if adapter_class is None:
            logger.error(f"Unknown adapter type: {adapter_type}")
            return None

        try:
            adapter = adapter_class(**kwargs)
            logger.info(f"Created adapter of type: {adapter_type}")
        except Exception:
            logger.exception(f"Error creating adapter of type {adapter_type}")
            return None
        return adapter

    @classmethod
    def get_available_adapter_types(cls) -> List[str]:
        """Get a list of available adapter types.

        Returns:
            List of available adapter type names
        """
        return list(cls._adapter_registry.keys())
