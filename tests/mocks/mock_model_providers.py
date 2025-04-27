"""
Mock implementations of AI model providers for testing.

This module provides mock implementations of various AI model providers
that can be used for consistent testing without external dependencies.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Generator
from unittest.mock import MagicMock
from datetime import datetime

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
        self.available_models = self.config.get("available_models", [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "capabilities": ["text-generation", "chat"],
                "created": int(datetime.now().timestamp()),
                "owned_by": "mock-provider"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "capabilities": ["text-generation", "chat"],
                "created": int(datetime.now().timestamp()),
                "owned_by": "mock-provider" 
            },
            {
                "id": "dall-e-3",
                "name": "DALL-E 3",
                "capabilities": ["image-generation"],
                "created": int(datetime.now().timestamp()),
                "owned_by": "mock-provider"
            },
            {
                "id": "text-embedding-ada-002",
                "name": "Text Embedding Ada 002",
                "capabilities": ["embeddings"],
                "created": int(datetime.now().timestamp()),
                "owned_by": "mock-provider"
            }
        ])
        
        # Set up success rates
        self.success_rate = self.config.get("success_rate", 0.95)
        self.latency_range = self.config.get("latency_range", (100, 500))  # ms
        self.error_messages = self.config.get("error_messages", {
            "rate_limit": "Rate limit exceeded. Please try again later.",
            "invalid_model": "The model does not exist or you don't have access to it.",
            "invalid_request": "The request is not valid for this model.",
            "context_length": "The context length exceeds the model's limit."
        })
        
        # Track call history for assertions
        self.call_history = []
    
    def record_call(self, method_name: str, **kwargs):
        """Record a method call for testing assertions."""
        self.call_history.append({
            "method": method_name,
            "timestamp": datetime.now().isoformat(),
            "args": kwargs
        })
    
    def get_call_history(self, method_name: Optional[str] = None) -> List[Dict[str, Any]]:
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
                            "content": self.config.get("default_completion", "This is a mock response from the AI model.")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                }
            },
            "text_completion": {
                "id": "cmpl-mock-id",
                "object": "text_completion",
                "created": int(datetime.now().timestamp()),
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "text": self.config.get("default_completion", "This is a mock response from the AI model."),
                        "index": 0,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 15,
                    "total_tokens": 25
                }
            },
            "embeddings": {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                        "index": 0
                    }
                ],
                "model": "text-embedding-ada-002",
                "usage": {
                    "prompt_tokens": 8,
                    "total_tokens": 8
                }
            },
            "images": {
                "created": int(datetime.now().timestamp()),
                "data": [
                    {
                        "url": "https://mock-url.com/image.png",
                        "b64_json": None
                    }
                ]
            }
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
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a text completion."""
        self.record_call(
            "create_completion",
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
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
                                "finish_reason": "stop" if i == len(words) - 1 else None
                            }
                        ]
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
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a chat completion."""
        self.record_call(
            "create_chat_completion",
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
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
                                "delta": {
                                    "content": word + " "
                                },
                                "finish_reason": "stop" if i == len(words) - 1 else None
                            }
                        ]
                    }
            
            return generate_stream()
        
        return response
    
    def create_embedding(
        self,
        model: str,
        input: Union[str, List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Create embeddings for the given input."""
        self.record_call(
            "create_embedding",
            model=model,
            input=input,
            **kwargs
        )
        
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
                response["data"].append({
                    "object": "embedding",
                    # Generate deterministic but different vectors for different inputs
                    "embedding": [0.1 * (i + 1) + 0.01 * j for j in range(10)],
                    "index": i
                })
            response["usage"]["prompt_tokens"] = sum(len(text.split()) for text in input)
            response["usage"]["total_tokens"] = response["usage"]["prompt_tokens"]
        
        return response
    
    def create_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Create images from a prompt."""
        self.record_call(
            "create_image",
            prompt=prompt,
            model=model,
            size=size,
            n=n,
            **kwargs
        )
        
        # Use DALL-E 3 as default model if none specified
        model = model or "dall-e-3"
        
        # Check if model exists and has image generation capability
        model_info = self.get_model_info(model)
        if not model_info or "image-generation" not in model_info.get("capabilities", []):
            raise ValueError(self.error_messages["invalid_model"])
        
        response = self.mock_responses["images"].copy()
        
        # Generate multiple images if requested
        if n > 1:
            response["data"] = []
            for i in range(n):
                response["data"].append({
                    "url": f"https://mock-url.com/image_{i}.png",
                    "b64_json": None
                })
        
        return response


class MockOllamaProvider(MockBaseModelProvider):
    """Mock implementation of Ollama API."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock Ollama provider."""
        super().__init__(config)
        
        # Override available models for Ollama
        self.available_models = self.config.get("available_models", [
            {
                "id": "llama2",
                "name": "Llama 2",
                "capabilities": ["text-generation", "chat"],
                "modified_at": datetime.now().isoformat(),
                "size": 3791730293
            },
            {
                "id": "llama2:13b",
                "name": "Llama 2 13B",
                "capabilities": ["text-generation", "chat"],
                "modified_at": datetime.now().isoformat(),
                "size": 7323315540
            },
            {
                "id": "mistral",
                "name": "Mistral 7B",
                "capabilities": ["text-generation", "chat"],
                "modified_at": datetime.now().isoformat(),
                "size": 4032639651
            }
        ])
        
        # Mock responses
        self.mock_responses = {
            "completion": {
                "model": "llama2",
                "created_at": datetime.now().isoformat(),
                "response": self.config.get("default_completion", "This is a mock response from the Ollama model."),
                "done": True,
                "context": [1, 2, 3, 4, 5],
                "total_duration": 635163166,
                "load_duration": 1795833,
                "prompt_eval_duration": 129356000,
                "eval_count": 114,
                "eval_duration": 504010000
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
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Generate a completion from the model."""
        self.record_call(
            "generate",
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
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
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Generate a chat completion from the model."""
        self.record_call(
            "chat",
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
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
        self.available_models = self.config.get("available_models", [
            {
                "id": "local-model",
                "name": "Local Model",
                "capabilities": ["text-generation", "chat"],
                "created": int(datetime.now().timestamp()),
                "owned_by": "user"
            }
        ])
        
        # Mock responses - LM Studio uses OpenAI compatible API
        self.mock_responses = {
            "completion": {
                "id": "cmpl-lmstudio-mock",
                "object": "text_completion",
                "created": int(datetime.now().timestamp()),
                "model": "local-model",
                "choices": [
                    {
                        "text": self.config.get("default_completion", "This is a mock response from LM Studio."),
                        "index": 0,
                        "finish_reason": "stop"
                    }
                ]
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
                            "content": self.config.get("default_completion", "This is a mock response from LM Studio.")
                        },
                        "finish_reason": "stop"
                    }
                ]
            }
        }
    
    def list_models(self) -> Dict[str, Any]:
        """List available models."""
        self.record_call("list_models")
        return {
            "data": self.available_models,
            "object": "list"
        }
    
    def create_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a text completion."""
        self.record_call(
            "create_completion",
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
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
                                "finish_reason": "stop" if i == len(words) - 1 else None
                            }
                        ]
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
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Create a chat completion."""
        self.record_call(
            "create_chat_completion",
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
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
                                "delta": {
                                    "content": word + " "
                                },
                                "finish_reason": "stop" if i == len(words) - 1 else None
                            }
                        ]
                    }
            
            return generate_stream()
        
        return response


# Helper function to create the appropriate mock provider
def create_mock_provider(provider_type: str, config: Optional[Dict[str, Any]] = None) -> Union[MockOpenAIProvider, MockOllamaProvider, MockLMStudioProvider]:
    """
    Create a mock provider of the specified type.
    
    Args:
        provider_type: Type of provider to create ("openai", "ollama", or "lmstudio")
        config: Optional configuration for the provider
        
    Returns:
        A mock provider instance
    """
    providers = {
        "openai": MockOpenAIProvider,
        "ollama": MockOllamaProvider,
        "lmstudio": MockLMStudioProvider
    }
    
    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return provider_class(config)