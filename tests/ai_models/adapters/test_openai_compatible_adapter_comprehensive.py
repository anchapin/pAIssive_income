"""Comprehensive tests for the ai_models.adapters.openai_compatible_adapter module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from ai_models.adapters.openai_compatible_adapter import OpenAICompatibleAdapter


class TestOpenAICompatibleAdapterComprehensive:
    """Comprehensive test suite for the OpenAICompatibleAdapter class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a mock session for testing
        self.mock_session = MagicMock()
        self.mock_response = MagicMock()
        self.mock_session.post = AsyncMock(return_value=self.mock_response)
        self.mock_session.get = AsyncMock(return_value=self.mock_response)

        # Create an adapter instance with the mock session
        self.adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
        self.adapter._session = self.mock_session

    @pytest.mark.asyncio
    async def test_init(self):
        """Test initialization of OpenAICompatibleAdapter."""
        # Create a new adapter
        adapter = OpenAICompatibleAdapter(
            base_url="https://custom-api.example.com/v1",
            api_key="custom-key",
            timeout=60
        )

        # Verify the adapter properties
        assert adapter.base_url == "https://custom-api.example.com/v1"
        assert adapter.api_key == "custom-key"
        assert adapter.timeout == 60
        assert adapter._session is None

    @pytest.mark.asyncio
    async def test_init_default_values(self):
        """Test initialization of OpenAICompatibleAdapter with default values."""
        # Create a new adapter with default values
        adapter = OpenAICompatibleAdapter()

        # Verify the adapter properties
        assert adapter.base_url == "https://api.openai.com/v1"
        assert adapter.api_key == "sk-"
        assert adapter.timeout == 60
        assert adapter._session is None

    @pytest.mark.asyncio
    async def test_ensure_session(self):
        """Test _get_session method."""
        adapter = OpenAICompatibleAdapter()
        assert adapter._session is None
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session_class.return_value = mock_session
            await adapter._get_session()
            assert adapter._session is mock_session
            mock_session_class.assert_called_once()
            await adapter._get_session()
            mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        adapter = OpenAICompatibleAdapter()
        mock_session = MagicMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        adapter._session = mock_session
        await adapter.close()
        mock_session.close.assert_awaited_once()
        assert adapter._session is None
        await adapter.close()

    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test list_models method."""
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = self.mock_response
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "data": [
                {"id": "gpt-4", "object": "model"},
                {"id": "gpt-3.5-turbo", "object": "model"}
            ]
        })
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session.get.return_value = mock_cm
            mock_session_class.return_value = mock_session
            adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
            models = await adapter.list_models()
            mock_session.get.assert_called_once_with("https://api.example.com/v1/models")
            assert len(models) == 2
            assert models[0]["id"] == "gpt-4"
            assert models[1]["id"] == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        """Test list_models method with an error response."""
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = self.mock_response
        self.mock_response.status = 401
        self.mock_response.text = AsyncMock(return_value="Unauthorized")
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session.get.return_value = mock_cm
            mock_session_class.return_value = mock_session
            adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
            result = await adapter.list_models()
            assert result == []

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test generate_text method."""
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = self.mock_response
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1677858242,
            "model": "text-davinci-003",
            "choices": [
                {
                    "text": "Generated text",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 7,
                "total_tokens": 12
            }
        })
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session.post.return_value = mock_cm
            mock_session_class.return_value = mock_session
            adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
            response = await adapter.generate_text(
                "text-davinci-003",
                "Test prompt",
                temperature=0.7,
                max_tokens=100
            )
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "https://api.example.com/v1/completions"
            assert call_args[1]["json"]["model"] == "text-davinci-003"
            assert call_args[1]["json"]["prompt"] == "Test prompt"
            assert call_args[1]["json"]["temperature"] == 0.7
            assert call_args[1]["json"]["max_tokens"] == 100
            assert response["id"] == "cmpl-123"
            assert response["choices"][0]["text"] == "Generated text"

    @pytest.mark.asyncio
    async def test_generate_text_error(self):
        """Test generate_text method with an error response."""
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = self.mock_response
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session.post.return_value = mock_cm
            mock_session_class.return_value = mock_session
            adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
            result = await adapter.generate_text("text-davinci-003", "Test prompt")
            assert "error" in result
            assert result["error"] == "Bad Request"

    @pytest.mark.asyncio
    async def test_generate_chat_completions(self):
        """Test generate_chat_completions method."""
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = self.mock_response
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Chat response"
                    },
                    "index": 0,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 15,
                "total_tokens": 25
            }
        })
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session.post.return_value = mock_cm
            mock_session_class.return_value = mock_session
            adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
            response = await adapter.generate_chat_completions(
                "gpt-3.5-turbo", messages, temperature=0.8
            )
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "https://api.example.com/v1/chat/completions"
            assert call_args[1]["json"]["model"] == "gpt-3.5-turbo"
            assert call_args[1]["json"]["messages"] == messages
            assert call_args[1]["json"]["temperature"] == 0.8
            assert response["id"] == "chatcmpl-123"
            assert response["choices"][0]["message"]["role"] == "assistant"
            assert response["choices"][0]["message"]["content"] == "Chat response"

    @pytest.mark.asyncio
    async def test_generate_chat_completions_error(self):
        """Test generate_chat_completions method with an error response."""
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = self.mock_response
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session.post.return_value = mock_cm
            mock_session_class.return_value = mock_session
            adapter = OpenAICompatibleAdapter(base_url="https://api.example.com/v1", api_key="test-key")
            messages = [{"role": "user", "content": "Hello!"}]
            result = await adapter.generate_chat_completions("gpt-3.5-turbo", messages)
            assert "error" in result
            assert result["error"] == "Bad Request"

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        self.mock_session.get.side_effect = aiohttp.ClientConnectionError("Connection refused")
        self.adapter._session = self.mock_session
        result = await self.adapter.list_models()
        assert "error" in result or result == []

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        import asyncio
        self.mock_session.post.side_effect = asyncio.TimeoutError()
        self.adapter._session = self.mock_session
        result = await self.adapter.generate_text("gpt-3.5-turbo", "Test prompt")
        assert "error" in result
