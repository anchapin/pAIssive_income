"""
Pytest fixtures for the pAIssive_income project.

This module provides fixtures that can be used across tests.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

# Import our centralized mock fixtures
from tests.mocks.mock_model_providers import (
    create_mock_provider,
)

# Keep existing mock payment APIs for backward compatibility
try:
    from tests.mocks.mock_payment_apis import (
        MockPayPalGateway,
        MockStripeGateway,
        create_payment_gateway,
    )
except ImportError:
    # Create mock versions if the module doesn't exist yet
    class MockStripeGateway:
        pass

    class MockPayPalGateway:
        pass

    def create_payment_gateway(gateway_type, config=None):
        return MagicMock()


# Re-export all fixtures from tests.mocks.fixtures
# This makes them available to all tests without explicit imports

# Continue with existing fixtures
# These will be kept for backward compatibility


@pytest.fixture
def mock_stripe_gateway():
    """Create a mock Stripe payment gateway."""
    gateway = create_payment_gateway("stripe")

    # Add some test data
    customer = gateway.create_customer(email="test@example.com", name="Test Customer")

    # Create a payment method
    payment_method = gateway.create_payment_method(
        customer_id=customer["id"],
        payment_type="card",
        payment_details={
            "number": "4242424242424242",  # Visa test card
            "exp_month": 12,
            "exp_year": datetime.now().year + 1,
            "cvc": "123",
        },
    )

    # Create a plan
    plan = gateway.create_plan(name="Test Plan", currency="USD", interval="month", amount=9.99)

    # Create a subscription
    subscription = gateway.create_subscription(
        customer_id=customer["id"],
        plan_id=plan["id"],
        payment_method_id=payment_method["id"],
    )

    return gateway


@pytest.fixture
def mock_paypal_gateway():
    """Create a mock PayPal payment gateway."""
    return create_payment_gateway("paypal")


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager with predefined models."""
    mock_manager = MagicMock()

    # Define available models
    mock_manager.list_models.return_value = [
        {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "capabilities": ["text-generation", "chat"],
            "provider": "openai",
        },
        {
            "id": "gpt-4",
            "name": "GPT-4",
            "capabilities": ["text-generation", "chat"],
            "provider": "openai",
        },
        {
            "id": "mistral-7b",
            "name": "Mistral 7B",
            "capabilities": ["text-generation", "chat"],
            "provider": "ollama",
        },
        {
            "id": "llama2",
            "name": "Llama 2",
            "capabilities": ["text-generation", "chat"],
            "provider": "lmstudio",
        },
    ]

    # Mock the get_model_info method
    def get_model_info(model_id):
        for model in mock_manager.list_models():
            if model["id"] == model_id:
                return model
        return None

    mock_manager.get_model_info.side_effect = get_model_info

    # Mock the load_model method
    mock_manager.load_model.return_value = MagicMock()

    return mock_manager


@pytest.fixture
def mock_test_solution():
    """Create a mock solution for testing."""
    return {
        "id": "solution1",
        "name": "AI Inventory Manager",
        "description": "An AI-powered solution for inventory management",
        "features": [
            {
                "id": "feature1",
                "name": "Demand Forecasting",
                "description": "Predict future inventory needs based on historical data",
                "complexity": "high",
                "development_cost": "high",
                "value_proposition": "Save time and reduce stockouts",
            },
            {
                "id": "feature2",
                "name": "Reorder Alerts",
                "description": "Get alerts when inventory is running low",
                "complexity": "medium",
                "development_cost": "medium",
                "value_proposition": "Never run out of stock again",
            },
            {
                "id": "feature3",
                "name": "Custom Reporting",
                "description": "Generate custom inventory reports",
                "complexity": "medium",
                "development_cost": "medium",
                "value_proposition": "Get the insights you need",
            },
            {
                "id": "feature4",
                "name": "API Access",
                "description": "Access inventory data through API",
                "complexity": "high",
                "development_cost": "high",
                "value_proposition": "Integrate with your existing systems",
            },
        ],
        "market_data": {
            "target_audience": "E-commerce store owners and inventory managers",
            "market_size": "large",
            "competition": "medium",
        },
    }


