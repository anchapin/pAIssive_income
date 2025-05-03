"""
Content performance analytics for the pAIssive Income project.

This module provides classes and functions for tracking and analyzing the performance
of marketing content across different channels. It helps identify which content
is performing best and provides insights to improve content strategy.
"""

import time


import json
import logging
import os
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


from interfaces.marketing_interfaces import IContentPerformanceAnalyzer
from marketing.errors import 

# Standard library imports


# Local imports
(
    ContentNotFoundError,
    InvalidParameterError,
    StorageError,
)

# Configure logging
logger = logging.getLogger(__name__)

# Define constants
ENGAGEMENT_TYPES = {
    # Awareness metrics
    "impression": "awareness",
    "view": "awareness",
    "reach": "awareness",
    # Engagement metrics
    "click": "engagement",
    "like": "engagement",
    "comment": "engagement",
    "share": "engagement",
    "save": "engagement",
    "follow": "engagement",
    # Conversion metrics
    "lead": "conversion",
    "signup": "conversion",
    "download": "conversion",
    "purchase": "conversion",
}

# Content performance benchmarks by content type and channel
DEFAULT_BENCHMARKS = {
    "blog_post": {
        "views": 1000,
        "clicks": 50,
        "comments": 5,
        "shares": 10,
        "conversion_rate": 2.0,  # percentage
    },
    "social_media": {
        "impressions": 1000,
        "likes": 20,
        "comments": 5,
        "shares": 7,
        "click_through_rate": 1.5,  # percentage
    },
    "email": {
        "opens": 25,  # percentage
        "clicks": 3,  # percentage
        "replies": 0.5,  # percentage
        "conversion_rate": 1.0,  # percentage
    },
    "video": {
        "views": 500,
        "watch_time": 120,  # seconds
        "likes": 15,
        "comments": 3,
        "shares": 5,
        "click_through_rate": 1.0,  # percentage
    },
}


