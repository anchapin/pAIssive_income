"""
Integration tests for CLI UI integration with backend services.

This module contains tests for the Command Line Interface integration with backend services.
"""


from unittest.mock import MagicMock, patch

import pytest

from agent_team.agent_team import AgentTeam
from ai_models.model_manager import ModelManager
from monetization.subscription_manager import SubscriptionManager
from niche_analysis.market_analyzer import MarketAnalyzer
from ui.cli_ui import CommandLineInterface


@pytest.fixture
def mock_agent_team():
    """Create a mock agent team."""
    mock_team = MagicMock(spec=AgentTeam)

    # Set up mock return values
    mock_team.run_niche_analysis.return_value = [
    {
    "id": "niche1",
    "name": "AI Inventory Management",
    "market_segment": "e-commerce",
    "opportunity_score": 0.85,
    }
    ]

    mock_team.develop_solution.return_value = {
    "id": "solution1",
    "name": "AI Inventory Optimizer",
    "description": "AI-powered inventory management solution",
    "features": ["Demand forecasting", "Stock optimization", "Supplier management"],
    }

    mock_team.create_monetization_strategy.return_value = {
    "id": "monetization1",
    "model": "subscription",
    "tiers": [
    {"name": "Basic", "price": 29.99, "features": ["Demand forecasting"]},
    {"name": "Pro", "price": 99.99, "features": ["Demand forecasting", "Stock optimization"]},
    {"name": "Enterprise", "price": 299.99, "features": ["Demand forecasting", "Stock optimization", "Supplier management"]},
    ],
    }

    mock_team.create_marketing_plan.return_value = {
    "id": "marketing1",
    "channels": ["content_marketing", "social_media", "email"],
    "target_audience": "e-commerce store owners",
    "messaging": "Reduce inventory costs by 30% with AI",
    }

    return mock_team


    @pytest.fixture
    def mock_model_manager():
    """Create a mock model manager."""
    mock_manager = MagicMock(spec=ModelManager)

    # Set up mock return values
    mock_manager.list_models.return_value = [
    {"name": "GPT-4", "type": "text", "provider": "openai"},
    {"name": "DALL-E 3", "type": "image", "provider": "openai"},
    ]

    return mock_manager


    @pytest.fixture
    def mock_subscription_manager():
    """Create a mock subscription manager."""
    mock_manager = MagicMock(spec=SubscriptionManager)

    # Set up mock return values
    mock_manager.get_subscription_models.return_value = [
    {"name": "Freemium", "has_free_tier": True},
    {"name": "Premium", "has_free_tier": False},
    ]

    return mock_manager


    @pytest.fixture
    def cli_ui(mock_agent_team, mock_model_manager, mock_subscription_manager):
    """Create a CLI UI instance with mock dependencies."""
    return CommandLineInterface(
    agent_team=mock_agent_team,
    model_manager=mock_model_manager,
    subscription_manager=mock_subscription_manager
    )


    class TestCLIUIIntegration:

    def test_cli_ui_initialization(self, cli_ui):
    """Test CLI UI initialization with backend services."""
    assert cli_ui.agent_team is not None
    assert cli_ui.model_manager is not None
    assert cli_ui.subscription_manager is not None

    def test_cli_ui_niche_analysis_integration(self, cli_ui, mock_agent_team):
    """Test CLI UI integration with niche analysis service."""
    # Run niche analysis command
    result = cli_ui.handle_command("analyze e-commerce digital-marketing")

    # Check that the agent team's method was called
    mock_agent_team.run_niche_analysis.assert_called_once_with(["e-commerce", "digital-marketing"])

    # Check that the result contains information about the niches
    assert "AI Inventory Management" in result

    def test_cli_ui_solution_development_integration(self, cli_ui, mock_agent_team):
    """Test CLI UI integration with solution development service."""
    # First, run niche analysis to populate current_niches
    cli_ui.handle_command("analyze e-commerce")

    # Select a niche
    cli_ui.handle_command("select niche 0")

    # Develop a solution
    result = cli_ui.handle_command("develop solution")

    # Check that the agent team's method was called
    mock_agent_team.develop_solution.assert_called_once()

    # Check that the result contains information about the solution
    assert "AI Inventory Optimizer" in result

    def test_cli_ui_monetization_integration(self, cli_ui, mock_agent_team):
    """Test CLI UI integration with monetization service."""
    # Set up the state for monetization
    cli_ui.handle_command("analyze e-commerce")
    cli_ui.handle_command("select niche 0")
    cli_ui.handle_command("develop solution")

    # Create monetization strategy
    result = cli_ui.handle_command("create monetization")

    # Check that the agent team's method was called
    mock_agent_team.create_monetization_strategy.assert_called_once()

    # Check that the result contains information about the monetization strategy
    assert "subscription" in result
    assert "Basic" in result
    assert "Pro" in result
    assert "Enterprise" in result

    def test_cli_ui_marketing_integration(self, cli_ui, mock_agent_team):
    """Test CLI UI integration with marketing service."""
    # Set up the state for marketing
    cli_ui.handle_command("analyze e-commerce")
    cli_ui.handle_command("select niche 0")
    cli_ui.handle_command("develop solution")
    cli_ui.handle_command("create monetization")

    # Create marketing plan
    result = cli_ui.handle_command("create marketing")

    # Check that the agent team's method was called
    mock_agent_team.create_marketing_plan.assert_called_once()

    # Check that the result contains information about the marketing plan
    assert "content_marketing" in result
    assert "social_media" in result
    assert "email" in result

    def test_cli_ui_model_manager_integration(self, cli_ui, mock_model_manager):
    """Test CLI UI integration with model manager."""
    # Add a command to list models
    with patch.object(cli_ui, '_handle_list_models', return_value="Models listed") as mock_method:
    cli_ui.handle_command("list models")
    mock_method.assert_called_once()

    def test_cli_ui_subscription_manager_integration(self, cli_ui, mock_subscription_manager):
    """Test CLI UI integration with subscription manager."""
    # Add a command to list subscription models
    with patch.object(cli_ui, '_handle_list_subscriptions', return_value="Subscriptions listed") as mock_method:
    cli_ui.handle_command("list subscriptions")
    mock_method.assert_called_once()

    def test_cli_ui_full_workflow_integration(self, cli_ui, mock_agent_team):
    """Test the CommandLineInterface integration with the full workflow."""
    # Simulate a complete workflow through the CLI

    # Step 1: Run niche analysis
    cli_ui.handle_command("analyze e-commerce digital-marketing")
    mock_agent_team.run_niche_analysis.assert_called_once_with(["e-commerce", "digital-marketing"])

    # Step 2: Select a niche and develop a solution
    cli_ui.handle_command("select niche 0")  # Select the first niche
    cli_ui.handle_command("develop solution")
    mock_agent_team.develop_solution.assert_called_once()

    # Step 3: Create a monetization strategy
    cli_ui.handle_command("create monetization")
    mock_agent_team.create_monetization_strategy.assert_called_once()

    # Step 4: Create a marketing plan
    cli_ui.handle_command("create marketing")
    mock_agent_team.create_marketing_plan.assert_called_once()

    # Step 5: Export the complete plan
    with patch.object(cli_ui, '_handle_export', return_value="Plan exported") as mock_export:
    cli_ui.handle_command("export plan")
    mock_export.assert_called_once()


    if __name__ == "__main__":
    pytest.main(["-v", "test_cli_ui_integration.py"])