@pytest.fixture
def mock_test_monetization_strategy():
    """Create a mock monetization strategy for testing."""
    return {
        "id": "strategy1",
        "name": "Freemium Strategy",
        "description": "A freemium monetization strategy",
        "subscription_model": {
            "name": "Inventory Manager Subscription",
            "tiers": [
                {
                    "id": "tier1",
                    "name": "Free",
                    "price_monthly": 0.0,
                    "features": ["Basic Forecasting"],
                    "limits": {"api_calls": 100, "exports": 10},
                },
                {
                    "id": "tier2",
                    "name": "Pro",
                    "price_monthly": 19.99,
                    "features": ["Advanced Forecasting", "Reorder Alerts"],
                    "limits": {"api_calls": 1000, "exports": 100},
                },
                {
                    "id": "tier3",
                    "name": "Business",
                    "price_monthly": 49.99,
                    "features": [
                        "Advanced Forecasting",
                        "Reorder Alerts",
                        "Custom Reporting",
                        "API Access",
                    ],
                    "limits": {"api_calls": 10000, "exports": 1000},
                },
            ],
        },
        "target_audience": {
            "segments": [
                "Small businesses",
                "E-commerce store owners",
                "Retail inventory managers",
            ],
            "user_personas": {
                "free_tier": "Small business owners looking for basic inventory management",
                "pro_tier": "Growing e-commerce businesses with moderate inventory needs",
                "business_tier": "Established businesses with complex inventory requirements",
            },
        },
        "pricing_strategy": {
            "model_type": "freemium",
            "pricing_psychology": "price_anchoring",
            "discount_strategy": "annual_discount",
        },
        "revenue_projections": {
            "year_1": {
                "total": 250000,
                "by_tier": {"Free": 0, "Pro": 150000, "Business": 100000},
            },
            "year_3": {
                "total": 1200000,
                "by_tier": {"Free": 0, "Pro": 500000, "Business": 700000},
            },
        },
    }


@pytest.fixture
def mock_test_niche():
    """Create a mock niche for testing."""
    return {
        "id": "niche1",
        "name": "Inventory Management",
        "market_segment": "e-commerce",
        "description": "AI tools for inventory management",
        "opportunity_score": 0.8,
        "market_data": {
            "market_size": "large",
            "growth_rate": "high",
            "competition": "medium",
        },
        "problems": [
            {
                "id": "problem1",
                "name": "Inventory Forecasting",
                "description": "Difficulty predicting inventory needs",
                "severity": "high",
            }
        ],
    }


# The patch_payment_processor and patch_model_provider fixtures are now
# deprecated in favor of the more comprehensive patch_external_apis and
# patch_model_providers fixtures. They are kept for backward compatibility.


@pytest.fixture
def patch_payment_processor(monkeypatch):
    """
    Patch the payment processor with a mock implementation.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        A mock stripe gateway instance
    """
    mock_gateway = create_payment_gateway("stripe")

    # Define a function to return the mock gateway
    def mock_get_payment_gateway(*args, **kwargs):
        return mock_gateway

    # Apply the patch
    if hasattr(monkeypatch, "setattr"):
        try:
            # Try to patch the appropriate module
            monkeypatch.setattr(
                "monetization.payment_processor.get_payment_gateway",
                mock_get_payment_gateway,
            )
        except (ImportError, AttributeError):
            pass  # Module might not exist yet

    return mock_gateway


@pytest.fixture
def patch_model_provider(monkeypatch):
    """
    Patch the model provider with a mock implementation.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        A mock OpenAI provider instance
    """
    mock_provider = create_mock_provider("openai")

    # Define a function to return the mock provider
    def mock_get_model_provider(*args, **kwargs):
        return mock_provider

    # Apply the patch
    if hasattr(monkeypatch, "setattr"):
        try:
            # Try to patch the appropriate module
            monkeypatch.setattr(
                "ai_models.model_manager.get_model_provider", mock_get_model_provider
            )
        except (ImportError, AttributeError):
            pass  # Module might not exist yet

    return mock_provider
