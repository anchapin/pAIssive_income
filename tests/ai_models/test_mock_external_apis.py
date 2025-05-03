"""
Tests for mock external API implementations.

This module demonstrates how to use the mock external API implementations in tests.
"""


import json
import os
import sys
import unittest

import pytest

from tests.mocks.mock_http import mock_requests
from tests.mocks.mock_huggingface_hub import 

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
(
    mock_huggingface_hub,
)


class TestMockExternalAPIs(unittest.TestCase):
    """Test the mock external API implementations."""

    def setUp(self):
        """Set up the tests."""
        # Reset the mock requests
        mock_requests.reset()

        # Reset the mock Hugging Face Hub
        mock_huggingface_hub.reset()

        # Set up common test data
        self.setup_mock_data()

    def setup_mock_data(self):
        """Set up mock data for tests."""
        # Add mock HTTP responses
        mock_requests.add_response(
            "https://api.openai.com/v1/chat/completions",
            {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-3.5-turbo-0613",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Hello! How can I help you today?",
                        },
                        "finish_reason": "stop",
                    }
                ],
            },
            method="POST",
        )

        mock_requests.add_response(
            "https://api.openai.com/v1/embeddings",
            {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                        "index": 0,
                    }
                ],
                "model": "text-embedding-ada-002",
            },
            method="POST",
        )

        # Add mock responses for Ollama API
        mock_requests.add_response(
            "http://localhost:11434/api/generate",
            {
                "model": "llama2",
                "created_at": "2023-01-01T00:00:00Z",
                "response": "This is a response from Ollama",
                "done": True,
            },
            method="POST",
        )

        # Add mock responses for LM Studio API
        mock_requests.add_response(
            "http://localhost:1234/v1/chat/completions",
            {
                "id": "chatcmpl-lmstudio",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "local-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a response from LM Studio",
                        },
                        "finish_reason": "stop",
                    }
                ],
            },
            method="POST",
        )

        # Add mock Hugging Face repositories
        mock_huggingface_hub.add_repo(
            {
                "id": "gpt2",
                "downloads": 1000000,
                "likes": 5000,
                "tags": ["text-generation", "pytorch"],
                "pipeline_tag": "text-generation",
            }
        )

        mock_huggingface_hub.add_repo(
            {
                "id": "sentence-transformers/all-MiniLM-L6-v2",
                "downloads": 500000,
                "likes": 2000,
                "tags": ["sentence-similarity", "pytorch"],
                "pipeline_tag": "feature-extraction",
            }
        )

        # Add mock files to repositories
        mock_huggingface_hub.add_file(
            repo_id="gpt2",
            file_path="config.json",
            content=json.dumps(
                {
                    "model_type": "gpt2",
                    "vocab_size": 50257,
                    "n_positions": 1024,
                    "n_embd": 768,
                    "n_layer": 12,
                    "n_head": 12,
                }
            ),
        )

        mock_huggingface_hub.add_file(
            repo_id="gpt2",
            file_path="pytorch_model.bin",
            content=b"MOCK_MODEL_DATA",
            file_size=1000000,
        )

        mock_huggingface_hub.add_file(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            file_path="config.json",
            content=json.dumps(
                {
                    "model_type": "bert",
                    "hidden_size": 384,
                    "num_attention_heads": 12,
                    "num_hidden_layers": 6,
                }
            ),
        )

    def test_mock_http_requests(self):
        """Test mock HTTP requests."""
        # Test GET request
        mock_requests.add_response(
            "https://api.example.com/data", {"key": "value", "items": [1, 2, 3]}
        )

        response = mock_requests.get("https://api.example.com/data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["key"], "value")
        self.assertEqual(response.json()["items"], [1, 2, 3])

        # Test POST request with different status code
        mock_requests.add_response(
            "https://api.example.com/create",
            {"id": 123, "status": "created"},
            method="POST",
            status_code=201,
        )

        response = mock_requests.post(
            "https://api.example.com/create", json={"name": "Test"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], 123)

        # Test request not found
        response = mock_requests.get("https://api.example.com/nonexistent")
        self.assertEqual(response.status_code, 404)

        # Verify request history
        self.assertEqual(len(mock_requests.request_history), 3)
        self.assertEqual(mock_requests.request_history[0]["method"], "GET")
        self.assertEqual(
            mock_requests.request_history[0]["url"], "https://api.example.com/data"
        )
        self.assertEqual(mock_requests.request_history[1]["method"], "POST")
        self.assertEqual(
            mock_requests.request_history[1]["url"], "https://api.example.com/create"
        )

    def test_mock_openai_api(self):
        """Test mock OpenAI API."""
        # Test chat completions
        response = mock_requests.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello!"}],
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["choices"][0]["message"]["content"], "Hello! How can I help you today?"
        )

        # Test embeddings
        response = mock_requests.post(
            "https://api.openai.com/v1/embeddings",
            json={"model": "text-embedding-ada-002", "input": "Hello, world!"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["data"][0]["embedding"]), 5)

    def test_mock_ollama_api(self):
        """Test mock Ollama API."""
        # Test text generation
        response = mock_requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": "Hello, world!"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "This is a response from Ollama")
        self.assertEqual(data["model"], "llama2")
        self.assertTrue(data["done"])

    def test_mock_lmstudio_api(self):
        """Test mock LM Studio API."""
        # Test chat completion
        response = mock_requests.post(
            "http://localhost:1234/v1/chat/completions",
            json={
                "model": "local-model",
                "messages": [{"role": "user", "content": "Hello!"}],
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["choices"][0]["message"]["content"],
            "This is a response from LM Studio",
        )

    def test_mock_huggingface_hub(self):
        """Test mock Hugging Face Hub."""
        # Test downloading a file
        file_path = mock_huggingface_hub.hf_hub_download(
            repo_id="gpt2", filename="config.json"
        )

        self.assertTrue(os.path.exists(file_path))

        with open(file_path, "r") as f:
            config = json.loads(f.read())

        self.assertEqual(config["model_type"], "gpt2")
        self.assertEqual(config["vocab_size"], 50257)

        # Test downloading a snapshot
        repo_path = mock_huggingface_hub.snapshot_download(repo_id="gpt2")

        self.assertTrue(os.path.exists(repo_path))
        self.assertTrue(os.path.exists(os.path.join(repo_path, "config.json")))
        self.assertTrue(os.path.exists(os.path.join(repo_path, "pytorch_model.bin")))

        # Test listing models
        models = mock_huggingface_hub.list_models(search="gpt")
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].id, "gpt2")

        # Test authentication required
        # Make a private repo
        mock_huggingface_hub.add_repo({"id": "private/model", "private": True})

        # Test downloading without authentication
        with self.assertRaises(ValueError):
            mock_huggingface_hub.hf_hub_download(
                repo_id="private/model", filename="config.json"
            )

        # Test downloading with authentication
        mock_huggingface_hub.login(token="valid_token")

        # Now add a file to the private repo
        mock_huggingface_hub.add_file(
            repo_id="private/model",
            file_path="config.json",
            content=json.dumps({"private": True}),
        )

        # Download should work now
        file_path = mock_huggingface_hub.hf_hub_download(
            repo_id="private/model", filename="config.json"
        )

        self.assertTrue(os.path.exists(file_path))


