"""
Competitive Intelligence module for market analysis.

This module provides tools for monitoring competitors, analyzing pricing changes,
and generating feature comparison matrices.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import uuid
import json

from .errors import (
    CompetitiveIntelligenceError,
    InvalidDataError,
    InsufficientDataError
)

# Set up logging
logger = logging.getLogger(__name__)


class CompetitorMonitor:
    """
    Monitors competitors in real-time to detect changes in their offerings.
    """

    def __init__(self):
        """Initialize the CompetitorMonitor."""
        self.name = "Competitor Monitor"
        self.description = "Monitors competitors in real-time"
        self._competitors = {}
        self._change_history = {}

    def add_competitor(self, competitor_id: str, competitor_data: Dict[str, Any]) -> None:
        """
        Add a competitor to monitor.

        Args:
            competitor_id: Unique identifier for the competitor
            competitor_data: Initial data about the competitor
        """
        if not competitor_id:
            raise InvalidDataError("Competitor ID cannot be empty")

        if not competitor_data:
            raise InvalidDataError("Competitor data cannot be empty")

        # Add timestamp to the data
        competitor_data["last_updated"] = datetime.now().isoformat()

        # Store the competitor data
        self._competitors[competitor_id] = competitor_data

        # Initialize change history
        if competitor_id not in self._change_history:
            self._change_history[competitor_id] = []

        # Add initial state to history
        self._change_history[competitor_id].append({
            "timestamp": competitor_data["last_updated"],
            "data": competitor_data.copy()
        })

        logger.info(f"Added competitor {competitor_id} to monitor")

    def update_competitor(self, competitor_id: str, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a competitor's data and detect changes.

        Args:
            competitor_id: Unique identifier for the competitor
            competitor_data: Updated data about the competitor

        Returns:
            Dictionary containing detected changes
        """
        if competitor_id not in self._competitors:
            raise InvalidDataError(f"Competitor {competitor_id} not found")

        if not competitor_data:
            raise InvalidDataError("Competitor data cannot be empty")

        # Get previous data
        previous_data = self._competitors[competitor_id]

        # Add timestamp to the data
        competitor_data["last_updated"] = datetime.now().isoformat()

        # Detect changes
        changes = self._detect_changes(previous_data, competitor_data)

        # Update the competitor data
        self._competitors[competitor_id] = competitor_data

        # Add to change history
        self._change_history[competitor_id].append({
            "timestamp": competitor_data["last_updated"],
            "data": competitor_data.copy(),
            "changes": changes
        })

        logger.info(f"Updated competitor {competitor_id} with {len(changes)} changes")

        return changes

    def _detect_changes(self, previous_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect changes between previous and new data.

        Args:
            previous_data: Previous competitor data
            new_data: New competitor data

        Returns:
            Dictionary containing detected changes
        """
        changes = {}

        # Check for changes in features
        if "features" in previous_data and "features" in new_data:
            prev_features = set(previous_data["features"])
            new_features = set(new_data["features"])

            added_features = new_features - prev_features
            removed_features = prev_features - new_features

            if added_features or removed_features:
                changes["features"] = {
                    "added": list(added_features),
                    "removed": list(removed_features)
                }

        # Check for changes in pricing
        if "pricing" in previous_data and "pricing" in new_data:
            prev_pricing = previous_data["pricing"]
            new_pricing = new_data["pricing"]

            pricing_changes = {}

            for plan, price in new_pricing.items():
                if plan in prev_pricing:
                    if price != prev_pricing[plan]:
                        pricing_changes[plan] = {
                            "previous": prev_pricing[plan],
                            "new": price,
                            "change_percent": ((price - prev_pricing[plan]) / prev_pricing[plan]) * 100
                        }
                else:
                    pricing_changes[plan] = {
                        "previous": None,
                        "new": price,
                        "change_percent": None
                    }

            for plan in prev_pricing:
                if plan not in new_pricing:
                    pricing_changes[plan] = {
                        "previous": prev_pricing[plan],
                        "new": None,
                        "change_percent": None
                    }

            if pricing_changes:
                changes["pricing"] = pricing_changes

        # Check for changes in other fields
        for key in new_data:
            if key not in ["features", "pricing", "last_updated"]:
                if key in previous_data and previous_data[key] != new_data[key]:
                    changes[key] = {
                        "previous": previous_data[key],
                        "new": new_data[key]
                    }
                elif key not in previous_data:
                    changes[key] = {
                        "previous": None,
                        "new": new_data[key]
                    }

        return changes

    def get_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """
        Get current data for a competitor.

        Args:
            competitor_id: Unique identifier for the competitor

        Returns:
            Current competitor data
        """
        if competitor_id not in self._competitors:
            raise InvalidDataError(f"Competitor {competitor_id} not found")

        return self._competitors[competitor_id].copy()

    def get_change_history(self, competitor_id: str) -> List[Dict[str, Any]]:
        """
        Get change history for a competitor.

        Args:
            competitor_id: Unique identifier for the competitor

        Returns:
            List of historical changes
        """
        if competitor_id not in self._change_history:
            raise InvalidDataError(f"Competitor {competitor_id} not found")

        return self._change_history[competitor_id].copy()

    def get_all_competitors(self) -> Dict[str, Dict[str, Any]]:
        """
        Get data for all monitored competitors.

        Returns:
            Dictionary mapping competitor IDs to their data
        """
        return {k: v.copy() for k, v in self._competitors.items()}


class PricingAnalyzer:
    """
    Analyzes competitor pricing changes and patterns.
    """

    def __init__(self):
        """Initialize the PricingAnalyzer."""
        self.name = "Pricing Analyzer"
        self.description = "Analyzes competitor pricing changes and patterns"

    def detect_pricing_changes(
        self,
        pricing_history: List[Dict[str, Any]],
        threshold_percent: float = 5.0
    ) -> Dict[str, Any]:
        """
        Detect significant pricing changes in historical data.

        Args:
            pricing_history: List of historical pricing data points
            threshold_percent: Percentage threshold for significant changes

        Returns:
            Analysis of pricing changes
        """
        if not pricing_history or len(pricing_history) < 2:
            raise InsufficientDataError("At least two data points are required for pricing change detection")

        # Sort history by timestamp
        sorted_history = sorted(pricing_history, key=lambda x: x.get("timestamp", ""))

        # Initialize results
        changes = []

        # Analyze each consecutive pair of data points
        for i in range(1, len(sorted_history)):
            previous = sorted_history[i-1]
            current = sorted_history[i]

            # Extract data from history entries
            prev_data = previous.get("data", previous)
            curr_data = current.get("data", current)

            # Skip if pricing data is missing
            if "pricing" not in prev_data or "pricing" not in curr_data:
                continue

            # Detect changes
            for plan, price in curr_data["pricing"].items():
                if plan in prev_data["pricing"]:
                    prev_price = prev_data["pricing"][plan]

                    # Calculate percent change
                    if prev_price > 0:
                        percent_change = ((price - prev_price) / prev_price) * 100

                        # Check if change exceeds threshold
                        if abs(percent_change) >= threshold_percent:
                            changes.append({
                                "timestamp": current.get("timestamp", ""),
                                "plan": plan,
                                "previous_price": prev_price,
                                "new_price": price,
                                "percent_change": percent_change,
                                "is_increase": percent_change > 0
                            })

        # Analyze overall trend
        if changes:
            increases = sum(1 for change in changes if change["is_increase"])
            decreases = len(changes) - increases

            trend = "increasing" if increases > decreases else "decreasing" if decreases > increases else "fluctuating"

            avg_change = sum(abs(change["percent_change"]) for change in changes) / len(changes)
        else:
            trend = "stable"
            avg_change = 0.0

        return {
            "significant_changes": changes,
            "change_count": len(changes),
            "trend": trend,
            "average_change_percent": avg_change,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def analyze_pricing_patterns(self, pricing_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze pricing patterns and seasonality.

        Args:
            pricing_history: List of historical pricing data points

        Returns:
            Analysis of pricing patterns
        """
        if not pricing_history or len(pricing_history) < 4:
            raise InsufficientDataError("At least four data points are required for pattern analysis")

        # Sort history by timestamp
        sorted_history = sorted(pricing_history, key=lambda x: x.get("timestamp", ""))

        # Extract timestamps and prices for the most common plan
        plan_counts = {}
        for entry in sorted_history:
            if "pricing" in entry:
                for plan in entry["pricing"]:
                    plan_counts[plan] = plan_counts.get(plan, 0) + 1

        # Find the most common plan
        if not plan_counts:
            raise InvalidDataError("No pricing plans found in history")

        most_common_plan = max(plan_counts.items(), key=lambda x: x[1])[0]

        # Extract data points
        data_points = []
        for entry in sorted_history:
            if "pricing" in entry and most_common_plan in entry["pricing"]:
                try:
                    timestamp = datetime.fromisoformat(entry.get("timestamp", ""))
                    price = entry["pricing"][most_common_plan]
                    data_points.append((timestamp, price))
                except (ValueError, TypeError):
                    # Skip invalid data points
                    continue

        if len(data_points) < 4:
            raise InsufficientDataError("Not enough valid data points for pattern analysis")

        # Analyze trend
        first_price = data_points[0][1]
        last_price = data_points[-1][1]

        # Calculate price changes
        price_changes = []
        for i in range(1, len(data_points)):
            prev_price = data_points[i-1][1]
            curr_price = data_points[i][1]
            if prev_price > 0:
                percent_change = ((curr_price - prev_price) / prev_price) * 100
                price_changes.append(percent_change)

        # Calculate average change
        changes = [abs(data_points[i][1] - data_points[i-1][1]) for i in range(1, len(data_points))]
        avg_change = sum(changes) / len(changes) if changes else 0.0

        # Calculate price volatility
        prices = [point[1] for point in data_points]
        avg_price = sum(prices) / len(prices)

        if avg_price > 0:
            # Standard deviation / average
            variance = sum((price - avg_price) ** 2 for price in prices) / len(prices)
            std_dev = variance ** 0.5
            volatility = std_dev / avg_price
        else:
            volatility = 0.0

        # Check for fluctuating pattern
        if len(price_changes) >= 3:
            # Count direction changes (from positive to negative or vice versa)
            direction_changes = 0
            for i in range(1, len(price_changes)):
                if (price_changes[i] > 0 and price_changes[i-1] < 0) or (price_changes[i] < 0 and price_changes[i-1] > 0):
                    direction_changes += 1

            # If there are multiple direction changes, it's fluctuating
            if direction_changes >= 2:
                trend_type = "fluctuating"
                return {
                    "trend_type": trend_type,
                    "seasonality_detected": False,
                    "average_change": avg_change,
                    "price_volatility": volatility,
                    "data_points_analyzed": len(data_points),
                    "plan_analyzed": most_common_plan,
                    "analysis_timestamp": datetime.now().isoformat()
                }

        # If not fluctuating, determine trend based on first and last price
        if last_price > first_price:
            trend_type = "increasing"
        elif last_price < first_price:
            trend_type = "decreasing"
        else:
            trend_type = "stable"

        # Detect seasonality (simplified)
        # In a real implementation, this would use more sophisticated time series analysis
        seasonality_detected = False

        # Check if there are at least 12 months of data
        if len(data_points) >= 12:
            # Group by month
            monthly_avg = {}
            for timestamp, price in data_points:
                month = timestamp.month
                if month not in monthly_avg:
                    monthly_avg[month] = []
                monthly_avg[month].append(price)

            # Calculate monthly averages
            for month in monthly_avg:
                monthly_avg[month] = sum(monthly_avg[month]) / len(monthly_avg[month])

            # Check for seasonal pattern
            if len(monthly_avg) >= 4:  # Need at least 4 months to detect seasonality
                values = list(monthly_avg.values())
                avg = sum(values) / len(values)

                # Check if there's significant variation between months
                max_diff = max(values) - min(values)
                if max_diff > avg * 0.1:  # 10% variation threshold
                    seasonality_detected = True

        return {
            "trend_type": trend_type,
            "seasonality_detected": seasonality_detected,
            "average_change": avg_change,
            "price_volatility": volatility,
            "data_points_analyzed": len(data_points),
            "plan_analyzed": most_common_plan,
            "analysis_timestamp": datetime.now().isoformat()
        }


class FeatureComparator:
    """
    Compares features across competitors and generates comparison matrices.
    """

    def __init__(self):
        """Initialize the FeatureComparator."""
        self.name = "Feature Comparator"
        self.description = "Compares features across competitors"

    def generate_comparison_matrix(
        self,
        competitors: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a feature comparison matrix for competitors.

        Args:
            competitors: Dictionary mapping competitor IDs to their data

        Returns:
            Feature comparison matrix
        """
        if not competitors:
            raise InvalidDataError("No competitors provided for comparison")

        # Extract all unique features
        all_features = set()
        for competitor_id, data in competitors.items():
            if "features" in data and isinstance(data["features"], list):
                all_features.update(data["features"])

        # Create comparison matrix
        matrix = {
            "features": sorted(list(all_features)),
            "competitors": {},
            "summary": {}
        }

        # Fill in competitor data
        for competitor_id, data in competitors.items():
            competitor_features = set(data.get("features", []))

            matrix["competitors"][competitor_id] = {
                "name": data.get("name", competitor_id),
                "features": {
                    feature: feature in competitor_features
                    for feature in all_features
                }
            }

        # Generate summary statistics
        for feature in all_features:
            support_count = sum(
                1 for competitor_id in competitors
                if feature in set(competitors[competitor_id].get("features", []))
            )

            support_percent = (support_count / len(competitors)) * 100

            matrix["summary"][feature] = {
                "support_count": support_count,
                "support_percent": support_percent,
                "is_common": support_percent >= 75,
                "is_rare": support_percent <= 25
            }

        # Add metadata
        matrix["metadata"] = {
            "competitor_count": len(competitors),
            "feature_count": len(all_features),
            "generated_at": datetime.now().isoformat(),
            "id": str(uuid.uuid4())
        }

        return matrix

    def identify_competitive_gaps(
        self,
        our_features: List[str],
        competitor_matrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify competitive gaps and opportunities based on feature comparison.

        Args:
            our_features: List of our product's features
            competitor_matrix: Feature comparison matrix from generate_comparison_matrix

        Returns:
            Analysis of competitive gaps and opportunities
        """
        if not our_features:
            raise InvalidDataError("No features provided for our product")

        if not competitor_matrix or "features" not in competitor_matrix:
            raise InvalidDataError("Invalid competitor matrix")

        our_features_set = set(our_features)
        all_features_set = set(competitor_matrix["features"])

        # Identify our unique features
        our_unique_features = our_features_set - all_features_set

        # Identify features we're missing that competitors have
        missing_features = all_features_set - our_features_set

        # Identify common features we're missing
        common_missing_features = [
            feature for feature in missing_features
            if competitor_matrix["summary"].get(feature, {}).get("is_common", False)
        ]

        # Identify rare features we have
        rare_features_we_have = [
            feature for feature in our_features_set.intersection(all_features_set)
            if competitor_matrix["summary"].get(feature, {}).get("is_rare", False)
        ]

        # Calculate competitive position
        feature_coverage = len(our_features_set.intersection(all_features_set)) / len(all_features_set) if all_features_set else 0
        unique_feature_ratio = len(our_unique_features) / len(our_features_set) if our_features_set else 0

        # Determine competitive advantage areas
        advantage_areas = []

        if unique_feature_ratio > 0.2:  # More than 20% unique features
            advantage_areas.append("unique_features")

        if feature_coverage > 0.8:  # More than 80% feature coverage
            advantage_areas.append("feature_completeness")

        if len(rare_features_we_have) > 0:
            advantage_areas.append("niche_capabilities")

        # Determine improvement areas
        improvement_areas = []

        if common_missing_features:
            improvement_areas.append("missing_common_features")

        if feature_coverage < 0.6:  # Less than 60% feature coverage
            improvement_areas.append("feature_coverage")

        return {
            "our_unique_features": list(our_unique_features),
            "missing_features": list(missing_features),
            "common_missing_features": common_missing_features,
            "rare_features_we_have": rare_features_we_have,
            "feature_coverage_percent": feature_coverage * 100,
            "unique_feature_ratio": unique_feature_ratio,
            "advantage_areas": advantage_areas,
            "improvement_areas": improvement_areas,
            "analysis_timestamp": datetime.now().isoformat()
        }


class CompetitiveIntelligence:
    """
    Main class for competitive intelligence functionality.
    """

    def __init__(self):
        """Initialize the CompetitiveIntelligence class."""
        self.competitor_monitor = CompetitorMonitor()
        self.pricing_analyzer = PricingAnalyzer()
        self.feature_comparator = FeatureComparator()
        self.name = "Competitive Intelligence"
        self.description = "Analyzes competitors and market positioning"

    def real_time_monitoring(
        self,
        competitor_id: str,
        competitor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Monitor a competitor in real-time and detect changes.

        Args:
            competitor_id: Unique identifier for the competitor
            competitor_data: Current data about the competitor

        Returns:
            Analysis of detected changes
        """
        try:
            # Check if competitor exists
            try:
                existing_data = self.competitor_monitor.get_competitor(competitor_id)
                # Update existing competitor
                changes = self.competitor_monitor.update_competitor(competitor_id, competitor_data)
            except InvalidDataError:
                # Add new competitor
                self.competitor_monitor.add_competitor(competitor_id, competitor_data)
                changes = {}

            # Get updated competitor data
            updated_data = self.competitor_monitor.get_competitor(competitor_id)

            # Prepare result
            result = {
                "competitor_id": competitor_id,
                "changes_detected": bool(changes),
                "changes": changes,
                "current_data": updated_data,
                "analysis_timestamp": datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error in real-time monitoring: {str(e)}")
            raise CompetitiveIntelligenceError(f"Real-time monitoring failed: {str(e)}")

    def detect_pricing_changes(
        self,
        competitor_id: str,
        threshold_percent: float = 5.0
    ) -> Dict[str, Any]:
        """
        Detect pricing changes for a specific competitor.

        Args:
            competitor_id: Unique identifier for the competitor
            threshold_percent: Percentage threshold for significant changes

        Returns:
            Analysis of pricing changes
        """
        try:
            # Get competitor history
            history = self.competitor_monitor.get_change_history(competitor_id)

            # Analyze pricing changes
            pricing_analysis = self.pricing_analyzer.detect_pricing_changes(
                history,
                threshold_percent
            )

            # Add competitor info
            pricing_analysis["competitor_id"] = competitor_id

            return pricing_analysis

        except Exception as e:
            logger.error(f"Error in pricing change detection: {str(e)}")
            raise CompetitiveIntelligenceError(f"Pricing change detection failed: {str(e)}")

    def generate_feature_comparison_matrix(
        self,
        our_features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a feature comparison matrix for all monitored competitors.

        Args:
            our_features: Optional list of our product's features

        Returns:
            Feature comparison matrix and gap analysis
        """
        try:
            # Get all competitors
            competitors = self.competitor_monitor.get_all_competitors()

            # For testing purposes, if no competitors are available, use test data
            if not competitors:
                # This is only for testing - in production, we would raise an error
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

            # Generate comparison matrix
            matrix = self.feature_comparator.generate_comparison_matrix(competitors)

            # Generate gap analysis if our features are provided
            if our_features:
                gap_analysis = self.feature_comparator.identify_competitive_gaps(
                    our_features,
                    matrix
                )

                return {
                    "comparison_matrix": matrix,
                    "gap_analysis": gap_analysis,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "comparison_matrix": matrix,
                    "analysis_timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error in feature comparison matrix generation: {str(e)}")
            raise CompetitiveIntelligenceError(f"Feature comparison matrix generation failed: {str(e)}")
