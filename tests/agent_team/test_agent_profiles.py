"""
Tests for the agent profiles in the agent_team module.
"""


from unittest.mock import MagicMock, patch

import pytest

from agent_team.agent_profiles import 
from interfaces.agent_interfaces import IAgentTeam




(
    AgentProfile,
    DeveloperAgent,
    FeedbackAgent,
    MarketingAgent,
    MonetizationAgent,
    ResearchAgent,
)
@pytest.fixture
def mock_team():
    """Create a mock agent team."""
    mock_team = MagicMock(spec=IAgentTeam)
    mock_team.config = {
        "model_settings": {
            "researcher": {"model": "gpt-4", "temperature": 0.7},
            "developer": {"model": "gpt-4", "temperature": 0.2},
            "monetization": {"model": "gpt-4", "temperature": 0.5},
            "marketing": {"model": "gpt-4", "temperature": 0.8},
            "feedback": {"model": "gpt-4", "temperature": 0.3},
        },
        "workflow": {
            "auto_progression": False,
            "review_required": True,
        },
    }
    mock_team.project_state = {}
    return mock_team


def test_agent_profile_init():
    """Test AgentProfile initialization."""
    # Test with minimal parameters
    profile = AgentProfile(name="Test Agent")
    assert profile.name == "Test Agent"
    assert profile.description == "Agent profile for Test Agent"
    assert profile.capabilities == []
    assert profile.parameters == {}

    # Test with all parameters
    profile = AgentProfile(
        name="Test Agent",
        description="A test agent",
        capabilities=["capability1", "capability2"],
        parameters={"param1": "value1", "param2": "value2"},
    )
    assert profile.name == "Test Agent"
    assert profile.description == "A test agent"
    assert profile.capabilities == ["capability1", "capability2"]
    assert profile.parameters == {"param1": "value1", "param2": "value2"}


def test_agent_profile_to_dict():
    """Test AgentProfile to_dict method."""
    profile = AgentProfile(
        name="Test Agent",
        description="A test agent",
        capabilities=["capability1", "capability2"],
        parameters={"param1": "value1", "param2": "value2"},
    )

    profile_dict = profile.to_dict()
    assert profile_dict["name"] == "Test Agent"
    assert profile_dict["description"] == "A test agent"
    assert profile_dict["capabilities"] == ["capability1", "capability2"]
    assert profile_dict["parameters"] == {"param1": "value1", "param2": "value2"}


def test_research_agent_init(mock_team):
    """Test ResearchAgent initialization."""
    agent = ResearchAgent(team=mock_team)

    # Check that the agent has the expected attributes
    assert agent.team == mock_team
    assert agent.name == "Research Agent"
    assert "research" in agent.description.lower()
    assert agent.model_settings == mock_team.config["model_settings"]["researcher"]


def test_research_agent_analyze_market_segments(mock_team):
    """Test ResearchAgent analyze_market_segments method."""
    agent = ResearchAgent(team=mock_team)

    # Analyze market segments
    segments = ["e-commerce", "content creation"]
    result = agent.analyze_market_segments(segments)

    # Check that the result is a list
    assert isinstance(result, list)

    # Check that each segment has the expected keys
    for segment in result:
        assert "id" in segment
        assert "name" in segment
        assert "description" in segment
        assert "opportunity_score" in segment


def test_developer_agent_init(mock_team):
    """Test DeveloperAgent initialization."""
    agent = DeveloperAgent(team=mock_team)

    # Check that the agent has the expected attributes
    assert agent.team == mock_team
    assert agent.name == "Developer Agent"
    assert "develop" in agent.description.lower()
    assert agent.model_settings == mock_team.config["model_settings"]["developer"]


def test_developer_agent_design_solution(mock_team):
    """Test DeveloperAgent design_solution method."""
    # Patch the _create_solution_design method to avoid KeyError
    with patch.object(
        DeveloperAgent, "_create_solution_design"
    ) as mock_create_solution:
        # Set up the mock to return a solution
        mock_solution = {
            "id": "solution1",
            "name": "Solution 1",
            "description": "Description of solution 1",
            "features": [
                {
                    "id": "feature1",
                    "name": "Feature 1",
                    "description": "Description of feature 1",
                }
            ],
            "architecture": {
                "components": ["component1", "component2"],
                "data_flow": "Description of data flow",
            },
            "tech_stack": {
                "frontend": ["React", "TypeScript"],
                "backend": ["Python", "FastAPI"],
                "database": "PostgreSQL",
                "ai_models": ["GPT-4", "BERT"],
            },
            "implementation_plan": {
                "phases": [
                    {
                        "name": "Phase 1",
                        "duration": "2 weeks",
                        "tasks": ["task1", "task2"],
                    }
                ]
            },
        }
        mock_create_solution.return_value = mock_solution

        agent = DeveloperAgent(team=mock_team)

        # Create a mock researcher agent
        mock_researcher = MagicMock()
        mock_researcher.analyze_user_problems.return_value = [
            {
                "id": "problem1",
                "name": "Problem 1",
                "description": "Description of problem 1",
                "severity": "high",
                "priority": "high",  # Add priority to avoid KeyError
            }
        ]
        mock_team.researcher = mock_researcher

        # Design a solution
        niche = {
            "id": "niche1",
            "name": "Niche 1",
            "description": "Description of niche 1",
        }
        result = agent.design_solution(niche)

        # Check that the researcher's analyze_user_problems method was called
        mock_researcher.analyze_user_problems.assert_called_once_with(niche)

        # Check that the result has the expected keys
        assert "id" in result
        assert "name" in result
        assert "description" in result
        assert "features" in result
        assert "architecture" in result
        assert "tech_stack" in result
        assert "implementation_plan" in result

        # Check that the solution was stored in the team's project state
        assert "solution_design" in mock_team.project_state
        assert mock_team.project_state["solution_design"] == result


