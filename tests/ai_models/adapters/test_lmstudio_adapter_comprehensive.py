"""Comprehensive tests for the ai_models.adapters.lmstudio_adapter module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
import json

from ai_models.adapters.lmstudio_adapter import LMStudioAdapter


class TestLMStudioAdapterComprehensive:
    """Comprehensive test suite for the LMStudioAdapter class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a mock session for testing
        self.mock_session = MagicMock()
        self.mock_response = MagicMock()
        self.mock_session.post = AsyncMock(return_value=self.mock_response)
        self.mock_session.get = AsyncMock(return_value=self.mock_response)
        
        # Create an adapter instance with the mock session
        self.adapter = LMStudioAdapter("localhost", 8000)
        self.adapter._session = self.mock_session

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
        # Create a new adapter
        adapter = LMStudioAdapter("localhost", 8000)
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
        adapter = LMStudioAdapter("localhost", 8000)
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
                {"id": "model1", "object": "model"},
                {"id": "model2", "object": "model"}
            ]
        })
        
        # Call list_models
        models = await self.adapter.list_models()
        
        # Verify the request
        self.mock_session.get.assert_called_once_with(
            "http://localhost:8000/v1/models",
            headers={"Content-Type": "application/json"}
        )
        
        # Verify the response
        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[1]["id"] == "model2"

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
        
        # Call generate_text
        response = await self.adapter.generate_text("test-model", "Test prompt", temperature=0.7, max_tokens=100)
        
        # Verify the request
        self.mock_session.post.assert_called_once()
        call_args = self.mock_session.post.call_args
        assert call_args[0][0] == "http://localhost:8000/v1/completions"
        assert call_args[1]["headers"] == {"Content-Type": "application/json"}
        
        # Verify the request body
        request_body = json.loads(call_args[1]["data"])
        assert request_body["model"] == "test-model"
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
            await self.adapter.generate_text("test-model", "Test prompt")
        
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
        
        # Call generate_chat_completions
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        response = await self.adapter.generate_chat_completions("test-model", messages, temperature=0.8)
        
        # Verify the request
        self.mock_session.post.assert_called_once()
        call_args = self.mock_session.post.call_args
        assert call_args[0][0] == "http://localhost:8000/v1/chat/completions"
        assert call_args[1]["headers"] == {"Content-Type": "application/json"}
        
        # Verify the request body
        request_body = json.loads(call_args[1]["data"])
        assert request_body["model"] == "test-model"
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
            await self.adapter.generate_chat_completions("test-model", messages)
        
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
        
        assert "Failed to connect to LMStudio server" in str(excinfo.value)
        assert "Connection refused" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        # Setup mock session to raise a timeout error
        self.mock_session.post.side_effect = aiohttp.ClientTimeout("Timeout")
        
        # Call generate_text and verify it raises an exception
        with pytest.raises(Exception) as excinfo:
            await self.adapter.generate_text("test-model", "Test prompt")
        
        assert "Request to LMStudio server timed out" in str(excinfo.value)
