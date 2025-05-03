"""
Integration tests for Web UI integration with backend services.

This module contains tests for the Web UI integration with backend services.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent_team.agent_team import AgentTeam
from ai_models.model_manager import ModelManager
from monetization.subscription_manager import SubscriptionManager
from niche_analysis.market_analyzer import MarketAnalyzer
from ui.web_ui import WebUI


@pytest.fixture
def mock_agent_team():
    """Create a mock agent team."""
    mock_team = MagicMock(spec=AgentTeam)

    # Set up mock return values
    mock_team.run_niche_analysis.return_value = [
        {
            "id": "niche1",
            "name": "AI Inventory Management",
            "market_segment": "e - commerce",
            "opportunity_score": 0.85,
        }
    ]

    mock_team.develop_solution.return_value = {
        "id": "solution1",
        "name": "AI Inventory Optimizer",
        "description": "AI - powered inventory management solution",
        "features": ["Demand forecasting", "Stock optimization", "Supplier management"],
    }

    mock_team.create_monetization_strategy.return_value = {
        "id": "monetization1",
        "model": "subscription",
        "tiers": [
            {"name": "Basic", "price": 29.99, "features": ["Demand forecasting"]},
            {
                "name": "Pro",
                "price": 99.99,
                "features": ["Demand forecasting", "Stock optimization"],
            },
            {
                "name": "Enterprise",
                "price": 299.99,
                "features": ["Demand forecasting", "Stock optimization", "Supplier management"],
            },
        ],
    }

    mock_team.create_marketing_plan.return_value = {
        "id": "marketing1",
        "channels": ["content_marketing", "social_media", "email"],
        "target_audience": "e - commerce store owners",
        "messaging": "Reduce inventory costs by 30% with AI",
    }

    return mock_team


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager."""
    mock_manager = MagicMock(spec=ModelManager)

    # Set up mock return values
    mock_manager.list_models.return_value = [
        {"name": "GPT - 4", "type": "text", "provider": "openai"},
        {"name": "DALL - E 3", "type": "image", "provider": "openai"},
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
def web_ui(mock_agent_team, mock_model_manager, mock_subscription_manager):
    """Create a Web UI instance with mock dependencies."""
    ui = WebUI()
    ui.agent_team = mock_agent_team
    ui.model_manager = mock_model_manager
    ui.subscription_manager = mock_subscription_manager
    ui.current_niches = []
    ui.current_solution = None
    ui.current_monetization = None
    ui.current_marketing_plan = None
    return ui


class TestWebUIIntegration:
    """Test Web UI integration with backend services."""

    def test_web_ui_initialization(self, web_ui):
        """Test Web UI initialization with backend services."""
        assert web_ui.agent_team is not None
        assert web_ui.model_manager is not None
        assert web_ui.subscription_manager is not None

    @patch("ui.web_ui.WebUI.render_template")
    def test_web_ui_niche_analysis_integration(self, mock_render_template, web_ui, mock_agent_team):
        """Test Web UI integration with niche analysis service."""
        # Set up the mock to return a tuple
        mock_render_template.return_value = (
            "niche_analysis.html",
            {"niches": mock_agent_team.run_niche_analysis.return_value},
        )

        # Run niche analysis
        web_ui.analyze_niches(["e - commerce", "digital - marketing"])

        # Check that the agent team's method was called
        mock_agent_team.run_niche_analysis.assert_called_once_with(
            ["e - commerce", "digital - marketing"]
        )

        # Check that the UI has stored the niches
        assert len(web_ui.current_niches) > 0
        assert web_ui.current_niches[0]["name"] == "AI Inventory Management"

    @patch("ui.web_ui.WebUI.render_template")
    def test_web_ui_solution_development_integration(
        self, mock_render_template, web_ui, mock_agent_team
    ):
        """Test Web UI integration with solution development service."""
        # Set up the mock to return a tuple
        mock_render_template.return_value = (
            "solution.html",
            {"solution": mock_agent_team.develop_solution.return_value},
        )

        # Set up the state for solution development
        web_ui.current_niches = mock_agent_team.run_niche_analysis.return_value

        # Develop a solution
        web_ui.develop_solution(niche_id="niche1")

        # Check that the agent team's method was called
        mock_agent_team.develop_solution.assert_called_once()

        # Check that the UI has stored the solution
        assert web_ui.current_solution is not None
        assert web_ui.current_solution["name"] == "AI Inventory Optimizer"

    @patch("ui.web_ui.WebUI.render_template")
    def test_web_ui_monetization_integration(self, mock_render_template, web_ui, mock_agent_team):
        """Test Web UI integration with monetization service."""
        # Set up the mock to return a tuple
        mock_render_template.return_value = (
            "monetization.html",
            {"monetization": mock_agent_team.create_monetization_strategy.return_value},
        )

        # Set up the state for monetization
        web_ui.current_niches = mock_agent_team.run_niche_analysis.return_value
        web_ui.current_solution = mock_agent_team.develop_solution.return_value

        # Create monetization strategy
        web_ui.create_monetization()

        # Check that the agent team's method was called
        mock_agent_team.create_monetization_strategy.assert_called_once()

        # Check that the UI has stored the monetization strategy
        assert web_ui.current_monetization is not None
        assert web_ui.current_monetization["model"] == "subscription"
        assert len(web_ui.current_monetization["tiers"]) == 3

    @patch("ui.web_ui.WebUI.render_template")
    def test_web_ui_marketing_integration(self, mock_render_template, web_ui, mock_agent_team):
        """Test Web UI integration with marketing service."""
        # Set up the mock to return a tuple
        mock_render_template.return_value = (
            "marketing.html",
            {"marketing_plan": mock_agent_team.create_marketing_plan.return_value},
        )

        # Set up the state for marketing
        web_ui.current_niches = mock_agent_team.run_niche_analysis.return_value
        web_ui.current_solution = mock_agent_team.develop_solution.return_value
        web_ui.current_monetization = mock_agent_team.create_monetization_strategy.return_value

        # Create marketing plan
        web_ui.create_marketing_plan()

        # Check that the agent team's method was called
        mock_agent_team.create_marketing_plan.assert_called_once()

        # Check that the UI has stored the marketing plan
        assert web_ui.current_marketing_plan is not None
        assert "content_marketing" in web_ui.current_marketing_plan["channels"]
        assert "social_media" in web_ui.current_marketing_plan["channels"]
        assert "email" in web_ui.current_marketing_plan["channels"]

    @patch("ui.web_ui.WebUI.render_template")
    def test_web_ui_render_integration(self, mock_render_template, web_ui, mock_agent_team):
        """Test the WebUI template rendering integration."""
        # Set up some data
        web_ui.current_niches = mock_agent_team.run_niche_analysis.return_value
        web_ui.current_solution = mock_agent_team.develop_solution.return_value
        web_ui.current_monetization = mock_agent_team.create_monetization_strategy.return_value
        web_ui.current_marketing_plan = mock_agent_team.create_marketing_plan.return_value

        # Set up the mock to return a tuple
        mock_render_template.return_value = (
            "dashboard.html",
            {
                "niches": web_ui.current_niches,
                "solution": web_ui.current_solution,
                "monetization": web_ui.current_monetization,
                "marketing_plan": web_ui.current_marketing_plan,
            },
        )

        # Render the dashboard
        template, context = web_ui.render_dashboard()

        # Check that the render_template method was called
        mock_render_template.assert_called_once()

        # Check that the context contains all the data
        assert template == "dashboard.html"
        assert "niches" in context
        assert "solution" in context
        assert "monetization" in context
        assert "marketing_plan" in context

    def test_web_ui_model_manager_integration(self, web_ui, mock_model_manager):
        """Test the WebUI integration with model manager."""
        # Simulate a request to list available models
        models = web_ui.list_available_models()

        # Check that the model manager's method was called
        mock_model_manager.list_models.assert_called_once()

        # Check that the UI returned the expected results
        assert len(models) == 2
        assert models[0]["name"] == "GPT - 4"
        assert models[1]["name"] == "DALL - E 3"

    def test_web_ui_subscription_manager_integration(self, web_ui, mock_subscription_manager):
        """Test the WebUI integration with subscription manager."""
        # Simulate a request to list subscription models
        subscription_models = web_ui.list_subscription_models()

        # Check that the subscription manager's method was called
        mock_subscription_manager.get_subscription_models.assert_called_once()

        # Check that the UI returned the expected results
        assert len(subscription_models) == 2
        assert subscription_models[0]["name"] == "Freemium"
        assert subscription_models[1]["name"] == "Premium"

    @patch("ui.event_handlers.handle_niche_selected")
    def test_web_ui_event_handling_integration(self, mock_handle_niche_selected, web_ui):
        """Test the WebUI integration with event handlers."""
        # Set up some data
        niches = [
            {
                "id": "niche1",
                "name": "AI Inventory Management",
                "market_segment": "e - commerce",
                "opportunity_score": 0.85,
            }
        ]
        web_ui.current_niches = niches

        # Simulate a niche selection event
        event_data = {"niche_id": "niche1"}
        web_ui.handle_event("niche_selected", event_data)

        # Check that the event handler was called with the right parameters
        mock_handle_niche_selected.assert_called_once()
        ui_arg, data_arg = mock_handle_niche_selected.call_args[0]
        assert ui_arg == web_ui
        assert data_arg == event_data


if __name__ == "__main__":
    pytest.main([" - v", "test_web_ui_integration.py"])
