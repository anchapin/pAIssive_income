"""test_lmstudio_adapter - Module for tests/ai_models/adapters.test_lmstudio_adapter."""

# Standard library imports
import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest

# Local imports
from ai_models.adapters import LMStudioAdapter


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
def test_list_models(mock_aiohttp_session):
    """Test listing models from LM Studio."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "data": [
            {"id": "model1", "object": "model", "name": "Model 1"},
            {"id": "model2", "object": "model", "name": "Model 2"}
        ]
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        models = asyncio.run(adapter.list_models())

        # Verify the request was made correctly
        mock_session.get.assert_called_once_with(
            "http://test-lmstudio:1234/v1/models",
            headers={"Content-Type": "application/json"}
        )
        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[1]["name"] == "Model 2"


@pytest.mark.asyncio
def test_list_models_error(mock_aiohttp_session):
    """Test error handling when listing models from LM Studio."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 500
    mock_response.text.return_value = "Internal server error"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.list_models())
        assert "Failed to list models" in str(excinfo.value)
        assert "500" in str(excinfo.value)
        assert "Internal server error" in str(excinfo.value)


@pytest.mark.asyncio
def test_list_models_exception(mock_aiohttp_session):
    """Test exception handling when listing models from LM Studio."""
    mock_session, _ = mock_aiohttp_session
    mock_session.get.side_effect = Exception("Connection refused")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.list_models())
        assert "Connection refused" in str(excinfo.value)


@pytest.mark.asyncio
def test_generate_text(mock_aiohttp_session):
    """Test generating text with LM Studio."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
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
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 7,
            "total_tokens": 12
        }
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        result = asyncio.run(adapter.generate_text("model1", "This is a test"))
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-lmstudio:1234/v1/completions"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        payload = json.loads(kwargs["data"])
        assert payload["model"] == "model1"
        assert payload["prompt"] == "This is a test"
        assert result["model"] == "model1"
        assert result["choices"][0]["text"] == "This is a test response"


@pytest.mark.asyncio
def test_generate_text_error(mock_aiohttp_session):
    """Test error handling in generate_text."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.generate_text("model1", "This is a test"))
        assert "Failed to generate text" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad request" in str(excinfo.value)


@pytest.mark.asyncio
def test_generate_chat_completions(mock_aiohttp_session):
    """Test generating chat completions with LM Studio."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
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
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 12,
            "total_tokens": 22
        }
    }
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"}
    ]
    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        result = asyncio.run(adapter.generate_chat_completions("model1", messages))
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-lmstudio:1234/v1/chat/completions"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        payload = json.loads(kwargs["data"])
        assert payload["model"] == "model1"
        assert payload["messages"] == messages
        assert result["model"] == "model1"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert "I'm an AI assistant" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
def test_generate_chat_completions_error(mock_aiohttp_session):
    """Test error handling in generate_chat_completions."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"
    messages = [{"role": "user", "content": "Hello"}]
    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.generate_chat_completions("model1", messages))
        assert "Failed to generate chat completion" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad request" in str(excinfo.value)


@pytest.mark.asyncio
def test_generate_text_with_params(mock_aiohttp_session):
    """Test generating text with additional parameters."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
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
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
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
        assert args[0] == "http://test-lmstudio:1234/v1/completions"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        payload = json.loads(kwargs["data"])
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
        assert result["model"] == "model1"
        assert result["choices"][0]["text"] == "This is a test response"


@pytest.mark.asyncio
def test_generate_chat_completions_with_params(mock_aiohttp_session):
    """Test generating chat completions with additional parameters."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
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
    }
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who are you?"}
    ]
    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
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
        assert args[0] == "http://test-lmstudio:1234/v1/chat/completions"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        payload = json.loads(kwargs["data"])
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
        assert result["model"] == "model1"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert "I'm an AI assistant" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
def test_error_handling(mock_aiohttp_session):
    """Test error handling in the LM Studio adapter."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.generate_text("model1", "This is a test"))
        assert "Failed to generate text" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad request" in str(excinfo.value)


@pytest.mark.asyncio
def test_exception_handling(mock_aiohttp_session):
    """Test exception handling in the LM Studio adapter."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection refused")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.generate_text("model1", "This is a test"))
        assert "Connection refused" in str(excinfo.value)


@pytest.mark.asyncio
def test_chat_completions_error_handling(mock_aiohttp_session):
    """Test error handling in chat completions."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"

    messages = [
        {"role": "user", "content": "Hello"}
    ]

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.generate_chat_completions("model1", messages))
        assert "Failed to generate chat completion" in str(excinfo.value)
        assert "400" in str(excinfo.value)
        assert "Bad request" in str(excinfo.value)


@pytest.mark.asyncio
def test_chat_completions_exception_handling(mock_aiohttp_session):
    """Test exception handling in chat completions."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection refused")

    messages = [
        {"role": "user", "content": "Hello"}
    ]

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        with pytest.raises(Exception) as excinfo:
            asyncio.run(adapter.generate_chat_completions("model1", messages))
        assert "Connection refused" in str(excinfo.value)


@pytest.mark.asyncio
async def test_close_session(mock_aiohttp_session):
    """Test closing the session."""
    mock_session, _ = mock_aiohttp_session

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")

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
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1")
        adapter._session = mock_session

        # Close the session
        await adapter.close()

        # Verify session close was not called
        mock_session.close.assert_not_called()

        # Verify session is set to None
        assert adapter._session is None


@pytest.mark.asyncio
async def test_get_session_with_api_key():
    """Test getting a session with an API key."""
    mock_session = MagicMock()

    with patch("aiohttp.ClientSession", return_value=mock_session) as mock_client_session:
        adapter = LMStudioAdapter(host_or_base_url="http://test-lmstudio:1234/v1", api_key="test-key", timeout=30)

        # Get session
        session = await adapter._get_session()

        # Verify session was created with correct parameters
        mock_client_session.assert_called_once()
        _, kwargs = mock_client_session.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["timeout"].total == 30
