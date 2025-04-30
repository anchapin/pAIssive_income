"""
Fixtures for UI integration tests.
"""

import pytest
from unittest.mock import MagicMock, patch

from agent_team import AgentTeam
from ai_models import ModelManager
from monetization import SubscriptionManager
from interfaces.ui_interfaces import IAgentTeamService
from dependency_container import get_container


@pytest.fixture
def mock_agent_team():
    """Create a mock agent team."""
    team = MagicMock()

    # Mock the run_niche_analysis method
    team.run_niche_analysis.return_value = [
        {
            "id": "niche1",
            "name": "AI Inventory Management",
            "market_segment": "e-commerce",
            "opportunity_score": 0.85,
        },
        {
            "id": "niche2",
            "name": "Content Generation for Marketing",
            "market_segment": "digital-marketing",
            "opportunity_score": 0.78,
        },
    ]

    # Mock the develop_solution method
    team.develop_solution.return_value = {
        "id": "solution1",
        "name": "AI Inventory Optimizer",
        "description": "An AI tool that helps e-commerce businesses optimize inventory levels.",
        "features": [
            {"id": "feature1", "name": "Demand Forecasting"},
            {"id": "feature2", "name": "Reorder Alerts"},
        ],
    }

    # Mock the create_monetization_strategy method
    team.create_monetization_strategy.return_value = {
        "id": "monetization1",
        "name": "Freemium Strategy",
        "subscription_model": {
            "name": "Inventory Optimizer Subscription",
            "tiers": [
                {"name": "Free", "price_monthly": 0},
                {"name": "Pro", "price_monthly": 29.99},
            ],
        },
    }

    # Mock the create_marketing_plan method
    team.create_marketing_plan.return_value = {
        "id": "marketing1",
        "name": "Inventory Optimizer Marketing Plan",
        "channels": ["content", "social", "email"],
        "target_audience": "E-commerce store owners",
    }

    return team


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager."""
    manager = MagicMock()

    # Mock the list_models method
    manager.list_models.return_value = [
        {"id": "model1", "name": "GPT-4", "capabilities": ["text-generation"]},
        {"id": "model2", "name": "DALL-E 3", "capabilities": ["image-generation"]},
    ]

    return manager


@pytest.fixture
def mock_subscription_manager():
    """Create a mock subscription manager."""
    # Create a mock without specifying the spec
    manager = MagicMock()

    # Mock the get_active_subscriptions method
    manager.get_active_subscriptions.return_value = [
        {
            "id": "sub1",
            "user_id": "user1",
            "plan_name": "Pro Plan",
            "status": "active",
            "created_at": "2025-04-01T10:00:00Z",
            "expires_at": "2026-04-01T10:00:00Z",
        }
    ]

    return manager


@pytest.fixture
def mock_agent_team_service():
    """Create a mock agent team service."""
    # Create a mock service
    service = MagicMock()

    # Mock the create_project method
    service.create_project.return_value = {
        "id": "project1",
        "name": "Test Project",
        "status": "active",
    }

    # Mock the get_projects method
    service.get_projects.return_value = [
        {"id": "project1", "name": "Test Project", "status": "active"}
    ]

    return service


@pytest.fixture
def register_mock_services(
    mock_agent_team_service,
    mock_agent_team,
    mock_model_manager,
    mock_subscription_manager,
):
    """Register mock services in the dependency container."""
    from interfaces.ui_interfaces import (
        IAgentTeamService,
        INicheAnalysisService,
        IDeveloperService,
        IMonetizationService,
        IMarketingService,
    )
    from interfaces.agent_interfaces import IAgentTeam
    from interfaces.model_interfaces import IModelManager
    from interfaces.monetization_interfaces import ISubscriptionManager

    # Get the container
    container = get_container()

    # Register mock services
    container.register(
        IAgentTeamService, lambda: mock_agent_team_service, singleton=True
    )
    container.register(INicheAnalysisService, lambda: MagicMock(), singleton=True)
    container.register(IDeveloperService, lambda: MagicMock(), singleton=True)
    container.register(IMonetizationService, lambda: MagicMock(), singleton=True)
    container.register(IMarketingService, lambda: MagicMock(), singleton=True)

    # Register mock dependencies
    container.register(IAgentTeam, lambda: mock_agent_team, singleton=True)
    container.register(IModelManager, lambda: mock_model_manager, singleton=True)
    container.register(
        ISubscriptionManager, lambda: mock_subscription_manager, singleton=True
    )

    return container
