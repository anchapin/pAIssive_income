"""
Tests for competitive intelligence functionality.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from market_analysis.competitive_intelligence import (
    CompetitiveIntelligence,
    CompetitorMonitor,
    PricingAnalyzer,
    FeatureComparator
)
from market_analysis.errors import (
    CompetitiveIntelligenceError,
    InvalidDataError,
    InsufficientDataError
)


class TestCompetitiveIntelligence(unittest.TestCase):
    """Test cases for competitive intelligence functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.competitive_intelligence = CompetitiveIntelligence()
        self.competitor_monitor = CompetitorMonitor()
        self.pricing_analyzer = PricingAnalyzer()
        self.feature_comparator = FeatureComparator()

    def test_real_time_competitor_monitoring(self):
        """Test real-time competitor monitoring."""
        # Initial competitor data
        competitor_id = "competitor1"
        initial_data = {
            "name": "Competitor One",
            "features": ["feature1", "feature2"],
            "pricing": {
                "basic": 9.99,
                "premium": 19.99
            },
            "market_share": 0.15
        }

        # Add competitor
        result = self.competitive_intelligence.real_time_monitoring(competitor_id, initial_data)

        # Verify initial monitoring
        self.assertEqual(result["competitor_id"], competitor_id)
        self.assertFalse(result["changes_detected"])
        self.assertIn("changes", result)
        self.assertIn("current_data", result)
        self.assertIn("analysis_timestamp", result)

        # Updated competitor data with changes
        updated_data = {
            "name": "Competitor One",
            "features": ["feature1", "feature2", "feature3"],  # Added feature
            "pricing": {
                "basic": 9.99,
                "premium": 24.99  # Price increase
            },
            "market_share": 0.17  # Market share increase
        }

        # Update competitor
        result = self.competitive_intelligence.real_time_monitoring(competitor_id, updated_data)

        # Verify changes detected
        self.assertEqual(result["competitor_id"], competitor_id)
        self.assertTrue(result["changes_detected"])
        self.assertIn("changes", result)
        self.assertIn("features", result["changes"])
        self.assertIn("pricing", result["changes"])
        self.assertIn("market_share", result["changes"])

        # Verify feature changes
        self.assertIn("added", result["changes"]["features"])
        self.assertIn("feature3", result["changes"]["features"]["added"])

        # Verify pricing changes
        self.assertIn("premium", result["changes"]["pricing"])
        self.assertEqual(result["changes"]["pricing"]["premium"]["previous"], 19.99)
        self.assertEqual(result["changes"]["pricing"]["premium"]["new"], 24.99)

        # Verify market share changes
        self.assertEqual(result["changes"]["market_share"]["previous"], 0.15)
        self.assertEqual(result["changes"]["market_share"]["new"], 0.17)

    def test_competitor_pricing_change_detection(self):
        """Test competitor pricing change detection."""
        # Set up competitor with pricing history
        competitor_id = "competitor2"

        # Add competitor with initial data
        self.competitor_monitor.add_competitor(competitor_id, {
            "name": "Competitor Two",
            "features": ["feature1", "feature2"],
            "pricing": {
                "basic": 9.99,
                "premium": 19.99
            }
        })

        # Create pricing history by updating multiple times
        # First update - small change (below threshold)
        self.competitor_monitor.update_competitor(competitor_id, {
            "name": "Competitor Two",
            "features": ["feature1", "feature2"],
            "pricing": {
                "basic": 10.49,  # 5% increase
                "premium": 19.99
            }
        })

        # Second update - significant change
        self.competitor_monitor.update_competitor(competitor_id, {
            "name": "Competitor Two",
            "features": ["feature1", "feature2"],
            "pricing": {
                "basic": 10.49,
                "premium": 24.99  # 25% increase
            }
        })

        # Third update - another significant change
        self.competitor_monitor.update_competitor(competitor_id, {
            "name": "Competitor Two",
            "features": ["feature1", "feature2"],
            "pricing": {
                "basic": 8.99,  # 14% decrease
                "premium": 24.99
            }
        })

        # Analyze pricing changes
        result = self.pricing_analyzer.detect_pricing_changes(
            self.competitor_monitor.get_change_history(competitor_id),
            threshold_percent=10.0  # Set threshold to 10%
        )

        # Verify pricing change detection
        self.assertIn("significant_changes", result)
        self.assertEqual(len(result["significant_changes"]), 2)  # Should detect 2 significant changes

        # Verify premium price increase was detected
        premium_change = next(
            (change for change in result["significant_changes"] if change["plan"] == "premium"),
            None
        )
        self.assertIsNotNone(premium_change)
        self.assertEqual(premium_change["previous_price"], 19.99)
        self.assertEqual(premium_change["new_price"], 24.99)
        self.assertGreater(premium_change["percent_change"], 20)  # Should be around 25%
        self.assertTrue(premium_change["is_increase"])

        # Verify basic price decrease was detected
        basic_change = next(
            (change for change in result["significant_changes"] if change["plan"] == "basic" and not change["is_increase"]),
            None
        )
        self.assertIsNotNone(basic_change)
        self.assertEqual(basic_change["previous_price"], 10.49)
        self.assertEqual(basic_change["new_price"], 8.99)
        self.assertLess(basic_change["percent_change"], -10)  # Should be around -14%
        self.assertFalse(basic_change["is_increase"])

        # Verify trend analysis
        self.assertIn("trend", result)
        self.assertIn(result["trend"], ["increasing", "decreasing", "fluctuating", "stable"])
        self.assertIn("average_change_percent", result)
        self.assertGreater(result["average_change_percent"], 0)

    def test_feature_comparison_matrix_generation(self):
        """Test feature comparison matrix generation."""
        # Set up multiple competitors
        competitors = {
            "competitor1": {
                "name": "Competitor One",
                "features": ["feature1", "feature2", "feature3"],
                "pricing": {"basic": 9.99, "premium": 19.99}
            },
            "competitor2": {
                "name": "Competitor Two",
                "features": ["feature1", "feature4", "feature5"],
                "pricing": {"basic": 8.99, "premium": 17.99}
            },
            "competitor3": {
                "name": "Competitor Three",
                "features": ["feature2", "feature3", "feature6"],
                "pricing": {"basic": 12.99, "premium": 24.99}
            }
        }

        # Add competitors to monitor
        for competitor_id, data in competitors.items():
            self.competitor_monitor.add_competitor(competitor_id, data)

        # Generate feature comparison matrix
        our_features = ["feature1", "feature2", "feature7", "feature8"]
        result = self.competitive_intelligence.generate_feature_comparison_matrix(our_features)

        # Verify matrix structure
        self.assertIn("comparison_matrix", result)
        self.assertIn("gap_analysis", result)

        matrix = result["comparison_matrix"]
        gap_analysis = result["gap_analysis"]

        # Verify matrix content
        self.assertIn("features", matrix)
        self.assertIn("competitors", matrix)
        self.assertIn("summary", matrix)

        # Verify all features are included
        all_features = set(["feature1", "feature2", "feature3", "feature4", "feature5", "feature6"])
        self.assertEqual(set(matrix["features"]), all_features)

        # Verify all competitors are included
        self.assertEqual(set(matrix["competitors"].keys()), set(competitors.keys()))

        # Verify feature support is correctly identified
        self.assertTrue(matrix["competitors"]["competitor1"]["features"]["feature1"])
        self.assertTrue(matrix["competitors"]["competitor1"]["features"]["feature2"])
        self.assertFalse(matrix["competitors"]["competitor1"]["features"]["feature4"])

        # Verify summary statistics
        self.assertIn("feature1", matrix["summary"])
        self.assertIn("support_count", matrix["summary"]["feature1"])
        self.assertIn("support_percent", matrix["summary"]["feature1"])

        # Verify gap analysis
        self.assertIn("our_unique_features", gap_analysis)
        self.assertIn("missing_features", gap_analysis)
        self.assertIn("common_missing_features", gap_analysis)
        self.assertIn("rare_features_we_have", gap_analysis)

        # Verify unique features
        self.assertIn("feature7", gap_analysis["our_unique_features"])
        self.assertIn("feature8", gap_analysis["our_unique_features"])

        # Verify missing features
        missing_features = set(["feature3", "feature4", "feature5", "feature6"]) - set(our_features)
        self.assertEqual(set(gap_analysis["missing_features"]), missing_features)


