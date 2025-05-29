"""test_ollama_adapter - Module for tests/ai_models/adapters.test_ollama_adapter."""

# Standard library imports
import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest

# Local imports
from ai_models.adapters import OllamaAdapter


@pytest.fixture
def mock_aiohttp_session():
    """Create a mock aiohttp session for testing."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock()
    mock_response.text = AsyncMock(return_value="")

    # Context manager for session.get and session.post
    mock_cm = MagicMock()
    mock_cm.__aenter__.return_value = mock_response
    mock_session.get.return_value = mock_cm
    mock_session.post.return_value = mock_cm

    return mock_session, mock_response


@pytest.mark.asyncio
async def test_list_models(mock_aiohttp_session):
    """Test listing models from Ollama."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {"models": [{"name": "llama2"}, {"name": "mistral"}]}

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")
        models = await adapter.list_models()

        # Verify the request was made correctly
        mock_session.get.assert_called_once_with("http://test-ollama:11434/api/tags")

        # Verify the response was processed correctly
        assert len(models) == 2
        assert models[0]["name"] == "llama2"
        assert models[1]["name"] == "mistral"


@pytest.mark.asyncio
async def test_generate_text(mock_aiohttp_session):
    """Test generating text with Ollama."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "model": "llama2",
        "created_at": "2023-11-15T12:34:56Z",
        "response": "Hello, world!",
        "done": True
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")
        result = await adapter.generate_text("llama2", "Say hello")

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-ollama:11434/api/generate"
        assert kwargs["json"]["model"] == "llama2"
        assert kwargs["json"]["prompt"] == "Say hello"

        # Verify the response was processed correctly
        assert result["model"] == "llama2"
        assert result["response"] == "Hello, world!"
        assert result["done"] is True


@pytest.mark.asyncio
async def test_generate_chat_completions(mock_aiohttp_session):
    """Test generating chat completions with Ollama."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "model": "llama2",
        "created_at": "2023-11-15T12:34:56Z",
        "message": {"role": "assistant", "content": "I'm doing well, thank you!"},
        "done": True
    }

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How are you?"}
    ]

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")
        result = await adapter.generate_chat_completions("llama2", messages)

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-ollama:11434/api/chat"
        assert kwargs["json"]["model"] == "llama2"
        assert kwargs["json"]["messages"] == messages

        # Verify the response was processed correctly
        assert result["model"] == "llama2"
        assert result["message"]["role"] == "assistant"
        assert result["message"]["content"] == "I'm doing well, thank you!"
        assert result["done"] is True


@pytest.mark.asyncio
async def test_error_handling(mock_aiohttp_session):
    """Test error handling in the Ollama adapter."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 500
    mock_response.text.return_value = "Internal server error"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")
        with pytest.raises(Exception) as excinfo:
            await adapter.generate_text("llama2", "Say hello")
        assert "Failed to generate text" in str(excinfo.value)
        assert "500" in str(excinfo.value)
        assert "Internal server error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_exception_handling(mock_aiohttp_session):
    """Test exception handling in the Ollama adapter."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection error")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")
        with pytest.raises(Exception) as excinfo:
            await adapter.generate_text("llama2", "Say hello")
        assert "Error generating text" in str(excinfo.value)
        assert "Connection error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_close_session(mock_aiohttp_session):
    """Test closing the session."""
    mock_session, _ = mock_aiohttp_session

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")

        # Get session to initialize it
        session = await adapter._get_session()
        assert session == mock_session

        # Close the session
        await adapter.close()

        # Verify session is set to None
        assert adapter._session is None


@pytest.mark.asyncio
async def test_close_session_when_already_closed(mock_aiohttp_session):
    """Test closing the session when it's already closed."""
    mock_session, _ = mock_aiohttp_session
    mock_session.closed = True

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OllamaAdapter(base_url="http://test-ollama:11434")
        adapter._session = mock_session

        # Close the session
        await adapter.close()

        # Verify session close was not called
        mock_session.close.assert_not_called()

        # Verify session is set to None
        assert adapter._session is None
