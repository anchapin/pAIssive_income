"""
Mock implementations of AI model providers for testing.

This module provides mock implementations of various AI model providers
that can be used for consistent testing without external dependencies.
"""

import time


import logging
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


class MockBaseModelProvider:
    """Base class for mock model providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mock model provider.

        Args:
            config: Optional configuration for the mock provider
        """
        self.config = config or {}
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "capabilities": ["text-generation", "chat"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "mock-provider",
                },
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "capabilities": ["text-generation", "chat"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "mock-provider",
                },
                {
                    "id": "dall-e-3",
                    "name": "DALL-E 3",
                    "capabilities": ["image-generation"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "mock-provider",
                },
                {
                    "id": "text-embedding-ada-002",
                    "name": "Text Embedding Ada 002",
                    "capabilities": ["embeddings"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "mock-provider",
                },
            ],
        )

        # Set up success rates
        self.success_rate = self.config.get("success_rate", 0.95)
        self.latency_range = self.config.get("latency_range", (100, 500))  # ms
        self.error_messages = self.config.get(
            "error_messages",
            {
                "rate_limit": "Rate limit exceeded. Please try again later.",
                "invalid_model": "The model does not exist or you don't have access to it.",
                "invalid_request": "The request is not valid for this model.",
                "context_length": "The context length exceeds the model's limit.",
            },
        )

        # Track call history for assertions
        self.call_history = []

    def record_call(self, method_name: str, **kwargs):
        """Record a method call for testing assertions."""
        self.call_history.append(
            {
                "method": method_name,
                "timestamp": datetime.now().isoformat(),
                "args": kwargs,
            }
        )

    def get_call_history(
        self, method_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get the call history, optionally filtered by method name."""
        if method_name:
            return [call for call in self.call_history if call["method"] == method_name]
        return self.call_history

    def clear_call_history(self):
        """Clear the call history."""
        self.call_history = []


class MockOpenAIProvider(MockBaseModelProvider):
    """Mock implementation of OpenAI API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock OpenAI provider."""
        super().__init__(config)

        # Default available models
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "capabilities": ["text-generation", "chat", "function-calling"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "openai",
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "capabilities": ["text-generation", "chat", "function-calling"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "openai",
                },
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "capabilities": ["text-generation", "chat", "function-calling"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "openai",
                },
                {
                    "id": "text-embedding-ada-002",
                    "name": "Text Embedding Ada 002",
                    "capabilities": ["embeddings"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "openai",
                },
                {
                    "id": "dall-e-3",
                    "name": "DALL-E 3",
                    "capabilities": ["image-generation"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "openai",
                },
            ],
        )

        # Set up custom responses for specific prompts
        self.config["custom_responses"] = self.config.get(
            "custom_responses",
            {
                "analyze market trends": "Market analysis shows positive growth trends.",
                "market trends": "Market analysis shows positive growth trends.",
            },
        )

        # Mock responses for each endpoint
        self.mock_responses = {
            "chat_completion": {
                "id": "chatcmpl-mock-id",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": self.config.get(
                                "default_completion",
                                "This is a mock response from the AI model.",
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                },
            },
            "text_completion": {
                "id": "cmpl-mock-id",
                "object": "text_completion",
                "created": int(datetime.now().timestamp()),
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "text": self.config.get(
                            "default_completion",
                            "This is a mock response from the AI model.",
                        ),
                        "index": 0,
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 15,
                    "total_tokens": 25,
                },
            },
            "embeddings": {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                        "index": 0,
                    }
                ],
                "model": "text-embedding-ada-002",
                "usage": {"prompt_tokens": 8, "total_tokens": 8},
            },
            "images": {
                "created": int(datetime.now().timestamp()),
                "data": [{"url": "https://mock-url.com/image.png", "b64_json": None}],
            },
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        self.record_call("list_models")
        return self.available_models

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        self.record_call("get_model_info", model_id=model_id)

        # Find the model in available models
        for model in self.available_models:
            if model["id"] == model_id:
                return model

        return None

    def create_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a text completion."""
        self.record_call(
            "create_completion",
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        # Check if model exists
        if not any(m["id"] == model for m in self.available_models):
            raise ValueError(self.error_messages["invalid_model"])

        response = self.mock_responses["text_completion"].copy()
        response["model"] = model

        # If a custom response is provided for this specific prompt, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in prompt:
                response["choices"][0]["text"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["choices"][0]["text"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    yield {
                        "id": f"cmpl-mock-id-stream-{i}",
                        "object": "text_completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "model": model,
                        "choices": [
                            {
                                "text": word + " ",
                                "index": 0,
                                "finish_reason": (
                                    "stop" if i == len(words) - 1 else None
                                ),
                            }
                        ],
                    }

            return generate_stream()

        return response

    def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a chat completion."""
        self.record_call(
            "create_chat_completion",
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        # Check if model exists
        if not any(m["id"] == model for m in self.available_models):
            raise ValueError(self.error_messages["invalid_model"])

        response = self.mock_responses["chat_completion"].copy()
        response["model"] = model

        # Extract the user's message for matching custom responses
        user_message = ""
        for message in messages:
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break

        # If a custom response is provided for this specific message, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in user_message:
                response["choices"][0]["message"]["content"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["choices"][0]["message"]["content"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    yield {
                        "id": f"chatcmpl-mock-id-stream-{i}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": word + " "},
                                "finish_reason": (
                                    "stop" if i == len(words) - 1 else None
                                ),
                            }
                        ],
                    }

            return generate_stream()

        return response

    def create_embedding(
        self, model: str, input: Union[str, List[str]], **kwargs
    ) -> Dict[str, Any]:
        """Create embeddings for the given input."""
        self.record_call("create_embedding", model=model, input=input, **kwargs)

        # Check if model exists and has embedding capability
        model_info = self.get_model_info(model)
        if not model_info or "embeddings" not in model_info.get("capabilities", []):
            raise ValueError(self.error_messages["invalid_model"])

        response = self.mock_responses["embeddings"].copy()
        response["model"] = model

        # Handle list of inputs
        if isinstance(input, list):
            response["data"] = []
            for i, text in enumerate(input):
                response["data"].append(
                    {
                        "object": "embedding",
                        # Generate deterministic but different vectors for different inputs
                        "embedding": [0.1 * (i + 1) + 0.01 * j for j in range(10)],
                        "index": i,
                    }
                )
            response["usage"]["prompt_tokens"] = sum(
                len(text.split()) for text in input
            )
            response["usage"]["total_tokens"] = response["usage"]["prompt_tokens"]

        return response

    def create_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = "1024x1024",
        n: int = 1,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create images from a prompt."""
        self.record_call(
            "create_image", prompt=prompt, model=model, size=size, n=n, **kwargs
        )

        # Use DALL-E 3 as default model if none specified
        model = model or "dall-e-3"

        # Check if model exists and has image generation capability
        model_info = self.get_model_info(model)
        if not model_info or "image-generation" not in model_info.get(
            "capabilities", []
        ):
            raise ValueError(self.error_messages["invalid_model"])

        response = self.mock_responses["images"].copy()

        # Generate multiple images if requested
        if n > 1:
            response["data"] = []
            for i in range(n):
                response["data"].append(
                    {"url": f"https://mock-url.com/image_{i}.png", "b64_json": None}
                )

        return response


class MockOllamaProvider(MockBaseModelProvider):
    """Mock implementation of Ollama API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock Ollama provider."""
        super().__init__(config)

        # Override available models for Ollama
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "llama2",
                    "name": "Llama 2",
                    "capabilities": ["text-generation", "chat"],
                    "modified_at": datetime.now().isoformat(),
                    "size": 3791730293,
                },
                {
                    "id": "llama2:13b",
                    "name": "Llama 2 13B",
                    "capabilities": ["text-generation", "chat"],
                    "modified_at": datetime.now().isoformat(),
                    "size": 7323315540,
                },
                {
                    "id": "mistral",
                    "name": "Mistral 7B",
                    "capabilities": ["text-generation", "chat"],
                    "modified_at": datetime.now().isoformat(),
                    "size": 4032639651,
                },
            ],
        )

        # Mock responses
        self.mock_responses = {
            "completion": {
                "model": "llama2",
                "created_at": datetime.now().isoformat(),
                "response": self.config.get(
                    "default_completion",
                    "This is a mock response from the Ollama model.",
                ),
                "done": True,
                "context": [1, 2, 3, 4, 5],
                "total_duration": 635163166,
                "load_duration": 1795833,
                "prompt_eval_duration": 129356000,
                "eval_count": 114,
                "eval_duration": 504010000,
            }
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        self.record_call("list_models")
        return {"models": self.available_models}

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        self.record_call("get_model_info", model_id=model_id)

        # Find the model in available models
        for model in self.available_models:
            if model["id"] == model_id:
                return model

        return None

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Generate a completion from the model."""
        self.record_call(
            "generate",
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        # Check if model exists
        if not any(m["id"] == model for m in self.available_models):
            raise ValueError(f"Model {model} not found")

        response = self.mock_responses["completion"].copy()
        response["model"] = model

        # If a custom response is provided for this specific prompt, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in prompt:
                response["response"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["response"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    done = i == len(words) - 1
                    chunk = response.copy()
                    chunk["response"] = word + " "
                    chunk["done"] = done
                    yield chunk

            return generate_stream()

        return response

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Generate a chat completion from the model."""
        self.record_call(
            "chat",
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        # Check if model exists
        if not any(m["id"] == model for m in self.available_models):
            raise ValueError(f"Model {model} not found")

        response = self.mock_responses["completion"].copy()
        response["model"] = model

        # Extract the user's message for matching custom responses
        user_message = ""
        for message in messages:
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break

        # If a custom response is provided for this specific message, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in user_message:
                response["response"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["response"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    done = i == len(words) - 1
                    chunk = response.copy()
                    chunk["response"] = word + " "
                    chunk["done"] = done
                    yield chunk

            return generate_stream()

        return response


class MockLMStudioProvider(MockBaseModelProvider):
    """Mock implementation of LM Studio API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock LM Studio provider."""
        super().__init__(config)

        # Override available models for LM Studio
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "local-model",
                    "name": "Local Model",
                    "capabilities": ["text-generation", "chat"],
                    "created": int(datetime.now().timestamp()),
                    "owned_by": "user",
                }
            ],
        )

        # Mock responses - LM Studio uses OpenAI compatible API
        self.mock_responses = {
            "completion": {
                "id": "cmpl-lmstudio-mock",
                "object": "text_completion",
                "created": int(datetime.now().timestamp()),
                "model": "local-model",
                "choices": [
                    {
                        "text": self.config.get(
                            "default_completion",
                            "This is a mock response from LM Studio.",
                        ),
                        "index": 0,
                        "finish_reason": "stop",
                    }
                ],
            },
            "chat_completion": {
                "id": "chatcmpl-lmstudio-mock",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": "local-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": self.config.get(
                                "default_completion",
                                "This is a mock response from LM Studio.",
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
            },
        }

    def list_models(self) -> Dict[str, Any]:
        """List available models."""
        self.record_call("list_models")
        return {"data": self.available_models, "object": "list"}

    def create_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a text completion."""
        self.record_call(
            "create_completion",
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        response = self.mock_responses["completion"].copy()
        response["model"] = model

        # If a custom response is provided for this specific prompt, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in prompt:
                response["choices"][0]["text"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["choices"][0]["text"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    yield {
                        "id": f"cmpl-lmstudio-mock-stream-{i}",
                        "object": "text_completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "model": model,
                        "choices": [
                            {
                                "text": word + " ",
                                "index": 0,
                                "finish_reason": (
                                    "stop" if i == len(words) - 1 else None
                                ),
                            }
                        ],
                    }

            return generate_stream()

        return response

    def create_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a chat completion."""
        self.record_call(
            "create_chat_completion",
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        response = self.mock_responses["chat_completion"].copy()
        response["model"] = model

        # Extract the user's message for matching custom responses
        user_message = ""
        for message in messages:
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break

        # If a custom response is provided for this specific message, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in user_message:
                response["choices"][0]["message"]["content"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["choices"][0]["message"]["content"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    yield {
                        "id": f"chatcmpl-lmstudio-mock-stream-{i}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": word + " "},
                                "finish_reason": (
                                    "stop" if i == len(words) - 1 else None
                                ),
                            }
                        ],
                    }

            return generate_stream()

        return response


class MockHuggingFaceProvider(MockBaseModelProvider):
    """Mock implementation of Hugging Face API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock Hugging Face provider."""
        super().__init__(config)

        # Override available models for Hugging Face
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "gpt2",
                    "name": "GPT-2",
                    "capabilities": ["text-generation"],
                    "created": int(datetime.now().timestamp()),
                    "pipeline_tag": "text-generation",
                },
                {
                    "id": "t5-small",
                    "name": "T5 Small",
                    "capabilities": [
                        "text2text-generation",
                        "summarization",
                        "translation",
                    ],
                    "created": int(datetime.now().timestamp()),
                    "pipeline_tag": "text2text-generation",
                },
                {
                    "id": "distilbert-base-uncased",
                    "name": "DistilBERT Base Uncased",
                    "capabilities": ["text-classification", "token-classification"],
                    "created": int(datetime.now().timestamp()),
                    "pipeline_tag": "text-classification",
                },
                {
                    "id": "all-MiniLM-L6-v2",
                    "name": "MiniLM L6 v2",
                    "capabilities": ["embedding", "sentence-similarity"],
                    "created": int(datetime.now().timestamp()),
                    "pipeline_tag": "feature-extraction",
                },
            ],
        )

        # Mock responses
        self.mock_responses = {
            "text_generation": {
                "generated_text": self.config.get(
                    "default_completion",
                    "This is a mock response from the Hugging Face model.",
                )
            },
            "text2text_generation": {
                "generated_text": self.config.get(
                    "default_completion", "This is a mock text2text response."
                )
            },
            "summarization": {
                "summary_text": self.config.get(
                    "default_summary", "This is a mock summary."
                )
            },
            "translation": {
                "translation_text": self.config.get(
                    "default_translation", "This is a mock translation."
                )
            },
            "text_classification": [
                {"label": "POSITIVE", "score": 0.95},
                {"label": "NEGATIVE", "score": 0.05},
            ],
            "token_classification": [
                {
                    "entity": "B-PER",
                    "score": 0.98,
                    "word": "John",
                    "start": 0,
                    "end": 4,
                },
                {"entity": "I-PER", "score": 0.92, "word": "Doe", "start": 5, "end": 8},
            ],
            "embeddings": np.random.rand(
                1, 384
            ).tolist(),  # Common embedding size for MiniLM
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        self.record_call("list_models")
        return self.available_models

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        self.record_call("get_model_info", model_id=model_id)

        # Find the model in available models
        for model in self.available_models:
            if model["id"] == model_id:
                return model

        return None

    def text_generation(
        self,
        model_id: str,
        text: str,
        max_length: int = 100,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate text with a text generation model."""
        self.record_call(
            "text_generation",
            model_id=model_id,
            text=text,
            max_length=max_length,
            temperature=temperature,
            **kwargs,
        )

        # Check if model exists and has text generation capability
        model_info = self.get_model_info(model_id)
        if not model_info or "text-generation" not in model_info.get(
            "capabilities", []
        ):
            raise ValueError(
                f"Model {model_id} not found or does not support text generation"
            )

        response = self.mock_responses["text_generation"].copy()

        # If a custom response is provided for this specific text, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in text:
                response["generated_text"] = custom_response
                break

        return [response]

    def text2text_generation(
        self, model_id: str, text: str, max_length: int = 100, **kwargs
    ) -> Dict[str, Any]:
        """Generate text from text with a text2text generation model."""
        self.record_call(
            "text2text_generation",
            model_id=model_id,
            text=text,
            max_length=max_length,
            **kwargs,
        )

        # Check if model exists and has text2text generation capability
        model_info = self.get_model_info(model_id)
        if not model_info or "text2text-generation" not in model_info.get(
            "capabilities", []
        ):
            raise ValueError(
                f"Model {model_id} not found or does not support text2text generation"
            )

        response = self.mock_responses["text2text_generation"].copy()

        # If a custom response is provided for this specific text, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in text:
                response["generated_text"] = custom_response
                break

        return [response]

    def summarization(
        self,
        model_id: str,
        text: str,
        max_length: int = 100,
        min_length: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a summary with a summarization model."""
        self.record_call(
            "summarization",
            model_id=model_id,
            text=text,
            max_length=max_length,
            min_length=min_length,
            **kwargs,
        )

        # Check if model exists and has summarization capability
        model_info = self.get_model_info(model_id)
        if not model_info or "summarization" not in model_info.get("capabilities", []):
            raise ValueError(
                f"Model {model_id} not found or does not support summarization"
            )

        response = self.mock_responses["summarization"].copy()

        # If a custom response is provided for this specific text, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in text:
                response["summary_text"] = custom_response
                break

        return [response]

    def translation(
        self,
        model_id: str,
        text: str,
        src_lang: str = "en",
        tgt_lang: str = "fr",
        **kwargs,
    ) -> Dict[str, Any]:
        """Translate text with a translation model."""
        self.record_call(
            "translation",
            model_id=model_id,
            text=text,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            **kwargs,
        )

        # Check if model exists and has translation capability
        model_info = self.get_model_info(model_id)
        if not model_info or "translation" not in model_info.get("capabilities", []):
            raise ValueError(
                f"Model {model_id} not found or does not support translation"
            )

        response = self.mock_responses["translation"].copy()

        # If a custom response is provided for this specific text, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in text:
                response["translation_text"] = custom_response
                break

        return [response]

    def text_classification(
        self, model_id: str, text: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """Classify text with a text classification model."""
        self.record_call("text_classification", model_id=model_id, text=text, **kwargs)

        # Check if model exists and has text classification capability
        model_info = self.get_model_info(model_id)
        if not model_info or "text-classification" not in model_info.get(
            "capabilities", []
        ):
            raise ValueError(
                f"Model {model_id} not found or does not support text classification"
            )

        response = self.mock_responses["text_classification"].copy()

        return response

    def token_classification(
        self, model_id: str, text: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """Classify tokens with a token classification model."""
        self.record_call("token_classification", model_id=model_id, text=text, **kwargs)

        # Check if model exists and has token classification capability
        model_info = self.get_model_info(model_id)
        if not model_info or "token-classification" not in model_info.get(
            "capabilities", []
        ):
            raise ValueError(
                f"Model {model_id} not found or does not support token classification"
            )

        response = self.mock_responses["token_classification"].copy()

        return response

    def embedding(
        self, model_id: str, text: Union[str, List[str]], **kwargs
    ) -> np.ndarray:
        """Generate embeddings with an embedding model."""
        self.record_call("embedding", model_id=model_id, text=text, **kwargs)

        # Check if model exists and has embedding capability
        model_info = self.get_model_info(model_id)
        if not model_info or "embedding" not in model_info.get("capabilities", []):
            raise ValueError(
                f"Model {model_id} not found or does not support embeddings"
            )

        # Get base embedding from mock responses
        base_embedding = np.array(self.mock_responses["embeddings"])

        # Handle list of inputs
        if isinstance(text, list):
            # Create slightly different embeddings for each text
            embeddings = []
            for i, t in enumerate(text):
                # Add a small offset based on the index for deterministic but different vectors
                offset = (
                    np.random.RandomState(hash(t) % 2**32).rand(*base_embedding.shape)
                    * 0.1
                )
                embeddings.append(base_embedding + offset)
            return np.vstack(embeddings)
        else:
            # Add a small random offset for determinism based on text hash
            offset = (
                np.random.RandomState(hash(text) % 2**32).rand(*base_embedding.shape)
                * 0.1
            )
            return base_embedding + offset


class MockLocalModelProvider(MockBaseModelProvider):
    """Mock implementation of local model inference (like llama.cpp)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock Local Model provider."""
        super().__init__(config)

        # Override available models
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "llama-2-7b-chat.ggu",
                    "name": "Llama 2 7B Chat",
                    "capabilities": ["text-generation", "chat"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/llama-2-7b-chat.ggu",
                    "size_mb": 3900,
                    "format": "ggu",
                    "quantization": "q4_k_m",
                },
                {
                    "id": "llama-3-8b-instruct.ggu",
                    "name": "Llama 3 8B Instruct",
                    "capabilities": ["text-generation", "chat"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/llama-3-8b-instruct.ggu",
                    "size_mb": 4200,
                    "format": "ggu",
                    "quantization": "q5_k_m",
                },
                {
                    "id": "mistral-7b-instruct-v0.2.Q4_K_M.ggu",
                    "name": "Mistral 7B Instruct",
                    "capabilities": ["text-generation", "chat"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/mistral-7b-instruct-v0.2.Q4_K_M.ggu",
                    "size_mb": 3800,
                    "format": "ggu",
                    "quantization": "q4_k_m",
                },
                {
                    "id": "phi-2.Q4_K_M.ggu",
                    "name": "Phi-2",
                    "capabilities": ["text-generation"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/phi-2.Q4_K_M.ggu",
                    "size_mb": 1700,
                    "format": "ggu",
                    "quantization": "q4_k_m",
                },
            ],
        )

        # Mock responses
        self.mock_responses = {
            "completion": {
                "text": self.config.get(
                    "default_completion",
                    "This is a mock response from the local GGUF model.",
                ),
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                },
                "timings": {"prompt_ms": 100, "completion_ms": 500},
            },
            "embeddings": {
                "embedding": list(
                    np.random.rand(4096)
                ),  # Common size for GGUF embeddings
                "usage": {"prompt_tokens": 8, "total_tokens": 8},
            },
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        self.record_call("list_models")
        return self.available_models

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        self.record_call("get_model_info", model_id=model_id)

        # Find the model in available models
        for model in self.available_models:
            if model["id"] == model_id:
                return model

        return None

    def generate_completion(
        self,
        model_id: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Generate a completion from a GGUF model."""
        self.record_call(
            "generate_completion",
            model_id=model_id,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        # Check if model exists
        if not any(m["id"] == model_id for m in self.available_models):
            raise ValueError(f"Model {model_id} not found")

        response = self.mock_responses["completion"].copy()

        # If a custom response is provided for this specific prompt, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in prompt:
                response["text"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["text"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    chunk = {"text": word + " "}
                    if i == len(words) - 1:
                        chunk["stop"] = True
                    yield chunk

            return generate_stream()

        return response

    def generate_chat_completion(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Generate a chat completion from a GGUF model."""
        self.record_call(
            "generate_chat_completion",
            model_id=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        # Check if model exists and has chat capability
        model_info = self.get_model_info(model_id)
        if not model_info or "chat" not in model_info.get("capabilities", []):
            raise ValueError(f"Model {model_id} not found or does not support chat")

        response = self.mock_responses["completion"].copy()

        # Extract the user's message for matching custom responses
        user_message = ""
        for message in messages:
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break

        # If a custom response is provided for this specific message, use it
        custom_responses = self.config.get("custom_responses", {})
        for pattern, custom_response in custom_responses.items():
            if pattern in user_message:
                response["text"] = custom_response
                break

        # Simulate streaming if requested
        if stream:

            def generate_stream():
                text = response["text"]
                # Split into words and yield one at a time
                words = text.split()
                for i, word in enumerate(words):
                    chunk = {"text": word + " "}
                    if i == len(words) - 1:
                        chunk["stop"] = True
                    yield chunk

            return generate_stream()

        return response


class MockONNXProvider(MockBaseModelProvider):
    """Mock implementation of ONNX model inference."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock ONNX provider."""
        super().__init__(config)

        # Override available models
        self.available_models = self.config.get(
            "available_models",
            [
                {
                    "id": "bert-base-onnx",
                    "name": "BERT Base ONNX",
                    "capabilities": ["text-classification", "feature-extraction"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/bert-base.onnx",
                },
                {
                    "id": "resnet50-onnx",
                    "name": "ResNet 50 ONNX",
                    "capabilities": ["image-classification"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/resnet50.onnx",
                },
                {
                    "id": "gpt2-onnx",
                    "name": "GPT-2 ONNX",
                    "capabilities": ["text-generation"],
                    "created": int(datetime.now().timestamp()),
                    "path": "/path/to/gpt2.onnx",
                },
            ],
        )

        # Mock responses
        self.mock_responses = {
            "text_classification": {
                "label_scores": [["positive", 0.95], ["negative", 0.05]]
            },
            "feature_extraction": {
                "features": list(np.random.rand(768))  # BERT hidden size
            },
            "image_classification": {
                "label_scores": [["cat", 0.8], ["dog", 0.15], ["bird", 0.05]]
            },
            "text_generation": {
                "generated_text": self.config.get(
                    "default_completion", "This is a mock response from the ONNX model."
                )
            },
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        self.record_call("list_models")
        return self.available_models

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        self.record_call("get_model_info", model_id=model_id)

        # Find the model in available models
        for model in self.available_models:
            if model["id"] == model_id:
                return model

        return None

    def run_inference(
        self, model_id: str, inputs: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Run inference with an ONNX model."""
        self.record_call("run_inference", model_id=model_id, inputs=inputs, **kwargs)

        # Check if model exists
        model_info = self.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found")

        # Get capabilities
        capabilities = model_info.get("capabilities", [])

        if "text-classification" in capabilities:
            return self.mock_responses["text_classification"].copy()
        elif "feature-extraction" in capabilities:
            return self.mock_responses["feature_extraction"].copy()
        elif "image-classification" in capabilities:
            return self.mock_responses["image_classification"].copy()
        elif "text-generation" in capabilities:
            return self.mock_responses["text_generation"].copy()
        else:
            raise ValueError(f"Unsupported capability for model {model_id}")


# Helper function to create the appropriate mock provider
def create_mock_provider(
    provider_type: str, config: Optional[Dict[str, Any]] = None
) -> Union[
    MockOpenAIProvider,
    MockOllamaProvider,
    MockLMStudioProvider,
    MockHuggingFaceProvider,
    MockLocalModelProvider,
    MockONNXProvider,
]:
    """
    Create a mock provider of the specified type.

    Args:
        provider_type: Type of provider to create
        config: Optional configuration for the provider

    Returns:
        A mock provider instance
    """
    providers = {
        "openai": MockOpenAIProvider,
        "ollama": MockOllamaProvider,
        "lmstudio": MockLMStudioProvider,
        "huggingface": MockHuggingFaceProvider,
        "local": MockLocalModelProvider,
        "onnx": MockONNXProvider,
    }

    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider type: {provider_type}")

    return provider_class(config)