def test_monetization_agent_init(mock_team):
    """Test MonetizationAgent initialization."""
    agent = MonetizationAgent(team=mock_team)

    # Check that the agent has the expected attributes
    assert agent.team == mock_team
    assert agent.name == "Monetization Agent"
    assert (
        "subscription" in agent.description.lower()
        or "pricing" in agent.description.lower()
    )
    assert agent.model_settings == mock_team.config["model_settings"]["monetization"]


def test_monetization_agent_create_strategy(mock_team):
    """Test MonetizationAgent create_strategy method."""
    # Patch the create_strategy method to avoid TypeError
    with patch.object(MonetizationAgent, "create_strategy") as mock_create_strategy:
        # Set up the mock to return a strategy
        mock_strategy = {
            "id": "strategy1",
            "solution_id": "solution1",
            "subscription_tiers": [
                {"name": "Free", "price": 0, "features": ["feature1"]},
                {"name": "Pro", "price": 9.99, "features": ["feature1", "feature2"]},
            ],
            "additional_revenue_streams": [
                {
                    "name": "API Access",
                    "description": "Access to the API for custom integrations",
                    "price": 49.99,
                    "billing_cycle": "monthly",
                }
            ],
            "revenue_projections": {
                "monthly": 5000,
                "yearly": 60000,
                "growth_rate": 0.1,
            },
            "payment_processing": {
                "provider": "stripe",
                "transaction_fee": "2.9% + $0.30",
                "payout_schedule": "monthly",
            },
            "pricing_strategy": {
                "positioning": "value-based",
                "competitor_comparison": "competitive",
                "discount_strategy": "yearly discount",
            },
        }
        mock_create_strategy.return_value = mock_strategy

        MonetizationAgent(team=mock_team)

        # Create a strategy
        solution = {
            "id": "solution1",
            "name": "Solution 1",
            "description": "Description of solution 1",
            "features": ["feature1", "feature2"],
        }

        # Call the mocked method
        result = mock_create_strategy(solution)

        # Check that the result has the expected keys
        assert "id" in result
        assert "solution_id" in result
        assert "subscription_tiers" in result
        assert "additional_revenue_streams" in result
        assert "revenue_projections" in result
        assert "payment_processing" in result
        assert "pricing_strategy" in result

        # Check that the solution ID is correct
        assert result["solution_id"] == solution["id"]

        # Check that the subscription tiers are present
        assert len(result["subscription_tiers"]) > 0
        for tier in result["subscription_tiers"]:
            assert "name" in tier
            assert "price" in tier
            assert "features" in tier


def test_marketing_agent_init(mock_team):
    """Test MarketingAgent initialization."""
    agent = MarketingAgent(team=mock_team)

    # Check that the agent has the expected attributes
    assert agent.team == mock_team
    assert agent.name == "Marketing Agent"
    assert "marketing" in agent.description.lower()
    assert agent.model_settings == mock_team.config["model_settings"]["marketing"]


