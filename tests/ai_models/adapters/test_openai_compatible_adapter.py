"""test_openai_compatible_adapter - Module for tests/ai_models/adapters.test_openai_compatible_adapter."""

# Standard library imports
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Third-party imports
import pytest
import aiohttp

# Local imports
from ai_models.adapters import OpenAICompatibleAdapter


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
    """Test listing models from OpenAI-compatible API."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "data": [
            {"id": "gpt-3.5-turbo", "object": "model", "name": "GPT-3.5 Turbo"},
            {"id": "gpt-4", "object": "model", "name": "GPT-4"}
        ]
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        models = await adapter.list_models()

        # Verify the request was made correctly
        mock_session.get.assert_called_once_with("http://test-openai:8000/v1/models")

        # Verify the response was processed correctly
        assert len(models) == 2
        assert models[0]["id"] == "gpt-3.5-turbo"
        assert models[1]["name"] == "GPT-4"


@pytest.mark.asyncio
async def test_generate_text(mock_aiohttp_session):
    """Test generating text with OpenAI-compatible API."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "id": "cmpl-123",
        "object": "text_completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo",
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
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_text("gpt-3.5-turbo", "This is a test")

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-openai:8000/v1/completions"
        assert kwargs["json"]["model"] == "gpt-3.5-turbo"
        assert kwargs["json"]["prompt"] == "This is a test"

        # Verify the response was processed correctly
        assert result["model"] == "gpt-3.5-turbo"
        assert result["choices"][0]["text"] == "This is a test response"


@pytest.mark.asyncio
async def test_generate_chat_completions(mock_aiohttp_session):
    """Test generating chat completions with OpenAI-compatible API."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo",
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
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_chat_completions("gpt-3.5-turbo", messages)

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-openai:8000/v1/chat/completions"
        assert kwargs["json"]["model"] == "gpt-3.5-turbo"
        assert kwargs["json"]["messages"] == messages

        # Verify the response was processed correctly
        assert result["model"] == "gpt-3.5-turbo"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert "I'm an AI assistant" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
async def test_create_embedding(mock_aiohttp_session):
    """Test creating embeddings with OpenAI-compatible API."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "index": 0
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 8,
            "total_tokens": 8
        }
    }

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.create_embedding("text-embedding-ada-002", "This is a test")

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-openai:8000/v1/embeddings"
        assert kwargs["json"]["model"] == "text-embedding-ada-002"
        assert kwargs["json"]["input"] == "This is a test"

        # Verify the response was processed correctly
        assert result["model"] == "text-embedding-ada-002"
        assert result["data"][0]["embedding"] == [0.1, 0.2, 0.3, 0.4, 0.5]


@pytest.mark.asyncio
async def test_error_handling(mock_aiohttp_session):
    """Test error handling in the OpenAI-compatible adapter."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 401
    mock_response.text.return_value = "Unauthorized"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="invalid-key")
        result = await adapter.generate_text("gpt-3.5-turbo", "This is a test")

        # Verify error handling
        assert "error" in result
        assert result["error"] == "Unauthorized"


@pytest.mark.asyncio
async def test_exception_handling(mock_aiohttp_session):
    """Test exception handling in the OpenAI-compatible adapter."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection timeout")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_text("gpt-3.5-turbo", "This is a test")

        # Verify exception handling
        assert "error" in result
        assert result["error"] == "Connection timeout"


@pytest.mark.asyncio
async def test_list_models_error(mock_aiohttp_session):
    """Test error handling when listing models."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 500
    mock_response.text.return_value = "Internal server error"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        models = await adapter.list_models()

        # Verify empty list is returned on error
        assert models == []


@pytest.mark.asyncio
async def test_list_models_exception(mock_aiohttp_session):
    """Test exception handling when listing models."""
    mock_session, _ = mock_aiohttp_session
    mock_session.get.side_effect = Exception("Connection refused")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        models = await adapter.list_models()

        # Verify empty list is returned on exception
        assert models == []


@pytest.mark.asyncio
async def test_generate_text_with_params(mock_aiohttp_session):
    """Test generating text with additional parameters."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "id": "cmpl-123",
        "object": "text_completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo",
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
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_text(
            "gpt-3.5-turbo",
            "This is a test",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            n=2,
            stream=True,
            stop=["END"],
            presence_penalty=0.1,
            frequency_penalty=0.2
        )

        # Verify the request was made with all parameters
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-openai:8000/v1/completions"
        assert kwargs["json"]["model"] == "gpt-3.5-turbo"
        assert kwargs["json"]["prompt"] == "This is a test"
        assert kwargs["json"]["max_tokens"] == 100
        assert kwargs["json"]["temperature"] == 0.5
        assert kwargs["json"]["top_p"] == 0.9
        assert kwargs["json"]["n"] == 2
        assert kwargs["json"]["stream"] == True
        assert kwargs["json"]["stop"] == ["END"]
        assert kwargs["json"]["presence_penalty"] == 0.1
        assert kwargs["json"]["frequency_penalty"] == 0.2


