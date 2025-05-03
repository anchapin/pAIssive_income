"""
Test fixtures for common testing scenarios.

This module provides pytest fixtures for common testing scenarios,
making it easier to use mocks consistently across tests.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from .mock_external_apis import (
    MockEmailAPI,
    MockHuggingFaceAPI,
    MockPaymentAPI,
    MockStorageAPI,
    create_mock_api,
)
from .mock_http import MockResponse, mock_requests
from .mock_huggingface_hub import HfHubHTTPError, MockRepoInfo, mock_huggingface_hub

# Import our mock implementations
from .mock_model_providers import (
    MockHuggingFaceProvider,
    MockLMStudioProvider,
    MockLocalModelProvider,
    MockOllamaProvider,
    MockONNXProvider,
    MockOpenAIProvider,
    create_mock_provider,
)

# Model Provider Fixtures


@pytest.fixture
def mock_openai_provider(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock OpenAI provider for testing.

    Args:
        config: Optional configuration for the mock provider

    Returns:
        A mock OpenAI provider instance
    """
    return MockOpenAIProvider(config)


@pytest.fixture
def mock_ollama_provider(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock Ollama provider for testing.

    Args:
        config: Optional configuration for the mock provider

    Returns:
        A mock Ollama provider instance
    """
    return MockOllamaProvider(config)


@pytest.fixture
def mock_lmstudio_provider(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock LM Studio provider for testing.

    Args:
        config: Optional configuration for the mock provider

    Returns:
        A mock LM Studio provider instance
    """
    return MockLMStudioProvider(config)


@pytest.fixture
def mock_huggingface_provider(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock Hugging Face provider for testing.

    Args:
        config: Optional configuration for the mock provider

    Returns:
        A mock Hugging Face provider instance
    """
    return MockHuggingFaceProvider(config)


@pytest.fixture
def mock_local_model_provider(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock local model provider (like llama.cpp) for testing.

    Args:
        config: Optional configuration for the mock provider

    Returns:
        A mock local model provider instance
    """
    return MockLocalModelProvider(config)


@pytest.fixture
def mock_onnx_provider(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock ONNX model provider for testing.

    Args:
        config: Optional configuration for the mock provider

    Returns:
        A mock ONNX provider instance
    """
    return MockONNXProvider(config)


@pytest.fixture
def patch_model_providers(monkeypatch):
    """
    Patch all model providers with mock implementations.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        A dictionary of mock provider instances
    """
    mock_providers = {
        "openai": MockOpenAIProvider(),
        "ollama": MockOllamaProvider(),
        "lmstudio": MockLMStudioProvider(),
        "huggingface": MockHuggingFaceProvider(),
        "local": MockLocalModelProvider(),
        "onnx": MockONNXProvider(),
    }

    # Define a function to return the appropriate mock provider
    def mock_get_model_provider(provider_type, *args, **kwargs):
        return mock_providers.get(provider_type.lower(), mock_providers["openai"])

    # Apply the patch to adapters
    try:
        monkeypatch.setattr(
            "ai_models.adapters.adapter_factory.adapter_factory.create_adapter",
            mock_get_model_provider,
        )
    except (ImportError, AttributeError):
        pass

    return mock_providers


# HTTP and External API Fixtures


@pytest.fixture
def mock_http():
    """
    Create a mock HTTP requests interface for testing.

    Returns:
        A mock requests interface instance
    """
    mock_requests.reset()
    return mock_requests


@pytest.fixture
def mock_http_with_common_responses():
    """
    Create a mock HTTP requests interface with common API responses pre - configured.

    Returns:
        A mock requests interface instance with common responses
    """
    mock_requests.reset()

    # Add mock response for OpenAI API
    mock_requests.add_response(
        "https://api.openai.com / v1 / chat / completions",
        {
            "id": "chatcmpl - 123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt - 3.5 - turbo - 0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from the AI.",
                    },
                    "finish_reason": "stop",
                }
            ],
        },
        method="POST",
    )

    mock_requests.add_response(
        "https://api.openai.com / v1 / embeddings",
        {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    "index": 0,
                }
            ],
            "model": "text - embedding - ada - 002",
            "usage": {"prompt_tokens": 8, "total_tokens": 8},
        },
        method="POST",
    )

    # Add mock response for Ollama API
    mock_requests.add_response(
        "http://localhost:11434 / api / generate",
        {
            "model": "llama2",
            "created_at": "2023 - 01 - 01T00:00:00Z",
            "response": "This is a mock response from Ollama.",
            "done": True,
        },
        method="POST",
    )

    mock_requests.add_response(
        "http://localhost:11434 / api / chat",
        {
            "model": "llama2",
            "created_at": "2023 - 01 - 01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "This is a mock chat response from Ollama.",
            },
            "done": True,
        },
        method="POST",
    )

    # Add mock response for LM Studio API
    mock_requests.add_response(
        "http://localhost:1234 / v1 / chat / completions",
        {
            "id": "chatcmpl - lmstudio",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "local - model",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from LM Studio.",
                    },
                    "finish_reason": "stop",
                }
            ],
        },
        method="POST",
    )

    return mock_requests


@pytest.fixture
def patch_requests(monkeypatch):
    """
    Patch the requests library with our mock implementation.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        The mock requests object
    """
    # Reset the mock requests
    mock_requests.reset()

    # Patch all the commonly used requests functions
    monkeypatch.setattr("requests.get", mock_requests.get)
    monkeypatch.setattr("requests.post", mock_requests.post)
    monkeypatch.setattr("requests.put", mock_requests.put)
    monkeypatch.setattr("requests.delete", mock_requests.delete)
    monkeypatch.setattr("requests.patch", mock_requests.patch)
    monkeypatch.setattr("requests.head", mock_requests.head)
    monkeypatch.setattr("requests.options", mock_requests.options)
    monkeypatch.setattr("requests.request", mock_requests.request)
    monkeypatch.setattr("requests.session", mock_requests.session)

    return mock_requests


@pytest.fixture
def mock_hf_hub():
    """
    Create a mock Hugging Face Hub instance for testing.

    Returns:
        A mock Hugging Face Hub instance
    """
    mock_huggingface_hub.reset()
    return mock_huggingface_hub


@pytest.fixture
def mock_hf_hub_with_models():
    """
    Create a mock Hugging Face Hub instance with common models pre - configured.

    Returns:
        A mock Hugging Face Hub instance with common models
    """
    mock_huggingface_hub.reset()

    # Add common repositories
    mock_huggingface_hub.add_repo(
        {
            "id": "gpt2",
            "downloads": 1000000,
            "likes": 5000,
            "tags": ["text - generation", "pytorch"],
            "pipeline_tag": "text - generation",
        }
    )

    mock_huggingface_hub.add_repo(
        {
            "id": "sentence - transformers / all - MiniLM - L6 - v2",
            "downloads": 500000,
            "likes": 2000,
            "tags": ["sentence - similarity", "pytorch"],
            "pipeline_tag": "feature - extraction",
        }
    )

    mock_huggingface_hub.add_repo(
        {
            "id": "mistralai / Mistral - 7B - v0.1",
            "downloads": 800000,
            "likes": 3000,
            "tags": ["text - generation", "pytorch"],
            "pipeline_tag": "text - generation",
        }
    )

    mock_huggingface_hub.add_repo(
        {
            "id": "bert - base - uncased",
            "downloads": 900000,
            "likes": 4000,
            "tags": ["fill - mask", "pytorch"],
            "pipeline_tag": "fill - mask",
        }
    )

    # Add common files
    import json

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
        repo_id="bert - base - uncased",
        file_path="config.json",
        content=json.dumps(
            {
                "model_type": "bert",
                "hidden_size": 768,
                "num_attention_heads": 12,
                "num_hidden_layers": 12,
            }
        ),
    )

    mock_huggingface_hub.add_file(
        repo_id="sentence - transformers / all - MiniLM - L6 - v2",
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

    return mock_huggingface_hub


@pytest.fixture
def patch_huggingface_hub(monkeypatch):
    """
    Patch the huggingface_hub library with our mock implementation.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        The mock huggingface_hub object
    """
    # Reset the mock huggingface_hub
    mock_huggingface_hub.reset()

    # Patch the huggingface_hub functions
    monkeypatch.setattr("huggingface_hub.hf_hub_download", mock_huggingface_hub.hf_hub_download)
    monkeypatch.setattr("huggingface_hub.snapshot_download", mock_huggingface_hub.snapshot_download)
    monkeypatch.setattr("huggingface_hub.list_models", mock_huggingface_hub.list_models)
    monkeypatch.setattr("huggingface_hub.login", mock_huggingface_hub.login)

    # Patch the HfHubHTTPError exception
    monkeypatch.setattr("huggingface_hub.utils.HfHubHTTPError", HfHubHTTPError)

    return mock_huggingface_hub


@pytest.fixture
def mock_huggingface_api(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock Hugging Face API for testing.

    Args:
        config: Optional configuration for the mock API

    Returns:
        A mock Hugging Face API instance
    """
    return MockHuggingFaceAPI(config)


@pytest.fixture
def mock_payment_api(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock payment API for testing.

    Args:
        config: Optional configuration for the mock API

    Returns:
        A mock payment API instance
    """
    return MockPaymentAPI(config)


@pytest.fixture
def mock_email_api(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock email API for testing.

    Args:
        config: Optional configuration for the mock API

    Returns:
        A mock email API instance
    """
    return MockEmailAPI(config)


@pytest.fixture
def mock_storage_api(config: Optional[Dict[str, Any]] = None):
    """
    Create a mock storage API for testing.

    Args:
        config: Optional configuration for the mock API

    Returns:
        A mock storage API instance
    """
    return MockStorageAPI(config)


@pytest.fixture
def patch_external_apis(monkeypatch):
    """
    Patch all external APIs with mock implementations.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        A dictionary of mock API instances
    """
    mock_apis = {
        "huggingface": MockHuggingFaceAPI(),
        "payment": MockPaymentAPI(),
        "email": MockEmailAPI(),
        "storage": MockStorageAPI(),
    }

    # Patch HuggingFace Hub if available
    try:
        monkeypatch.setattr("huggingface_hub.HfApi", lambda: mock_apis["huggingface"])
        monkeypatch.setattr(
            "huggingface_hub.hf_hub_download",
            lambda model_id, *args, **kwargs: mock_apis["huggingface"].download_model(
                model_id, "mock_path"
            ),
        )
    except (ImportError, AttributeError):
        pass

    # Patch other external APIs based on project structure
    # These paths would need to be adjusted based on the actual project structure
    try:
        # Example patches for payment processing
        monkeypatch.setattr(
            "monetization.payment_method_manager.create_payment_client",
            lambda *args, **kwargs: mock_apis["payment"],
        )

        # Example patches for email services
        monkeypatch.setattr(
            "marketing.content_generators.get_email_client",
            lambda *args, **kwargs: mock_apis["email"],
        )
    except (ImportError, AttributeError):
        pass

    return mock_apis


# Common Test Scenario Fixtures


@pytest.fixture
def mock_model_inference_result():
    """
    Create a mock model inference result.

    Returns:
        A dictionary representing a model inference result
    """
    return {
        "id": f"result_{int(datetime.now().timestamp())}",
        "model": "test - model",
        "choices": [
            {
                "text": "This is a mock model response for testing purposes.",
                "index": 0,
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "created": int(datetime.now().timestamp()),
    }


@pytest.fixture
def mock_chat_completion_result():
    """
    Create a mock chat completion result.

    Returns:
        A dictionary representing a chat completion result
    """
    return {
        "id": f"chatcmpl_{int(datetime.now().timestamp())}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": "test - chat - model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a mock response from the chat model.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
    }


@pytest.fixture
def mock_embedding_result():
    """
    Create a mock embedding result.

    Returns:
        A dictionary representing an embedding result
    """
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                "index": 0,
            }
        ],
        "model": "text - embedding - model",
        "usage": {"prompt_tokens": 8, "total_tokens": 8},
    }


@pytest.fixture
def mock_subscription_data():
    """
    Create mock subscription data.

    Returns:
        A dictionary representing subscription data
    """
    now = datetime.now()
    timestamp = int(now.timestamp())

    return {
        "customer": {
            "id": f"cus_test_{timestamp}",
            "email": "test @ example.com",
            "name": "Test User",
            "created": timestamp,
            "metadata": {"user_id": "user_123"},
        },
        "subscription": {
            "id": f"sub_test_{timestamp}",
            "status": "active",
            "plan": {
                "id": "premium - monthly",
                "name": "Premium Monthly",
                "amount": 1999,
                "currency": "usd",
                "interval": "month",
            },
            "current_period_start": timestamp,
            "current_period_end": timestamp + (30 * 24 * 60 * 60),  # 30 days later
            "created": timestamp,
        },
        "payment_method": {
            "id": f"pm_test_{timestamp}",
            "type": "credit_card",
            "last4": "4242",
            "exp_month": 12,
            "exp_year": 2025,
            "brand": "visa",
        },
    }


@pytest.fixture
def mock_niche_analysis_data():
    """
    Create mock niche analysis data.

    Returns:
        A dictionary representing niche analysis results
    """
    return {
        "niches": [
            {
                "name": "AI Productivity Tools",
                "opportunity_score": 85.3,
                "market_size": "Large",
                "competition_level": "Medium",
                "growth_trend": "Increasing",
                "challenges": [
                    "Integration with existing workflows",
                    "Privacy concerns",
                    "Technical complexity",
                ],
                "target_audience": ["Knowledge workers", "Small businesses", "Freelancers"],
            },
            {
                "name": "Content Creator Automation",
                "opportunity_score": 79.2,
                "market_size": "Medium",
                "competition_level": "Low",
                "growth_trend": "Rapidly increasing",
                "challenges": ["Quality control", "Customization needs", "Ethical considerations"],
                "target_audience": ["YouTubers", "Bloggers", "Social media influencers"],
            },
            {
                "name": "AI - powered Personal Finance",
                "opportunity_score": 73.8,
                "market_size": "Medium",
                "competition_level": "Medium - high",
                "growth_trend": "Steady increase",
                "challenges": ["Regulatory compliance", "Data security", "Trust building"],
                "target_audience": [
                    "Young professionals",
                    "Financial enthusiasts",
                    "Small business owners",
                ],
            },
        ],
        "analysis_summary": "The AI tools market shows significant growth potential across multiple niches. The highest opportunity scores are in productivity tools, content creation, and personal finance applications. Each niche presents unique challenges but also substantial monetization potential.",
        "recommended_focus": "AI Productivity Tools",
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def mock_marketing_campaign_data():
    """
    Create mock marketing campaign data.

    Returns:
        A dictionary representing marketing campaign data
    """
    return {
        "campaign_name": "Spring Product Launch",
        "target_audience": [
            {
                "name": "Tech - savvy Professionals",
                "demographics": {
                    "age_range": "25 - 45",
                    "education": "College degree or higher",
                    "income": "Above average",
                },
                "pain_points": [
                    "Limited time for repetitive tasks",
                    "Need for better organization",
                    "Information overload",
                ],
                "goals": ["Increase productivity", "Streamline workflows", "Reduce stress"],
            }
        ],
        "channels": [
            {
                "name": "Email",
                "content_types": ["Product announcement", "Tutorial series", "Case studies"],
                "frequency": "Weekly",
                "performance_metrics": {
                    "open_rate": 0.25,
                    "click_rate": 0.08,
                    "conversion_rate": 0.02,
                },
            },
            {
                "name": "Social Media",
                "platforms": ["Twitter", "LinkedIn", "Instagram"],
                "content_types": ["Feature highlights", "User testimonials", "Tips and tricks"],
                "frequency": "Daily",
                "performance_metrics": {
                    "engagement_rate": 0.04,
                    "share_rate": 0.01,
                    "conversion_rate": 0.015,
                },
            },
        ],
        "content_calendar": [
            {
                "date": (datetime.now().replace(day=1) + timedelta(days=7)).strftime(" % Y-%m-%d"),
                "channel": "Email",
                "title": "Introducing Our New AI - Powered Feature",
                "content_type": "Product announcement",
                "status": "Draft",
            },
            {
                "date": (datetime.now().replace(day=1) + timedelta(days=9)).strftime(" % Y-%m-%d"),
                "channel": "LinkedIn",
                "title": "How Our Tool Saved Client X 10 Hours Per Week",
                "content_type": "Case study",
                "status": "Planned",
            },
        ],
    }


# Complete Test Scenario Fixtures


@pytest.fixture
def mock_ai_model_testing_setup(patch_requests, patch_huggingface_hub, patch_model_providers):
    """
    Create a complete setup for AI model testing.

    This fixture combines multiple fixtures to create a comprehensive
    testing environment for AI model integrations.

    Args:
        patch_requests: The patched requests library
        patch_huggingface_hub: The patched huggingface_hub library
        patch_model_providers: The patched model providers

    Returns:
        A dictionary containing all the mock objects
    """
    # Set up mock HTTP responses
    patch_requests.add_response(
        "https://api.openai.com / v1 / chat / completions",
        {
            "id": "chatcmpl - 123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt - 3.5 - turbo - 0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from the AI model testing environment.",
                    },
                    "finish_reason": "stop",
                }
            ],
        },
        method="POST",
    )

    # Set up mock Hugging Face models
    patch_huggingface_hub.add_repo({"id": "gpt2", "pipeline_tag": "text - generation"})

    patch_huggingface_hub.add_file(
        repo_id="gpt2", file_path="config.json", content='{"model_type": "gpt2"}'
    )

    # Create a temporary directory for file operations
    temp_dir = tempfile.mkdtemp(prefix="ai_model_test_")

    # Add generate method to model providers
    for provider_name, provider in patch_model_providers.items():
        if not hasattr(provider, "generate"):
            provider.generate = (
                lambda text, **kwargs: "This is a mock response generated for: " + text
            )

    return {
        "http": patch_requests,
        "huggingface_hub": patch_huggingface_hub,
        "model_providers": patch_model_providers,
        "temp_dir": temp_dir,
    }


@pytest.fixture
def mock_monetization_testing_setup(patch_requests, mock_subscription_data):
    """
    Create a complete setup for monetization testing.

    This fixture provides a comprehensive testing environment
    for monetization - related functionality.

    Args:
        patch_requests: The patched requests library
        mock_subscription_data: Mock subscription data

    Returns:
        A dictionary containing all the mock objects
    """
    # Set up mock payment gateway responses
    patch_requests.add_response(
        "https://api.stripe.com / v1 / customers",
        {
            "id": mock_subscription_data["customer"]["id"],
            "email": mock_subscription_data["customer"]["email"],
            "name": mock_subscription_data["customer"]["name"],
            "created": mock_subscription_data["customer"]["created"],
        },
        method="POST",
        status_code=200,
    )

    patch_requests.add_response(
        "https://api.stripe.com / v1 / subscriptions",
        {
            "id": mock_subscription_data["subscription"]["id"],
            "status": mock_subscription_data["subscription"]["status"],
            "current_period_start": mock_subscription_data["subscription"]["current_period_start"],
            "current_period_end": mock_subscription_data["subscription"]["current_period_end"],
        },
        method="POST",
        status_code=200,
    )

    # Create a temporary directory for file operations
    temp_dir = tempfile.mkdtemp(prefix="monetization_test_")

    # Create mock database
    mock_db = {
        "customers": [mock_subscription_data["customer"]],
        "subscriptions": [mock_subscription_data["subscription"]],
        "payment_methods": [mock_subscription_data["payment_method"]],
        "invoices": [],
    }

    return {
        "http": patch_requests,
        "temp_dir": temp_dir,
        "mock_db": mock_db,
        "subscription_data": mock_subscription_data,
    }


@pytest.fixture
def mock_marketing_testing_setup(patch_requests, mock_marketing_campaign_data):
    """
    Create a complete setup for marketing testing.

    This fixture provides a comprehensive testing environment
    for marketing - related functionality.

    Args:
        patch_requests: The patched requests library
        mock_marketing_campaign_data: Mock marketing campaign data

    Returns:
        A dictionary containing all the mock objects
    """
    # Set up mock email API responses
    patch_requests.add_response(
        "https://api.sendgrid.com / v3 / mail / send",
        {"message": "Email sent successfully"},
        method="POST",
        status_code=202,
    )

    # Set up mock social media API responses
    patch_requests.add_response(
        "https://api.twitter.com / 2/tweets",
        {"data": {"id": "1234567890", "text": "Test tweet"}},
        method="POST",
        status_code=201,
    )

    patch_requests.add_response(
        "https://api.linkedin.com / v2 / ugcPosts",
        {"id": "urn:li:share:1234567890"},
        method="POST",
        status_code=201,
    )

    # Create a temporary directory for file operations
    temp_dir = tempfile.mkdtemp(prefix="marketing_test_")

    return {
        "http": patch_requests,
        "temp_dir": temp_dir,
        "campaign_data": mock_marketing_campaign_data,
    }


@pytest.fixture
def mock_niche_analysis_testing_setup(patch_model_providers, mock_niche_analysis_data):
    """
    Create a complete setup for niche analysis testing.

    This fixture provides a comprehensive testing environment
    for niche analysis - related functionality.

    Args:
        patch_model_providers: The patched model providers
        mock_niche_analysis_data: Mock niche analysis data

    Returns:
        A dictionary containing all the mock objects
    """
    # Configure the OpenAI provider to return appropriate responses
    openai_provider = patch_model_providers["openai"]

    # Set up custom responses for different prompts
    openai_provider.config["custom_responses"] = {
        "identify niches": json.dumps(mock_niche_analysis_data["niches"]),
        "analyze market": "The market shows significant growth potential.",
        "competition analysis": "The competition level varies by niche.",
        "target audience": "The primary target audience consists of knowledge workers and small businesses.",
        "analyze market trends": "Market analysis shows positive growth trends in AI inventory management.",
        "identify target audience": "The target audience is primarily e - commerce businesses and retail chains.",
        "evaluate competition": "Competition analysis reveals 3 major competitors with basic AI features.",
    }

    # Add generate method to model providers if not already present
    for provider_name, provider in patch_model_providers.items():
        if not hasattr(provider, "generate"):
            provider.generate = lambda text, **kwargs: f"This is a mock response for: {text}"

    # Create a temporary directory for file operations
    temp_dir = tempfile.mkdtemp(prefix="niche_analysis_test_")

    return {
        "model_providers": patch_model_providers,
        "temp_dir": temp_dir,
        "niche_data": mock_niche_analysis_data,
    }
