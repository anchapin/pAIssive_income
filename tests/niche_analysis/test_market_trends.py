"""
Tests for market trend analysis functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from niche_analysis.market_trends import (
    MarketTrendAnalyzer,
    TrendIdentifier,
    TrendSeverityClassifier,
    HistoricalTrendAnalyzer
)
from niche_analysis.errors import InsufficientDataError, InvalidTimeRangeError


class TestMarketTrendAnalysis:
    """Test cases for market trend analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.trend_analyzer = MarketTrendAnalyzer()
        self.trend_identifier = TrendIdentifier()
        self.severity_classifier = TrendSeverityClassifier()
        self.historical_analyzer = HistoricalTrendAnalyzer()

    def test_trend_identification(self):
        """Test trend identification algorithms."""
        # Test data: simulated market trend data points
        trend_data = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 120},
            {"date": "2025-03-01", "value": 150},
            {"date": "2025-04-01", "value": 200}
        ]

        # Identify trends
        result = self.trend_identifier.identify_trends(trend_data)

        # Validate trend identification
        assert "trend_direction" in result
        assert "trend_strength" in result
        assert "confidence_score" in result
        assert result["trend_direction"] in ["up", "down", "stable"]
        assert 0 <= result["confidence_score"] <= 1

    def test_trend_severity_classification(self):
        """Test trend severity classification."""
        # Test data with different trend severities
        mild_trend = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 105},
            {"date": "2025-03-01", "value": 108},
            {"date": "2025-04-01", "value": 110}
        ]

        severe_trend = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 150},
            {"date": "2025-03-01", "value": 200},
            {"date": "2025-04-01", "value": 300}
        ]

        # Classify trends
        mild_result = self.severity_classifier.classify_severity(mild_trend)
        severe_result = self.severity_classifier.classify_severity(severe_trend)

        # Validate classifications
        assert mild_result["severity_level"] in ["mild", "moderate", "severe"]
        assert severe_result["severity_level"] in ["mild", "moderate", "severe"]
        assert mild_result["severity_score"] < severe_result["severity_score"]
        assert 0 <= mild_result["severity_score"] <= 1
        assert 0 <= severe_result["severity_score"] <= 1

    def test_historical_trend_analysis(self):
        """Test historical trend analysis."""
        # Test data: historical market data
        historical_data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-04-01", "value": 120},
            {"date": "2024-07-01", "value": 90},
            {"date": "2024-10-01", "value": 140},
            {"date": "2025-01-01", "value": 160}
        ]

        # Analyze seasonal patterns
        seasonal_patterns = self.historical_analyzer.analyze_seasonality(historical_data)

        # Validate seasonal analysis
        assert "has_seasonality" in seasonal_patterns
        assert "seasonal_peaks" in seasonal_patterns
        assert "seasonal_troughs" in seasonal_patterns
        assert isinstance(seasonal_patterns["has_seasonality"], bool)
        assert isinstance(seasonal_patterns["seasonal_peaks"], list)
        assert isinstance(seasonal_patterns["seasonal_troughs"], list)

        # Analyze long-term trends
        long_term_trends = self.historical_analyzer.analyze_long_term_trends(historical_data)

        # Validate long-term trend analysis
        assert "trend_type" in long_term_trends
        assert "growth_rate" in long_term_trends
        assert long_term_trends["trend_type"] in ["linear", "exponential", "cyclical", "random"]
        assert isinstance(long_term_trends["growth_rate"], float)

    def test_market_cycle_detection(self):
        """Test market cycle detection."""
        # Test data for market cycles
        cycle_data = [
            {"date": "2024-01-01", "value": 100},  # Start of cycle
            {"date": "2024-04-01", "value": 150},  # Peak
            {"date": "2024-07-01", "value": 80},   # Trough
            {"date": "2024-10-01", "value": 120},  # Recovery
            {"date": "2025-01-01", "value": 110}   # New cycle
        ]

        # Detect market cycles
        cycles = self.trend_analyzer.detect_market_cycles(cycle_data)

        # Validate cycle detection
        assert "cycles_found" in cycles
        assert "cycle_length" in cycles
        assert "cycle_peaks" in cycles
        assert "cycle_troughs" in cycles
        assert isinstance(cycles["cycles_found"], bool)
        assert isinstance(cycles["cycle_length"], (int, float))
        assert isinstance(cycles["cycle_peaks"], list)
        assert isinstance(cycles["cycle_troughs"], list)

    def test_trend_correlation(self):
        """Test trend correlation analysis."""
        # Test data for multiple related trends
        trend1 = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 120}
        ]
        trend2 = [
            {"date": "2025-01-01", "value": 50},
            {"date": "2025-02-01", "value": 55}
        ]

        # Analyze correlation between trends
        correlation = self.trend_analyzer.analyze_trend_correlation(trend1, trend2)

        # Validate correlation analysis
        assert "correlation_coefficient" in correlation
        assert "correlation_type" in correlation
        assert -1 <= correlation["correlation_coefficient"] <= 1
        assert correlation["correlation_type"] in ["positive", "negative", "none"]

    def test_trend_breakpoint_detection(self):
        """Test trend breakpoint detection."""
        # Test data with a clear trend breakpoint
        data = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 110},
            {"date": "2025-03-01", "value": 120},
            {"date": "2025-04-01", "value": 90},   # Breakpoint
            {"date": "2025-05-01", "value": 85},
            {"date": "2025-06-01", "value": 80}
        ]

        # Detect breakpoints
        breakpoints = self.trend_analyzer.detect_breakpoints(data)

        # Validate breakpoint detection
        assert "breakpoints_found" in breakpoints
        assert "breakpoint_dates" in breakpoints
        assert "breakpoint_confidence" in breakpoints
        assert isinstance(breakpoints["breakpoints_found"], bool)
        assert isinstance(breakpoints["breakpoint_dates"], list)
        assert all(0 <= conf <= 1 for conf in breakpoints["breakpoint_confidence"])

    def test_invalid_data_handling(self):
        """Test handling of invalid trend data."""
        # Test with insufficient data points
        with pytest.raises(InsufficientDataError):
            self.trend_identifier.identify_trends([
                {"date": "2025-01-01", "value": 100}
            ])

        # Test with invalid date format
        with pytest.raises(ValueError):
            self.trend_identifier.identify_trends([
                {"date": "invalid_date", "value": 100}
            ])

        # Test with missing values
        with pytest.raises(ValueError):
            self.trend_identifier.identify_trends([
                {"date": "2025-01-01"}
            ])

    def test_trend_forecasting(self):
        """Test trend forecasting capabilities."""
        # Historical data for forecasting
        historical_data = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 120},
            {"date": "2025-03-01", "value": 140}
        ]

        # Generate forecast
        forecast = self.trend_analyzer.forecast_trend(
            historical_data,
            periods=2  # Forecast 2 periods ahead
        )

        # Validate forecast
        assert "forecast_values" in forecast
        assert "confidence_intervals" in forecast
        assert len(forecast["forecast_values"]) == 2
        assert len(forecast["confidence_intervals"]) == 2
        assert all(isinstance(v, (int, float)) for v in forecast["forecast_values"])
        assert all(len(ci) == 2 for ci in forecast["confidence_intervals"])

    def test_trend_significance(self):
        """Test trend significance testing."""
        # Test data
        trend_data = [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-02-01", "value": 120},
            {"date": "2025-03-01", "value": 140},
            {"date": "2025-04-01", "value": 160}
        ]

        # Test trend significance
        significance = self.trend_analyzer.test_trend_significance(trend_data)

        # Validate significance testing
        assert "is_significant" in significance
        assert "p_value" in significance
        assert "test_statistic" in significance
        assert isinstance(significance["is_significant"], bool)
        assert 0 <= significance["p_value"] <= 1


if __name__ == "__main__":
    pytest.main(["-v", "test_market_trends.py"])