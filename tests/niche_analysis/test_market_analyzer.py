"""
Tests for the MarketAnalyzer class.
"""

from datetime import datetime
from unittest.mock import patch


from niche_analysis.market_analyzer import MarketAnalyzer


def test_market_analyzer_init():
    """Test MarketAnalyzer initialization."""
    analyzer = MarketAnalyzer()

    # Check that the analyzer has the expected attributes
    assert analyzer.name == "Market Analyzer"
    assert analyzer.description == "Analyzes market segments to identify potential niches"


def test_analyze_market():
    """Test analyze_market method."""
    analyzer = MarketAnalyzer()

    # Analyze a market segment
    result = analyzer.analyze_market("e-commerce")

    # Check that the result has the expected keys
    assert "id" in result
    assert "name" in result
    assert "description" in result
    assert "market_size" in result
    assert "growth_rate" in result
    assert "competition" in result
    assert "barriers_to_entry" in result
    assert "technological_adoption" in result
    assert "potential_niches" in result
    assert "target_users" in result

    # Check that the values are as expected
    assert result["name"] == "E-Commerce"
    assert "e-commerce" in result["description"].lower()


def test_analyze_market_unknown_segment():
    """Test analyze_market method with an unknown segment."""
    analyzer = MarketAnalyzer()

    # Analyze an unknown market segment
    result = analyzer.analyze_market("unknown_segment")

    # Check that the result has the expected keys
    assert "id" in result
    assert "name" in result
    assert "description" in result
    assert "market_size" in result
    assert "growth_rate" in result
    assert "competition" in result
    assert "barriers_to_entry" in result
    assert "technological_adoption" in result
    assert "potential_niches" in result
    assert "target_users" in result

    # Check that the values are as expected
    assert result["name"] == "Unknown_segment"
    assert "unknown_segment" in result["description"].lower()
    assert result["market_size"] == "unknown"
    assert result["growth_rate"] == "unknown"


def test_analyze_competition():
    """Test analyze_competition method."""
    analyzer = MarketAnalyzer()

    # Analyze competition in a niche
    result = analyzer.analyze_competition("inventory management")

    # Check that the result has the expected keys
    assert "id" in result
    assert "niche" in result
    assert "competitor_count" in result
    assert "top_competitors" in result
    assert "market_saturation" in result
    assert "entry_barriers" in result
    assert "differentiation_opportunities" in result
    assert "timestamp" in result

    # Check that the values are as expected
    assert result["niche"] == "inventory management"
    assert isinstance(result["competitor_count"], int)
    assert len(result["top_competitors"]) > 0
    assert isinstance(result["top_competitors"][0], dict)
    assert "name" in result["top_competitors"][0]
    assert "description" in result["top_competitors"][0]
    assert "market_share" in result["top_competitors"][0]
    assert "strengths" in result["top_competitors"][0]
    assert "weaknesses" in result["top_competitors"][0]
    assert "pricing" in result["top_competitors"][0]


@patch("niche_analysis.market_analyzer.datetime")
def test_analyze_competition_timestamp(mock_datetime):
    """Test that analyze_competition includes a timestamp."""
    # Mock datetime.now() to return a fixed datetime
    mock_now = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = mock_now

    analyzer = MarketAnalyzer()

    # Analyze competition in a niche
    result = analyzer.analyze_competition("inventory management")

    # Check that the timestamp is the mocked datetime
    assert result["timestamp"] == mock_now.isoformat()


def test_analyze_target_users():
    """Test analyze_target_users method."""
    analyzer = MarketAnalyzer()

    # Analyze target users for a niche
    result = analyzer.analyze_target_users("content creation")

    # Check that the result has the expected keys
    assert "id" in result
    assert "niche" in result
    assert "user_segments" in result
    assert "demographics" in result
    assert "psychographics" in result
    assert "pain_points" in result
    assert "goals" in result
    assert "buying_behavior" in result
    assert "timestamp" in result

    # Check that the values are as expected
    assert result["niche"] == "content creation"
    assert len(result["user_segments"]) > 0
    assert isinstance(result["user_segments"][0], dict)
    assert "name" in result["user_segments"][0]
    assert "description" in result["user_segments"][0]
    assert "size" in result["user_segments"][0]
    assert "priority" in result["user_segments"][0]