@pytest.mark.asyncio
async def test_generate_chat_completions_with_params(mock_aiohttp_session):
    """Test generating chat completions with additional parameters."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo",
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
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_chat_completions(
            "gpt-3.5-turbo",
            messages,
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            n=2,
            stream=True,
            stop=["END"],
            presence_penalty=0.1,
            frequency_penalty=0.2
        )

        # Verify the request was made with all parameters
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-openai:8000/v1/chat/completions"
        assert kwargs["json"]["model"] == "gpt-3.5-turbo"
        assert kwargs["json"]["messages"] == messages
        assert kwargs["json"]["max_tokens"] == 100
        assert kwargs["json"]["temperature"] == 0.5
        assert kwargs["json"]["top_p"] == 0.9
        assert kwargs["json"]["n"] == 2
        assert kwargs["json"]["stream"] == True
        assert kwargs["json"]["stop"] == ["END"]
        assert kwargs["json"]["presence_penalty"] == 0.1
        assert kwargs["json"]["frequency_penalty"] == 0.2


@pytest.mark.asyncio
async def test_create_embedding_with_list_input(mock_aiohttp_session):
    """Test creating embeddings with a list of inputs."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.json.return_value = {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3],
                "index": 0
            },
            {
                "object": "embedding",
                "embedding": [0.4, 0.5, 0.6],
                "index": 1
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 16,
            "total_tokens": 16
        }
    }

    input_texts = ["First text", "Second text"]

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.create_embedding("text-embedding-ada-002", input_texts)

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        args, kwargs = mock_session.post.call_args
        assert args[0] == "http://test-openai:8000/v1/embeddings"
        assert kwargs["json"]["model"] == "text-embedding-ada-002"
        assert kwargs["json"]["input"] == input_texts

        # Verify the response was processed correctly
        assert result["model"] == "text-embedding-ada-002"
        assert len(result["data"]) == 2
        assert result["data"][0]["embedding"] == [0.1, 0.2, 0.3]
        assert result["data"][1]["embedding"] == [0.4, 0.5, 0.6]


@pytest.mark.asyncio
async def test_embedding_error_handling(mock_aiohttp_session):
    """Test error handling in embedding creation."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.create_embedding("text-embedding-ada-002", "This is a test")

        # Verify error handling
        assert "error" in result
        assert result["error"] == "Bad request"


@pytest.mark.asyncio
async def test_embedding_exception_handling(mock_aiohttp_session):
    """Test exception handling in embedding creation."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection timeout")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.create_embedding("text-embedding-ada-002", "This is a test")

        # Verify exception handling
        assert "error" in result
        assert result["error"] == "Connection timeout"


@pytest.mark.asyncio
async def test_chat_completions_error_handling(mock_aiohttp_session):
    """Test error handling in chat completions."""
    mock_session, mock_response = mock_aiohttp_session
    mock_response.status = 400
    mock_response.text.return_value = "Bad request"

    messages = [
        {"role": "user", "content": "Hello"}
    ]

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_chat_completions("gpt-3.5-turbo", messages)

        # Verify error handling
        assert "error" in result
        assert result["error"] == "Bad request"


@pytest.mark.asyncio
async def test_chat_completions_exception_handling(mock_aiohttp_session):
    """Test exception handling in chat completions."""
    mock_session, _ = mock_aiohttp_session
    mock_session.post.side_effect = Exception("Connection timeout")

    messages = [
        {"role": "user", "content": "Hello"}
    ]

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        result = await adapter.generate_chat_completions("gpt-3.5-turbo", messages)

        # Verify exception handling
        assert "error" in result
        assert result["error"] == "Connection timeout"


@pytest.mark.asyncio
async def test_close_session(mock_aiohttp_session):
    """Test closing the session."""
    mock_session, _ = mock_aiohttp_session

    with patch("aiohttp.ClientSession", return_value=mock_session):
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")

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
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key")
        adapter._session = mock_session

        # Close the session
        await adapter.close()

        # Verify session close was not called
        mock_session.close.assert_not_called()


@pytest.mark.asyncio
async def test_get_session():
    """Test getting a session."""
    mock_session = MagicMock()

    with patch("aiohttp.ClientSession", return_value=mock_session) as mock_client_session:
        adapter = OpenAICompatibleAdapter(base_url="http://test-openai:8000/v1", api_key="test-key", timeout=30)

        # Get session
        session = await adapter._get_session()

        # Verify session was created with correct parameters
        mock_client_session.assert_called_once()
        _, kwargs = mock_client_session.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["timeout"].total == 30
