"""
Tests for mock model providers.

This module demonstrates how to use the mock model providers in tests.
"""

import unittest
import os
import sys
from typing import Dict, List, Any, Optional
import pytest
import numpy as np

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tests.mocks.mock_model_providers import (
    create_mock_provider,
    MockOpenAIProvider,
    MockOllamaProvider,
    MockLMStudioProvider,
    MockHuggingFaceProvider,
    MockLocalModelProvider,
    MockONNXProvider
)
from ai_models.model_manager import ModelManager, ModelInfo
from ai_models.model_config import ModelConfig


class TestMockProviders(unittest.TestCase):
    """Test the mock AI model providers."""

    def test_create_mock_provider(self):
        """Test creating different mock providers."""
        # Test creating each type of provider
        openai_provider = create_mock_provider("openai")
        self.assertIsInstance(openai_provider, MockOpenAIProvider)

        ollama_provider = create_mock_provider("ollama")
        self.assertIsInstance(ollama_provider, MockOllamaProvider)

        lmstudio_provider = create_mock_provider("lmstudio")
        self.assertIsInstance(lmstudio_provider, MockLMStudioProvider)

        huggingface_provider = create_mock_provider("huggingface")
        self.assertIsInstance(huggingface_provider, MockHuggingFaceProvider)

        local_provider = create_mock_provider("local")
        self.assertIsInstance(local_provider, MockLocalModelProvider)

        onnx_provider = create_mock_provider("onnx")
        self.assertIsInstance(onnx_provider, MockONNXProvider)

        # Test with custom configuration
        custom_config = {
            "default_completion": "This is a custom response",
            "success_rate": 1.0
        }
        custom_provider = create_mock_provider("openai", config=custom_config)
        self.assertEqual(custom_provider.success_rate, 1.0)
        self.assertEqual(
            custom_provider.mock_responses["chat_completion"]["choices"][0]["message"]["content"],
            "This is a custom response"
        )

        # Test with invalid provider type
        with self.assertRaises(ValueError):
            create_mock_provider("invalid_provider")

    def test_openai_mock_provider(self):
        """Test the OpenAI mock provider."""
        provider = MockOpenAIProvider()

        # Test listing models
        models = provider.list_models()
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)

        # Test getting model info
        model_info = provider.get_model_info("gpt-3.5-turbo")
        self.assertIsNotNone(model_info)
        self.assertEqual(model_info["id"], "gpt-3.5-turbo")

        # Test creating a chat completion
        messages = [{"role": "user", "content": "Hello, world!"}]
        completion = provider.create_chat_completion("gpt-3.5-turbo", messages)
        self.assertIsInstance(completion, dict)
        self.assertIn("choices", completion)
        self.assertIn("message", completion["choices"][0])
        self.assertIn("content", completion["choices"][0]["message"])

        # Test creating an embedding
        embedding = provider.create_embedding("text-embedding-ada-002", "Hello, world!")
        self.assertIsInstance(embedding, dict)
        self.assertIn("data", embedding)
        self.assertIn("embedding", embedding["data"][0])

        # Check call history
        call_history = provider.get_call_history()
        # The call history should include: list_models, get_model_info, create_chat_completion, create_embedding
        # and possibly other internal calls
        self.assertGreaterEqual(len(call_history), 4)

        # Test with invalid model
        with self.assertRaises(ValueError):
            provider.create_chat_completion("nonexistent-model", messages)

    def test_huggingface_mock_provider(self):
        """Test the Hugging Face mock provider."""
        provider = MockHuggingFaceProvider()

        # Test text generation
        text_gen = provider.text_generation("gpt2", "Hello, world!")
        self.assertIsInstance(text_gen, list)
        self.assertIn("generated_text", text_gen[0])

        # Test embedding
        embeddings = provider.embedding("all-MiniLM-L6-v2", "Hello, world!")
        self.assertIsInstance(embeddings, np.ndarray)

        # Test with multiple texts for embedding
        multi_embeddings = provider.embedding("all-MiniLM-L6-v2", ["Hello", "World"])
        self.assertIsInstance(multi_embeddings, np.ndarray)
        self.assertEqual(multi_embeddings.shape[0], 2)  # 2 embeddings

        # Test with invalid model
        with self.assertRaises(ValueError):
            provider.text_generation("nonexistent-model", "Hello, world!")

        # Test with invalid capability
        with self.assertRaises(ValueError):
            provider.text_classification("gpt2", "Hello, world!")  # gpt2 doesn't support classification

    def test_local_mock_provider(self):
        """Test the local model mock provider."""
        provider = MockLocalModelProvider()

        # Test completion
        completion = provider.generate_completion("llama-2-7b-chat.gguf", "Hello, world!")
        self.assertIsInstance(completion, dict)
        self.assertIn("text", completion)

        # Test chat completion
        messages = [{"role": "user", "content": "Hello, world!"}]
        chat_completion = provider.generate_chat_completion("llama-2-7b-chat.gguf", messages)
        self.assertIsInstance(chat_completion, dict)
        self.assertIn("text", chat_completion)

        # Test with streaming
        stream = provider.generate_completion("llama-2-7b-chat.gguf", "Hello", stream=True)
        chunks = list(stream)
        self.assertTrue(len(chunks) > 0)
        self.assertIn("text", chunks[0])
        self.assertTrue("stop" in chunks[-1])  # Last chunk should indicate stop

        # Test with invalid model
        with self.assertRaises(ValueError):
            provider.generate_completion("nonexistent-model", "Hello, world!")

    def test_onnx_mock_provider(self):
        """Test the ONNX mock provider."""
        provider = MockONNXProvider()

        # Test text classification
        inputs = {"input_ids": [1, 2, 3, 4, 5]}
        result = provider.run_inference("bert-base-onnx", inputs)
        self.assertIsInstance(result, dict)
        self.assertIn("label_scores", result)

        # Test text generation
        result = provider.run_inference("gpt2-onnx", {"input_ids": [1, 2, 3, 4, 5]})
        self.assertIsInstance(result, dict)
        self.assertIn("generated_text", result)

        # Test with invalid model
        with self.assertRaises(ValueError):
            provider.run_inference("nonexistent-model", inputs)

    def test_integration_with_model_manager(self):
        """Test integrating mock providers with the ModelManager."""
        # Create a mock model manager instead of a real one
        import tempfile
        from unittest.mock import MagicMock

        # Create a mock ModelManager that implements the required abstract methods
        class MockModelManager:
            def __init__(self, config):
                self.config = config
                self.models = {}

            def list_models(self):
                return list(self.models.values())

            def get_all_models(self):
                return list(self.models.values())

            def register_model(self, model_info):
                self.models[model_info.id] = model_info

            def unload_model(self, model_id):
                pass

        # Create the mock manager
        temp_dir = tempfile.mkdtemp()
        config = ModelConfig()
        config.models_dir = temp_dir
        config.cache_dir = temp_dir
        manager = MockModelManager(config)

        # Register mock models
        # 1. Register a mock Hugging Face model
        hf_model = ModelInfo(
            id="mock-hf-model",
            name="Mock HF Model",
            type="huggingface",
            path="gpt2",
            description="Mock Hugging Face model for testing"
        )
        manager.register_model(hf_model)

        # 2. Register a mock local GGUF model
        local_model = ModelInfo(
            id="mock-local-model",
            name="Mock Local Model",
            type="llama",
            path=os.path.join(temp_dir, "mock-model.gguf"),
            description="Mock local GGUF model for testing",
            format="gguf",
            quantization="q4_k_m"
        )
        # Create an empty file to simulate the model
        with open(local_model.path, "w") as f:
            f.write("MOCK MODEL DATA")
        manager.register_model(local_model)

        # Verify the models are registered
        models = manager.get_all_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0].name, "Mock HF Model")
        self.assertEqual(models[1].name, "Mock Local Model")


