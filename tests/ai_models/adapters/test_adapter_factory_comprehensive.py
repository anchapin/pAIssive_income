"""Comprehensive tests for the ai_models.adapters.adapter_factory module."""

from unittest.mock import MagicMock, patch

import pytest

from ai_models.adapters.adapter_factory import (
    AdapterFactory,
    LMStudioAdapter,
    MCPAdapterNotAvailableError,
    OllamaAdapter,
    OpenAICompatibleAdapter,
    UnsupportedServerTypeError,
    get_adapter,
)


class TestAdapterFactoryComprehensive:
    """Comprehensive test suite for the adapter factory."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Reset the adapter registry before each test
        AdapterFactory._adapter_registry = {}

    def teardown_method(self):
        """Clean up after each test."""
        # Reset the adapter registry after each test
        AdapterFactory._adapter_registry = {}

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_get_adapter_ollama(self, mock_ollama_adapter):
        """Test get_adapter with Ollama server type."""
        # Setup mock
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance

        # Call get_adapter
        adapter = get_adapter("ollama", "localhost", 11434)

        # Verify
        mock_ollama_adapter.assert_called_once_with("localhost", 11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OpenAICompatibleAdapter")
    def test_get_adapter_openai(self, mock_openai_adapter):
        """Test get_adapter with OpenAI server type."""
        # Setup mock
        mock_instance = MagicMock()
        mock_openai_adapter.return_value = mock_instance

        # Call get_adapter
        adapter = get_adapter("openai", "api.openai.com", 443)

        # Verify
        mock_openai_adapter.assert_called_once_with("api.openai.com", 443)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.LMStudioAdapter")
    def test_get_adapter_lmstudio(self, mock_lmstudio_adapter):
        """Test get_adapter with LMStudio server type."""
        # Setup mock
        mock_instance = MagicMock()
        mock_lmstudio_adapter.return_value = mock_instance

        # Call get_adapter
        adapter = get_adapter("lmstudio", "localhost", 8000)

        # Verify
        mock_lmstudio_adapter.assert_called_once_with("localhost", 8000)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.TensorRTAdapter")
    def test_get_adapter_tensorrt(self, mock_tensorrt_adapter):
        """Test get_adapter with TensorRT server type."""
        # Setup mock
        mock_instance = MagicMock()
        mock_tensorrt_adapter.return_value = mock_instance

        # Call get_adapter
        adapter = get_adapter("tensorrt", "localhost", 8000)

        # Verify
        mock_tensorrt_adapter.assert_called_once_with("localhost", 8000)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.MCPAdapter", None)
    def test_get_adapter_mcp_not_available(self):
        """Test get_adapter with MCP server type when MCP adapter is not available."""
        # Call get_adapter and verify it raises the expected exception
        with pytest.raises(MCPAdapterNotAvailableError) as excinfo:
            get_adapter("mcp", "localhost", 9000)

        assert "MCPAdapter missing" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.MCPAdapter")
    def test_get_adapter_mcp_available(self, mock_mcp_adapter):
        """Test get_adapter with MCP server type when MCP adapter is available."""
        # Setup mock
        mock_instance = MagicMock()
        mock_mcp_adapter.return_value = mock_instance

        # Call get_adapter
        adapter = get_adapter("mcp", "localhost", 9000)

        # Verify
        mock_mcp_adapter.assert_called_once_with("localhost", 9000)
        assert adapter == mock_instance

    def test_get_adapter_unsupported(self):
        """Test get_adapter with an unsupported server type."""
        # Call get_adapter and verify it raises the expected exception
        with pytest.raises(UnsupportedServerTypeError) as excinfo:
            get_adapter("unsupported", "localhost", 8000)

        assert "Unsupported server type: unsupported" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_get_adapter_case_insensitive(self, mock_ollama_adapter):
        """Test get_adapter with case-insensitive server type."""
        # Setup mock
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance

        # Call get_adapter with uppercase server type
        adapter = get_adapter("OLLAMA", "localhost", 11434)

        # Verify
        mock_ollama_adapter.assert_called_once_with("localhost", 11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_get_adapter_with_kwargs(self, mock_ollama_adapter):
        """Test get_adapter with additional keyword arguments."""
        # Setup mock
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance

        # Call get_adapter with additional kwargs
        adapter = get_adapter("ollama", "localhost", 11434, model="llama2", temperature=0.7)

        # Verify
        mock_ollama_adapter.assert_called_once_with("localhost", 11434, model="llama2", temperature=0.7)
        assert adapter == mock_instance

    def test_adapter_factory_initialize_registry(self):
        """Test AdapterFactory._initialize_registry method."""
        # Call _initialize_registry
        registry = AdapterFactory._initialize_registry()

        # Verify the registry contains the expected adapters
        assert "ollama" in registry
        assert "openai" in registry
        assert "lmstudio" in registry
        assert "tensorrt" in registry
        assert registry["ollama"] == OllamaAdapter
        assert registry["openai"] == OpenAICompatibleAdapter
        assert registry["lmstudio"] == LMStudioAdapter

    @patch("ai_models.adapters.adapter_factory.MCPAdapter", None)
    def test_adapter_factory_initialize_registry_no_mcp(self):
        """Test AdapterFactory._initialize_registry when MCP adapter is not available."""
        # Call _initialize_registry
        registry = AdapterFactory._initialize_registry()

        # Verify MCP adapter is not in the registry
        assert "mcp" not in registry

    @patch("ai_models.adapters.adapter_factory.MCPAdapter")
    def test_adapter_factory_initialize_registry_with_mcp(self, mock_mcp_adapter):
        """Test AdapterFactory._initialize_registry when MCP adapter is available."""
        # Call _initialize_registry
        registry = AdapterFactory._initialize_registry()

        # Verify MCP adapter is in the registry
        assert "mcp" in registry
        assert registry["mcp"] == mock_mcp_adapter

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_adapter_factory_create_adapter(self, mock_ollama_adapter):
        """Test AdapterFactory.create_adapter method."""
        # Setup mock
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        # Call create_adapter
        adapter = AdapterFactory.create_adapter("ollama", host="localhost", port=11434)

        # Verify
        mock_ollama_adapter.assert_called_once_with(host="localhost", port=11434)
        assert adapter == mock_instance

    def test_adapter_factory_create_adapter_unsupported(self):
        """Test AdapterFactory.create_adapter with an unsupported adapter type."""
        # Initialize registry
        AdapterFactory._initialize_registry()

        # Call create_adapter and verify it raises the expected exception
        with pytest.raises(UnsupportedServerTypeError) as excinfo:
            AdapterFactory.create_adapter("unsupported", host="localhost", port=8000)

        assert "Unsupported server type: unsupported" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.MCPAdapter", None)
    def test_adapter_factory_create_adapter_mcp_not_available(self):
        """Test AdapterFactory.create_adapter with MCP when it's not available."""
        # Initialize registry but manually add 'mcp' to it
        AdapterFactory._initialize_registry()
        # Manually add 'mcp' to the registry to simulate it being recognized but not available
        AdapterFactory._adapter_registry["mcp"] = None

        # Call create_adapter and verify it raises the expected exception
        with pytest.raises(MCPAdapterNotAvailableError) as excinfo:
            AdapterFactory.create_adapter("mcp", host="localhost", port=9000)

        assert "MCPAdapter missing" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_adapter_factory_create_adapter_case_insensitive(self, mock_ollama_adapter):
        """Test AdapterFactory.create_adapter with case-insensitive adapter type."""
        # Setup mock
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        # Call create_adapter with uppercase adapter type
        adapter = AdapterFactory.create_adapter("OLLAMA", host="localhost", port=11434)

        # Verify
        mock_ollama_adapter.assert_called_once_with(host="localhost", port=11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_adapter_factory_create_adapter_with_kwargs(self, mock_ollama_adapter):
        """Test AdapterFactory.create_adapter with additional keyword arguments."""
        # Setup mock
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance
        AdapterFactory._adapter_registry = {"ollama": mock_ollama_adapter}

        # Call create_adapter with additional kwargs
        adapter = AdapterFactory.create_adapter("ollama", host="localhost", port=11434, model="llama2", temperature=0.7)

        # Verify
        mock_ollama_adapter.assert_called_once_with(host="localhost", port=11434, model="llama2", temperature=0.7)
        assert adapter == mock_instance
