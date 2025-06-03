"""Tests for the mock adapters module."""

import logging
from unittest.mock import MagicMock, patch

import pytest

# Patch the logger at the module level
patch_path = "ai_models.mock_adapters.logger"
mock_logger = MagicMock()
patcher = patch(patch_path, mock_logger)
patcher.start()

# Add a teardown function to stop the patcher
def teardown_module():
    """Stop the patcher when the module is unloaded."""
    patcher.stop()

from ai_models.mock_adapters import (
    MockAdapterFactory,
    MockBaseModelAdapter,
    MockLMStudioAdapter,
    MockMCPAdapter,
    MockOllamaAdapter,
    MockOpenAICompatibleAdapter,
    MockTensorRTAdapter,
)


class TestMockBaseModelAdapter:
    """Tests for the MockBaseModelAdapter class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_initialization(self):
        """Test that the adapter initializes correctly."""
        MockBaseModelAdapter()

        mock_logger.info.assert_called_with("Initialized MockBaseModelAdapter")

    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test that list_models returns the expected mock models."""
        mock_logger.reset_mock()

        adapter = MockBaseModelAdapter()
        models = await adapter.list_models()

        assert len(models) == 2
        assert models[0]["name"] == "mock-model-1"
        assert models[0]["size"] == "7B"
        assert models[1]["name"] == "mock-model-2"
        assert models[1]["size"] == "13B"

        mock_logger.info.assert_any_call("Listing mock models")
        mock_logger.info.assert_any_call("Found 2 mock models")

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test that generate_text returns the expected mock response."""
        mock_logger.reset_mock()

        adapter = MockBaseModelAdapter()
        response = await adapter.generate_text("test-model", "Hello, world!")

        assert response["model"] == "test-model"
        assert response["response"] == "Mock response for prompt: Hello, world!"
        assert response["done"] is True

        mock_logger.info.assert_any_call("Generating text with model test-model")
        mock_logger.info.assert_any_call("Text generation completed")

    @pytest.mark.asyncio
    async def test_generate_chat_completions(self):
        """Test that generate_chat_completions returns the expected mock response."""
        mock_logger.reset_mock()

        adapter = MockBaseModelAdapter()
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        response = await adapter.generate_chat_completions("test-model", messages)

        assert response["model"] == "test-model"
        assert response["message"]["role"] == "assistant"
        assert response["message"]["content"] == "Mock chat response for 2 messages"

        mock_logger.info.assert_any_call("Generating chat completion with model test-model for 2 messages")
        mock_logger.info.assert_any_call("Chat completion generated")

    @pytest.mark.asyncio
    async def test_close(self):
        """Test that close doesn't raise any exceptions."""
        mock_logger.reset_mock()

        adapter = MockBaseModelAdapter()
        await adapter.close()

        mock_logger.info.assert_any_call("Closing mock adapter resources")


class TestMockOllamaAdapter:
    """Tests for the MockOllamaAdapter class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_initialization(self):
        """Test that the adapter initializes correctly."""
        adapter = MockOllamaAdapter(base_url="http://test-url:11434", timeout=30)

        assert adapter.base_url == "http://test-url:11434"
        assert adapter.timeout == 30
        assert adapter._session is None
        mock_logger.info.assert_any_call("Initialized MockOllamaAdapter with base_url=http://test-url:11434")


class TestMockLMStudioAdapter:
    """Tests for the MockLMStudioAdapter class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_initialization(self):
        """Test that the adapter initializes correctly."""
        adapter = MockLMStudioAdapter(base_url="http://test-url:1234/v1", api_key="test-key", timeout=30)

        assert adapter.base_url == "http://test-url:1234/v1"
        assert adapter.api_key == "test-key"
        assert adapter.timeout == 30
        assert adapter._session is None
        mock_logger.info.assert_any_call("Initialized MockLMStudioAdapter with base_url=http://test-url:1234/v1")


class TestMockOpenAICompatibleAdapter:
    """Tests for the MockOpenAICompatibleAdapter class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_initialization(self):
        """Test that the adapter initializes correctly."""
        adapter = MockOpenAICompatibleAdapter(base_url="http://test-url/v1", api_key="test-key", timeout=30)

        assert adapter.base_url == "http://test-url/v1"
        assert adapter.api_key == "test-key"
        assert adapter.timeout == 30
        assert adapter._session is None
        mock_logger.info.assert_any_call("Initialized MockOpenAICompatibleAdapter with base_url=http://test-url/v1")


class TestMockTensorRTAdapter:
    """Tests for the MockTensorRTAdapter class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_initialization(self):
        """Test that the adapter initializes correctly."""
        adapter = MockTensorRTAdapter(base_url="http://test-url:8000", timeout=30)

        assert adapter.base_url == "http://test-url:8000"
        assert adapter.timeout == 30
        assert adapter._session is None
        mock_logger.info.assert_any_call("Initialized MockTensorRTAdapter with base_url=http://test-url:8000")


