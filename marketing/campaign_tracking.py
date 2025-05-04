"""
Campaign tracking module for monitoring and analyzing marketing campaign performance.

This module provides tools for:
    - Tracking campaign metrics and performance data
    - Analyzing campaign effectiveness
    - Comparing campaigns
    - Visualizing campaign performance
    - Generating campaign reports
    """

    import json
    import logging
    import os
    import time
    import uuid
    from collections import defaultdict
    from datetime import datetime, timedelta
    from typing import Any, Dict, List, Optional

    from interfaces.marketing_interfaces import ICampaignTracker

    (
    InvalidParameterError,
    MarketingError,
    )

    logger = logging.getLogger(__name__)


    class CampaignTrackingError(MarketingError):
    """Error raised when there's an issue with campaign tracking."""

    def __init__(self, message: str, campaign_id: Optional[str] = None, **kwargs):
    """
    Initialize the campaign tracking error.

    Args:
    message: Human-readable error message
    campaign_id: ID of the campaign that caused the error
    **kwargs: Additional arguments to pass to the base class
    """
    details = kwargs.pop("details", {})
    if campaign_id:
    details["campaign_id"] = campaign_id

    super().__init__(
    message=message, code="campaign_tracking_error", details=details, **kwargs
    )


    class CampaignNotFoundError(CampaignTrackingError):
    """Error raised when a campaign is not found."""

    def __init__(self, campaign_id: str, **kwargs):
    """
    Initialize the campaign not found error.

    Args:
    campaign_id: ID of the campaign that was not found
    **kwargs: Additional arguments to pass to the base class
    """
    super().__init__(
    message=f"Campaign with ID {campaign_id} not found",
    campaign_id=campaign_id,
    code="campaign_not_found",
    **kwargs,
    )


    class InvalidMetricError(CampaignTrackingError):
    """Error raised when an invalid metric is provided."""

    def __init__(self, metric: str, campaign_id: Optional[str] = None, **kwargs):
    """
    Initialize the invalid metric error.

    Args:
    metric: Name of the invalid metric
    campaign_id: ID of the campaign that caused the error
    **kwargs: Additional arguments to pass to the base class
    """
    details = kwargs.pop("details", {})
    details["metric"] = metric

    super().__init__(
    message=f"Invalid metric: {metric}",
    campaign_id=campaign_id,
    code="invalid_metric",
    details=details,
    **kwargs,
    )


    class MetricGroup:
    """Group of related metrics for a campaign."""

    # Standard metric groups
    AWARENESS = "awareness"
    ENGAGEMENT = "engagement"
    ACQUISITION = "acquisition"
    CONVERSION = "conversion"
    RETENTION = "retention"
    REVENUE = "revenue"

    # Common metrics mapped to groups
    METRIC_TO_GROUP = {
    # Awareness metrics
    "impressions": AWARENESS,
    "reach": AWARENESS,
    "website_visits": AWARENESS,
    "page_views": AWARENESS,
    "unique_visitors": AWARENESS,
    "brand_mentions": AWARENESS,
    # Engagement metrics
    "clicks": ENGAGEMENT,
    "likes": ENGAGEMENT,
    "comments": ENGAGEMENT,
    "shares": ENGAGEMENT,
    "time_on_page": ENGAGEMENT,
    "bounce_rate": ENGAGEMENT,
    "email_opens": ENGAGEMENT,
    # Acquisition metrics
    "new_leads": ACQUISITION,
    "email_signups": ACQUISITION,
    "free_trial_signups": ACQUISITION,
    "cost_per_lead": ACQUISITION,
    # Conversion metrics
    "conversions": CONVERSION,
    "conversion_rate": CONVERSION,
    "cost_per_acquisition": CONVERSION,
    "user_signups": CONVERSION,
    # Retention metrics
    "active_users": RETENTION,
    "repeat_purchases": RETENTION,
    "churn_rate": RETENTION,
    "customer_lifetime_value": RETENTION,
    # Revenue metrics
    "revenue": REVENUE,
    "average_order_value": REVENUE,
    "mrr": REVENUE,
    "arr": REVENUE,
    }

    # All available groups
    ALL_GROUPS = {AWARENESS, ENGAGEMENT, ACQUISITION, CONVERSION, RETENTION, REVENUE}


    class CampaignTracker(ICampaignTracker):

    def __init__(self, storage_path: Optional[str] = None):
    """
    Initialize the campaign tracker.

    Args:
    storage_path: Optional path to store campaign data. If None, data will be stored in memory only.
    """
    self.campaigns = {}
    self.metrics = {}
    self.storage_path = storage_path

    # Create storage directory if it doesn't exist
    if storage_path and not os.path.exists(storage_path):
    os.makedirs(storage_path)

    # Load existing data if available
    if storage_path and os.path.exists(
    os.path.join(storage_path, "campaigns.json")
    ):
    self._load_campaigns()

    if storage_path and os.path.exists(os.path.join(storage_path, "metrics.json")):
    self._load_metrics()

    def create_campaign(
    self,
    name: str,
    description: str,
    channels: List[str],
    goals: List[Dict[str, Any]],
    target_metrics: Dict[str, float],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    budget: Optional[float] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Create a new campaign for tracking.

    Args:
    name: Campaign name
    description: Campaign description
    channels: Marketing channels used (e.g., "email", "social_media", "content")
    goals: List of campaign goals with metrics and targets
    target_metrics: Dictionary mapping metric names to target values
    start_date: Optional start date for the campaign, defaults to current time
    end_date: Optional end date for the campaign
    budget: Optional campaign budget
    tags: Optional tags for categorizing the campaign
    metadata: Optional additional data about the campaign

    Returns:
    Dictionary containing the created campaign data
    """
    campaign_id = str(uuid.uuid4())
    now = datetime.now()

    if start_date is None:
    start_date = now

    campaign = {
    "id": campaign_id,
    "name": name,
    "description": description,
    "channels": channels,
    "goals": goals,
    "target_metrics": target_metrics,
    "start_date": (
    start_date.isoformat()
    if isinstance(start_date, datetime)
    else start_date
    ),
    "end_date": (
    end_date.isoformat() if isinstance(end_date, datetime) else end_date
    ),
    "budget": budget,
    "tags": tags or [],
    "metadata": metadata or {},
    "status": (
    "active"
    if start_date <= now and (end_date is None or end_date >= now)
    else "scheduled"
    ),
    "created_at": now.isoformat(),
    "updated_at": now.isoformat(),
    }

    self.campaigns[campaign_id] = campaign

    # Initialize metrics for this campaign
    self.metrics[campaign_id] = {}

    # Save to disk if storage path is set
    self._save_campaigns()
    self._save_metrics()

    return campaign

    def update_campaign(self, campaign_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update a campaign's details.

    Args:
    campaign_id: ID of the campaign to update
    **kwargs: Campaign attributes to update

    Returns:
    Updated campaign dictionary

    Raises:
    CampaignNotFoundError: If the campaign is not found
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    campaign = self.campaigns[campaign_id]

    # Update allowed fields
    allowed_fields = [
    "name",
    "description",
    "channels",
    "goals",
    "target_metrics",
    "start_date",
    "end_date",
    "budget",
    "tags",
    "metadata",
    "status",
    ]

    for field, value in kwargs.items():
    if field in allowed_fields:
    # Handle datetime conversion for dates
    if field in ["start_date", "end_date"] and isinstance(value, datetime):
    campaign[field] = value.isoformat()
    else:
    campaign[field] = value

    # Update timestamp
    campaign["updated_at"] = datetime.now().isoformat()

    # Save to disk
    self._save_campaigns()

    return campaign

    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
    """
    Get campaign details.

    Args:
    campaign_id: ID of the campaign to retrieve

    Returns:
    Campaign dictionary

    Raises:
    CampaignNotFoundError: If the campaign is not found
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    return self.campaigns[campaign_id]

    def list_campaigns(
    self,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    tag: Optional[str] = None,
    start_date_after: Optional[datetime] = None,
    start_date_before: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
    """
    List campaigns with optional filtering.

    Args:
    status: Optional filter for campaign status
    channel: Optional filter for campaigns using a specific channel
    tag: Optional filter for campaigns with a specific tag
    start_date_after: Optional filter for campaigns starting after a date
    start_date_before: Optional filter for campaigns starting before a date

    Returns:
    List of campaign dictionaries matching the filters
    """
    results = []

    for campaign in self.campaigns.values():
    # Apply filters
    if status and campaign.get("status") != status:
    continue

    if channel and channel not in campaign.get("channels", []):
    continue

    if tag and tag not in campaign.get("tags", []):
    continue

    if start_date_after:
    campaign_start = datetime.fromisoformat(campaign["start_date"])
    if campaign_start < start_date_after:
    continue

    if start_date_before:
    campaign_start = datetime.fromisoformat(campaign["start_date"])
    if campaign_start > start_date_before:
    continue

    results.append(campaign)

    return results

    def delete_campaign(self, campaign_id: str) -> bool:
    """
    Delete a campaign and its associated metrics.

    Args:
    campaign_id: ID of the campaign to delete

    Returns:
    True if the campaign was deleted, False otherwise

    Raises:
    CampaignNotFoundError: If the campaign is not found
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    # Remove campaign and its metrics
    del self.campaigns[campaign_id]
    if campaign_id in self.metrics:
    del self.metrics[campaign_id]

    # Save to disk
    self._save_campaigns()
    self._save_metrics()

    return True

    def record_metric(
    self,
    campaign_id: str,
    metric_name: str,
    value: float,
    timestamp: Optional[datetime] = None,
    channel: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
    """
    Record a metric value for a campaign.

    Args:
    campaign_id: ID of the campaign
    metric_name: Name of the metric to record
    value: Value of the metric
    timestamp: Optional timestamp for the metric, defaults to current time
    channel: Optional channel to associate with the metric
    metadata: Optional additional data about the metric

    Returns:
    Dictionary containing the recorded metric

    Raises:
    CampaignNotFoundError: If the campaign is not found
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    # Default timestamp to now if not provided
    if timestamp is None:
    timestamp = datetime.now()

    # Create unique ID for this metric record
    metric_id = str(uuid.uuid4())

    # Initialize metrics dictionary for this campaign if it doesn't exist
    if campaign_id not in self.metrics:
    self.metrics[campaign_id] = {}

    # Get metric group
    metric_group = MetricGroup.METRIC_TO_GROUP.get(metric_name.lower(), "custom")

    # Create metric record
    metric_record = {
    "id": metric_id,
    "campaign_id": campaign_id,
    "name": metric_name,
    "group": metric_group,
    "value": value,
    "timestamp": (
    timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp
    ),
    "channel": channel,
    "metadata": metadata or {},
    }

    # Add to metrics dictionary
    self.metrics[campaign_id][metric_id] = metric_record

    # Save to disk
    self._save_metrics()

    return metric_record

    def get_metrics(
    self,
    campaign_id: str,
    metric_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    channel: Optional[str] = None,
    group_by: Optional[str] = None,
    aggregation: str = "sum",
    ) -> Dict[str, Any]:
    """
    Get metrics for a campaign with optional filtering and aggregation.

    Args:
    campaign_id: ID of the campaign
    metric_name: Optional name of a specific metric to retrieve
    start_time: Optional start time to filter metrics
    end_time: Optional end time to filter metrics
    channel: Optional channel to filter metrics
    group_by: Optional grouping ("channel", "daily", "weekly", "monthly")
    aggregation: Aggregation method ("sum", "avg", "min", "max", "count")

    Returns:
    Dictionary containing the campaign metrics data

    Raises:
    CampaignNotFoundError: If the campaign is not found
    InvalidParameterError: If an invalid parameter is provided
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    # Validate aggregation method
    valid_aggregations = ["sum", "avg", "min", "max", "count"]
    if aggregation not in valid_aggregations:
    raise InvalidParameterError(
    f"Invalid aggregation method: {aggregation}. Must be one of {valid_aggregations}"
    )

    # Validate group_by parameter
    valid_groupings = [None, "channel", "daily", "weekly", "monthly", "metric"]
    if group_by not in valid_groupings:
    raise InvalidParameterError(
    f"Invalid group_by value: {group_by}. Must be one of {valid_groupings}"
    )

    # Initialize result
    result = {
    "campaign_id": campaign_id,
    "campaign_name": self.campaigns[campaign_id]["name"],
    "metrics": [],
    "total_count": 0,
    }

    # Initialize grouped data if requested
    if group_by:
    result["grouped_data"] = {}

    # Initialize aggregates for each metric
    aggregates = defaultdict(list)

    # Get campaign metrics
    campaign_metrics = self.metrics.get(campaign_id, {}).values()

    # Apply filters
    filtered_metrics = []
    for metric in campaign_metrics:
    # Filter by metric name
    if metric_name and metric["name"] != metric_name:
    continue

    # Filter by channel
    if channel and metric.get("channel") != channel:
    continue

    # Filter by time range
    metric_time = datetime.fromisoformat(metric["timestamp"])

    if start_time and metric_time < start_time:
    continue

    if end_time and metric_time > end_time:
    continue

    # Add to filtered metrics
    filtered_metrics.append(metric)

    # Add to result metrics list
    result["metrics"].append(metric)

    # Add to aggregates
    aggregates[metric["name"]].append(metric["value"])

    # Set total count
    result["total_count"] = len(filtered_metrics)

    # Perform aggregations
    result["aggregate"] = {}
    for metric_name, values in aggregates.items():
    if aggregation == "sum":
    result["aggregate"][metric_name] = sum(values)
    elif aggregation == "avg":
    result["aggregate"][metric_name] = (
    sum(values) / len(values) if values else 0
    )
    elif aggregation == "min":
    result["aggregate"][metric_name] = min(values) if values else 0
    elif aggregation == "max":
    result["aggregate"][metric_name] = max(values) if values else 0
    elif aggregation == "count":
    result["aggregate"][metric_name] = len(values)

    # Group data if requested
    if group_by:
    if group_by == "channel":
    # Group by channel
    channels = {}
    for metric in filtered_metrics:
    channel = metric.get("channel", "unknown")
    if channel not in channels:
    channels[channel] = defaultdict(list)
    channels[channel][metric["name"]].append(metric["value"])

    # Calculate aggregates for each channel
    for channel_name, channel_metrics in channels.items():
    result["grouped_data"][channel_name] = {}
    for metric_name, values in channel_metrics.items():
    if aggregation == "sum":
    result["grouped_data"][channel_name][metric_name] = sum(
    values
    )
    elif aggregation == "avg":
    result["grouped_data"][channel_name][metric_name] = sum(
    values
    ) / len(values)
    elif aggregation == "min":
    result["grouped_data"][channel_name][metric_name] = min(
    values
    )
    elif aggregation == "max":
    result["grouped_data"][channel_name][metric_name] = max(
    values
    )
    elif aggregation == "count":
    result["grouped_data"][channel_name][metric_name] = len(
    values
    )

    elif group_by == "metric":
    # Group by metric name
    metrics_dict = {}
    for metric in filtered_metrics:
    metric_name = metric["name"]
    if metric_name not in metrics_dict:
    metrics_dict[metric_name] = {
    "values": [],
    "group": metric.get("group", "custom"),
    }
    metrics_dict[metric_name]["values"].append(metric["value"])

    # Calculate aggregates for each metric
    for metric_name, metric_data in metrics_dict.items():
    values = metric_data["values"]
    result["grouped_data"][metric_name] = {
    "group": metric_data["group"],
    "aggregate": 0,
    }

    if aggregation == "sum":
    result["grouped_data"][metric_name]["aggregate"] = sum(values)
    elif aggregation == "avg":
    result["grouped_data"][metric_name]["aggregate"] = sum(
    values
    ) / len(values)
    elif aggregation == "min":
    result["grouped_data"][metric_name]["aggregate"] = min(values)
    elif aggregation == "max":
    result["grouped_data"][metric_name]["aggregate"] = max(values)
    elif aggregation == "count":
    result["grouped_data"][metric_name]["aggregate"] = len(values)

    else:
    # Group by time period
    time_periods = {}

    for metric in filtered_metrics:
    metric_time = datetime.fromisoformat(metric["timestamp"])

    if group_by == "daily":
    period_key = metric_time.date().isoformat()
    elif group_by == "weekly":
    # Get start of week (Monday)
    start_of_week = metric_time - timedelta(
    days=metric_time.weekday()
    )
    period_key = start_of_week.date().isoformat()
    elif group_by == "monthly":
    period_key = f"{metric_time.year}-{metric_time.month:02d}"

    if period_key not in time_periods:
    time_periods[period_key] = defaultdict(list)

    time_periods[period_key][metric["name"]].append(metric["value"])

    # Calculate aggregates for each time period
    for period, period_metrics in time_periods.items():
    result["grouped_data"][period] = {}
    for metric_name, values in period_metrics.items():
    if aggregation == "sum":
    result["grouped_data"][period][metric_name] = sum(values)
    elif aggregation == "avg":
    result["grouped_data"][period][metric_name] = sum(
    values
    ) / len(values)
    elif aggregation == "min":
    result["grouped_data"][period][metric_name] = min(values)
    elif aggregation == "max":
    result["grouped_data"][period][metric_name] = max(values)
    elif aggregation == "count":
    result["grouped_data"][period][metric_name] = len(values)

    return result

    def analyze_performance(
    self,
    campaign_id: str,
    metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
    """
    Analyze campaign performance against target metrics.

    Args:
    campaign_id: ID of the campaign
    metrics: Optional list of metrics to include in the analysis

    Returns:
    Dictionary containing the performance analysis

    Raises:
    CampaignNotFoundError: If the campaign is not found
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    campaign = self.campaigns[campaign_id]
    target_metrics = campaign["target_metrics"]

    # Get current metrics data
    metrics_data = self.get_metrics(
    campaign_id=campaign_id, group_by="metric", aggregation="sum"
    )

    # Initialize result
    result = {
    "campaign_id": campaign_id,
    "campaign_name": campaign["name"],
    "overall_performance": 0,
    "metrics_performance": {},
    "metrics_achievement": {},
    "metrics_remaining": {},
    "groups_performance": {},
    }

    # Filter metrics if requested
    metric_names = metrics or list(target_metrics.keys())

    # Calculate performance for each metric
    performance_scores = []
    for metric_name in metric_names:
    if metric_name not in target_metrics:
    continue

    target_value = target_metrics[metric_name]
    current_value = 0

    # Get current value from metrics data
    if (
    "grouped_data" in metrics_data
    and metric_name in metrics_data["grouped_data"]
    ):
    current_value = metrics_data["grouped_data"][metric_name]["aggregate"]

    # Calculate achievement percentage
    achievement = 0
    if target_value > 0:
    achievement = min(100, (current_value / target_value) * 100)

    # Calculate remaining value
    remaining = max(0, target_value - current_value)

    # Store results
    result["metrics_performance"][metric_name] = {
    "target": target_value,
    "current": current_value,
    "achievement_percentage": achievement,
    "remaining": remaining,
    "group": MetricGroup.METRIC_TO_GROUP.get(metric_name.lower(), "custom"),
    }

    result["metrics_achievement"][metric_name] = achievement
    result["metrics_remaining"][metric_name] = remaining

    # Add to performance scores
    performance_scores.append(achievement)

    # Add to group performance
    group = MetricGroup.METRIC_TO_GROUP.get(metric_name.lower(), "custom")
    if group not in result["groups_performance"]:
    result["groups_performance"][group] = {
    "metrics": [],
    "average_achievement": 0,
    }

    result["groups_performance"][group]["metrics"].append(metric_name)

    # Calculate overall performance
    result["overall_performance"] = (
    sum(performance_scores) / len(performance_scores)
    if performance_scores
    else 0
    )

    # Calculate group average achievements
    for group, group_data in result["groups_performance"].items():
    metrics_list = group_data["metrics"]
    achievements = [result["metrics_achievement"][m] for m in metrics_list]
    group_data["average_achievement"] = (
    sum(achievements) / len(achievements) if achievements else 0
    )

    return result

    def compare_campaigns(
    self, campaign_ids: List[str], metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
    """
    Compare performance of multiple campaigns.

    Args:
    campaign_ids: List of campaign IDs to compare
    metrics: Optional list of metrics to include in the comparison

    Returns:
    Dictionary containing the campaign comparison

    Raises:
    CampaignNotFoundError: If any campaign is not found
    """
    # Validate campaigns
    for campaign_id in campaign_ids:
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    # Initialize result
    result = {
    "campaign_ids": campaign_ids,
    "campaigns": {},
    "metrics_comparison": {},
    "overall_ranking": [],
    }

    # Add campaign info
    for campaign_id in campaign_ids:
    campaign = self.campaigns[campaign_id]
    result["campaigns"][campaign_id] = {
    "name": campaign["name"],
    "status": campaign["status"],
    "start_date": campaign["start_date"],
    "end_date": campaign.get("end_date"),
    "channels": campaign["channels"],
    "budget": campaign.get("budget"),
    }

    # Get all metrics from all campaigns
    all_metrics = set()
    for campaign_id in campaign_ids:
    campaign = self.campaigns[campaign_id]
    all_metrics.update(campaign.get("target_metrics", {}).keys())

    # Add metrics from recorded data
    if campaign_id in self.metrics:
    for metric_record in self.metrics[campaign_id].values():
    all_metrics.add(metric_record["name"])

    # Filter metrics if requested
    metric_names = metrics if metrics is not None else list(all_metrics)

    # Get performance analysis for each campaign
    campaign_analyses = {}
    for campaign_id in campaign_ids:
    try:
    analysis = self.analyze_performance(campaign_id, metric_names)
    campaign_analyses[campaign_id] = analysis
except Exception as e:
    logger.warning(f"Error analyzing campaign {campaign_id}: {e}")
    campaign_analyses[campaign_id] = {
    "overall_performance": 0,
    "metrics_performance": {},
    }

    # Compare metrics across campaigns
    for metric_name in metric_names:
    metric_comparison = {
    "campaign_values": {},
    "highest_value": {"campaign_id": None, "value": 0},
    "highest_achievement": {"campaign_id": None, "percentage": 0},
    "average_value": 0,
    "average_achievement": 0,
    }

    values = []
    achievements = []

    for campaign_id in campaign_ids:
    analysis = campaign_analyses[campaign_id]
    performance = analysis.get("metrics_performance", {}).get(
    metric_name, {}
    )

    if performance:
    current_value = performance.get("current", 0)
    achievement = performance.get("achievement_percentage", 0)

    metric_comparison["campaign_values"][campaign_id] = {
    "current": current_value,
    "target": performance.get("target", 0),
    "achievement": achievement,
    }

    values.append(current_value)
    achievements.append(achievement)

    # Update highest value
    if current_value > metric_comparison["highest_value"]["value"]:
    metric_comparison["highest_value"] = {
    "campaign_id": campaign_id,
    "value": current_value,
    }

    # Update highest achievement
    if (
    achievement
    > metric_comparison["highest_achievement"]["percentage"]
    ):
    metric_comparison["highest_achievement"] = {
    "campaign_id": campaign_id,
    "percentage": achievement,
    }

    # Calculate averages
    metric_comparison["average_value"] = (
    sum(values) / len(values) if values else 0
    )
    metric_comparison["average_achievement"] = (
    sum(achievements) / len(achievements) if achievements else 0
    )

    # Add to result
    result["metrics_comparison"][metric_name] = metric_comparison

    # Create overall ranking
    ranking = []
    for campaign_id in campaign_ids:
    analysis = campaign_analyses[campaign_id]
    ranking.append(
    {
    "campaign_id": campaign_id,
    "name": result["campaigns"][campaign_id]["name"],
    "performance": analysis.get("overall_performance", 0),
    }
    )

    # Sort by performance (highest first)
    ranking.sort(key=lambda x: x["performance"], reverse=True)
    result["overall_ranking"] = ranking

    return result

    def generate_report(
    self,
    campaign_id: str,
    report_type: str = "summary",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
    """
    Generate a campaign performance report.

    Args:
    campaign_id: ID of the campaign
    report_type: Type of report to generate ("summary", "detailed", "goals")
    start_date: Optional start date for report data
    end_date: Optional end date for report data

    Returns:
    Dictionary containing the report data

    Raises:
    CampaignNotFoundError: If the campaign is not found
    """
    if campaign_id not in self.campaigns:
    raise CampaignNotFoundError(campaign_id)

    campaign = self.campaigns[campaign_id]

    # Initialize report
    report = {
    "campaign_id": campaign_id,
    "campaign_name": campaign["name"],
    "report_type": report_type,
    "generated_at": datetime.now().isoformat(),
    "time_period": {
    "start": (
    start_date.isoformat() if start_date else campaign["start_date"]
    ),
    "end": (
    end_date.isoformat()
    if end_date
    else (campaign.get("end_date") or datetime.now().isoformat())
    ),
    },
    "performance_summary": {},
    }

    # Get metrics
    self.get_metrics(
    campaign_id=campaign_id,
    start_time=start_date,
    end_time=end_date,
    group_by="metric",
    )

    # Get performance analysis
    performance = self.analyze_performance(campaign_id)

    # Add performance summary
    report["performance_summary"] = {
    "overall_performance": performance["overall_performance"],
    "top_metrics": [],
    "bottom_metrics": [],
    "metrics_by_group": {},
    }

    # Add metrics by group
    for group, group_data in performance["groups_performance"].items():
    report["performance_summary"]["metrics_by_group"][group] = {
    "metrics": [],
    "average_achievement": group_data["average_achievement"],
    }

    for metric_name in group_data["metrics"]:
    metric_perf = performance["metrics_performance"][metric_name]
    report["performance_summary"]["metrics_by_group"][group][
    "metrics"
    ].append(
    {
    "name": metric_name,
    "current": metric_perf["current"],
    "target": metric_perf["target"],
    "achievement": metric_perf["achievement_percentage"],
    }
    )

    # Sort metrics by achievement
    sorted_metrics = sorted(
    performance["metrics_achievement"].items(), key=lambda x: x[1], reverse=True
    )

    # Add top 5 metrics
    top_metrics = sorted_metrics[:5]
    for metric_name, achievement in top_metrics:
    metric_perf = performance["metrics_performance"][metric_name]
    report["performance_summary"]["top_metrics"].append(
    {
    "name": metric_name,
    "current": metric_perf["current"],
    "target": metric_perf["target"],
    "achievement": achievement,
    }
    )

    # Add bottom 5 metrics
    bottom_metrics = (
    sorted_metrics[-5:] if len(sorted_metrics) >= 5 else sorted_metrics
    )
    for metric_name, achievement in bottom_metrics:
    metric_perf = performance["metrics_performance"][metric_name]
    report["performance_summary"]["bottom_metrics"].append(
    {
    "name": metric_name,
    "current": metric_perf["current"],
    "target": metric_perf["target"],
    "achievement": achievement,
    }
    )

    # Add additional details based on report type
    if report_type == "detailed":
    # Add time-based data
    time_metrics = self.get_metrics(
    campaign_id=campaign_id,
    start_time=start_date,
    end_time=end_date,
    group_by="daily" if (end_date - start_date).days <= 30 else "weekly",
    )

    report["time_series"] = time_metrics.get("grouped_data", {})

    # Add channel data
    channel_metrics = self.get_metrics(
    campaign_id=campaign_id,
    start_time=start_date,
    end_time=end_date,
    group_by="channel",
    )

    report["channel_performance"] = channel_metrics.get("grouped_data", {})

    # Add all metrics
    report["all_metrics"] = {}
    for metric_name, metric_data in performance["metrics_performance"].items():
    report["all_metrics"][metric_name] = {
    "current": metric_data["current"],
    "target": metric_data["target"],
    "achievement": metric_data["achievement_percentage"],
    "remaining": metric_data["remaining"],
    "group": metric_data["group"],
    }

    elif report_type == "goals":
    # Add goals-focused data
    report["goals"] = []

    for goal in campaign["goals"]:
    goal_metrics = {}
    goal_achievement = 0
    metrics_count = 0

    for metric_name in goal.get("metrics", []):
    if metric_name in performance["metrics_performance"]:
    metric_perf = performance["metrics_performance"][metric_name]
    goal_metrics[metric_name] = {
    "current": metric_perf["current"],
    "target": metric_perf["target"],
    "achievement": metric_perf["achievement_percentage"],
    }

    goal_achievement += metric_perf["achievement_percentage"]
    metrics_count += 1

    avg_achievement = (
    goal_achievement / metrics_count if metrics_count > 0 else 0
    )

    report["goals"].append(
    {
    "name": goal["name"],
    "description": goal.get("description", ""),
    "metrics": goal_metrics,
    "average_achievement": avg_achievement,
    }
    )

    return report

    def _load_campaigns(self) -> None:
    """Load campaigns from disk."""
    if not self.storage_path:
    return campaigns_path = os.path.join(self.storage_path, "campaigns.json")

    try:
    with open(campaigns_path, "r") as f:
    self.campaigns = json.load(f)
except Exception as e:
    logger.error(f"Error loading campaigns: {e}")
    self.campaigns = {}

    def _save_campaigns(self) -> None:
    """Save campaigns to disk."""
    if not self.storage_path:
    return campaigns_path = os.path.join(self.storage_path, "campaigns.json")

    try:
    with open(campaigns_path, "w") as f:
    json.dump(self.campaigns, f, indent=2)
except Exception as e:
    logger.error(f"Error saving campaigns: {e}")

    def _load_metrics(self) -> None:
    """Load metrics from disk."""
    if not self.storage_path:
    return metrics_path = os.path.join(self.storage_path, "metrics.json")

    try:
    with open(metrics_path, "r") as f:
    self.metrics = json.load(f)
except Exception as e:
    logger.error(f"Error loading metrics: {e}")
    self.metrics = {}

    def _save_metrics(self) -> None:
    """Save metrics to disk."""
    if not self.storage_path:
    return metrics_path = os.path.join(self.storage_path, "metrics.json")

    try:
    with open(metrics_path, "w") as f:
    json.dump(self.metrics, f, indent=2)
except Exception as e:
    logger.error(f"Error saving metrics: {e}")