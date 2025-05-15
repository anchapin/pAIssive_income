"""test_adapter_factory - Module for tests/ai_models/adapters.test_adapter_factory."""

# Standard library imports
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest

# Local imports
from ai_models.adapters import (
    BaseModelAdapter,
    OllamaAdapter,
    LMStudioAdapter,
    OpenAICompatibleAdapter,
)
from ai_models.adapters.adapter_factory import AdapterFactory


def test_get_available_adapter_types():
    """Test getting available adapter types."""
    adapter_types = AdapterFactory.get_available_adapter_types()

    # Verify that the default adapter types are available
    assert "ollama" in adapter_types
    assert "lmstudio" in adapter_types
    assert "openai" in adapter_types


def test_register_adapter():
    """Test registering a new adapter type."""
    # Create a mock adapter class
    mock_adapter_class = MagicMock(spec=BaseModelAdapter)

    # Register the mock adapter
    AdapterFactory.register_adapter("mock_adapter", mock_adapter_class)

    # Verify that the mock adapter is registered
    adapter_types = AdapterFactory.get_available_adapter_types()
    assert "mock_adapter" in adapter_types

    # Clean up by removing the mock adapter
    AdapterFactory._adapter_registry.pop("mock_adapter")


def test_create_adapter_ollama():
    """Test creating an Ollama adapter."""
    # Create an adapter
    adapter = AdapterFactory.create_adapter("ollama", base_url="http://test-ollama:11434")

    # Verify that the adapter was created correctly
    assert adapter is not None
    assert isinstance(adapter, OllamaAdapter)
    assert adapter.base_url == "http://test-ollama:11434"


def test_create_adapter_lmstudio():
    """Test creating an LM Studio adapter."""
    # Create an adapter
    adapter = AdapterFactory.create_adapter("lmstudio", base_url="http://test-lmstudio:1234/v1", api_key="test-key")

    # Verify that the adapter was created correctly
    assert adapter is not None
    assert isinstance(adapter, LMStudioAdapter)
    assert adapter.base_url == "http://test-lmstudio:1234/v1"
    assert adapter.api_key == "test-key"


def test_create_adapter_openai():
    """Test creating an OpenAI-compatible adapter."""
    # Create an adapter
    adapter = AdapterFactory.create_adapter("openai", base_url="http://test-openai:8000/v1", api_key="test-key")

    # Verify that the adapter was created correctly
    assert adapter is not None
    assert isinstance(adapter, OpenAICompatibleAdapter)
    assert adapter.base_url == "http://test-openai:8000/v1"
    assert adapter.api_key == "test-key"


def test_create_adapter_unknown_type():
    """Test creating an adapter with an unknown type."""
    adapter = AdapterFactory.create_adapter("unknown_type")

    # Verify that None is returned for unknown adapter types
    assert adapter is None


def test_create_adapter_error():
    """Test error handling when creating an adapter."""
    # Create a custom adapter class that raises an exception
    class ErrorAdapter(BaseModelAdapter):
        def __init__(self):
            raise Exception("Test error")

        async def list_models(self):
            pass

        async def generate_text(self, model, prompt, **kwargs):
            pass

        async def generate_chat_completions(self, model, messages, **kwargs):
            pass

        async def close(self):
            pass

    # Register the error adapter
    AdapterFactory.register_adapter("error_adapter", ErrorAdapter)

    # Create an adapter
    adapter = AdapterFactory.create_adapter("error_adapter")

    # Verify that None is returned when an error occurs
    assert adapter is None

    # Clean up
    AdapterFactory._adapter_registry.pop("error_adapter")