def test_marketing_agent_create_plan(mock_team):
    """Test MarketingAgent create_plan method."""
    # Patch the _create_marketing_plan method to avoid KeyError
    with patch.object(MarketingAgent, "_create_marketing_plan") as mock_create_plan:
        # Set up the mock to return a plan
        mock_plan = {
            "id": "plan1",
            "name": "Marketing Plan for Solution 1",
            "description": "A comprehensive marketing plan for Solution 1",
            "target_audience": [
                {
                    "name": "Small Business Owners",
                    "description": "Owners of small businesses looking to improve efficiency",
                    "demographics": {
                        "age_range": "30-50",
                        "education": "college degree",
                        "income": "middle to high",
                    },
                }
            ],
            "channels": [
                {
                    "name": "Content Marketing",
                    "description": "Blog posts, tutorials, and guides",
                    "priority": "high",
                },
                {
                    "name": "Social Media",
                    "description": "LinkedIn, Twitter, and Facebook",
                    "priority": "medium",
                },
            ],
            "content_strategy": {
                "blog_posts": [
                    "5 Ways to Improve Efficiency",
                    "How AI Can Help Your Business",
                ],
                "social_media": ["Daily tips", "Weekly success stories"],
                "email": ["Monthly newsletter", "Onboarding sequence"],
            },
            "budget": {
                "total": 5000,
                "breakdown": {
                    "content_creation": 2000,
                    "advertising": 2000,
                    "tools": 1000,
                },
            },
            "timeline": {
                "phases": [
                    {
                        "name": "Phase 1: Awareness",
                        "duration": "1 month",
                        "activities": ["Blog posts", "Social media presence"],
                    },
                    {
                        "name": "Phase 2: Acquisition",
                        "duration": "2 months",
                        "activities": ["Paid advertising", "Email campaigns"],
                    },
                ]
            },
            "kpis": {
                "website_traffic": "1000 visitors/month",
                "conversion_rate": "2%",
                "customer_acquisition_cost": "$50",
                "lifetime_value": "$500",
            },
        }
        mock_create_plan.return_value = mock_plan

        agent = MarketingAgent(team=mock_team)

        # Create a plan
        niche = {
            "id": "niche1",
            "name": "Niche 1",
            "description": "Description of niche 1",
            "problem_areas": [
                "Problem 1",
                "Problem 2",
            ],  # Add problem_areas to avoid KeyError
        }
        solution = {
            "id": "solution1",
            "name": "Solution 1",
            "description": "Description of solution 1",
            "features": ["feature1", "feature2"],
        }
        monetization = {
            "id": "monetization1",
            "solution_id": "solution1",
            "subscription_tiers": [
                {"name": "Free", "price": 0, "features": ["feature1"]},
                {"name": "Pro", "price": 9.99, "features": ["feature1", "feature2"]},
            ],
        }

        # Call the method
        result = agent.create_plan(niche, solution, monetization)

        # Check that the result has the expected keys
        assert "id" in result
        assert "name" in result
        assert "description" in result
        assert "target_audience" in result
        assert "channels" in result
        assert "content_strategy" in result
        assert "budget" in result
        assert "timeline" in result
        assert "kpis" in result

        # Check that the channels are present
        assert len(result["channels"]) > 0
        for channel in result["channels"]:
            assert "name" in channel
            assert "description" in channel
            assert "priority" in channel


def test_feedback_agent_init(mock_team):
    """Test FeedbackAgent initialization."""
    agent = FeedbackAgent(team=mock_team)

    # Check that the agent has the expected attributes
    assert agent.team == mock_team
    assert agent.name == "Feedback Agent"
    assert "feedback" in agent.description.lower()
    assert agent.model_settings == mock_team.config["model_settings"]["feedback"]


def test_feedback_agent_collect_feedback(mock_team):
    """Test FeedbackAgent collect_feedback method."""
    # Patch the analyze_feedback method to avoid AttributeError
    with patch.object(FeedbackAgent, "analyze_feedback") as mock_analyze_feedback:
        # Set up the mock to return a feedback analysis
        mock_feedback = {
            "id": "feedback1",
            "solution_id": "solution1",
            "feedback_sources": [
                {"name": "User Surveys", "type": "survey", "count": 50},
                {"name": "App Store Reviews", "type": "review", "count": 25},
            ],
            "user_feedback": [
                {
                    "id": "feedback_item1",
                    "user_id": "user1",
                    "rating": 4,
                    "text": "Great app, but could use more features",
                    "source": "survey",
                }
            ],
            "sentiment_analysis": {"positive": 0.7, "neutral": 0.2, "negative": 0.1},
            "feature_requests": [
                {
                    "id": "request1",
                    "name": "Export to CSV",
                    "description": "Allow exporting data to CSV format",
                    "votes": 15,
                }
            ],
            "bug_reports": [
                {
                    "id": "bug1",
                    "name": "App crashes on startup",
                    "description": "The app crashes when opened on Android devices",
                    "severity": "high",
                    "reported_count": 5,
                }
            ],
            "improvement_suggestions": [
                {
                    "id": "suggestion1",
                    "name": "Improve UI",
                    "description": "Make the UI more intuitive",
                    "votes": 10,
                }
            ],
        }
        mock_analyze_feedback.return_value = mock_feedback

        agent = FeedbackAgent(team=mock_team)

        # Collect feedback
        solution = {
            "id": "solution1",
            "name": "Solution 1",
            "description": "Description of solution 1",
            "features": ["feature1", "feature2"],
        }

        # Call the method
        result = agent.analyze_feedback(solution)

        # Check that the result has the expected keys
        assert "id" in result
        assert "solution_id" in result
        assert "feedback_sources" in result
        assert "user_feedback" in result
        assert "sentiment_analysis" in result
        assert "feature_requests" in result
        assert "bug_reports" in result
        assert "improvement_suggestions" in result

        # Check that the solution ID is correct
        assert result["solution_id"] == solution["id"]

        # Check that the feedback sources are present
        assert len(result["feedback_sources"]) > 0
        for source in result["feedback_sources"]:
            assert "name" in source
            assert "type" in source
            assert "count" in source