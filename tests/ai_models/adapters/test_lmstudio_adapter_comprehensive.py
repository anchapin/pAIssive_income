"""Comprehensive tests for the ai_models.adapters.lmstudio_adapter module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import asyncio

from ai_models.adapters.lmstudio_adapter import LMStudioAdapter


class TestLMStudioAdapterComprehensive:
    """Comprehensive test suite for the LMStudioAdapter class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a mock response for testing
        self.mock_response = MagicMock()
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock()
        self.mock_response.text = AsyncMock()

        # Helper to create an async context manager mock
        def make_ctx_mgr():
            ctx_mgr = AsyncMock()
            ctx_mgr.__aenter__.return_value = self.mock_response
            ctx_mgr.__aexit__.return_value = None
            return ctx_mgr

        self.make_ctx_mgr = make_ctx_mgr
        self.adapter = LMStudioAdapter("localhost", 8000)
        # Do NOT set self.adapter._session here; let tests patch and create as needed

    @pytest.mark.asyncio
    async def test_init(self):
        """Test initialization of LMStudioAdapter."""
        # Create a new adapter
        adapter = LMStudioAdapter("test-host", 1234, timeout=30)

        # Verify the adapter properties
        assert adapter.host == "test-host"
        assert adapter.port == 1234
        assert adapter.timeout == 30
        assert adapter.base_url == "http://test-host:1234/v1"
        assert adapter._session is None

    @pytest.mark.asyncio
    async def test_ensure_session(self):
        """Test _ensure_session method."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False
            mock_session_class.return_value = mock_session
            adapter = LMStudioAdapter("localhost", 8000)
            adapter._session = None
            await adapter._ensure_session()
            assert adapter._session is mock_session
            mock_session_class.assert_called_once()
            # Call _ensure_session again
            await adapter._ensure_session()
            mock_session_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        mock_session = MagicMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        adapter = LMStudioAdapter("localhost", 8000)
        adapter._session = mock_session
        await adapter.close()
        mock_session.close.assert_awaited_once()
        assert adapter._session is None
        # Call close again (should not raise an error)
        await adapter.close()

    @pytest.mark.asyncio
    async def test_list_models(self):
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "data": [
                {"id": "model1", "object": "model"},
                {"id": "model2", "object": "model"}
            ]
        })
        mock_session = MagicMock()
        mock_session.get.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            models = await adapter.list_models()
            mock_session.get.assert_called_once_with(
                "http://localhost:8000/v1/models",
                headers={"Content-Type": "application/json"}
            )
            assert len(models) == 2
            assert models[0]["id"] == "model1"
            assert models[1]["id"] == "model2"

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        self.mock_response.status = 500
        self.mock_response.text = AsyncMock(return_value="Internal Server Error")
        mock_session = MagicMock()
        mock_session.get.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            with pytest.raises(Exception) as excinfo:
                await adapter.list_models()
            assert "Failed to list models" in str(excinfo.value)
            assert "500" in str(excinfo.value)
            assert "Internal Server Error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text(self):
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1677858242,
            "model": "test-model",
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
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            response = await adapter.generate_text("test-model", "Test prompt", temperature=0.7, max_tokens=100)
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "http://localhost:8000/v1/completions"
            assert call_args[1]["headers"] == {"Content-Type": "application/json"}
            request_body = json.loads(call_args[1]["data"])
            assert request_body["model"] == "test-model"
            assert request_body["prompt"] == "Test prompt"
            assert request_body["temperature"] == 0.7
            assert request_body["max_tokens"] == 100
            assert response["id"] == "cmpl-123"
            assert response["choices"][0]["text"] == "Generated text"

    @pytest.mark.asyncio
    async def test_generate_text_error(self):
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            with pytest.raises(Exception) as excinfo:
                await adapter.generate_text("test-model", "Test prompt")
            assert "Failed to generate text" in str(excinfo.value)
            assert "400" in str(excinfo.value)
            assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_chat_completions(self):
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "test-model",
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
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
            response = await adapter.generate_chat_completions("test-model", messages, temperature=0.8)
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "http://localhost:8000/v1/chat/completions"
            assert call_args[1]["headers"] == {"Content-Type": "application/json"}
            request_body = json.loads(call_args[1]["data"])
            assert request_body["model"] == "test-model"
            assert request_body["messages"] == messages
            assert request_body["temperature"] == 0.8
            assert response["id"] == "chatcmpl-123"
            assert response["choices"][0]["message"]["role"] == "assistant"
            assert response["choices"][0]["message"]["content"] == "Chat response"

    @pytest.mark.asyncio
    async def test_generate_chat_completions_error(self):
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            messages = [{"role": "user", "content": "Hello!"}]
            with pytest.raises(Exception) as excinfo:
                await adapter.generate_chat_completions("test-model", messages)
            assert "Failed to generate chat completion" in str(excinfo.value)
            assert "400" in str(excinfo.value)
            assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_connection_error(self):
        # For connection errors, the context manager itself should raise
        mock_session = MagicMock()
        ctx_mgr = self.make_ctx_mgr()
        ctx_mgr.__aenter__.side_effect = aiohttp.ClientConnectionError("Connection refused")
        mock_session.get.return_value = ctx_mgr
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            with pytest.raises(Exception) as excinfo:
                await adapter.list_models()
            assert "Failed to connect to LMStudio server" in str(excinfo.value)
            assert "Connection refused" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        import asyncio
        mock_session = MagicMock()
        ctx_mgr = self.make_ctx_mgr()
        ctx_mgr.__aenter__.side_effect = asyncio.TimeoutError()
        mock_session.post.return_value = ctx_mgr
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            with pytest.raises(Exception) as excinfo:
                await adapter.generate_text("test-model", "Test prompt")
            assert "Request to LMStudio server timed out" in str(excinfo.value)

    @pytest.mark.asyncio
    def test_generate_text_with_params(self):
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "id": "cmpl-123",
            "object": "text_completion",
            "created": 1677858242,
            "model": "model1",
            "choices": [
                {
                    "text": "This is a test response",
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ]
        })
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            result = asyncio.run(adapter.generate_text(
                "model1",
                "This is a test",
                max_tokens=100,
                temperature=0.5,
                top_p=0.9,
                n=2,
                stream=True,
                stop=["END"],
                presence_penalty=0.1,
                frequency_penalty=0.2
            ))
            mock_session.post.assert_called_once()
            args, kwargs = mock_session.post.call_args
            assert args[0] == "http://localhost:8000/v1/completions"
            assert kwargs["headers"] == {"Content-Type": "application/json"}
            import json as _json
            payload = _json.loads(kwargs["data"])
            assert payload["model"] == "model1"
            assert payload["prompt"] == "This is a test"
            assert payload["max_tokens"] == 100
            assert payload["temperature"] == 0.5
            assert payload["top_p"] == 0.9
            assert payload["n"] == 2
            assert payload["stream"] is True
            assert payload["stop"] == ["END"]
            assert payload["presence_penalty"] == 0.1
            assert payload["frequency_penalty"] == 0.2
            assert result["id"] == "cmpl-123"
            assert result["choices"][0]["text"] == "This is a test response"

    @pytest.mark.asyncio
    def test_generate_chat_completions_with_params(self):
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "model1",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'm an AI assistant. How can I help you today?"
                    },
                    "index": 0,
                    "finish_reason": "stop"
                }
            ]
        })
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who are you?"}
        ]
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = LMStudioAdapter("localhost", 8000)
            result = asyncio.run(adapter.generate_chat_completions(
                "model1",
                messages,
                max_tokens=100,
                temperature=0.5,
                top_p=0.9,
                n=2,
                stream=True,
                stop=["END"],
                presence_penalty=0.1,
                frequency_penalty=0.2
            ))
            mock_session.post.assert_called_once()
            args, kwargs = mock_session.post.call_args
            assert args[0] == "http://localhost:8000/v1/chat/completions"
            assert kwargs["headers"] == {"Content-Type": "application/json"}
            import json as _json
            payload = _json.loads(kwargs["data"])
            assert payload["model"] == "model1"
            assert payload["messages"] == messages
            assert payload["max_tokens"] == 100
            assert payload["temperature"] == 0.5
            assert payload["top_p"] == 0.9
            assert payload["n"] == 2
            assert payload["stream"] is True
            assert payload["stop"] == ["END"]
            assert payload["presence_penalty"] == 0.1
            assert payload["frequency_penalty"] == 0.2
            assert result["id"] == "chatcmpl-123"
            assert result["choices"][0]["message"]["role"] == "assistant"
            assert "I'm an AI assistant" in result["choices"][0]["message"]["content"]
