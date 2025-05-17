"""Tests for the adapter factory."""

# Standard library imports

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

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_get_adapter_ollama(self, mock_ollama_adapter):
        """Test get_adapter with Ollama server type."""
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance

        adapter = get_adapter("ollama", "localhost", 11434)

        mock_ollama_adapter.assert_called_once_with("localhost", 11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OpenAICompatibleAdapter")
    def test_get_adapter_openai(self, mock_openai_adapter):
        """Test get_adapter with OpenAI server type."""
        mock_instance = MagicMock()
        mock_openai_adapter.return_value = mock_instance

        adapter = get_adapter("openai", "api.openai.com", 443)

        mock_openai_adapter.assert_called_once_with("api.openai.com", 443)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.LMStudioAdapter")
    def test_get_adapter_lmstudio(self, mock_lmstudio_adapter):
        """Test get_adapter with LMStudio server type."""
        mock_instance = MagicMock()
        mock_lmstudio_adapter.return_value = mock_instance

        adapter = get_adapter("lmstudio", "localhost", 8000)

        mock_lmstudio_adapter.assert_called_once_with("localhost", 8000)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.TensorRTAdapter")
    def test_get_adapter_tensorrt(self, mock_tensorrt_adapter):
        """Test get_adapter with TensorRT server type."""
        mock_instance = MagicMock()
        mock_tensorrt_adapter.return_value = mock_instance

        adapter = get_adapter("tensorrt", "localhost", 8001)

        mock_tensorrt_adapter.assert_called_once_with("localhost", 8001)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_get_adapter_case_insensitive(self, mock_ollama_adapter):
        """Test get_adapter with case-insensitive server type."""
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance

        adapter = get_adapter("OLLAMA", "localhost", 11434)

        mock_ollama_adapter.assert_called_once_with("localhost", 11434)
        assert adapter == mock_instance

    @patch("ai_models.adapters.adapter_factory.OllamaAdapter")
    def test_get_adapter_with_kwargs(self, mock_ollama_adapter):
        """Test get_adapter with additional keyword arguments."""
        mock_instance = MagicMock()
        mock_ollama_adapter.return_value = mock_instance

        adapter = get_adapter("ollama", "localhost", 11434, model={"name": "llama2"})

        mock_ollama_adapter.assert_called_once_with(
            "localhost", 11434, model={"name": "llama2"}
        )
        assert adapter == mock_instance

    def test_get_adapter_unsupported_type(self):
        """Test get_adapter with unsupported server type."""
        with pytest.raises(UnsupportedServerTypeError) as excinfo:
            get_adapter("unsupported", "localhost", 8000)
        assert "Unsupported server type: unsupported" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.MCPAdapter", None)
    def test_get_adapter_mcp_not_available(self):
        """Test get_adapter with MCP server type when not available."""
        with pytest.raises(MCPAdapterNotAvailableError) as excinfo:
            get_adapter("mcp", "localhost", 9000)
        assert "MCPAdapter missing" in str(excinfo.value)

    @patch("ai_models.adapters.adapter_factory.MCPAdapter")
    def test_get_adapter_mcp_available(self, mock_mcp_adapter):
        """Test get_adapter with MCP server type when available."""
        mock_instance = MagicMock()
        mock_mcp_adapter.return_value = mock_instance

        adapter = get_adapter("mcp", "localhost", 9000)

        mock_mcp_adapter.assert_called_once_with("localhost", 9000)
        assert adapter == mock_instance
