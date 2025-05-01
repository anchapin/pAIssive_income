"""
Integration tests for the niche-to-solution workflow.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent_team import AgentTeam
from niche_analysis import MarketAnalyzer, OpportunityScorer, ProblemIdentifier


@pytest.fixture
def mock_agents():
    """Create mock agents for testing."""
    # Mock the ResearchAgent
    mock_researcher = MagicMock()
    mock_researcher.analyze_market_segments.return_value = [
        {
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
        },
        {
            "id": "niche2",
            "name": "Product Description Generation",
            "market_segment": "e-commerce",
            "description": "AI tools for generating product descriptions",
            "opportunity_score": 0.7,
            "market_data": {
                "market_size": "medium",
                "growth_rate": "high",
                "competition": "low",
            },
            "problems": [
                {
                    "id": "problem2",
                    "name": "Description Quality",
                    "description": "Creating high-quality product descriptions is time-consuming",
                    "severity": "medium",
                }
            ],
        },
    ]

    # Mock the DeveloperAgent
    mock_developer = MagicMock()
    mock_developer.design_solution.return_value = {
        "id": "solution1",
        "name": "AI Inventory Manager",
        "description": "An AI-powered solution for inventory management",
        "features": [
            {
                "id": "feature1",
                "name": "Demand Forecasting",
                "description": "Predict future inventory needs based on historical data",
            },
            {
                "id": "feature2",
                "name": "Reorder Alerts",
                "description": "Get alerts when inventory is running low",
            },
        ],
    }

    # Mock the MonetizationAgent
    mock_monetization = MagicMock()
    mock_monetization.create_strategy.return_value = {
        "id": "strategy1",
        "name": "Freemium Strategy",
        "description": "A freemium monetization strategy",
        "subscription_model": {
            "name": "Inventory Manager Subscription",
            "tiers": [
                {
                    "name": "Free",
                    "price_monthly": 0.0,
                    "features": ["Basic Forecasting"],
                },
                {
                    "name": "Pro",
                    "price_monthly": 19.99,
                    "features": ["Advanced Forecasting", "Reorder Alerts"],
                },
            ],
        },
    }

    # Mock the MarketingAgent
    mock_marketing = MagicMock()
    mock_marketing.create_plan.return_value = {
        "id": "plan1",
        "name": "Inventory Manager Marketing Plan",
        "description": "A marketing plan for the AI Inventory Manager",
        "channels": ["content", "social", "email"],
        "target_audience": "E-commerce store owners",
    }

    return {
        "researcher": mock_researcher,
        "developer": mock_developer,
        "monetization": mock_monetization,
        "marketing": mock_marketing,
    }


@patch("agent_team.team_config.ResearchAgent")
@patch("agent_team.team_config.DeveloperAgent")
@patch("agent_team.team_config.MonetizationAgent")
@patch("agent_team.team_config.MarketingAgent")
def test_niche_to_solution_workflow(
    mock_marketing_class,
    mock_monetization_class,
    mock_developer_class,
    mock_researcher_class,
    mock_agents,
):
    """Test the complete niche-to-solution workflow."""
    # Set up the mock agents
    mock_researcher_class.return_value = mock_agents["researcher"]
    mock_developer_class.return_value = mock_agents["developer"]
    mock_monetization_class.return_value = mock_agents["monetization"]
    mock_marketing_class.return_value = mock_agents["marketing"]

    # Create a team
    team = AgentTeam("Test Team")

    # Run niche analysis
    niches = team.run_niche_analysis(["e-commerce"])

    # Check that the researcher's analyze_market_segments method was called
    mock_agents["researcher"].analyze_market_segments.assert_called_once_with(
        ["e-commerce"]
    )

    # Check that niches were returned
    assert len(niches) == 2
    assert niches[0]["name"] == "Inventory Management"
    assert niches[1]["name"] == "Product Description Generation"

    # Select the top niche
    selected_niche = niches[0]

    # Develop a solution
    solution = team.develop_solution(selected_niche)

    # Check that the developer's design_solution method was called
    mock_agents["developer"].design_solution.assert_called_once_with(selected_niche)

    # Check that a solution was returned
    assert solution["name"] == "AI Inventory Manager"
    assert len(solution["features"]) == 2

    # Create a monetization strategy
    monetization = team.create_monetization_strategy(solution)

    # Check that the monetization agent's create_strategy method was called
    mock_agents["monetization"].create_strategy.assert_called_once_with(solution)

    # Check that a monetization strategy was returned
    assert monetization["name"] == "Freemium Strategy"
    assert (
        monetization["subscription_model"]["name"] == "Inventory Manager Subscription"
    )
    assert len(monetization["subscription_model"]["tiers"]) == 2

    # Create a marketing plan
    marketing_plan = team.create_marketing_plan(selected_niche, solution, monetization)

    # Check that the marketing agent's create_plan method was called
    mock_agents["marketing"].create_plan.assert_called_once_with(
        selected_niche, solution, monetization
    )

    # Check that a marketing plan was returned
    assert marketing_plan["name"] == "Inventory Manager Marketing Plan"
    assert "content" in marketing_plan["channels"]
    assert marketing_plan["target_audience"] == "E-commerce store owners"
