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
        self.mock_response = MagicMock()
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock()
        self.mock_response.text = AsyncMock()
        def make_ctx_mgr():
            ctx_mgr = AsyncMock()
            ctx_mgr.__aenter__.return_value = self.mock_response
            ctx_mgr.__aexit__.return_value = None
            return ctx_mgr
        self.make_ctx_mgr = make_ctx_mgr
        self.adapter = OllamaAdapter(base_url="http://localhost:11434", timeout=60)
        # Do NOT set self.adapter._session here; let tests patch and create as needed

    @pytest.mark.asyncio
    async def test_init(self):
        """Test initialization of OllamaAdapter."""
        adapter = OllamaAdapter(base_url="http://test-host:1234", timeout=30)
        assert adapter.base_url == "http://test-host:1234"
        assert adapter.timeout == 30
        assert adapter._session is None

    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test _get_session method."""
        adapter = OllamaAdapter(base_url="http://localhost:11434")
        assert adapter._session is None
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.closed = False  # Ensure session is not considered closed
            mock_session_class.return_value = mock_session
            # First call should create the session
            await adapter._get_session()
            assert adapter._session is mock_session
            assert mock_session_class.call_count == 1
            # Second call should reuse the session, not create a new one
            mock_session.closed = False  # Still not closed
            await adapter._get_session()
            assert mock_session_class.call_count == 1

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        adapter = OllamaAdapter(base_url="http://localhost:11434")
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
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "models": [
                {"name": "llama2", "modified_at": "2023-01-01T00:00:00Z"},
                {"name": "mistral", "modified_at": "2023-01-02T00:00:00Z"}
            ]
        })
        mock_session = MagicMock()
        mock_session.get.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            models = await adapter.list_models()
            mock_session.get.assert_called_once_with(
                "http://localhost:11434/api/tags"
            )
            assert len(models) == 2
            assert models[0]["name"] == "llama2"
            assert models[1]["name"] == "mistral"

    @pytest.mark.asyncio
    async def test_list_models_error(self):
        """Test list_models method with an error response."""
        self.mock_response.status = 500
        self.mock_response.text = AsyncMock(return_value="Internal Server Error")
        mock_session = MagicMock()
        mock_session.get.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            with pytest.raises(Exception) as excinfo:
                await adapter.list_models()
            assert "Failed to list models" in str(excinfo.value)
            assert "500" in str(excinfo.value)
            assert "Internal Server Error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test generate_text method."""
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "model": "llama2",
            "created_at": "2023-01-01T00:00:00Z",
            "response": "Generated text",
            "done": True
        })
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            response = await adapter.generate_text("llama2", "Test prompt", temperature=0.7, max_tokens=100)
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "http://localhost:11434/api/generate"
            request_body = call_args[1]["json"]
            assert request_body["model"] == "llama2"
            assert request_body["prompt"] == "Test prompt"
            assert request_body["temperature"] == 0.7
            assert request_body["max_tokens"] == 100
            assert response["model"] == "llama2"
            assert response["response"] == "Generated text"
            assert response["done"] is True

    @pytest.mark.asyncio
    async def test_generate_text_error(self):
        """Test generate_text method with an error response."""
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            with pytest.raises(Exception) as excinfo:
                await adapter.generate_text("llama2", "Test prompt")
            assert "Failed to generate text" in str(excinfo.value)
            assert "400" in str(excinfo.value)
            assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_chat_completions(self):
        """Test generate_chat_completions method."""
        self.mock_response.status = 200
        self.mock_response.json = AsyncMock(return_value={
            "model": "llama2",
            "created_at": "2023-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "Chat response"},
            "done": True
        })
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
            response = await adapter.generate_chat_completions("llama2", messages, temperature=0.8)
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            assert call_args[0][0] == "http://localhost:11434/api/chat"
            request_body = call_args[1]["json"]
            assert request_body["model"] == "llama2"
            assert request_body["messages"] == messages
            assert request_body["temperature"] == 0.8
            assert response["model"] == "llama2"
            assert response["message"]["role"] == "assistant"
            assert response["message"]["content"] == "Chat response"
            assert response["done"] is True

    @pytest.mark.asyncio
    async def test_generate_chat_completions_error(self):
        """Test generate_chat_completions method with an error response."""
        self.mock_response.status = 400
        self.mock_response.text = AsyncMock(return_value="Bad Request")
        mock_session = MagicMock()
        mock_session.post.return_value = self.make_ctx_mgr()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            messages = [{"role": "user", "content": "Hello!"}]
            with pytest.raises(Exception) as excinfo:
                await adapter.generate_chat_completions("llama2", messages)
            assert "Failed to generate chat completion" in str(excinfo.value)
            assert "400" in str(excinfo.value)
            assert "Bad Request" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        mock_session = MagicMock()
        ctx_mgr = self.make_ctx_mgr()
        ctx_mgr.__aenter__.side_effect = aiohttp.ClientConnectionError("Connection refused")
        mock_session.get.return_value = ctx_mgr
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            with pytest.raises(Exception) as excinfo:
                await adapter.list_models()
            assert "Failed to connect to Ollama server" in str(excinfo.value)
            assert "Connection refused" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        import asyncio
        mock_session = MagicMock()
        ctx_mgr = self.make_ctx_mgr()
        ctx_mgr.__aenter__.side_effect = asyncio.TimeoutError()
        mock_session.post.return_value = ctx_mgr
        with patch("aiohttp.ClientSession", return_value=mock_session):
            adapter = OllamaAdapter(base_url="http://localhost:11434")
            with pytest.raises(Exception) as excinfo:
                await adapter.generate_text("llama2", "Test prompt")
            assert "Request to Ollama server timed out" in str(excinfo.value)