class TestRealTimeCompetitorMonitoring(unittest.TestCase):
    """Test cases specifically for real-time competitor monitoring."""

    def setUp(self):
        """Set up test fixtures."""
        self.competitor_monitor = CompetitorMonitor()

    def test_detect_feature_changes(self):
        """Test detection of feature changes."""
        # Initial competitor data
        competitor_id = "competitor_features"
        initial_data = {
            "name": "Feature Competitor",
            "features": ["feature1", "feature2", "feature3"],
            "pricing": {"basic": 9.99}
        }

        # Add competitor
        self.competitor_monitor.add_competitor(competitor_id, initial_data)

        # Update with added features
        updated_data1 = {
            "name": "Feature Competitor",
            "features": ["feature1", "feature2", "feature3", "feature4", "feature5"],
            "pricing": {"basic": 9.99}
        }

        changes1 = self.competitor_monitor.update_competitor(competitor_id, updated_data1)

        # Verify added features
        assert "features" in changes1
        assert "added" in changes1["features"]
        assert set(changes1["features"]["added"]) == set(["feature4", "feature5"])
        assert len(changes1["features"]["removed"]) == 0

        # Update with removed features
        updated_data2 = {
            "name": "Feature Competitor",
            "features": ["feature1", "feature4", "feature5"],  # Removed feature2 and feature3
            "pricing": {"basic": 9.99}
        }

        changes2 = self.competitor_monitor.update_competitor(competitor_id, updated_data2)

        # Verify removed features
        assert "features" in changes2
        assert "removed" in changes2["features"]
        assert set(changes2["features"]["removed"]) == set(["feature2", "feature3"])
        assert len(changes2["features"]["added"]) == 0

    def test_detect_pricing_plan_changes(self):
        """Test detection of pricing plan changes."""
        # Initial competitor data
        competitor_id = "competitor_pricing_plans"
        initial_data = {
            "name": "Pricing Plan Competitor",
            "features": ["feature1"],
            "pricing": {
                "basic": 9.99,
                "premium": 19.99
            }
        }

        # Add competitor
        self.competitor_monitor.add_competitor(competitor_id, initial_data)

        # Update with new pricing plan
        updated_data1 = {
            "name": "Pricing Plan Competitor",
            "features": ["feature1"],
            "pricing": {
                "basic": 9.99,
                "premium": 19.99,
                "enterprise": 49.99  # New plan
            }
        }

        changes1 = self.competitor_monitor.update_competitor(competitor_id, updated_data1)

        # Verify new pricing plan
        assert "pricing" in changes1
        assert "enterprise" in changes1["pricing"]
        assert changes1["pricing"]["enterprise"]["previous"] is None
        assert changes1["pricing"]["enterprise"]["new"] == 49.99

        # Update with removed pricing plan
        updated_data2 = {
            "name": "Pricing Plan Competitor",
            "features": ["feature1"],
            "pricing": {
                "basic": 9.99,
                "enterprise": 49.99  # Removed premium plan
            }
        }

        changes2 = self.competitor_monitor.update_competitor(competitor_id, updated_data2)

        # Verify removed pricing plan
        assert "pricing" in changes2
        assert "premium" in changes2["pricing"]
        assert changes2["pricing"]["premium"]["previous"] == 19.99
        assert changes2["pricing"]["premium"]["new"] is None

    def test_continuous_monitoring(self):
        """Test continuous monitoring over time."""
        # Initial competitor data
        competitor_id = "competitor_continuous"
        initial_data = {
            "name": "Continuous Monitoring",
            "features": ["feature1", "feature2"],
            "pricing": {"basic": 9.99},
            "market_share": 0.10
        }

        # Add competitor
        self.competitor_monitor.add_competitor(competitor_id, initial_data)

        # Series of updates over time
        updates = [
            {
                "name": "Continuous Monitoring",
                "features": ["feature1", "feature2"],
                "pricing": {"basic": 10.99},  # Price increase
                "market_share": 0.11
            },
            {
                "name": "Continuous Monitoring",
                "features": ["feature1", "feature2", "feature3"],  # New feature
                "pricing": {"basic": 10.99},
                "market_share": 0.12
            },
            {
                "name": "Continuous Monitoring Rebranded",  # Name change
                "features": ["feature1", "feature2", "feature3"],
                "pricing": {"basic": 10.99, "premium": 19.99},  # New plan
                "market_share": 0.13
            }
        ]

        # Apply updates
        all_changes = []
        for update in updates:
            changes = self.competitor_monitor.update_competitor(competitor_id, update)
            all_changes.append(changes)

        # Verify history tracking
        history = self.competitor_monitor.get_change_history(competitor_id)

        # Should have initial state plus updates
        assert len(history) == len(updates) + 1

        # Verify final state
        final_state = self.competitor_monitor.get_competitor(competitor_id)
        assert final_state["name"] == "Continuous Monitoring Rebranded"
        assert set(final_state["features"]) == set(["feature1", "feature2", "feature3"])
        assert "basic" in final_state["pricing"]
        assert "premium" in final_state["pricing"]
        assert final_state["market_share"] == 0.13


