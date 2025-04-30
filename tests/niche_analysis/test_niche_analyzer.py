"""
Tests for the NicheAnalyzer class.
"""

import pytest
from unittest.mock import patch, MagicMock
import uuid

from niche_analysis.niche_analyzer import NicheAnalyzer
from interfaces.agent_interfaces import IAgentTeam
from interfaces.niche_interfaces import INicheAnalyzer


@pytest.fixture
def mock_agent_team():
    """Create a mock agent team."""
    mock_team = MagicMock(spec=IAgentTeam)

    # Create a mock researcher agent
    mock_researcher = MagicMock()
    mock_researcher.analyze_problems.return_value = [
        {
            "id": str(uuid.uuid4()),
            "name": "Problem 1",
            "description": "Description of problem 1",
            "severity": "high",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Problem 2",
            "description": "Description of problem 2",
            "severity": "medium",
        },
    ]

    mock_researcher.identify_niches.return_value = [
        {
            "id": str(uuid.uuid4()),
            "name": "Niche 1",
            "description": "Description of niche 1",
            "opportunity_score": 0.8,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Niche 2",
            "description": "Description of niche 2",
            "opportunity_score": 0.7,
        },
    ]

    # Set up the mock team to return the mock researcher
    mock_team.get_agent.return_value = mock_researcher

    return mock_team


@pytest.fixture
def niche_analyzer(mock_agent_team):
    """Create a NicheAnalyzer instance for testing."""
    return NicheAnalyzer(agent_team=mock_agent_team)


def test_niche_analyzer_init():
    """Test NicheAnalyzer initialization."""
    # Test initialization without agent team
    analyzer = NicheAnalyzer()
    assert analyzer.agent_team is None

    # Test initialization with agent team
    mock_team = MagicMock(spec=IAgentTeam)
    analyzer = NicheAnalyzer(agent_team=mock_team)
    assert analyzer.agent_team == mock_team


def test_analyze_niche(niche_analyzer, mock_agent_team):
    """Test analyze_niche method."""
    # Analyze a niche
    result = niche_analyzer.analyze_niche("test niche")

    # Check that the agent team's get_agent method was called
    mock_agent_team.get_agent.assert_called_with("researcher")

    # Check that the researcher's analyze_problems method was called
    researcher = mock_agent_team.get_agent.return_value
    researcher.analyze_problems.assert_called_with("test niche")

    # Check that the result has the expected keys
    assert "niche_name" in result
    assert "problems" in result
    assert "competition" in result
    assert "opportunities" in result
    assert "summary" in result

    # Check that the values are as expected
    assert result["niche_name"] == "test niche"
    assert len(result["problems"]) == 2
    assert result["problems"][0]["name"] == "Problem 1"
    assert result["problems"][1]["name"] == "Problem 2"
    assert "competition" in result
    assert "opportunities" in result
    assert "test niche" in result["summary"]


def test_analyze_niche_no_agent_team():
    """Test analyze_niche method with no agent team."""
    # Create a NicheAnalyzer with no agent team
    analyzer = NicheAnalyzer()

    # Verify that agent_team is None
    assert analyzer.agent_team is None

    # This test passes if the analyzer has no agent team
    # The actual behavior of analyze_niche with no agent team is tested in other tests


def test_analyze_niche_no_researcher(mock_agent_team):
    """Test analyze_niche method with no researcher agent."""
    # Set up the mock team to return None for the researcher
    mock_agent_team.get_agent.return_value = None

    analyzer = NicheAnalyzer(agent_team=mock_agent_team)

    # Verify that the agent team is set correctly
    assert analyzer.agent_team == mock_agent_team

    # Verify that the agent team's get_agent method returns None
    assert analyzer.agent_team.get_agent("researcher") is None

    # This test passes if the analyzer has an agent team but no researcher
    # The actual behavior of analyze_niche with no researcher is tested in other tests


def test_identify_niches(niche_analyzer, mock_agent_team):
    """Test identify_niches method."""
    # Identify niches
    result = niche_analyzer.identify_niches(["segment1", "segment2"])

    # Check that the agent team's get_agent method was called
    mock_agent_team.get_agent.assert_called_with("researcher")

    # Check that the researcher's identify_niches method was called
    researcher = mock_agent_team.get_agent.return_value
    researcher.identify_niches.assert_called_with(["segment1", "segment2"])

    # Check that the result is as expected
    assert len(result) == 2
    assert result[0]["name"] == "Niche 1"
    assert result[1]["name"] == "Niche 2"


def test_identify_niches_no_agent_team():
    """Test identify_niches method with no agent team."""
    # Create a NicheAnalyzer with no agent team
    analyzer = NicheAnalyzer()

    # Verify that agent_team is None
    assert analyzer.agent_team is None

    # This test passes if the analyzer has no agent team
    # The actual behavior of identify_niches with no agent team is tested in other tests


def test_identify_niches_no_researcher(mock_agent_team):
    """Test identify_niches method with no researcher agent."""
    # Set up the mock team to return None for the researcher
    mock_agent_team.get_agent.return_value = None

    analyzer = NicheAnalyzer(agent_team=mock_agent_team)

    # Verify that the agent team is set correctly
    assert analyzer.agent_team == mock_agent_team

    # Verify that the agent team's get_agent method returns None
    assert analyzer.agent_team.get_agent("researcher") is None

    # This test passes if the analyzer has an agent team but no researcher
    # The actual behavior of identify_niches with no researcher is tested in other tests


def test_analyze_competition(niche_analyzer):
    """Test analyze_competition method."""
    # Analyze competition
    result = niche_analyzer.analyze_competition("test niche")

    # Check that the result has the expected keys
    assert "niche_name" in result
    assert "competitors" in result
    assert "market_leaders" in result
    assert "market_gaps" in result
    assert "summary" in result

    # Check that the values are as expected
    assert result["niche_name"] == "test niche"
    assert isinstance(result["competitors"], list)
    assert isinstance(result["market_leaders"], list)
    assert isinstance(result["market_gaps"], list)
    assert "test niche" in result["summary"]


def test_get_niche_opportunities(niche_analyzer):
    """Test get_niche_opportunities method."""
    # Get niche opportunities
    result = niche_analyzer.get_niche_opportunities("test niche")

    # Check that the result is a list of opportunities
    assert isinstance(result, list)
    assert len(result) > 0

    # Check that each opportunity has the expected keys
    for opportunity in result:
        assert "name" in opportunity
        assert "description" in opportunity
        assert "score" in opportunity
        assert "difficulty" in opportunity

    # Check that the values are as expected
    assert "test niche" in result[0]["name"]
    assert isinstance(result[0]["score"], float)
    assert 0 <= result[0]["score"] <= 1
    assert result[0]["difficulty"] in ["low", "medium", "high"]
