"""
Tests for the channel strategies components in the Marketing module.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from marketing.channel_strategies import (
    MarketingStrategy,
    ContentMarketingStrategy,
    SocialMediaStrategy,
    EmailMarketingStrategy
)


def test_marketing_strategy_init():
    """Test MarketingStrategy initialization."""
    strategy = MarketingStrategy(
        name="Test Marketing Strategy",
        description="A test marketing strategy"
    )
    
    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Marketing Strategy"
    assert strategy.description == "A test marketing strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")


def test_marketing_strategy_create_plan():
    """Test create_plan method of MarketingStrategy."""
    strategy = MarketingStrategy(
        name="Test Marketing Strategy",
        description="A test marketing strategy"
    )
    
    # Create a plan
    plan = strategy.create_plan(
        niche="e-commerce",
        target_audience="Small business owners",
        budget=1000,
        timeline="3 months"
    )
    
    # Check that the plan has the expected attributes
    assert "id" in plan
    assert "name" in plan
    assert "description" in plan
    assert "niche" in plan
    assert "target_audience" in plan
    assert "budget" in plan
    assert "timeline" in plan
    assert "channels" in plan
    assert "goals" in plan
    assert "metrics" in plan
    assert "created_at" in plan
    
    # Check specific values
    assert plan["niche"] == "e-commerce"
    assert plan["target_audience"] == "Small business owners"
    assert plan["budget"] == 1000
    assert plan["timeline"] == "3 months"
    assert isinstance(plan["channels"], list)
    assert isinstance(plan["goals"], list)
    assert isinstance(plan["metrics"], list)


def test_content_marketing_strategy_init():
    """Test ContentMarketingStrategy initialization."""
    strategy = ContentMarketingStrategy(
        name="Test Content Marketing Strategy",
        description="A test content marketing strategy"
    )
    
    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Content Marketing Strategy"
    assert strategy.description == "A test content marketing strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")
    assert hasattr(strategy, "content_types")
    assert isinstance(strategy.content_types, list)
    assert len(strategy.content_types) > 0


def test_content_marketing_strategy_create_content_plan():
    """Test create_content_plan method of ContentMarketingStrategy."""
    strategy = ContentMarketingStrategy(
        name="Test Content Marketing Strategy",
        description="A test content marketing strategy"
    )
    
    # Create a content plan
    plan = strategy.create_content_plan(
        niche="e-commerce",
        target_audience="Small business owners",
        content_types=["blog_posts", "videos", "infographics"],
        frequency="weekly",
        distribution_channels=["website", "social_media"]
    )
    
    # Check that the plan has the expected attributes
    assert "id" in plan
    assert "name" in plan
    assert "niche" in plan
    assert "target_audience" in plan
    assert "content_types" in plan
    assert "frequency" in plan
    assert "distribution_channels" in plan
    assert "content_calendar" in plan
    assert "created_at" in plan
    
    # Check specific values
    assert plan["niche"] == "e-commerce"
    assert plan["target_audience"] == "Small business owners"
    assert plan["content_types"] == ["blog_posts", "videos", "infographics"]
    assert plan["frequency"] == "weekly"
    assert plan["distribution_channels"] == ["website", "social_media"]
    assert isinstance(plan["content_calendar"], list)


def test_social_media_strategy_init():
    """Test SocialMediaStrategy initialization."""
    strategy = SocialMediaStrategy(
        name="Test Social Media Strategy",
        description="A test social media strategy"
    )
    
    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Social Media Strategy"
    assert strategy.description == "A test social media strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")
    assert hasattr(strategy, "platforms")
    assert isinstance(strategy.platforms, list)
    assert len(strategy.platforms) > 0


def test_social_media_strategy_create_platform_plan():
    """Test create_platform_plan method of SocialMediaStrategy."""
    strategy = SocialMediaStrategy(
        name="Test Social Media Strategy",
        description="A test social media strategy"
    )
    
    # Create a platform plan
    plan = strategy.create_platform_plan(
        platform="instagram",
        target_audience="Small business owners",
        content_types=["images", "stories", "reels"],
        posting_frequency="daily",
        engagement_tactics=["hashtags", "contests", "collaborations"]
    )
    
    # Check that the plan has the expected attributes
    assert "id" in plan
    assert "platform" in plan
    assert "target_audience" in plan
    assert "content_types" in plan
    assert "posting_frequency" in plan
    assert "engagement_tactics" in plan
    assert "content_ideas" in plan
    assert "metrics" in plan
    assert "created_at" in plan
    
    # Check specific values
    assert plan["platform"] == "instagram"
    assert plan["target_audience"] == "Small business owners"
    assert plan["content_types"] == ["images", "stories", "reels"]
    assert plan["posting_frequency"] == "daily"
    assert plan["engagement_tactics"] == ["hashtags", "contests", "collaborations"]
    assert isinstance(plan["content_ideas"], list)
    assert isinstance(plan["metrics"], list)


def test_email_marketing_strategy_init():
    """Test EmailMarketingStrategy initialization."""
    strategy = EmailMarketingStrategy(
        name="Test Email Marketing Strategy",
        description="A test email marketing strategy"
    )
    
    # Check that the strategy has the expected attributes
    assert strategy.name == "Test Email Marketing Strategy"
    assert strategy.description == "A test email marketing strategy"
    assert hasattr(strategy, "id")
    assert hasattr(strategy, "created_at")
    assert hasattr(strategy, "email_types")
    assert isinstance(strategy.email_types, list)
    assert len(strategy.email_types) > 0


def test_email_marketing_strategy_create_campaign():
    """Test create_campaign method of EmailMarketingStrategy."""
    strategy = EmailMarketingStrategy(
        name="Test Email Marketing Strategy",
        description="A test email marketing strategy"
    )
    
    # Create a campaign
    campaign = strategy.create_campaign(
        name="Welcome Campaign",
        target_audience="New subscribers",
        email_sequence=["welcome", "product_intro", "case_study", "offer"],
        frequency="3 days apart",
        goals=["build_relationship", "introduce_product", "convert"]
    )
    
    # Check that the campaign has the expected attributes
    assert "id" in campaign
    assert "name" in campaign
    assert "target_audience" in campaign
    assert "email_sequence" in campaign
    assert "frequency" in campaign
    assert "goals" in campaign
    assert "metrics" in campaign
    assert "created_at" in campaign
    
    # Check specific values
    assert campaign["name"] == "Welcome Campaign"
    assert campaign["target_audience"] == "New subscribers"
    assert campaign["email_sequence"] == ["welcome", "product_intro", "case_study", "offer"]
    assert campaign["frequency"] == "3 days apart"
    assert campaign["goals"] == ["build_relationship", "introduce_product", "convert"]
    assert isinstance(campaign["metrics"], list)
