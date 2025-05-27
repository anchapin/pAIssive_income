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
        """Test _ensure_session method."""
        # Create a new adapter
        adapter = OpenAICompatibleAdapter()
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
        adapter = OpenAICompatibleAdapter()
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
            "data": [
                {"id": "gpt-4", "object": "model"},
                {"id": "gpt-3.5-turbo", "object": "model"}
            ]
        })

        # Call list_models
        models = await self.adapter.list_models()

        # Verify the request
        self.mock_session.get.assert_called_once_with(
            "https://api.example.com/v1/models",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-key"
            }
        )

        # Verify the response
        assert len(models) == 2
        assert models[0]["id"] == "gpt-4"
        assert models[1]["id"] == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        """Test list_models method with an error response."""
        # Setup mock response
        self.mock_response.status = 401
        self.mock_response.text = AsyncMock(return_value="Unauthorized")

        # Call list_models and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.list_models()

        assert "Failed to list models" in str(excinfo.value)
        assert "401" in str(excinfo.value)
        assert "Unauthorized" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test generate_text method."""
        # Setup mock response
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

        # Call generate_text
        response = await self.adapter.generate_text(
            "text-davinci-003",
            "Test prompt",
            temperature=0.7,
            max_tokens=100
        )

        # Verify the request
        self.mock_session.post.assert_called_once()
        call_args = self.mock_session.post.call_args
        assert call_args[0][0] == "https://api.example.com/v1/completions"
        assert call_args[1]["headers"] == {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-key"
        }

        # Verify the request body
        request_body = json.loads(call_args[1]["data"])
        assert request_body["model"] == "text-davinci-003"
        assert request_body["prompt"] == "Test prompt"
        assert request_body["temperature"] == 0.7
        assert request_body["max_tokens"] == 100

        # Verify the response
        assert response["id"] == "cmpl-123"
        assert response["choices"][0]["text"] == "Generated text"

    @pytest.mark.asyncio
    async def test_generate_text_error(self):
        """Test generate_text method with an error response."""
        # Setup mock response
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")

        # Call generate_text and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_text("text-davinci-003", "Test prompt")

        assert "Failed to generate text" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_chat_completions(self):
        """Test generate_chat_completions method."""
        # Setup mock response
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

        # Call generate_chat_completions
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        response = await self.adapter.generate_chat_completions(
            "gpt-3.5-turbo",
            messages,
            temperature=0.8
        )

        # Verify the request
        self.mock_session.post.assert_called_once()
        call_args = self.mock_session.post.call_args
        assert call_args[0][0] == "https://api.example.com/v1/chat/completions"
        assert call_args[1]["headers"] == {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-key"
        }

        # Verify the request body
        request_body = json.loads(call_args[1]["data"])
        assert request_body["model"] == "gpt-3.5-turbo"
        assert request_body["messages"] == messages
        assert request_body["temperature"] == 0.8

        # Verify the response
        assert response["id"] == "chatcmpl-123"
        assert response["choices"][0]["message"]["role"] == "assistant"
        assert response["choices"][0]["message"]["content"] == "Chat response"

    @pytest.mark.asyncio
    async def test_generate_chat_completions_error(self):
        """Test generate_chat_completions method with an error response."""
        # Setup mock response
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")

        # Call generate_chat_completions and verify it raises an exception
        messages = [{"role": "user", "content": "Hello!"}]
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_chat_completions("gpt-3.5-turbo", messages)

        assert "Failed to generate chat completion" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        # Setup mock session to raise a connection error
        self.mock_session.get.side_effect = aiohttp.ClientConnectionError("Connection refused")

        # Call list_models and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.list_models()

        assert "Failed to connect to OpenAI API" in str(excinfo.value)
        assert "Connection refused" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        # Setup mock session to raise a timeout error
        self.mock_session.post.side_effect = aiohttp.ClientTimeout("Timeout")

        # Call generate_text and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_text("text-davinci-003", "Test prompt")

        assert "Request to OpenAI API timed out" in str(excinfo.value)
