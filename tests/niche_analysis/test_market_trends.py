"""Tests for market trend analysis functionality."""
import pytest
from datetime import datetime, timedelta
from niche_analysis.market_analyzer import MarketAnalyzer

@pytest.fixture
def market_analyzer():
    """Create a MarketAnalyzer instance for testing."""
    return MarketAnalyzer()

class TestMarketTrendAnalysis:
    """Tests for market trend analysis."""

    def test_current_trend_analysis(self, market_analyzer):
        """Test analysis of current trends."""
        result = market_analyzer.analyze_trends("e-commerce")
        
        # Verify current trends exist and have correct structure
        assert "current_trends" in result
        assert len(result["current_trends"]) > 0
        
        # Test first trend has all required fields
        trend = result["current_trends"][0]
        assert "name" in trend
        assert "description" in trend
        assert "impact" in trend
        assert "maturity" in trend
        
        # Verify impact levels are valid
        assert trend["impact"] in ["high", "medium", "low"]
        
        # Verify maturity levels are valid
        assert trend["maturity"] in ["emerging", "growing", "mature"]

    def test_future_predictions(self, market_analyzer):
        """Test future trend predictions."""
        result = market_analyzer.analyze_trends("e-commerce")
        
        # Verify future predictions exist and have correct structure
        assert "future_predictions" in result
        assert len(result["future_predictions"]) > 0
        
        # Test first prediction has all required fields
        prediction = result["future_predictions"][0]
        assert "name" in prediction
        assert "description" in prediction
        assert "likelihood" in prediction
        assert "timeframe" in prediction
        
        # Verify likelihood levels are valid
        assert prediction["likelihood"] in ["high", "medium", "low"]
        
        # Verify timeframes are valid
        assert prediction["timeframe"] in ["1 year", "2-3 years", "5+ years"]

    def test_technological_shifts(self, market_analyzer):
        """Test technological shift identification."""
        result = market_analyzer.analyze_trends("e-commerce")
        
        # Verify technological shifts exist
        assert "technological_shifts" in result
        assert len(result["technological_shifts"]) > 0
        
        # Verify common technology trends are included
        tech_shifts = result["technological_shifts"]
        expected_shifts = ["ai integration", "mobile-first approach", 
                         "voice interfaces", "automation"]
        
        for shift in expected_shifts:
            assert shift in tech_shifts

    def test_trend_severity_classification(self, market_analyzer):
        """Test trend severity and impact classification."""
        result = market_analyzer.analyze_trends("e-commerce")
        
        # Check first trend's impact classification
        trend = result["current_trends"][0]
        assert trend["impact"] == "high"  # First trend should be highest impact
        
        # Verify trends are ordered by impact
        impacts = [t["impact"] for t in result["current_trends"]]
        assert impacts == sorted(impacts, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x], 
                               reverse=True)

    def test_trend_caching(self, market_analyzer):
        """Test caching behavior for trend analysis."""
        # First call to get fresh data
        first_result = market_analyzer.analyze_trends("e-commerce")
        
        # Second call should return cached data
        second_result = market_analyzer.analyze_trends("e-commerce")
        
        # Results should be identical when using cache
        assert first_result == second_result
        
        # Force refresh should bypass cache
        fresh_result = market_analyzer.analyze_trends("e-commerce", force_refresh=True)
        
        # Verify timestamp is updated in fresh result
        assert fresh_result != first_result