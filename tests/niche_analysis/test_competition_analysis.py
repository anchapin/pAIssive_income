"""Tests for competitive analysis functionality."""

import pytest

from niche_analysis.market_analyzer import MarketAnalyzer


@pytest.fixture
def market_analyzer():
    """Create a MarketAnalyzer instance for testing."""
    return MarketAnalyzer()


class TestCompetitionAnalysis:
    """Tests for competition analysis."""

    def test_competitor_profile_generation(self, market_analyzer):
        """Test generation of competitor profiles."""
        result = market_analyzer.analyze_competition("inventory management")

        # Verify basic structure
        assert "id" in result
        assert "niche" in result
        assert "competitor_count" in result
        assert "top_competitors" in result

        # Test competitor count
        assert isinstance(result["competitor_count"], int)
        assert result["competitor_count"] > 0

        # Test competitor profiles
        competitors = result["top_competitors"]
        assert len(competitors) > 0

        # Test first competitor profile structure
        competitor = competitors[0]
        assert "name" in competitor
        assert "description" in competitor
        assert "market_share" in competitor
        assert "strengths" in competitor
        assert "weaknesses" in competitor
        assert "pricing" in competitor

        # Verify market share format
        assert isinstance(competitor["market_share"], str)
        assert "%" in competitor["market_share"]

        # Verify arrays have content
        assert len(competitor["strengths"]) > 0
        assert len(competitor["weaknesses"]) > 0

    def test_competitor_ranking(self, market_analyzer):
        """Test competitor ranking and ordering."""
        result = market_analyzer.analyze_competition("inventory management")

        # Get market shares as numbers for comparison
        shares = [float(c["market_share"].strip("%")) for c in result["top_competitors"]]

        # Verify competitors are ordered by market share
        assert shares == sorted(shares, reverse=True)

        # Verify total market share is realistic (< 100%)
        assert sum(shares) <= 100

    def test_market_position_analysis(self, market_analyzer):
        """Test market position and competitive landscape analysis."""
        result = market_analyzer.analyze_competition("inventory management")

        # Test market saturation assessment
        assert "market_saturation" in result
        assert result["market_saturation"] in ["high", "medium", "low"]

        # Test entry barriers assessment
        assert "entry_barriers" in result
        assert result["entry_barriers"] in ["high", "medium", "low"]

        # Test differentiation opportunities
        assert "differentiation_opportunities" in result
        assert isinstance(result["differentiation_opportunities"], list)
        assert len(result["differentiation_opportunities"]) > 0

    def test_strength_weakness_analysis(self, market_analyzer):
        """Test analysis of competitor strengths and weaknesses."""
        result = market_analyzer.analyze_competition("inventory management")

        for competitor in result["top_competitors"]:
            # Verify strengths and weaknesses exist
            assert len(competitor["strengths"]) > 0
            assert len(competitor["weaknesses"]) > 0

            # Verify strengths and weaknesses are different
            assert set(competitor["strengths"]).isdisjoint(set(competitor["weaknesses"]))

            # Verify pricing information exists and has expected format
            assert "$" in competitor["pricing"]
            assert "month" in competitor["pricing"].lower()

    def test_competition_cache_behavior(self, market_analyzer):
        """Test caching behavior for competition analysis."""
        # First analysis call
        first_result = market_analyzer.analyze_competition("inventory management")

        # Second call should use cache
        second_result = market_analyzer.analyze_competition("inventory management")
        assert first_result == second_result

        # Force refresh should bypass cache
        fresh_result = market_analyzer.analyze_competition(
            "inventory management", force_refresh=True
        )
