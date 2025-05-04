"""
Tests for competitive analysis functionality.
"""

import pytest

from niche_analysis.competitive_analysis import (
    CompetitorAnalyzer,
    MarketPositionMapper,
    StrengthWeaknessAnalyzer,
)
from niche_analysis.errors import InvalidCompetitorDataError

class TestCompetitiveAnalysis:
    """Test cases for competitive analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.competitor_analyzer = CompetitorAnalyzer()
        self.sw_analyzer = StrengthWeaknessAnalyzer()
        self.position_mapper = MarketPositionMapper()

    def test_competitor_identification(self):
        """Test competitor identification."""
        # Test data
        market_data = {
            "niche": "AI Development Tools",
            "target_audience": "Software Developers",
            "price_range": {"min": 0, "max": 500},
            "features": ["code completion", "test generation", "refactoring"],
        }

        # Identify competitors
        competitors = self.competitor_analyzer.identify_competitors(market_data)

        # Validate competitor identification
        assert "direct_competitors" in competitors
        assert "indirect_competitors" in competitors
        assert isinstance(competitors["direct_competitors"], list)
        assert isinstance(competitors["indirect_competitors"], list)
        assert "market_share" in competitors
        assert isinstance(competitors["market_share"], dict)

        # Validate competitor details
        for competitor in competitors["direct_competitors"]:
            assert "name" in competitor
            assert "website" in competitor
            assert "market_share" in competitor
            assert "features" in competitor
            assert "pricing" in competitor

    def test_strength_weakness_analysis(self):
        """Test strength / weakness analysis."""
        # Test data
        competitor_data = {
            "name": "CompetitorX",
            "features": ["code completion", "test generation"],
            "pricing": {"monthly": 29.99},
            "market_share": 0.15,
            "customer_ratings": 4.2,
            "support_quality": 0.8,
            "technology_score": 0.75,
        }

        # Analyze strengths and weaknesses
        analysis = self.sw_analyzer.analyze_competitor(competitor_data)

        # Validate analysis
        assert "strengths" in analysis
        assert "weaknesses" in analysis
        assert "competitive_advantages" in analysis
        assert "vulnerability_points" in analysis
        assert isinstance(analysis["strengths"], list)
        assert isinstance(analysis["weaknesses"], list)
        assert all(isinstance(score, 
            float) for score in analysis["strength_scores"].values())
        assert all(0 <= score <= 1 for score in analysis["strength_scores"].values())

    def test_market_position_mapping(self):
        """Test market position mapping."""
        # Test data
        competitors = [
            {
                "name": "CompetitorA",
                "price_point": 0.8,  # High price
                "feature_score": 0.9,  # High features
            },
            {
                "name": "CompetitorB",
                "price_point": 0.3,  # Low price
                "feature_score": 0.4,  # Low features
            },
        ]

        # Map market positions
        market_map = self.position_mapper.create_market_map(competitors)

        # Validate market mapping
        assert "segments" in market_map
        assert "positioning_map" in market_map
        assert "white_spaces" in market_map
        assert isinstance(market_map["segments"], dict)
        assert isinstance(market_map["positioning_map"], dict)
        assert isinstance(market_map["white_spaces"], list)

        # Validate segment analysis
        for segment in market_map["segments"].values():
            assert "competitors" in segment
            assert "saturation_level" in segment
            assert 0 <= segment["saturation_level"] <= 1

    def test_competitive_gap_analysis(self):
        """Test competitive gap analysis."""
        # Test data
        market_needs = ["automation", "integration", "customization"]
        competitor_offerings = [
            {"name": "CompetitorA", "features": ["automation", "integration"]},
            {"name": "CompetitorB", "features": ["integration", "analytics"]},
        ]

        # Analyze gaps
        gaps = self.competitor_analyzer.analyze_market_gaps(market_needs, 
            competitor_offerings)

        # Validate gap analysis
        assert "unmet_needs" in gaps
        assert "partial_solutions" in gaps
        assert "opportunity_score" in gaps
        assert isinstance(gaps["unmet_needs"], list)
        assert isinstance(gaps["opportunity_score"], float)
        assert 0 <= gaps["opportunity_score"] <= 1

    def test_competitive_advantage_analysis(self):
        """Test competitive advantage analysis."""
        # Test data
        our_offering = {
            "features": ["code completion", "test generation", "refactoring"],
            "pricing": {"monthly": 25.99},
            "unique_selling_points": ["AI - powered", "real - time", "customizable"],
        }
        competitor_offerings = [
            {
                "name": "CompetitorA",
                "features": ["code completion", "refactoring"],
                "pricing": {"monthly": 29.99},
            },
            {
                "name": "CompetitorB",
                "features": ["code completion", "test generation"],
                "pricing": {"monthly": 19.99},
            },
        ]

        # Analyze competitive advantages
        advantages = self.competitor_analyzer.analyze_competitive_advantages(
            our_offering, competitor_offerings
        )

        # Validate advantage analysis
        assert "feature_advantages" in advantages
        assert "price_positioning" in advantages
        assert "differentiation_score" in advantages
        assert isinstance(advantages["feature_advantages"], list)
        assert isinstance(advantages["differentiation_score"], float)
        assert 0 <= advantages["differentiation_score"] <= 1

    def test_competitor_trend_tracking(self):
        """Test competitor trend tracking."""
        # Test data
        competitor_history = [
            {"date": "2025 - 01 - 01", "features": ["code completion"], 
                "pricing": {"monthly": 29.99}},
            {
                "date": "2025 - 04 - 01",
                "features": ["code completion", "test generation"],
                "pricing": {"monthly": 34.99},
            },
        ]

        # Track competitor changes
        changes = self.competitor_analyzer.track_competitor_changes(competitor_history)

        # Validate change tracking
        assert "feature_changes" in changes
        assert "pricing_changes" in changes
        assert "trend_direction" in changes
        assert isinstance(changes["feature_changes"], list)
        assert isinstance(changes["pricing_changes"], list)
        assert changes["trend_direction"] in ["expanding", "stable", "contracting"]

    def test_market_concentration_analysis(self):
        """Test market concentration analysis."""
        # Test data
        market_shares = {
            "CompetitorA": 0.3,
            "CompetitorB": 0.25,
            "CompetitorC": 0.15,
            "Others": 0.3,
        }

        # Analyze market concentration
        concentration = \
            self.competitor_analyzer.analyze_market_concentration(market_shares)

        # Validate concentration analysis
        assert "herfindahl_index" in concentration
        assert "concentration_ratio" in concentration
        assert "market_type" in concentration
        assert 0 <= concentration["herfindahl_index"] <= 1
        assert 0 <= concentration["concentration_ratio"] <= 1
        assert concentration["market_type"] in [
            "concentrated",
            "moderately_concentrated",
            "competitive",
        ]

    def test_invalid_competitor_data_handling(self):
        """Test handling of invalid competitor data."""
        # Test with missing required fields
        with pytest.raises(InvalidCompetitorDataError):
            self.competitor_analyzer.identify_competitors({})

        # Test with invalid market shares
        with pytest.raises(ValueError):
            self.competitor_analyzer.analyze_market_concentration(
                {"CompetitorA": 1.5}  # Invalid market share > 1
            )

        # Test with invalid competitor history
        with pytest.raises(ValueError):
            self.competitor_analyzer.track_competitor_changes(
                [{"date": "invalid_date"}]  # Invalid date format
            )

if __name__ == "__main__":
    pytest.main([" - v", "test_competitive_analysis.py"])
