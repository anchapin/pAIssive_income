"""
Tests for API schema validation.

This module contains tests for validating API schemas across different modules.
"""

import pytest
from pydantic import ValidationError

from api.schemas.ai_models import ModelRequest
from api.schemas.marketing import CampaignCreate, MarketingStrategyCreate
from api.schemas.monetization import PricingTierCreate, SubscriptionModelCreate
from api.schemas.niche_analysis import NicheAnalysisCreate, NicheCreate
from api.schemas.user import UserCreate, UserRole, UserUpdate
from api.schemas.webhook import WebhookEventType, WebhookRequest, WebhookUpdate


class TestSchemaValidation:

    # Import schemas to test
    pass  # Added missing block
    """Tests for API schema validation."""

    def test_webhook_schema_validation(self):
    """Test webhook schema validation."""
    # Valid data
    valid_data = {
    "url": "https://example.com/webhook",
    "events": [
    WebhookEventType.USER_CREATED,
    WebhookEventType.PAYMENT_RECEIVED,
    ],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer token"},
    "is_active": True,
    }
    webhook = WebhookRequest(**valid_data)
    assert str(webhook.url) == "https://example.com/webhook"
    assert len(webhook.events) == 2
    assert webhook.is_active is True

    # Invalid URL
    invalid_url_data = {
    "url": "invalid-url",
    "events": [WebhookEventType.USER_CREATED],
    "is_active": True,
    }
    with pytest.raises(ValidationError):
    WebhookRequest(**invalid_url_data)

    # Empty events list
    empty_events_data = {
    "url": "https://example.com/webhook",
    "events": [],
    "is_active": True,
    }
    with pytest.raises(ValidationError):
    WebhookRequest(**empty_events_data)

    # Test update schema
    update_data = {"description": "Updated webhook", "is_active": False}
    webhook_update = WebhookUpdate(**update_data)
    assert webhook_update.description == "Updated webhook"
    assert webhook_update.is_active is False

    def test_user_schema_validation(self):
    """Test user schema validation."""
    # Valid data
    valid_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "full_name": "Test User",
    "role": UserRole.USER,
    }
    user = UserCreate(**valid_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.USER

    # Invalid email
    invalid_email_data = {
    "username": "testuser",
    "email": "invalid-email",
    "password": "Password123!",
    }
    with pytest.raises(ValidationError):
    UserCreate(**invalid_email_data)

    # Weak password
    weak_password_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "weak",
    }
    with pytest.raises(ValidationError):
    UserCreate(**weak_password_data)

    # Test update schema
    update_data = {"full_name": "Updated User", "role": UserRole.ADMIN}
    user_update = UserUpdate(**update_data)
    assert user_update.full_name == "Updated User"
    assert user_update.role == UserRole.ADMIN

    def test_niche_analysis_schema_validation(self):
    """Test niche analysis schema validation."""
    # Valid data
    valid_data = {
    "name": "Test Niche Analysis",
    "description": "Analysis of test niche",
    "market_segment": "Technology",
    "target_audience": ["Developers", "IT Professionals"],
    "opportunity_score": 85,
    "competition_level": "Medium",
    "niches": [
    {
    "name": "AI Development Tools",
    "description": "Tools for AI development",
    "market_size": 1000000,
    "growth_rate": 15.5,
    "competition_level": "Medium",
    }
    ],
    }
    niche_analysis = NicheAnalysisCreate(**valid_data)
    assert niche_analysis.name == "Test Niche Analysis"
    assert niche_analysis.opportunity_score == 85
    assert len(niche_analysis.niches) == 1

    # Invalid opportunity score
    invalid_score_data = {
    "name": "Test Niche Analysis",
    "description": "Analysis of test niche",
    "market_segment": "Technology",
    "opportunity_score": 110,  # Should be 0-100
    }
    with pytest.raises(ValidationError):
    NicheAnalysisCreate(**invalid_score_data)

    # Test niche schema
    niche_data = {
    "name": "AI Development Tools",
    "description": "Tools for AI development",
    "market_size": 1000000,
    "growth_rate": 15.5,
    "competition_level": "Medium",
    }
    niche = NicheCreate(**niche_data)
    assert niche.name == "AI Development Tools"
    assert niche.market_size == 1000000
    assert niche.growth_rate == 15.5

    def test_monetization_schema_validation(self):
    """Test monetization schema validation."""
    # Valid subscription model data
    valid_subscription_data = {
    "name": "Premium Plan",
    "description": "Premium subscription plan",
    "billing_cycle": "monthly",
    "pricing_tiers": [
    {
    "name": "Basic",
    "price": 9.99,
    "features": ["Feature 1", "Feature 2"],
    "is_popular": False,
    },
    {
    "name": "Pro",
    "price": 19.99,
    "features": ["Feature 1", "Feature 2", "Feature 3"],
    "is_popular": True,
    },
    ],
    }
    subscription_model = SubscriptionModelCreate(**valid_subscription_data)
    assert subscription_model.name == "Premium Plan"
    assert subscription_model.billing_cycle == "monthly"
    assert len(subscription_model.pricing_tiers) == 2

    # Invalid billing cycle
    invalid_billing_data = {
    "name": "Premium Plan",
    "description": "Premium subscription plan",
    "billing_cycle": "invalid",
    }
    with pytest.raises(ValidationError):
    SubscriptionModelCreate(**invalid_billing_data)

    # Test pricing tier schema
    pricing_tier_data = {
    "name": "Enterprise",
    "price": 99.99,
    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
    "is_popular": False,
    }
    pricing_tier = PricingTierCreate(**pricing_tier_data)
    assert pricing_tier.name == "Enterprise"
    assert pricing_tier.price == 99.99
    assert len(pricing_tier.features) == 4

    def test_marketing_schema_validation(self):
    """Test marketing schema validation."""
    # Valid marketing strategy data
    valid_strategy_data = {
    "name": "Growth Strategy",
    "description": "Marketing strategy for growth",
    "target_audience": ["Developers", "IT Professionals"],
    "channels": ["Social Media", "Email", "Content Marketing"],
    "budget": 5000,
    "campaigns": [
    {
    "name": "Summer Campaign",
    "description": "Summer promotion campaign",
    "channel": "Social Media",
    "budget": 1000,
    "start_date": "2023-06-01",
    "end_date": "2023-08-31",
    }
    ],
    }
    marketing_strategy = MarketingStrategyCreate(**valid_strategy_data)
    assert marketing_strategy.name == "Growth Strategy"
    assert marketing_strategy.budget == 5000
    assert len(marketing_strategy.campaigns) == 1

    # Invalid budget
    invalid_budget_data = {
    "name": "Growth Strategy",
    "description": "Marketing strategy for growth",
    "budget": -1000,  # Should be positive
    }
    with pytest.raises(ValidationError):
    MarketingStrategyCreate(**invalid_budget_data)

    # Test campaign schema
    campaign_data = {
    "name": "Winter Campaign",
    "description": "Winter promotion campaign",
    "channel": "Email",
    "budget": 2000,
    "start_date": "2023-12-01",
    "end_date": "2024-02-28",
    }
    campaign = CampaignCreate(**campaign_data)
    assert campaign.name == "Winter Campaign"
    assert campaign.budget == 2000
    assert campaign.channel == "Email"

    def test_ai_models_schema_validation(self):
    """Test AI models schema validation."""
    # Valid model request data
    valid_request_data = {
    "model_name": "gpt-3.5-turbo",
    "prompt": "Generate a marketing strategy",
    "max_tokens": 500,
    "temperature": 0.7,
    "options": {"top_p": 0.9, "frequency_penalty": 0.5},
    }
    model_request = ModelRequest(**valid_request_data)
    assert model_request.model_name == "gpt-3.5-turbo"
    assert model_request.max_tokens == 500
    assert model_request.temperature == 0.7

    # Invalid temperature
    invalid_temp_data = {
    "model_name": "gpt-3.5-turbo",
    "prompt": "Generate a marketing strategy",
    "temperature": 1.5,  # Should be 0-1
    }
    with pytest.raises(ValidationError):
    ModelRequest(**invalid_temp_data)

    # Missing required fields
    missing_fields_data = {
    "max_tokens": 500,
    "temperature": 0.7,
    }
    with pytest.raises(ValidationError):
    ModelRequest(**missing_fields_data)


    if __name__ == "__main__":
    pytest.main(["-v", "test_schema_validation.py"])
