"""test_lmstudio_adapter - Module for tests/ai_models/adapters.test_lmstudio_adapter."""

# Standard library imports
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

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
async def test_list_models(mock_aiohttp_session):
    """Test listing models from LM Studio."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "data": [
            {"id": "model1", "object": "model", "name": "Model 1"},
            {"id": "model2", "object": "model", "name": "Model 2"}
        ]
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(base_url="http://test-lmstudio:1234/v1")
        models = await adapter.list_models()

        # Verify the request was made correctly
        mock_session.get.assert_called_once_with("http://test-lmstudio:1234/v1/models")

        # Verify the response was processed correctly
        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[1]["name"] == "Model 2"


@pytest.mark.asyncio
async def test_generate_text(mock_aiohttp_session):
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
        adapter = LMStudioAdapter(base_url="http://test-lmstudio:1234/v1")
        result = await adapter.generate_text("model1", "This is a test")

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-lmstudio:1234/v1/completions"
        assert kwargs["json"]["model"] == "model1"
        assert kwargs["json"]["prompt"] == "This is a test"

        # Verify the response was processed correctly
        assert result["model"] == "model1"
        assert result["choices"][0]["text"] == "This is a test response"


@pytest.mark.asyncio
async def test_generate_chat_completions(mock_aiohttp_session):
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
        adapter = LMStudioAdapter(base_url="http://test-lmstudio:1234/v1")
        result = await adapter.generate_chat_completions("model1", messages)

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-lmstudio:1234/v1/chat/completions"
        assert kwargs["json"]["model"] == "model1"
        assert kwargs["json"]["messages"] == messages

        # Verify the response was processed correctly
        assert result["model"] == "model1"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert "I'm an AI assistant" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
async def test_error_handling(mock_aiohttp_session):
    """Test error handling in the LM Studio adapter."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(base_url="http://test-lmstudio:1234/v1")
        result = await adapter.generate_text("model1", "This is a test")

        # Verify error handling
        assert "error" in result
        assert result["error"] == "Bad request"


@pytest.mark.asyncio
async def test_exception_handling(mock_aiohttp_session):
    """Test exception handling in the LM Studio adapter."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection refused")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = LMStudioAdapter(base_url="http://test-lmstudio:1234/v1")
        result = await adapter.generate_text("model1", "This is a test")

        # Verify exception handling
        assert "error" in result
        assert result["error"] == "Connection refused"
