"""Tests for the adapter factory."""

# Standard library imports
import logging
from unittest.mock import patch, MagicMock

# Third-party imports
from unittest.mock import MagicMock, patch

import pytest

# Local imports
from ai_models.adapters.adapter_factory import (
    MCPAdapterNotAvailableError,
    UnsupportedServerTypeError,
    get_adapter,
)


class TestAdapterFactory:
    """Tests for the adapter factory."""

    def setup_method(self):
        """Set up test method."""
        # Clear the adapter registry before each test
        AdapterFactory._adapter_registry = {}

    def test_get_available_adapter_types(self):
        """Test getting available adapter types."""
        # Initialize the registry
        AdapterFactory._initialize_registry()
        adapter_types = AdapterFactory.get_available_adapter_types()

        # Verify that the adapter types are available
        # Note: The actual types depend on what's available in the environment
        assert isinstance(adapter_types, list)

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_create_adapter_ollama(self, mock_ollama_adapter):
        """Test creating an Ollama adapter."""
        # Setup
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        # Execute
        adapter = AdapterFactory.create_adapter("ollama", host="localhost", port=11434)

        # Verify
        mock_ollama_adapter.assert_called_once_with(host="localhost", port=11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OpenAICompatibleAdapter")
    def test_create_adapter_openai(self, mock_openai_adapter):
        """Test creating an OpenAI-compatible adapter."""
        # Setup
        mock_instance = MagicMock()
        mock_openai_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"openai": mock_openai_adapter}

        # Execute
        adapter = AdapterFactory.create_adapter("openai", host="api.openai.com", port=443)

        # Verify
        mock_openai_adapter.assert_called_once_with(host="api.openai.com", port=443)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.LMStudioAdapter")
    def test_create_adapter_lmstudio(self, mock_lmstudio_adapter):
        """Test creating an LM Studio adapter."""
        # Setup
        mock_instance = MagicMock()
        mock_lmstudio_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"lmstudio": mock_lmstudio_adapter}

        # Execute
        adapter = AdapterFactory.create_adapter("lmstudio", host="localhost", port=8000)

        # Verify
        mock_lmstudio_adapter.assert_called_once_with(host="localhost", port=8000)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.TensorRTAdapter")
    def test_create_adapter_tensorrt(self, mock_tensorrt_adapter):
        """Test creating a TensorRT adapter."""
        # Setup
        mock_instance = MagicMock()
        mock_tensorrt_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"tensorrt": mock_tensorrt_adapter}

        # Execute
        adapter = AdapterFactory.create_adapter("tensorrt", host="localhost", port=8001)

        # Verify
        mock_tensorrt_adapter.assert_called_once_with(host="localhost", port=8001)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_create_adapter_case_insensitive(self, mock_ollama_adapter):
        """Test creating an adapter with case-insensitive type."""
        # Setup
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        # Execute
        adapter = AdapterFactory.create_adapter("OLLAMA", host="localhost", port=11434)

        # Verify
        mock_ollama_adapter.assert_called_once_with(host="localhost", port=11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_create_adapter_with_kwargs(self, mock_ollama_adapter):
        """Test creating an adapter with additional keyword arguments."""
        # Setup
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        adapter = get_adapter("ollama", "localhost", 11434, model={"name": "llama2"})

        mock_ollama_adapter.assert_called_once_with(
            "localhost", 11434, model={"name": "llama2"}
        )
        assert adapter == mock_instance

    def test_create_adapter_unsupported_type(self):
        """Test creating an adapter with an unsupported type."""
        # Setup
        AdapterFactory._adapter_registry = {}

        # Execute and verify
        with pytest.raises(UnsupportedServerTypeError) as excinfo:
            AdapterFactory.create_adapter("unsupported", host="localhost", port=8000)
        assert "Unsupported server type: unsupported" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.MCPAdapter", None)
    def test_create_adapter_mcp_not_available(self):
        """Test creating an MCP adapter when not available."""
        # Setup
        AdapterFactory._adapter_registry = {}

        # Execute and verify
        with pytest.raises(MCPAdapterNotAvailableError) as excinfo:
            AdapterFactory.create_adapter("mcp", host="localhost", port=9000)
        assert "MCPAdapter missing" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.MCPAdapter")
    def test_create_adapter_mcp_available(self, mock_mcp_adapter):
        """Test creating an MCP adapter when available."""
        # Setup
        mock_instance = MagicMock()
        mock_mcp_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"mcp": mock_mcp_adapter}

        # Execute
        adapter = AdapterFactory.create_adapter("mcp", host="localhost", port=9000)

        # Verify
        mock_mcp_adapter.assert_called_once_with(host="localhost", port=9000)
        assert adapter == mock_instance

    def test_register_adapter(self):
        """Test registering a new adapter type."""
        # Setup
        mock_adapter_class = MagicMock()
        AdapterFactory._adapter_registry = {}

        # Execute
        AdapterFactory.register_adapter("mock_adapter", mock_adapter_class)

        # Verify
        adapter_types = AdapterFactory.get_available_adapter_types()
        assert "mock_adapter" in adapter_types

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_create_adapter_error(self, mock_ollama_adapter):
        """Test error handling when creating an adapter."""
        # Setup
        mock_ollama_adapter.side_effect = Exception("Test error")
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        # Execute and verify
        with pytest.raises(Exception) as excinfo:
            AdapterFactory.create_adapter("ollama", host="localhost", port=11434)
        assert "Test error" in str(excinfo.value)
