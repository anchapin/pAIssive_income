"""
Test fixtures for common testing scenarios.

This module provides pytest fixtures for common testing scenarios,
making it easier to use mocks consistently across tests.
"""

import os
import pytest
from typing import Dict, Any, Optional
from unittest.mock import MagicMock, patch
from datetime import datetime

from .mock_model_providers import (
    MockOpenAIProvider,
    MockOllamaProvider,
    MockLMStudioProvider,
    create_mock_provider
)

from .mock_external_apis import (
    MockHuggingFaceAPI, 
    MockPaymentAPI,
    MockEmailAPI,
    MockStorageAPI,
    create_mock_api
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
        "lmstudio": MockLMStudioProvider()
    }
    
    # Define a function to return the appropriate mock provider
    def mock_get_model_provider(provider_type, *args, **kwargs):
        return mock_providers.get(provider_type.lower(), mock_providers["openai"])
    
    # Apply the patch to model_manager
    monkeypatch.setattr('ai_models.model_manager.get_model_provider', mock_get_model_provider)
    
    # Apply the patch to adapters if available
    try:
        monkeypatch.setattr('ai_models.adapters.adapter_factory.get_adapter', mock_get_model_provider)
    except (ImportError, AttributeError):
        pass
    
    return mock_providers


# External API Fixtures

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
        "storage": MockStorageAPI()
    }
    
    # Patch HuggingFace Hub if available
    try:
        monkeypatch.setattr('huggingface_hub.HfApi', lambda: mock_apis["huggingface"])
        monkeypatch.setattr('huggingface_hub.hf_hub_download', 
                          lambda model_id, *args, **kwargs: mock_apis["huggingface"].download_model(model_id, "mock_path"))
    except (ImportError, AttributeError):
        pass
    
    # Patch other external APIs based on project structure
    # These paths would need to be adjusted based on the actual project structure
    try:
        # Example patches for payment processing
        monkeypatch.setattr('monetization.payment_method_manager.create_payment_client', 
                          lambda *args, **kwargs: mock_apis["payment"])
        
        # Example patches for email services
        monkeypatch.setattr('marketing.content_generators.get_email_client', 
                          lambda *args, **kwargs: mock_apis["email"])
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
        "model": "test-model",
        "choices": [
            {
                "text": "This is a mock model response for testing purposes.",
                "index": 0,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "created": int(datetime.now().timestamp())
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
                "index": 0
            }
        ],
        "model": "text-embedding-model",
        "usage": {
            "prompt_tokens": 8,
            "total_tokens": 8
        }
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
            "email": "test@example.com",
            "name": "Test User",
            "created": timestamp,
            "metadata": {"user_id": "user_123"}
        },
        "subscription": {
            "id": f"sub_test_{timestamp}",
            "status": "active",
            "plan": {
                "id": "premium-monthly",
                "name": "Premium Monthly",
                "amount": 1999,
                "currency": "usd",
                "interval": "month"
            },
            "current_period_start": timestamp,
            "current_period_end": timestamp + (30 * 24 * 60 * 60),  # 30 days later
            "created": timestamp
        },
        "payment_method": {
            "id": f"pm_test_{timestamp}",
            "type": "credit_card",
            "last4": "4242",
            "exp_month": 12,
            "exp_year": 2025,
            "brand": "visa"
        }
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
                    "Technical complexity"
                ],
                "target_audience": [
                    "Knowledge workers",
                    "Small businesses",
                    "Freelancers"
                ]
            },
            {
                "name": "Content Creator Automation",
                "opportunity_score": 79.2,
                "market_size": "Medium",
                "competition_level": "Low",
                "growth_trend": "Rapidly increasing",
                "challenges": [
                    "Quality control",
                    "Customization needs",
                    "Ethical considerations"
                ],
                "target_audience": [
                    "YouTubers",
                    "Bloggers",
                    "Social media influencers"
                ]
            },
            {
                "name": "AI-powered Personal Finance",
                "opportunity_score": 73.8,
                "market_size": "Medium",
                "competition_level": "Medium-high",
                "growth_trend": "Steady increase",
                "challenges": [
                    "Regulatory compliance",
                    "Data security",
                    "Trust building"
                ],
                "target_audience": [
                    "Young professionals",
                    "Financial enthusiasts",
                    "Small business owners"
                ]
            }
        ],
        "analysis_summary": "The AI tools market shows significant growth potential across multiple niches. The highest opportunity scores are in productivity tools, content creation, and personal finance applications. Each niche presents unique challenges but also substantial monetization potential.",
        "recommended_focus": "AI Productivity Tools",
        "timestamp": datetime.now().isoformat()
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
                "name": "Tech-savvy Professionals",
                "demographics": {
                    "age_range": "25-45",
                    "education": "College degree or higher",
                    "income": "Above average"
                },
                "pain_points": [
                    "Limited time for repetitive tasks",
                    "Need for better organization",
                    "Information overload"
                ],
                "goals": [
                    "Increase productivity",
                    "Streamline workflows",
                    "Reduce stress"
                ]
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
                    "conversion_rate": 0.02
                }
            },
            {
                "name": "Social Media",
                "platforms": ["Twitter", "LinkedIn", "Instagram"],
                "content_types": ["Feature highlights", "User testimonials", "Tips and tricks"],
                "frequency": "Daily",
                "performance_metrics": {
                    "engagement_rate": 0.04,
                    "share_rate": 0.01,
                    "conversion_rate": 0.015
                }
            }
        ],
        "content_calendar": [
            {
                "date": (datetime.now().replace(day=1) + 
                        datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                "channel": "Email",
                "title": "Introducing Our New AI-Powered Feature",
                "content_type": "Product announcement",
                "status": "Draft"
            },
            {
                "date": (datetime.now().replace(day=1) + 
                        datetime.timedelta(days=9)).strftime("%Y-%m-%d"),
                "channel": "LinkedIn",
                "title": "How Our Tool Saved Client X 10 Hours Per Week",
                "content_type": "Case study",
                "status": "Planned"
            }
        ]
    }