@pytest.fixture
def mock_http():
    """Fixture to provide mock HTTP requests."""
    # Reset the mock requests before each test
    mock_requests.reset()

    # Add common mock responses
    mock_requests.add_response(
        "https://api.openai.com/v1/chat/completions",
        {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?",
                    },
                    "finish_reason": "stop",
                }
            ],
        },
        method="POST",
    )

            return mock_requests


@pytest.fixture
def mock_hf_hub():
    """Fixture to provide mock Hugging Face Hub."""
    # Reset the mock Hugging Face Hub before each test
    mock_huggingface_hub.reset()

    # Add common repositories and files
    mock_huggingface_hub.add_repo({"id": "gpt2", "pipeline_tag": "text-generation"})

    mock_huggingface_hub.add_file(
        repo_id="gpt2",
        file_path="config.json",
        content=json.dumps({"model_type": "gpt2"}),
    )

            return mock_huggingface_hub


def test_with_pytest_fixtures(mock_http, mock_hf_hub):
    """Test using pytest fixtures."""
    # Test HTTP request
    response = mock_http.post(
        "https://api.openai.com/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert response.status_code == 200
    assert (
        response.json()["choices"][0]["message"]["content"]
        == "Hello! How can I help you today?"
    )

    # Test Hugging Face Hub download
    file_path = mock_hf_hub.hf_hub_download(repo_id="gpt2", filename="config.json")
    assert os.path.exists(file_path)

    with open(file_path, "r") as f:
        config = json.loads(f.read())
    assert config["model_type"] == "gpt2"


if __name__ == "__main__":
    unittest.main()