class TestCompetitorPricingChangeDetection(unittest.TestCase):
    """Test cases specifically for competitor pricing change detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.pricing_analyzer = PricingAnalyzer()

    def test_detect_significant_price_increases(self):
        """Test detection of significant price increases."""
        # Create pricing history with increases
        pricing_history = [
            {
                "timestamp": (datetime.now() - timedelta(days=90)).isoformat(),
                "pricing": {"basic": 9.99, "premium": 19.99}
            },
            {
                "timestamp": (datetime.now() - timedelta(days=60)).isoformat(),
                "pricing": {"basic": 10.99, "premium": 19.99}  # 10% increase in basic
            },
            {
                "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
                "pricing": {"basic": 10.99, "premium": 24.99}  # 25% increase in premium
            },
            {
                "timestamp": datetime.now().isoformat(),
                "pricing": {"basic": 12.99, "premium": 24.99}  # 18% increase in basic
            }
        ]

        # Detect changes with 10% threshold
        result = self.pricing_analyzer.detect_pricing_changes(pricing_history, threshold_percent=10.0)

        # Verify significant changes
        assert len(result["significant_changes"]) == 3  # Should detect 3 significant changes

        # Verify trend
        assert result["trend"] == "increasing"

        # Verify average change
        assert result["average_change_percent"] > 15  # Should be around 17-18%

    def test_detect_price_volatility(self):
        """Test detection of price volatility."""
        # Create pricing history with volatility
        pricing_history = [
            {
                "timestamp": (datetime.now() - timedelta(days=150)).isoformat(),
                "pricing": {"basic": 9.99}
            },
            {
                "timestamp": (datetime.now() - timedelta(days=120)).isoformat(),
                "pricing": {"basic": 11.99}  # 20% increase
            },
            {
                "timestamp": (datetime.now() - timedelta(days=90)).isoformat(),
                "pricing": {"basic": 8.99}  # 25% decrease
            },
            {
                "timestamp": (datetime.now() - timedelta(days=60)).isoformat(),
                "pricing": {"basic": 12.99}  # 44% increase
            },
            {
                "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
                "pricing": {"basic": 9.99}  # 23% decrease
            },
            {
                "timestamp": datetime.now().isoformat(),
                "pricing": {"basic": 10.99}  # 10% increase
            }
        ]

        # Analyze pricing patterns
        result = self.pricing_analyzer.analyze_pricing_patterns(pricing_history)

        # Verify volatility detection
        assert result["trend_type"] == "fluctuating"
        assert result["price_volatility"] > 0.1  # Should have high volatility
        assert result["average_change"] > 1.0  # Average change should be significant

    def test_detect_seasonal_pricing(self):
        """Test detection of seasonal pricing patterns."""
        # Create pricing history with seasonal pattern
        now = datetime.now()
        year = now.year

        # Create monthly data points for 2 years with seasonal pattern
        # Higher prices in summer (Jun-Aug), lower in winter (Dec-Feb)
        pricing_history = []

        for month in range(1, 13):
            # Previous year
            if month in [6, 7, 8]:  # Summer
                price = 14.99
            elif month in [12, 1, 2]:  # Winter
                price = 9.99
            else:  # Spring/Fall
                price = 12.99

            pricing_history.append({
                "timestamp": datetime(year-1, month, 15).isoformat(),
                "pricing": {"basic": price}
            })

            # Current year
            if month in [6, 7, 8]:  # Summer
                price = 15.99
            elif month in [12, 1, 2]:  # Winter
                price = 10.99
            else:  # Spring/Fall
                price = 13.99

            # Only add months that have already occurred this year
            if datetime(year, month, 15) <= now:
                pricing_history.append({
                    "timestamp": datetime(year, month, 15).isoformat(),
                    "pricing": {"basic": price}
                })

        # Analyze pricing patterns
        result = self.pricing_analyzer.analyze_pricing_patterns(pricing_history)

        # Verify seasonality detection
        assert result["seasonality_detected"]
        assert result["trend_type"] == "increasing"  # Overall trend is increasing


class TestFeatureComparisonMatrixGeneration(unittest.TestCase):
    """Test cases specifically for feature comparison matrix generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.feature_comparator = FeatureComparator()

    def test_generate_basic_comparison_matrix(self):
        """Test generation of a basic feature comparison matrix."""
        # Define competitors
        competitors = {
            "competitor1": {
                "name": "Competitor One",
                "features": ["feature1", "feature2", "feature3"]
            },
            "competitor2": {
                "name": "Competitor Two",
                "features": ["feature1", "feature4", "feature5"]
            },
            "competitor3": {
                "name": "Competitor Three",
                "features": ["feature2", "feature3", "feature6"]
            }
        }

        # Generate matrix
        matrix = self.feature_comparator.generate_comparison_matrix(competitors)

        # Verify matrix structure
        assert "features" in matrix
        assert "competitors" in matrix
        assert "summary" in matrix
        assert "metadata" in matrix

        # Verify features list
        expected_features = ["feature1", "feature2", "feature3", "feature4", "feature5", "feature6"]
        assert set(matrix["features"]) == set(expected_features)

        # Verify competitor data
        for competitor_id in competitors:
            assert competitor_id in matrix["competitors"]
            assert "name" in matrix["competitors"][competitor_id]
            assert "features" in matrix["competitors"][competitor_id]

            # Verify feature mapping
            for feature in expected_features:
                assert feature in matrix["competitors"][competitor_id]["features"]
                expected_value = feature in competitors[competitor_id]["features"]
                assert matrix["competitors"][competitor_id]["features"][feature] == expected_value

        # Verify summary data
        for feature in expected_features:
            assert feature in matrix["summary"]
            assert "support_count" in matrix["summary"][feature]
            assert "support_percent" in matrix["summary"][feature]
            assert "is_common" in matrix["summary"][feature]
            assert "is_rare" in matrix["summary"][feature]

            # Calculate expected support
            expected_count = sum(1 for c in competitors.values() if feature in c["features"])
            expected_percent = (expected_count / len(competitors)) * 100

            assert matrix["summary"][feature]["support_count"] == expected_count
            assert matrix["summary"][feature]["support_percent"] == expected_percent

    def test_identify_competitive_gaps(self):
        """Test identification of competitive gaps."""
        # Define competitors
        competitors = {
            "competitor1": {
                "name": "Competitor One",
                "features": ["feature1", "feature2", "feature3"]
            },
            "competitor2": {
                "name": "Competitor Two",
                "features": ["feature1", "feature4", "feature5"]
            },
            "competitor3": {
                "name": "Competitor Three",
                "features": ["feature1", "feature2", "feature6"]
            }
        }

        # Generate matrix
        matrix = self.feature_comparator.generate_comparison_matrix(competitors)

        # Define our features
        our_features = ["feature1", "feature2", "feature7", "feature8"]

        # Identify gaps
        gaps = self.feature_comparator.identify_competitive_gaps(our_features, matrix)

        # Verify gap analysis
        assert "our_unique_features" in gaps
        assert "missing_features" in gaps
        assert "common_missing_features" in gaps
        assert "rare_features_we_have" in gaps

        # Verify unique features
        assert set(gaps["our_unique_features"]) == set(["feature7", "feature8"])

        # Verify missing features
        assert set(gaps["missing_features"]) == set(["feature3", "feature4", "feature5", "feature6"])

        # Verify common missing features (feature1 is in all competitors)
        assert "feature1" in matrix["summary"]
        assert matrix["summary"]["feature1"]["is_common"]

        # Verify advantage areas
        assert "advantage_areas" in gaps
        assert "improvement_areas" in gaps
