import pytest
from niche_analysis import MarketAnalyzer
from niche_analysis.schemas import MarketSegmentAnalysis, CompetitionAnalysis, TrendAnalysis

def test_analyze_segment_known():
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_segment("e-commerce")
    assert isinstance(result, MarketSegmentAnalysis)
    assert result.name == "E-Commerce"
    assert result.market_size == "large"
    assert len(result.potential_niches) > 0

def test_analyze_segment_unknown():
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_segment("unknown_market")
    assert isinstance(result, MarketSegmentAnalysis)
    assert result.market_size == "unknown"
    assert result.potential_niches == []

def test_analyze_competition_properties():
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_competition("inventory management for small e-commerce")
    assert isinstance(result, CompetitionAnalysis)
    assert result.competitor_count >= 3
    assert len(result.top_competitors) >= 1
    assert result.market_saturation in ("high", "medium", "low")

def test_analyze_trends_basic():
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_trends("e-commerce")
    assert isinstance(result, TrendAnalysis)
    assert len(result.current_trends) > 0
    assert len(result.future_predictions) > 0
    assert len(result.technological_shifts) > 0