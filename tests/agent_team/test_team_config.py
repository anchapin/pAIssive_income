"""
Tests for the AgentTeam class.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from agent_team.team_config import AgentTeam


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock configuration file."""
    config = {
        "model_settings": {
            "researcher": {"model": "custom-model", "temperature": 0.5},
            "developer": {"model": "custom-model", "temperature": 0.2},
            "monetization": {"model": "custom-model", "temperature": 0.3},
            "marketing": {"model": "custom-model", "temperature": 0.7},
            "feedback": {"model": "custom-model", "temperature": 0.4},
        },
        "workflow": {
            "auto_progression": True,
            "review_required": False,
        },
    }

    config_path = os.path.join(temp_dir, "test_config.json")

    with open(config_path, "w") as f:
        json.dump(config, f)

    return config_path


def test_agent_team_init():
    """Test AgentTeam initialization with default config."""
    team = AgentTeam("Test Team")

    # Check that the team has the expected attributes
    assert team.project_name == "Test Team"
    assert isinstance(team.config, dict)
    assert "model_settings" in team.config
    assert "workflow" in team.config

    # Check that the agents were initialized
    assert team.researcher is not None
    assert team.developer is not None
    assert team.monetization is not None
    assert team.marketing is not None
    assert team.feedback is not None


def test_agent_team_init_with_config(mock_config_file):
    """Test AgentTeam initialization with custom config."""
    team = AgentTeam("Test Team", config_path=mock_config_file)

    # Check that the team has the expected attributes
    assert team.project_name == "Test Team"
    assert isinstance(team.config, dict)
    assert "model_settings" in team.config
    assert "workflow" in team.config

    # Check that the custom config was loaded
    assert team.config["workflow"]["auto_progression"] is True
    assert team.config["workflow"]["review_required"] is False
    assert team.config["model_settings"]["researcher"]["model"] == "custom-model"
    assert team.config["model_settings"]["researcher"]["temperature"] == 0.5


@patch("agent_team.team_config.ResearchAgent")
def test_run_niche_analysis(mock_researcher_class):
    """Test run_niche_analysis method."""
    # Mock the ResearchAgent.analyze_market_segments method
    mock_researcher = MagicMock()
    mock_researcher.analyze_market_segments.return_value = [
        {
            "id": "niche1",
            "name": "Niche 1",
            "opportunity_score": 0.8,
        },
        {
            "id": "niche2",
            "name": "Niche 2",
            "opportunity_score": 0.6,
        },
    ]
    mock_researcher_class.return_value = mock_researcher

    # Create a team
    team = AgentTeam("Test Team")

    # Run niche analysis
    result = team.run_niche_analysis(["e-commerce", "content creation"])

    # Check that the researcher's analyze_market_segments method was called
    mock_researcher.analyze_market_segments.assert_called_once_with(
        ["e-commerce", "content creation"]
    )

    # Check that the result is the return value from analyze_market_segments
    assert result == mock_researcher.analyze_market_segments.return_value
    assert len(result) == 2
    assert result[0]["name"] == "Niche 1"
    assert result[1]["name"] == "Niche 2"