class ContentPerformanceAnalyzer(IContentPerformanceAnalyzer):
    """
    Class for tracking and analyzing the performance of marketing content.

    This class provides tools to:
    1. Track content across different channels
    2. Record various engagement metrics
    3. Analyze content performance
    4. Identify top-performing content
    5. Compare content performance
    6. Generate performance reports
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the content performance analyzer.

        Args:
            storage_path: Optional path to store content data. If None, data will be stored in memory only.
        """
        self.content = {}
        self.engagements = {}
        self.storage_path = storage_path

        # Create storage directory if it doesn't exist
        if storage_path and not os.path.exists(storage_path):
            os.makedirs(storage_path)

        # Load existing data if available
        if storage_path:
            self._load_data()

    def _load_data(self):
        """Load content and engagement data from storage."""
        content_path = os.path.join(self.storage_path, "content.json")
        engagements_path = os.path.join(self.storage_path, "engagements.json")

        try:
            if os.path.exists(content_path):
                with open(content_path, "r", encoding="utf-8") as file:
                    self.content = json.load(file)

            if os.path.exists(engagements_path):
                with open(engagements_path, "r", encoding="utf-8") as file:
                    self.engagements = json.load(file)
        except Exception as e:
            logger.error(f"Error loading content performance data: {e}")
            raise StorageError(f"Could not load content performance data: {e}")

    def _save_data(self):
        """Save content and engagement data to storage."""
        if not self.storage_path:
            return

        content_path = os.path.join(self.storage_path, "content.json")
        engagements_path = os.path.join(self.storage_path, "engagements.json")

        try:
            with open(content_path, "w", encoding="utf-8") as file:
                json.dump(self.content, file, indent=2)

            with open(engagements_path, "w", encoding="utf-8") as file:
                json.dump(self.engagements, file, indent=2)
        except Exception as e:
            logger.error(f"Error saving content performance data: {e}")
            raise StorageError(f"Could not save content performance data: {e}")

    def track_content(
        self,
        content_id: str,
        content_type: str,
        title: str,
        channels: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register content for performance tracking.

        Args:
            content_id: Unique identifier for the content
            content_type: Type of content (blog_post, social_media, email, etc.)
            title: Title or headline of the content
            channels: List of channels where the content is published
            metadata: Optional additional data about the content

        Returns:
            Dictionary containing the registered content data

        Raises:
            InvalidParameterError: If required parameters are missing or invalid
        """
        # Validate parameters
        if not content_id:
            content_id = str(uuid.uuid4())

        if not content_type or not title or not channels:
            raise InvalidParameterError(
                "Content type, title, and channels are required parameters"
            )

        # Create content object
        now = datetime.now()
        content = {
            "content_id": content_id,
            "content_type": content_type,
            "title": title,
            "channels": channels,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": metadata or {},
            "tags": metadata.get("tags", []) if metadata else [],
        }

        # Store content
        self.content[content_id] = content

        # Initialize engagements for this content
        if content_id not in self.engagements:
            self.engagements[content_id] = []

        # Save to disk if storage path is set
        self._save_data()

        return content

    def record_engagement(
        self,
        content_id: str,
        engagement_type: str,
        channel: str,
        count: int = 1,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record an engagement with content.

        Args:
            content_id: ID of the content
            engagement_type: Type of engagement (view, click, comment, share, conversion, etc.)
            channel: Channel where the engagement occurred
            count: Number of engagements to record (default 1)
            timestamp: Optional timestamp for the engagement, defaults to current time
            metadata: Optional additional data about the engagement

        Returns:
            Dictionary containing the recorded engagement

        Raises:
            ContentNotFoundError: If the content ID is not found
            InvalidParameterError: If required parameters are missing or invalid
        """
        # Validate content exists
        if content_id not in self.content:
            raise ContentNotFoundError(content_id)

        # Validate parameters
        if not engagement_type or not channel or count < 1:
            raise InvalidParameterError(
                "Engagement type, channel, and positive count are required"
            )

        # Set timestamp if not provided
        if timestamp is None:
            timestamp = datetime.now()

        # Format timestamp as ISO string if it's a datetime object
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        # Create engagement object
        engagement_id = str(uuid.uuid4())
        engagement = {
            "engagement_id": engagement_id,
            "content_id": content_id,
            "engagement_type": engagement_type,
            "channel": channel,
            "count": count,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "engagement_category": ENGAGEMENT_TYPES.get(
                engagement_type.lower(), "other"
            ),
        }

        # Store engagement
        if content_id not in self.engagements:
            self.engagements[content_id] = []

        self.engagements[content_id].append(engagement)

        # Save to disk if storage path is set
        self._save_data()

        return engagement

    def get_content(self, content_id: str) -> Dict[str, Any]:
        """
        Get content details.

        Args:
            content_id: ID of the content to retrieve

        Returns:
            Content dictionary

        Raises:
            ContentNotFoundError: If the content ID is not found
        """
        if content_id not in self.content:
            raise ContentNotFoundError(content_id)

        return self.content[content_id]

    def list_content(
        self,
        content_type: Optional[str] = None,
        channel: Optional[str] = None,
        date_published_after: Optional[datetime] = None,
        date_published_before: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List content with optional filtering.

        Args:
            content_type: Optional filter for content type
            channel: Optional filter for content published on a specific channel
            date_published_after: Optional filter for content published after a date
            date_published_before: Optional filter for content published before a date
            tags: Optional filter for content with specific tags

        Returns:
            List of content dictionaries matching the filters
        """
        filtered_content = []

        for content in self.content.values():
            # Apply content type filter
            if content_type and content["content_type"] != content_type:
                continue

            # Apply channel filter
            if channel and channel not in content["channels"]:
                continue

            # Apply date filters
            created_at = datetime.fromisoformat(content["created_at"])

            if date_published_after and created_at < date_published_after:
                continue

            if date_published_before and created_at > date_published_before:
                continue

            # Apply tag filter
            if tags:
                content_tags = set(content.get("tags", []))
                if not content_tags.intersection(tags):
                    continue

            # Add to results
            filtered_content.append(content)

        return filtered_content

    def get_engagement_metrics(
        self,
        content_id: str,
        engagement_types: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        group_by: Optional[str] = None,
        aggregation: str = "sum",
    ) -> Dict[str, Any]:
        """
        Get engagement metrics for content with optional filtering and aggregation.

        Args:
            content_id: ID of the content
            engagement_types: Optional list of engagement types to include
            channels: Optional list of channels to include
            start_time: Optional start time to filter engagements
            end_time: Optional end time to filter engagements
            group_by: Optional grouping ("channel", "engagement_type", "daily", "weekly", "monthly")
            aggregation: Aggregation method ("sum", "avg", "min", "max", "count")

        Returns:
            Dictionary containing the engagement metrics

        Raises:
            ContentNotFoundError: If the content ID is not found
            InvalidParameterError: If parameters are invalid
        """
        # Check if content exists
        if content_id not in self.content:
            raise ContentNotFoundError(content_id)

        # Check if there are engagements for this content
        if content_id not in self.engagements or not self.engagements[content_id]:
            return {
                "content_id": content_id,
                "metrics": [],
                "total_count": 0,
                "aggregate": {},
                "grouped_data": {},
            }

        # Initialize result
        result = {
            "content_id": content_id,
            "metrics": [],
            "total_count": 0,
            "aggregate": {},
            "grouped_data": {},
        }

        # Get engagements for this content
        content_engagements = self.engagements[content_id]

        # Filter engagements
        filtered_engagements = []
        for engagement in content_engagements:
            # Filter by engagement type
            if (
                engagement_types
                and engagement["engagement_type"] not in engagement_types
            ):
                continue

            # Filter by channel
            if channels and engagement["channel"] not in channels:
                continue

            # Filter by time range
            if isinstance(engagement["timestamp"], str):
                engagement_time = datetime.fromisoformat(engagement["timestamp"])
            else:
                engagement_time = engagement["timestamp"]

            if start_time and engagement_time < start_time:
                continue

            if end_time and engagement_time > end_time:
                continue

            # Add to filtered engagements
            filtered_engagements.append(engagement)
            result["metrics"].append(engagement)

        # Set total count
        result["total_count"] = len(filtered_engagements)

        # Aggregate metrics by engagement type
        aggregates = defaultdict(list)
        for engagement in filtered_engagements:
            engagement_type = engagement["engagement_type"]
            aggregates[engagement_type].append(engagement["count"])

        # Calculate aggregates
        for engagement_type, values in aggregates.items():
            if aggregation == "sum":
                result["aggregate"][engagement_type] = sum(values)
            elif aggregation == "avg":
                result["aggregate"][engagement_type] = sum(values) / len(values)
            elif aggregation == "min":
                result["aggregate"][engagement_type] = min(values)
            elif aggregation == "max":
                result["aggregate"][engagement_type] = max(values)
            elif aggregation == "count":
                result["aggregate"][engagement_type] = len(values)
            else:
                result["aggregate"][engagement_type] = sum(values)

        # Group data if requested
        if group_by:
            if group_by == "channel":
                # Group by channel
                channels_data = defaultdict(lambda: defaultdict(list))
                for engagement in filtered_engagements:
                    channel = engagement["channel"]
                    engagement_type = engagement["engagement_type"]
                    channels_data[channel][engagement_type].append(engagement["count"])

                # Calculate aggregates for each channel
                for channel, channel_data in channels_data.items():
                    result["grouped_data"][channel] = {}
                    for engagement_type, values in channel_data.items():
                        if aggregation == "sum":
                            result["grouped_data"][channel][engagement_type] = sum(
                                values
                            )
                        elif aggregation == "avg":
                            result["grouped_data"][channel][engagement_type] = sum(
                                values
                            ) / len(values)
                        elif aggregation == "min":
                            result["grouped_data"][channel][engagement_type] = min(
                                values
                            )
                        elif aggregation == "max":
                            result["grouped_data"][channel][engagement_type] = max(
                                values
                            )
                        elif aggregation == "count":
                            result["grouped_data"][channel][engagement_type] = len(
                                values
                            )
                        else:
                            result["grouped_data"][channel][engagement_type] = sum(
                                values
                            )

            elif group_by == "engagement_type":
                # Group by engagement type
                for engagement_type, values in aggregates.items():
                    if aggregation == "sum":
                        result["grouped_data"][engagement_type] = sum(values)
                    elif aggregation == "avg":
                        result["grouped_data"][engagement_type] = sum(values) / len(
                            values
                        )
                    elif aggregation == "min":
                        result["grouped_data"][engagement_type] = min(values)
                    elif aggregation == "max":
                        result["grouped_data"][engagement_type] = max(values)
                    elif aggregation == "count":
                        result["grouped_data"][engagement_type] = len(values)
                    else:
                        result["grouped_data"][engagement_type] = sum(values)

            elif group_by in ["daily", "weekly", "monthly"]:
                # Group by time period
                time_periods = defaultdict(lambda: defaultdict(list))

                for engagement in filtered_engagements:
                    if isinstance(engagement["timestamp"], str):
                        timestamp = datetime.fromisoformat(engagement["timestamp"])
                    else:
                        timestamp = engagement["timestamp"]

                    # Format timestamp based on group_by
                    if group_by == "daily":
                        period = timestamp.strftime("%Y-%m-%d")
                    elif group_by == "weekly":
                        # Get start of the week (Monday)
                        start_of_week = timestamp - timedelta(days=timestamp.weekday())
                        period = start_of_week.strftime("%Y-%m-%d")
                    elif group_by == "monthly":
                        period = timestamp.strftime("%Y-%m")

                    engagement_type = engagement["engagement_type"]
                    time_periods[period][engagement_type].append(engagement["count"])

                # Calculate aggregates for each time period
                for period, period_data in sorted(time_periods.items()):
                    result["grouped_data"][period] = {}
                    for engagement_type, values in period_data.items():
                        if aggregation == "sum":
                            result["grouped_data"][period][engagement_type] = sum(
                                values
                            )
                        elif aggregation == "avg":
                            result["grouped_data"][period][engagement_type] = sum(
                                values
                            ) / len(values)
                        elif aggregation == "min":
                            result["grouped_data"][period][engagement_type] = min(
                                values
                            )
                        elif aggregation == "max":
                            result["grouped_data"][period][engagement_type] = max(
                                values
                            )
                        elif aggregation == "count":
                            result["grouped_data"][period][engagement_type] = len(
                                values
                            )
                        else:
                            result["grouped_data"][period][engagement_type] = sum(
                                values
                            )

        return result

    def analyze_performance(
        self, content_id: str, benchmark_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze content performance against benchmarks or averages.

        Args:
            content_id: ID of the content
            benchmark_metrics: Optional dictionary of benchmark metrics for comparison

        Returns:
            Dictionary containing the performance analysis

        Raises:
            ContentNotFoundError: If the content ID is not found
        """
        # Check if content exists
        if content_id not in self.content:
            raise ContentNotFoundError(content_id)

        content = self.content[content_id]
        content_type = content["content_type"]

        # Get engagement metrics
        metrics = self.get_engagement_metrics(
            content_id=content_id, group_by="engagement_type"
        )

        # Use provided benchmarks or defaults
        benchmarks = benchmark_metrics or DEFAULT_BENCHMARKS.get(content_type, {})

        # Calculate performance relative to benchmarks
        performance = {}
        for engagement_type, value in metrics["aggregate"].items():
            benchmark = benchmarks.get(engagement_type, 0)

            if benchmark > 0:
                performance_pct = (value / benchmark) * 100
            elif value > 0:
                performance_pct = float("inf")  # Undefined comparison
            else:
                performance_pct = 0

            performance[engagement_type] = {
                "actual": value,
                "benchmark": benchmark,
                "performance_percentage": performance_pct,
                "difference": value - benchmark,
            }

        # Calculate overall performance score
        if performance:
            pct_values = [
                p["performance_percentage"]
                for p in performance.values()
                if p["performance_percentage"] != float("in")
            ]
            overall_score = sum(pct_values) / len(pct_values) if pct_values else 0
        else:
            overall_score = 0

        # Calculate engagement rate
        views = metrics["aggregate"].get("view", 0) + metrics["aggregate"].get(
            "impression", 0
        )
        engagements = sum(
            metrics["aggregate"].get(e, 0)
            for e in ["click", "like", "comment", "share"]
        )

        engagement_rate = (engagements / views) * 100 if views > 0 else 0

        # Calculate conversion rate
        conversions = sum(
            metrics["aggregate"].get(c, 0)
            for c in ["lead", "signup", "download", "purchase"]
        )
        conversion_rate = (conversions / views) * 100 if views > 0 else 0

        # Create performance analysis result
        result = {
            "content_id": content_id,
            "content_type": content_type,
            "title": content["title"],
            "channels": content["channels"],
            "created_at": content["created_at"],
            "metrics": metrics["aggregate"],
            "performance": performance,
            "engagement_metrics": {
                "views": views,
                "engagements": engagements,
                "conversions": conversions,
                "engagement_rate": engagement_rate,
                "conversion_rate": conversion_rate,
            },
            "overall_performance_score": overall_score,
            "performance_rating": self._get_performance_rating(overall_score),
        }

        # Add performance insights
        result["insights"] = self._generate_performance_insights(result)

        return result

    def _get_performance_rating(self, score: float) -> str:
        """Get a performance rating based on score."""
        if score >= 150:
            return "exceptional"
        elif score >= 120:
            return "excellent"
        elif score >= 100:
            return "good"
        elif score >= 80:
            return "average"
        elif score >= 50:
            return "below_average"
        else:
            return "poor"

    def _generate_performance_insights(
        self, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate performance insights based on content analysis.

        Args:
            analysis: Content performance analysis dictionary

        Returns:
            List of insight dictionaries with message and type
        """
        insights = []
        metrics = analysis["metrics"]
        performance = analysis["performance"]
        engagement_metrics = analysis["engagement_metrics"]

        # Check engagement rate
        if engagement_metrics["engagement_rate"] > 10:
            insights.append(
                {
                    "type": "positive",
                    "message": "High engagement rate indicates strong audience interest in this content.",
                }
            )
        elif engagement_metrics["engagement_rate"] < 1:
            insights.append(
                {
                    "type": "negative",
                    "message": "Low engagement rate suggests the content isn't resonating with the audience.",
                }
            )

        # Check conversion rate
        if engagement_metrics["conversion_rate"] > 5:
            insights.append(
                {
                    "type": "positive",
                    "message": "Excellent conversion rate indicates effective call-to-action and valuable content.",
                }
            )
        elif (
            engagement_metrics["conversion_rate"] < 0.5
            and engagement_metrics["views"] > 100
        ):
            insights.append(
                {
                    "type": "negative",
                    "message": "Low conversion rate with good view count suggests a disconnect between content and call-to-action.",
                }
            )

        # Check for high-performing metrics
        for metric_name, metric_data in performance.items():
            if metric_data["performance_percentage"] > 150:
                insights.append(
                    {
                        "type": "positive",
                        "message": f"Exceptional performance in {metric_name} metric at {metric_data['performance_percentage']:.1f}% of benchmark.",
                    }
                )

        # Check for underperforming metrics
        underperforming = [
            m for m, d in performance.items() if d["performance_percentage"] < 50
        ]
        if underperforming:
            metrics_list = ", ".join(underperforming)
            insights.append(
                {
                    "type": "negative",
                    "message": f"Underperforming metrics that need attention: {metrics_list}.",
                }
            )

        # Check for trending potential
        if metrics.get("share", 0) > metrics.get("like", 0) * 0.2:
            insights.append(
                {
                    "type": "positive",
                    "message": "High share-to-like ratio indicates viral potential.",
                }
            )

        # Add generic insight if none generated
        if not insights:
            if analysis["overall_performance_score"] >= 100:
                insights.append(
                    {
                        "type": "positive",
                        "message": "Content is performing well across most metrics.",
                    }
                )
            else:
                insights.append(
                    {
                        "type": "neutral",
                        "message": "Content is performing at or below benchmark levels.",
                    }
                )

        return insights

    def compare_content(
        self, content_ids: List[str], metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare performance of multiple content items.

        Args:
            content_ids: List of content IDs to compare
            metrics: Optional list of metrics to include in the comparison

        Returns:
            Dictionary containing the content comparison

        Raises:
            InvalidParameterError: If no valid content IDs are provided
        """
        if not content_ids:
            raise InvalidParameterError("At least one content ID must be provided")

        # Get analysis for each content item
        content_analyses = {}
        valid_content_ids = []

        for content_id in content_ids:
            try:
                analysis = self.analyze_performance(content_id)
                content_analyses[content_id] = analysis
                valid_content_ids.append(content_id)
            except ContentNotFoundError:
                continue

        if not valid_content_ids:
            raise InvalidParameterError("None of the provided content IDs were found")

        # Extract content information
        content_info = {}
        for content_id in valid_content_ids:
            content = self.content[content_id]
            content_info[content_id] = {
                "title": content["title"],
                "content_type": content["content_type"],
                "channels": content["channels"],
                "created_at": content["created_at"],
            }

        # Determine metrics to compare
        all_metrics = set()
        for analysis in content_analyses.values():
            all_metrics.update(analysis["metrics"].keys())

        compare_metrics = metrics or list(all_metrics)

        # Compare metrics across content
        metrics_comparison = {}
        for metric_name in compare_metrics:
            metric_comparison = {
                "content_values": {},
                "highest_value": {"content_id": None, "value": 0},
                "lowest_value": {"content_id": None, "value": float("in")},
                "average_value": 0,
            }

            values = []

            for content_id, analysis in content_analyses.items():
                value = analysis["metrics"].get(metric_name, 0)

                metric_comparison["content_values"][content_id] = value
                values.append(value)

                # Update highest value
                if value > metric_comparison["highest_value"]["value"]:
                    metric_comparison["highest_value"] = {
                        "content_id": content_id,
                        "value": value,
                    }

                # Update lowest value
                if value < metric_comparison["lowest_value"]["value"]:
                    metric_comparison["lowest_value"] = {
                        "content_id": content_id,
                        "value": value,
                    }

            # Calculate average
            metric_comparison["average_value"] = (
                sum(values) / len(values) if values else 0
            )

            # Set lowest value to 0 if it was not updated
            if metric_comparison["lowest_value"]["value"] == float("in"):
                metric_comparison["lowest_value"] = {"content_id": None, "value": 0}

            metrics_comparison[metric_name] = metric_comparison

        # Rank content by overall performance
        ranking = []
        for content_id, analysis in content_analyses.items():
            ranking.append(
                {
                    "content_id": content_id,
                    "title": content_info[content_id]["title"],
                    "performance_score": analysis["overall_performance_score"],
                }
            )

        # Sort by performance score (highest first)
        ranking.sort(key=lambda x: x["performance_score"], reverse=True)

        # Create final comparison result
        result = {
            "content_ids": valid_content_ids,
            "content_info": content_info,
            "metrics_comparison": metrics_comparison,
            "performance_ranking": ranking,
        }

        return result

    def identify_top_performing_content(
        self,
        content_type: Optional[str] = None,
        channel: Optional[str] = None,
        engagement_metric: str = "views",
        time_period: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Identify top-performing content based on engagement metrics.

        Args:
            content_type: Optional filter for content type
            channel: Optional filter for a specific channel
            engagement_metric: Metric to use for ranking
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            limit: Maximum number of items to return

        Returns:
            List of top-performing content items with metrics
        """
        # Get all content matching filters
        content_list = self.list_content(content_type=content_type, channel=channel)

        if not content_list:
            return []

        # Get metrics for each content item
        content_metrics = []

        for content in content_list:
            content_id = content["content_id"]

            try:
                # Get metrics for this content
                metrics = self.get_engagement_metrics(
                    content_id=content_id,
                    start_time=time_period[0] if time_period else None,
                    end_time=time_period[1] if time_period else None,
                )

                # Get the value for the ranking metric
                metric_value = metrics["aggregate"].get(engagement_metric, 0)

                # Add to content metrics
                content_metrics.append(
                    {
                        "content_id": content_id,
                        "title": content["title"],
                        "content_type": content["content_type"],
                        "channels": content["channels"],
                        "created_at": content["created_at"],
                        "metric_value": metric_value,
                        "metrics": metrics["aggregate"],
                    }
                )
            except Exception as e:
                logger.warning(f"Error getting metrics for content {content_id}: {e}")
                continue

        # Sort by metric value (highest first)
        content_metrics.sort(key=lambda x: x["metric_value"], reverse=True)

        # Limit results
        top_content = content_metrics[:limit]

        return top_content

    def generate_content_report(
        self,
        content_id: str,
        report_type: str = "summary",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a content performance report.

        Args:
            content_id: ID of the content
            report_type: Type of report to generate ("summary", "detailed", "channel")
            start_date: Optional start date for report data
            end_date: Optional end date for report data

        Returns:
            Dictionary containing the report data

        Raises:
            ContentNotFoundError: If the content ID is not found
        """
        # Check if content exists
        if content_id not in self.content:
            raise ContentNotFoundError(content_id)

        content = self.content[content_id]

        # Initialize report
        report = {
            "content_id": content_id,
            "title": content["title"],
            "content_type": content["content_type"],
            "channels": content["channels"],
            "created_at": content["created_at"],
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "time_period": {
                "start": (
                    start_date.isoformat() if start_date else content["created_at"]
                ),
                "end": end_date.isoformat() if end_date else datetime.now().isoformat(),
            },
        }

        # Add performance analysis
        analysis = self.analyze_performance(content_id)

        # Create report based on type
        if report_type == "summary":
            # Summary report with high-level metrics
            report["performance_summary"] = {
                "overall_score": analysis["overall_performance_score"],
                "rating": analysis["performance_rating"],
                "engagement_rate": analysis["engagement_metrics"]["engagement_rate"],
                "conversion_rate": analysis["engagement_metrics"]["conversion_rate"],
                "top_metrics": [],
                "insights": analysis["insights"],
            }

            # Add top metrics
            sorted_metrics = sorted(
                analysis["metrics"].items(), key=lambda x: x[1], reverse=True
            )

            for metric_name, value in sorted_metrics[:5]:
                report["performance_summary"]["top_metrics"].append(
                    {
                        "name": metric_name,
                        "value": value,
                        "benchmark": analysis["performance"]
                        .get(metric_name, {})
                        .get("benchmark", 0),
                        "performance": analysis["performance"]
                        .get(metric_name, {})
                        .get("performance_percentage", 0),
                    }
                )

            # Add time series data
            time_metrics = self.get_engagement_metrics(
                content_id=content_id,
                start_time=start_date,
                end_time=end_date,
                group_by="daily",
            )

            report["time_series"] = time_metrics.get("grouped_data", {})

        elif report_type == "detailed":
            # Detailed report with all metrics and analysis
            report["performance_analysis"] = analysis

            # Add time series data with different groupings
            report["time_series"] = {}

            for group_by in ["daily", "weekly", "monthly"]:
                time_metrics = self.get_engagement_metrics(
                    content_id=content_id,
                    start_time=start_date,
                    end_time=end_date,
                    group_by=group_by,
                )

                report["time_series"][group_by] = time_metrics.get("grouped_data", {})

        elif report_type == "channel":
            # Channel report with metrics by channel
            report["channel_performance"] = {}

            for channel in content["channels"]:
                channel_metrics = self.get_engagement_metrics(
                    content_id=content_id,
                    start_time=start_date,
                    end_time=end_date,
                    channels=[channel],
                )

                report["channel_performance"][channel] = {
                    "metrics": channel_metrics["aggregate"],
                    "total_engagements": sum(channel_metrics["aggregate"].values()),
                }

            # Add channel comparison
            channels_data = []

            for channel, data in report["channel_performance"].items():
                channels_data.append(
                    {
                        "channel": channel,
                        "total_engagements": data["total_engagements"],
                        "metrics": data["metrics"],
                    }
                )

            # Sort by total engagements (highest first)
            channels_data.sort(key=lambda x: x["total_engagements"], reverse=True)

            report["channel_comparison"] = channels_data

            # Add recommendations for channels
            report["channel_recommendations"] = []

            # Find best and worst channels
            if channels_data:
                best_channel = channels_data[0]["channel"]
                worst_channel = (
                    channels_data[-1]["channel"] if len(channels_data) > 1 else None
                )

                report["channel_recommendations"].append(
                    {
                        "type": "positive",
                        "message": f"The {best_channel} channel is performing best. Consider allocating more resources to this channel.",
                    }
                )

                if worst_channel and worst_channel != best_channel:
                    report["channel_recommendations"].append(
                        {
                            "type": "negative",
                            "message": f"The {worst_channel} channel is underperforming. Consider reviewing content format or distribution strategy.",
                        }
                    )

        return report