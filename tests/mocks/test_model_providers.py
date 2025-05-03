"""Tests for mock model provider implementations."""

from typing import Any, Dict, Generator

import pytest

from .mock_model_providers import (
    BaseMockProvider,
    MockHuggingFaceProvider,
    MockLMStudioProvider,
    MockLocalModelProvider,
    MockOllamaProvider,
    MockONNXProvider,
    MockOpenAIProvider,
)


def test_base_mock_provider():
    """Test base mock provider functionality."""
    provider = BaseMockProvider({"deterministic": True, "simulate_errors": True})

    # Test deterministic response
    assert provider._get_mock_response() == "This is a deterministic mock response."

    # Test deterministic embedding
    embedding = provider._get_mock_embedding(dimension=5)
    assert len(embedding) == 5
    assert all(x == 0.1 for x in embedding)

    # Test error simulation
    assert provider._should_simulate_error() is True


def test_openai_provider():
    """Test OpenAI mock provider."""
    provider = MockOpenAIProvider()

    # Test regular chat completion
    response = provider.chat_completion([{"role": "user", "content": "Hello"}])
    assert "choices" in response
    assert len(response["choices"]) == 1
    assert "message" in response["choices"][0]

    # Test streaming chat completion
    stream = provider.chat_completion([{"role": "user", "content": "Hello"}], stream=True)
    assert isinstance(stream, Generator)
    chunks = list(stream)
    assert len(chunks) > 0
    assert all("choices" in chunk for chunk in chunks)

    # Test completion
    response = provider.completion("Test prompt")
    assert "choices" in response
    assert "text" in response["choices"][0]

    # Test embeddings
    response = provider.embeddings("Test text")
    assert "data" in response
    assert len(response["data"]) == 1
    assert "embedding" in response["data"][0]


def test_huggingface_provider():
    """Test HuggingFace mock provider."""
    provider = MockHuggingFaceProvider()

    # Test generation
    response = provider.generate("Test prompt")
    assert isinstance(response, list)
    assert len(response) == 1
    assert "generated_text" in response[0]

    # Test embeddings
    embeddings = provider.get_embeddings("Test text")
    assert isinstance(embeddings, list)
    assert all(isinstance(x, float) for x in embeddings)


def test_ollama_provider():
    """Test Ollama mock provider."""
    provider = MockOllamaProvider()

    # Test generation
    response = provider.generate("Test prompt")
    assert "response" in response
    assert "model" in response

    # Test chat
    response = provider.chat([{"role": "user", "content": "Hello"}])
    assert "message" in response
    assert "role" in response["message"]
    assert "content" in response["message"]


def test_lm_studio_provider():
    """Test LM Studio mock provider."""
    provider = MockLMStudioProvider()

    # Test chat completion
    response = provider.chat_completion([{"role": "user", "content": "Hello"}])
    assert "choices" in response
    assert "message" in response["choices"][0]

    # Test completion
    response = provider.completion("Test prompt")
    assert "choices" in response
    assert "text" in response["choices"][0]


def test_local_model_provider():
    """Test local model provider."""
    provider = MockLocalModelProvider()

    # Test inference
    response = provider.inference("Test prompt")
    assert "text" in response
    assert "tokens" in response
    assert "time_ms" in response

    # Test batch inference
    responses = provider.batch_inference(["Prompt 1", "Prompt 2"])
    assert len(responses) == 2
    assert all("text" in r for r in responses)
    assert all("tokens" in r for r in responses)
    assert all("time_ms" in r for r in responses)


def test_onnx_provider():
    """Test ONNX model provider."""
    provider = MockONNXProvider()

    # Test inference
    response = provider.run_inference("Test input")
    assert "output" in response
    assert "text" in response["output"]
    assert "probabilities" in response["output"]

    # Test optimization
    response = provider.optimize_model()
    assert "status" in response
    assert response["status"] == "success"


def test_error_simulation():
    """Test error simulation across providers."""
    config = {"simulate_errors": True, "error_rate": 1.0}  # Always simulate errors

    providers = [
        MockOpenAIProvider(config),
        MockHuggingFaceProvider(config),
        MockOllamaProvider(config),
        MockLMStudioProvider(config),
        MockLocalModelProvider(config),
        MockONNXProvider(config),
    ]

    for provider in providers:
        with pytest.raises(Exception):
            if isinstance(provider, MockOpenAIProvider):
                provider.chat_completion([{"role": "user", "content": "Test"}])
            elif isinstance(provider, MockHuggingFaceProvider):
                provider.generate("Test")
            elif isinstance(provider, MockOllamaProvider):
                provider.generate("Test")
            elif isinstance(provider, MockLMStudioProvider):
                provider.chat_completion([{"role": "user", "content": "Test"}])
            elif isinstance(provider, MockLocalModelProvider):
                provider.inference("Test")
            elif isinstance(provider, MockONNXProvider):
                provider.run_inference("Test")