class TestMockMCPAdapter:
    """Tests for the MockMCPAdapter class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_initialization(self):
        """Test that the adapter initializes correctly."""
        adapter = MockMCPAdapter(host="test-host", port=9000, timeout=30)

        assert adapter.host == "test-host"
        assert adapter.port == 9000
        assert adapter.timeout == 30
        assert adapter._client is None
        mock_logger.info.assert_any_call("Initialized MockMCPAdapter with host=test-host, port=9000")

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test that connect returns True."""
        mock_logger.reset_mock()

        adapter = MockMCPAdapter(host="test-host", port=9000)
        result = await adapter.connect()

        assert result is True
        mock_logger.info.assert_called_with("Connecting to mock MCP server at test-host:9000")

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test that send_message returns the expected mock response."""
        mock_logger.reset_mock()

        adapter = MockMCPAdapter()
        message = "Hello, world! This is a test message."
        response = await adapter.send_message(message)

        assert response["status"] == "success"
        assert "Mock MCP response for: Hello, world! This" in response["response"]
        # Use assert_called_with with a partial match to avoid exact string matching issues
        assert mock_logger.info.call_args is not None
        assert "Sending message to mock MCP server: Hello, world!" in mock_logger.info.call_args[0][0]


class TestMockAdapterFactory:
    """Tests for the MockAdapterFactory class."""

    def setup_method(self):
        """Reset the mock logger before each test."""
        mock_logger.reset_mock()

    def test_register_adapter(self):
        """Test that register_adapter adds the adapter to the registry."""
        # Create a mock adapter class
        mock_adapter_class = MagicMock()

        # Register the adapter
        MockAdapterFactory.register_adapter("test-adapter", mock_adapter_class)

        # Verify it was added to the registry
        assert MockAdapterFactory._adapter_registry["test-adapter"] == mock_adapter_class
        mock_logger.info.assert_any_call("Registered adapter type: test-adapter")

    def test_create_adapter_success(self):
        """Test that create_adapter returns an instance of the specified adapter type."""
        mock_logger.reset_mock()

        # Test creating Ollama adapter
        ollama_adapter = MockAdapterFactory.create_adapter("ollama", base_url="http://test-url:11434")
        assert isinstance(ollama_adapter, MockOllamaAdapter)
        assert ollama_adapter.base_url == "http://test-url:11434"
        mock_logger.info.assert_any_call("Created adapter of type: ollama")

        # Test creating LMStudio adapter
        mock_logger.reset_mock()
        lmstudio_adapter = MockAdapterFactory.create_adapter("lmstudio", base_url="http://test-url:1234/v1")
        assert isinstance(lmstudio_adapter, MockLMStudioAdapter)
        assert lmstudio_adapter.base_url == "http://test-url:1234/v1"
        mock_logger.info.assert_any_call("Created adapter of type: lmstudio")

        # Test creating OpenAI compatible adapter
        mock_logger.reset_mock()
        openai_adapter = MockAdapterFactory.create_adapter("openai", base_url="http://test-url/v1", api_key="test-key")
        assert isinstance(openai_adapter, MockOpenAICompatibleAdapter)
        assert openai_adapter.base_url == "http://test-url/v1"
        assert openai_adapter.api_key == "test-key"
        mock_logger.info.assert_any_call("Created adapter of type: openai")

        # Test creating TensorRT adapter
        mock_logger.reset_mock()
        tensorrt_adapter = MockAdapterFactory.create_adapter("tensorrt", base_url="http://test-url:8000")
        assert isinstance(tensorrt_adapter, MockTensorRTAdapter)
        assert tensorrt_adapter.base_url == "http://test-url:8000"
        mock_logger.info.assert_any_call("Created adapter of type: tensorrt")

        # Test creating MCP adapter
        mock_logger.reset_mock()
        mcp_adapter = MockAdapterFactory.create_adapter("mcp", host="test-host", port=9000)
        assert isinstance(mcp_adapter, MockMCPAdapter)
        assert mcp_adapter.host == "test-host"
        assert mcp_adapter.port == 9000
        mock_logger.info.assert_any_call("Created adapter of type: mcp")

    def test_create_adapter_unknown_type(self):
        """Test that create_adapter returns None for unknown adapter types."""
        mock_logger.reset_mock()

        # Try to create an adapter with an unknown type
        adapter = MockAdapterFactory.create_adapter("unknown-type")

        # Verify that None was returned
        assert adapter is None
        mock_logger.error.assert_called_with("Unknown adapter type: unknown-type")

    def test_create_adapter_error(self):
        """Test that create_adapter returns None when an error occurs."""
        mock_logger.reset_mock()

        # Create a mock adapter class that raises an exception
        mock_adapter_class = MagicMock(side_effect=Exception("Test error"))
        MockAdapterFactory._adapter_registry["error-adapter"] = mock_adapter_class

        # Try to create an adapter that will raise an exception
        adapter = MockAdapterFactory.create_adapter("error-adapter")

        # Verify that None was returned
        assert adapter is None
        mock_logger.exception.assert_called_with("Error creating adapter of type error-adapter")

    def test_get_available_adapter_types(self):
        """Test that get_available_adapter_types returns the expected adapter types."""
        mock_logger.reset_mock()

        # Get the available adapter types
        adapter_types = MockAdapterFactory.get_available_adapter_types()

        # Verify that the expected adapter types are returned
        assert "ollama" in adapter_types
        assert "lmstudio" in adapter_types
        assert "openai" in adapter_types
        assert "tensorrt" in adapter_types
        assert "mcp" in adapter_types

        # Verify that the logger was called with the expected messages
        mock_logger.info.assert_any_call("Getting available adapter types")
        mock_logger.info.assert_any_call(f"Found {len(adapter_types)} available adapter types")