@patch("agent_team.team_config.DeveloperAgent")
def test_develop_solution(mock_developer_class):
    """Test develop_solution method."""
    # Mock the DeveloperAgent.design_solution method
    mock_developer = MagicMock()
    mock_developer.design_solution.return_value = {
        "id": "solution1",
        "name": "Solution 1",
        "description": "A solution for the niche",
        "features": [
            {
                "id": "feature1",
                "name": "Feature 1",
                "description": "Description of feature 1",
                "complexity": "medium",
                "development_cost": "medium",
                "value_proposition": "Value of feature 1",
            },
            {
                "id": "feature2",
                "name": "Feature 2",
                "description": "Description of feature 2",
                "complexity": "low",
                "development_cost": "low",
                "value_proposition": "Value of feature 2",
            },
        ],
        "market_data": {
            "target_audience": "Target audience",
            "market_size": "medium",
            "competition": "low",
        },
    }
    mock_developer_class.return_value = mock_developer

    # Create a team
    team = AgentTeam("Test Team")

    # Create a mock niche that conforms to the NicheSchema
    niche = {
        "id": "niche1",
        "name": "Niche 1",
        "market_segment": "e-commerce",
        "description": "A niche in e-commerce",
        "opportunity_score": 0.8,
        "market_data": {"market_size": "medium", "growth_rate": "high", "competition": "low"},
        "problems": [
            {
                "id": "problem1",
                "name": "Problem 1",
                "description": "Description of problem 1",
                "severity": "high",
            }
        ],
    }

    # Develop a solution
    result = team.develop_solution(niche)

    # Check that the developer's design_solution method was called
    # We can't use assert_called_once_with because the niche object is modified
    # by the develop_solution method before it's passed to design_solution
    assert mock_developer.design_solution.call_count == 1
    call_args = mock_developer.design_solution.call_args[0][0]
    assert call_args["id"] == niche["id"]
    assert call_args["name"] == niche["name"]
    assert call_args["market_segment"] == niche["market_segment"]

    # Check that the result is the return value from design_solution
    assert result == mock_developer.design_solution.return_value
    assert result["name"] == "Solution 1"
    assert len(result["features"]) == 2
    assert result["features"][0]["id"] == "feature1"
    assert result["features"][1]["id"] == "feature2"


@patch("agent_team.team_config.MonetizationAgent")
def test_create_monetization_strategy(mock_monetization_class):
    """Test create_monetization_strategy method."""
    # Mock the MonetizationAgent.create_strategy method
    mock_monetization = MagicMock()
    mock_monetization.create_strategy.return_value = {
        "id": "strategy1",
        "name": "Strategy 1",
        "subscription_model": {
            "name": "Freemium Model",
            "tiers": ["free", "pro", "enterprise"],
        },
    }
    mock_monetization_class.return_value = mock_monetization

    # Create a team
    team = AgentTeam("Test Team")

    # Create a mock solution
    solution = {
        "id": "solution1",
        "name": "Solution 1",
        "features": ["feature1", "feature2"],
    }

    # Create a monetization strategy
    result = team.create_monetization_strategy(solution)

    # Check that the monetization agent's create_strategy method was called
    mock_monetization.create_strategy.assert_called_once_with(solution)

    # Check that the result is the return value from create_strategy
    assert result == mock_monetization.create_strategy.return_value
    assert result["name"] == "Strategy 1"
    assert result["subscription_model"]["name"] == "Freemium Model"
    assert "free" in result["subscription_model"]["tiers"]
    assert "pro" in result["subscription_model"]["tiers"]
    assert "enterprise" in result["subscription_model"]["tiers"]


@patch("agent_team.team_config.MarketingAgent")
def test_create_marketing_plan(mock_marketing_class):
    """Test create_marketing_plan method."""
    # Mock the MarketingAgent.create_plan method
    mock_marketing = MagicMock()
    mock_marketing.create_plan.return_value = {
        "id": "plan1",
        "name": "Marketing Plan 1",
        "channels": ["content", "social", "email"],
    }
    mock_marketing_class.return_value = mock_marketing

    # Create a team
    team = AgentTeam("Test Team")

    # Create mock data
    niche = {"id": "niche1", "name": "Niche 1"}
    solution = {"id": "solution1", "name": "Solution 1"}
    monetization = {"id": "strategy1", "name": "Strategy 1"}

    # Create a marketing plan
    result = team.create_marketing_plan(niche, solution, monetization)

    # Check that the marketing agent's create_plan method was called
    mock_marketing.create_plan.assert_called_once_with(niche, solution, monetization)

    # Check that the result is the return value from create_plan
    assert result == mock_marketing.create_plan.return_value
    assert result["name"] == "Marketing Plan 1"
    assert "content" in result["channels"]
    assert "social" in result["channels"]
    assert "email" in result["channels"]
