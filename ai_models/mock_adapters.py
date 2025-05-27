"""
mock_adapters - Module for ai_models.mock_adapters.

This module provides mock implementations of the adapter classes for testing.
"""

# Standard library imports
import logging
from typing import Any, Dict, List, Optional, Type

# Configure logging
logger = logging.getLogger(__name__)


# Configure logger

# Third-party imports

# Local imports

class MockBaseModelAdapter:
    """Mock implementation of BaseModelAdapter for testing."""

    def __init__(self):
        """Initialize the mock base model adapter."""
        logger.info("Initialized MockBaseModelAdapter")

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.

        Returns:
            List of model information dictionaries

        """
        logger.info("Listing mock models")
        models = [
            {"name": "mock-model-1", "size": "7B"},
            {"name": "mock-model-2", "size": "13B"},
        ]
        logger.info(f"Found {len(models)} mock models")
        return models

    async def generate_text(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using the specified model.

        Args:
            model: The name of the model to use
            prompt: The input prompt
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated text

        """
        logger.info(f"Generating text with model {model}")
        response = {
            "model": model,
            "response": f"Mock response for prompt: {prompt}",
            "done": True
        }
        logger.info("Text generation completed")
        return response

    async def generate_chat_completions(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generate chat completions using the specified model.

        Args:
            model: The name of the model to use
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the model

        Returns:
            Response dictionary containing the generated chat completion

        """
        logger.info(f"Generating chat completion with model {model} for {len(messages)} messages")
        response = {
            "model": model,
            "message": {
                "role": "assistant",
                "content": f"Mock chat response for {len(messages)} messages"
            }
        }
        logger.info("Chat completion generated")
        return response

    async def close(self):
        """Close any resources."""
        logger.info("Closing mock adapter resources")


class MockOllamaAdapter(MockBaseModelAdapter):
    """Mock implementation of OllamaAdapter for testing."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60):
        """
        Initialize the mock Ollama adapter.

        Args:
            base_url: The base URL of the Ollama API server
            timeout: Request timeout in seconds

        """
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockOllamaAdapter with base_url={base_url}")


class MockLMStudioAdapter(MockBaseModelAdapter):
    """Mock implementation of LMStudioAdapter for testing."""

    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: Optional[str] = None, timeout: int = 60):
        """
        Initialize the mock LM Studio adapter.

        Args:
            base_url: The base URL of the LM Studio API server
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds

        """
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockLMStudioAdapter with base_url={base_url}")


class MockOpenAICompatibleAdapter(MockBaseModelAdapter):
    """Mock implementation of OpenAICompatibleAdapter for testing."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        """
        Initialize the mock OpenAI-compatible adapter.

        Args:
            base_url: The base URL of the API server
            api_key: API key for authentication
            timeout: Request timeout in seconds

        """
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockOpenAICompatibleAdapter with base_url={base_url}")


class MockTensorRTAdapter(MockBaseModelAdapter):
    """Mock implementation of TensorRTAdapter for testing."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 60):
        """
        Initialize the mock TensorRT adapter.

        Args:
            base_url: The base URL of the TensorRT API server
            timeout: Request timeout in seconds

        """
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self._session = None
        logger.info(f"Initialized MockTensorRTAdapter with base_url={base_url}")


class MockMCPAdapter(MockBaseModelAdapter):
    """Mock implementation of MCPAdapter for testing."""

    def __init__(self, host: str = "localhost", port: int = 9000, timeout: int = 60):
        """
        Initialize the mock MCP adapter.

        Args:
            host: The hostname of the MCP server
            port: The port of the MCP server
            timeout: Request timeout in seconds

        """
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self._client = None
        logger.info(f"Initialized MockMCPAdapter with host={host}, port={port}")

    async def connect(self) -> bool:
        """
        Connect to the MCP server.

        Returns:
            True if connection was successful, False otherwise

        """
        logger.info(f"Connecting to mock MCP server at {self.host}:{self.port}")
        return True

    async def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a message to the MCP server.

        Args:
            message: The message to send

        Returns:
            Response dictionary from the server

        """
        logger.info(f"Sending message to mock MCP server: {message[:50]}...")
        return {
            "response": f"Mock MCP response for: {message[:20]}...",
            "status": "success"
        }


class MockAdapterFactory:
    """Mock factory class for creating model adapters."""

    # Registry of adapter types
    _adapter_registry = {
        "ollama": MockOllamaAdapter,
        "lmstudio": MockLMStudioAdapter,
        "openai": MockOpenAICompatibleAdapter,
        "tensorrt": MockTensorRTAdapter,
        "mcp": MockMCPAdapter,
    }

    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[MockBaseModelAdapter]) -> None:
        """
        Register a new adapter type.

        Args:
            name: The name of the adapter type
            adapter_class: The adapter class to register

        """
        cls._adapter_registry[name] = adapter_class
        logger.info(f"Registered adapter type: {name}")

    @classmethod
    def create_adapter(cls, adapter_type: str, **kwargs) -> Optional[MockBaseModelAdapter]:
        """
        Create an adapter of the specified type.

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
        """
        Get a list of available adapter types.

        Returns:
            List of available adapter type names

        """
        logger.info("Getting available adapter types")
        adapter_types = list(cls._adapter_registry.keys())
        logger.info(f"Found {len(adapter_types)} available adapter types")
        return adapter_types
