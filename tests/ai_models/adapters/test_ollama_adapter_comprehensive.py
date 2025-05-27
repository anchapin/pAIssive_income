"""Comprehensive tests for the ai_models.adapters.ollama_adapter module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from ai_models.adapters.ollama_adapter import OllamaAdapter


class TestOllamaAdapterComprehensive:
    """Comprehensive test suite for the OllamaAdapter class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a mock session for testing
        self.mock_session = MagicMock()
        self.mock_response = MagicMock()
        self.mock_session.post = AsyncMock(return_value=self.mock_response)

        # Create an adapter instance with the mock session
        self.adapter = OllamaAdapter("localhost", 11434)
        self.adapter._session = self.mock_session

    @pytest.mark.asyncio
    async def test_init(self):
        """Test initialization of OllamaAdapter."""
        # Create a new adapter
        adapter = OllamaAdapter("test-host", 1234, timeout=30)

        # Verify the adapter properties
        assert adapter.host == "test-host"
        assert adapter.port == 1234
        assert adapter.timeout == 30
        assert adapter.base_url == "http://test-host:1234"
        assert adapter._session is None

    @pytest.mark.asyncio
    async def test_ensure_session(self):
        """Test _ensure_session method."""
        # Create a new adapter
        adapter = OllamaAdapter("localhost", 11434)
        assert adapter._session is None

        # Call _ensure_session
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session

            await adapter._ensure_session()

            # Verify that a session was created
            assert adapter._session is mock_session
            mock_session_class.assert_called_once()

            # Call _ensure_session again
            await adapter._ensure_session()

            # Verify that a new session was not created
            mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        # Create a new adapter with a mock session
        adapter = OllamaAdapter("localhost", 11434)
        mock_session = MagicMock()
        mock_session.close = AsyncMock()
        adapter._session = mock_session

        # Call close
        await adapter.close()

        # Verify that the session was closed
        mock_session.close.assert_called_once()
        assert adapter._session is None

        # Call close again (should not raise an error)
        await adapter.close()

    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test list_models method."""
        # Setup mock response
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "models": [
                {"name": "llama2", "modified_at": "2023-01-01T00:00:00Z"},
                {"name": "mistral", "modified_at": "2023-01-02T00:00:00Z"}
            ]
        })

        # Call list_models
        models = await self.adapter.list_models()

        # Verify the request
        self.mock_session.post.assert_called_once_with(
            "http://localhost:11434/api/tags",
            headers={"Content-Type": "application/json"},
            data="{}"
        )

        # Verify the response
        assert len(models) == 2
        assert models[0]["id"] == "llama2"
        assert models[1]["id"] == "mistral"

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        """Test list_models method with an error response."""
        # Setup mock response
        self.mock_response.status = 500
        self.mock_response.text = AsyncMock(return_value="Internal Server Error")

        # Call list_models and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.list_models()

        assert "Failed to list models" in str(excinfo.value)
        assert "500" in str(excinfo.value)
        assert "Internal Server Error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test generate_text method."""
        # Setup mock response
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "model": "llama2",
            "created_at": "2023-01-01T00:00:00Z",
            "response": "Generated text",
            "done": True
        })

        # Call generate_text
        response = await self.adapter.generate_text("llama2", "Test prompt", temperature=0.7, max_tokens=100)

        # Verify the request
        self.mock_session.post.assert_called_once()
        call_args = self.mock_session.post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"
        assert call_args[1]["headers"] == {"Content-Type": "application/json"}

        # Verify the request body
        request_body = json.loads(call_args[1]["data"])
        assert request_body["model"] == "llama2"
        assert request_body["prompt"] == "Test prompt"
        assert request_body["temperature"] == 0.7
        assert request_body["max_tokens"] == 100

        # Verify the response
        assert response["model"] == "llama2"
        assert response["response"] == "Generated text"
        assert response["done"] is True

    @pytest.mark.asyncio
    async def test_generate_text_error(self):
        """Test generate_text method with an error response."""
        # Setup mock response
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")

        # Call generate_text and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_text("llama2", "Test prompt")

        assert "Failed to generate text" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_chat_completions(self):
        """Test generate_chat_completions method."""
        # Setup mock response
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "model": "llama2",
            "created_at": "2023-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "Chat response"},
            "done": True
        })

        # Call generate_chat_completions
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        response = await self.adapter.generate_chat_completions("llama2", messages, temperature=0.8)

        # Verify the request
        self.mock_session.post.assert_called_once()
        call_args = self.mock_session.post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/chat"
        assert call_args[1]["headers"] == {"Content-Type": "application/json"}

        # Verify the request body
        request_body = json.loads(call_args[1]["data"])
        assert request_body["model"] == "llama2"
        assert request_body["messages"] == messages
        assert request_body["temperature"] == 0.8

        # Verify the response
        assert response["model"] == "llama2"
        assert response["message"]["role"] == "assistant"
        assert response["message"]["content"] == "Chat response"
        assert response["done"] is True

    @pytest.mark.asyncio
    async def test_generate_chat_completions_error(self):
        """Test generate_chat_completions method with an error response."""
        # Setup mock response
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")

        # Call generate_chat_completions and verify it raises an exception
        messages = [{"role": "user", "content": "Hello!"}]
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_chat_completions("llama2", messages)

        assert "Failed to generate chat completion" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        # Setup mock session to raise a connection error
        self.mock_session.post.side_effect = aiohttp.ClientConnectionError("Connection refused")

        # Call list_models and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.list_models()

        assert "Failed to connect to Ollama server" in str(excinfo.value)
        assert "Connection refused" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        # Setup mock session to raise a timeout error
        self.mock_session.post.side_effect = aiohttp.ClientTimeout("Timeout")

        # Call generate_text and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_text("llama2", "Test prompt")

        assert "Request to Ollama server timed out" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_format_chat_messages(self):
        """Test _format_chat_messages method."""
        # Define test messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        # Call _format_chat_messages
        formatted = self.adapter._format_chat_messages(messages)

        # Verify the formatted messages
        assert formatted == "You are a helpful assistant.\n\nUser: Hello!\n\nAssistant: Hi there!\n\nUser: How are you?"