@pytest.fixture
def mock_openai_provider():
    """Fixture to create a mock OpenAI provider."""
    provider = MockOpenAIProvider()
    return provider


@pytest.fixture
def mock_huggingface_provider():
    """Fixture to create a mock Hugging Face provider."""
    provider = MockHuggingFaceProvider()
    return provider


@pytest.fixture
def mock_local_provider():
    """Fixture to create a mock local model provider."""
    provider = MockLocalModelProvider()
    return provider


@pytest.fixture
def mock_onnx_provider():
    """Fixture to create a mock ONNX provider."""
    provider = MockONNXProvider()
    return provider


@pytest.fixture
def mock_providers():
    """Fixture to create all mock providers."""
    providers = {
        "openai": MockOpenAIProvider(),
        "huggingface": MockHuggingFaceProvider(),
        "local": MockLocalModelProvider(),
        "onnx": MockONNXProvider(),
        "ollama": MockOllamaProvider(),
        "lmstudio": MockLMStudioProvider()
    }
    return providers


def test_usage_with_pytest(mock_openai_provider, mock_providers):
    """Example test using pytest fixtures."""
    # Test with a single provider fixture
    response = mock_openai_provider.create_chat_completion(
        "gpt-3.5-turbo",
        [{"role": "user", "content": "Hello, pytest!"}]
    )
    assert "choices" in response
    assert "message" in response["choices"][0]

    # Test with all providers
    hf_provider = mock_providers["huggingface"]
    response = hf_provider.text_generation("gpt2", "Hello from pytest!")
    assert "generated_text" in response[0]


if __name__ == "__main__":
    unittest.main()