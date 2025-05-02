"""
ROI analyzer module for calculating and optimizing marketing campaign ROI.

This module provides tools for:
- Analyzing return on investment for marketing campaigns
- Calculating cumulative ROI over time periods
- Comparing ROI across campaigns and channels
- Forecasting future ROI based on historical data
- Optimizing budget allocation for maximum ROI
- Generating comprehensive ROI reports
"""

import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import json
import os
import logging
import math
import statistics
import copy
from collections import defaultdict

import numpy as np
from scipy import stats
from scipy.optimize import minimize

from marketing.errors import MarketingError, InvalidParameterError
from interfaces.marketing_interfaces import IROIAnalyzer, ICampaignTracker
from marketing.campaign_tracking import CampaignNotFoundError

logger = logging.getLogger(__name__)

class ROIAnalysisError(MarketingError):
    """Error raised when there's an issue with ROI analysis."""
    
    def __init__(
        self, 
        message: str, 
        campaign_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the ROI analysis error.
        
        Args:
            message: Human-readable error message
            campaign_id: ID of the campaign that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        details = kwargs.pop("details", {})
        if campaign_id:
            details["campaign_id"] = campaign_id
        
        super().__init__(
            message=message,
            code="roi_analysis_error",
            details=details,
            **kwargs
        )


class InsufficientDataError(ROIAnalysisError):
    """Error raised when there's insufficient data for ROI analysis."""
    
    def __init__(
        self, 
        message: str,
        campaign_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the insufficient data error.
        
        Args:
            message: Human-readable error message
            campaign_id: ID of the campaign that caused the error
            **kwargs: Additional arguments to pass to the base class
        """
        super().__init__(
            message=message,
            campaign_id=campaign_id,
            code="insufficient_data",
            **kwargs
        )


class ROIAnalyzer(IROIAnalyzer):
    """Class for analyzing marketing campaign ROI."""
    
    def __init__(self, campaign_tracker: ICampaignTracker):
        """
        Initialize the ROI analyzer.
        
        Args:
            campaign_tracker: Campaign tracker instance for accessing campaign data
        """
        self.campaign_tracker = campaign_tracker
    
    def calculate_roi(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        time_period: Optional[Tuple[datetime, datetime]] = None,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate ROI for a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to analyze
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            include_details: Whether to include detailed breakdown in results
            
        Returns:
            Dictionary containing ROI analysis results
            
        Raises:
            CampaignNotFoundError: If the campaign is not found
            InvalidParameterError: If an invalid parameter is provided
        """
        # Validate campaign
        campaign = self.campaign_tracker.get_campaign(campaign_id)
        
        # Convert single metric to list
        if isinstance(revenue_metrics, str):
            revenue_metrics = [revenue_metrics]
            
        # Calculate total cost
        total_cost = sum(costs.values())
        if total_cost <= 0:
            raise InvalidParameterError("Total cost must be greater than zero")
            
        # Set time period if not provided
        if time_period is None:
            campaign_start = datetime.fromisoformat(campaign["start_date"])
            campaign_end = datetime.fromisoformat(campaign["end_date"]) if campaign.get("end_date") else datetime.now()
            time_period = (campaign_start, campaign_end)
            
        # Get metrics data for the specified time period
        metrics_data = self.campaign_tracker.get_metrics(
            campaign_id=campaign_id,
            metric_name=None,  # Get all metrics
            start_time=time_period[0],
            end_time=time_period[1],
            group_by="metric",
            aggregation="sum"
        )
        
        # Calculate total revenue
        total_revenue = 0
        revenue_breakdown = {}
        
        for metric_name in revenue_metrics:
            # Check if metric data exists
            if "grouped_data" in metrics_data and metric_name in metrics_data["grouped_data"]:
                metric_value = metrics_data["grouped_data"][metric_name]["aggregate"]
                revenue_breakdown[metric_name] = metric_value
                total_revenue += metric_value
                
        # Calculate ROI
        roi_value = 0
        roi_percentage = 0
        
        if total_cost > 0:
            roi_value = total_revenue - total_cost
            roi_percentage = (roi_value / total_cost) * 100
            
        # Prepare result
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "time_period": {
                "start": time_period[0].isoformat(),
                "end": time_period[1].isoformat()
            },
            "costs": {
                "total": total_cost,
                "breakdown": costs
            },
            "revenue": {
                "total": total_revenue,
                "breakdown": revenue_breakdown
            },
            "roi": {
                "value": roi_value,
                "percentage": roi_percentage
            }
        }
        
        # Add details if requested
        if include_details:
            # Add cost per acquisition if possible
            conversions = 0
            if "grouped_data" in metrics_data and "conversions" in metrics_data["grouped_data"]:
                conversions = metrics_data["grouped_data"]["conversions"]["aggregate"]
                
            cost_per_acquisition = 0
            if conversions > 0:
                cost_per_acquisition = total_cost / conversions
                
            # Add cost per click if possible
            clicks = 0
            if "grouped_data" in metrics_data and "clicks" in metrics_data["grouped_data"]:
                clicks = metrics_data["grouped_data"]["clicks"]["aggregate"]
                
            cost_per_click = 0
            if clicks > 0:
                cost_per_click = total_cost / clicks
                
            # Add more efficiency metrics
            result["efficiency_metrics"] = {
                "cost_per_acquisition": cost_per_acquisition,
                "cost_per_click": cost_per_click,
                "revenue_per_cost": total_revenue / total_cost if total_cost > 0 else 0,
                "break_even_point": total_cost / (total_revenue / total_cost) if total_revenue > 0 else float('inf')
            }
            
            # Add performance against targets
            target_metrics = campaign.get("target_metrics", {})
            performance = {}
            
            for metric_name in revenue_metrics:
                if metric_name in target_metrics:
                    target = target_metrics[metric_name]
                    actual = revenue_breakdown.get(metric_name, 0)
                    achievement = (actual / target) * 100 if target > 0 else 0
                    
                    performance[metric_name] = {
                        "target": target,
                        "actual": actual,
                        "achievement_percentage": achievement
                    }
            
            result["performance"] = performance
        
        return result
    
    def calculate_cumulative_roi(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        start_date: datetime,
        end_date: datetime,
        interval: str = "daily"
    ) -> Dict[str, Any]:
        """
        Calculate cumulative ROI over time for a campaign.
        
        Args:
            campaign_id: ID of the campaign to analyze
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            start_date: Start date for analysis
            end_date: End date for analysis
            interval: Time interval for ROI points ("daily", "weekly", "monthly")
            
        Returns:
            Dictionary containing cumulative ROI analysis
            
        Raises:
            CampaignNotFoundError: If the campaign is not found
            InvalidParameterError: If an invalid parameter is provided
        """
        # Validate campaign
        campaign = self.campaign_tracker.get_campaign(campaign_id)
        
        # Validate interval
        valid_intervals = ["daily", "weekly", "monthly"]
        if interval not in valid_intervals:
            raise InvalidParameterError(f"Invalid interval: {interval}. Must be one of {valid_intervals}")
            
        # Convert single metric to list
        if isinstance(revenue_metrics, str):
            revenue_metrics = [revenue_metrics]
            
        # Calculate total cost
        total_cost = sum(costs.values())
        if total_cost <= 0:
            raise InvalidParameterError("Total cost must be greater than zero")
            
        # Get time-based metrics
        metrics_data = self.campaign_tracker.get_metrics(
            campaign_id=campaign_id,
            start_time=start_date,
            end_time=end_date,
            group_by=interval,
            aggregation="sum"
        )
        
        # Initialize time periods
        time_periods = []
        current_date = start_date
        
        while current_date <= end_date:
            if interval == "daily":
                period_key = current_date.date().isoformat()
                time_periods.append(period_key)
                current_date += timedelta(days=1)
            elif interval == "weekly":
                # Get start of week (Monday)
                start_of_week = current_date - timedelta(days=current_date.weekday())
                period_key = start_of_week.date().isoformat()
                time_periods.append(period_key)
                current_date += timedelta(days=7)
            elif interval == "monthly":
                period_key = f"{current_date.year}-{current_date.month:02d}"
                time_periods.append(period_key)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # Remove duplicates and sort
        time_periods = sorted(list(set(time_periods)))
        
        # Calculate cost distribution across time periods
        # Simplified approach: distribute cost evenly across all time periods
        cost_per_period = total_cost / len(time_periods)
        
        # Initialize result
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "time_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "interval": interval
            },
            "cumulative_data": [],
            "summary": {
                "total_cost": total_cost,
                "total_revenue": 0,
                "final_roi_value": 0,
                "final_roi_percentage": 0
            }
        }
        
        # Calculate cumulative ROI over time
        cumulative_cost = 0
        cumulative_revenue = 0
        grouped_data = metrics_data.get("grouped_data", {})
        
        for period in time_periods:
            period_revenue = 0
            
            # Get revenue metrics for this period
            if period in grouped_data:
                period_metrics = grouped_data[period]
                
                for metric_name in revenue_metrics:
                    if metric_name in period_metrics:
                        period_revenue += period_metrics[metric_name]
            
            # Update cumulatives
            cumulative_cost += cost_per_period
            cumulative_revenue += period_revenue
            
            # Calculate ROI
            roi_value = cumulative_revenue - cumulative_cost
            roi_percentage = (roi_value / cumulative_cost) * 100 if cumulative_cost > 0 else 0
            
            # Add to result
            result["cumulative_data"].append({
                "period": period,
                "cost": cost_per_period,
                "revenue": period_revenue,
                "cumulative_cost": cumulative_cost,
                "cumulative_revenue": cumulative_revenue,
                "roi_value": roi_value,
                "roi_percentage": roi_percentage
            })
        
        # Update summary
        if result["cumulative_data"]:
            last_period = result["cumulative_data"][-1]
            result["summary"]["total_revenue"] = last_period["cumulative_revenue"]
            result["summary"]["final_roi_value"] = last_period["roi_value"]
            result["summary"]["final_roi_percentage"] = last_period["roi_percentage"]
            
            # Add break-even point if applicable
            for i, period_data in enumerate(result["cumulative_data"]):
                if period_data["cumulative_revenue"] >= period_data["cumulative_cost"]:
                    result["summary"]["break_even_index"] = i
                    result["summary"]["break_even_period"] = period_data["period"]
                    break
            else:
                result["summary"]["break_even_index"] = None
                result["summary"]["break_even_period"] = None
        
        return result
    
    def compare_campaign_roi(
        self,
        campaign_ids: List[str],
        costs: Dict[str, Dict[str, float]],
        revenue_metrics: Dict[str, Union[str, List[str]]],
        time_periods: Optional[Dict[str, Tuple[datetime, datetime]]] = None
    ) -> Dict[str, Any]:
        """
        Compare ROI across multiple campaigns.
        
        Args:
            campaign_ids: List of campaign IDs to compare
            costs: Dictionary mapping campaign IDs to their cost dictionaries
            revenue_metrics: Dictionary mapping campaign IDs to their revenue metrics
            time_periods: Optional dictionary mapping campaign IDs to time period tuples
            
        Returns:
            Dictionary containing comparative ROI analysis
            
        Raises:
            CampaignNotFoundError: If any campaign is not found
            InvalidParameterError: If an invalid parameter is provided
        """
        # Validate campaigns
        for campaign_id in campaign_ids:
            self.campaign_tracker.get_campaign(campaign_id)
        
        # Initialize result
        result = {
            "campaigns": {},
            "roi_comparison": {
                "values": [],
                "percentages": [],
                "revenue_cost_ratios": [],
                "highest_roi": {"campaign_id": None, "value": 0, "percentage": 0},
                "lowest_roi": {"campaign_id": None, "value": 0, "percentage": 0},
                "average_roi_percentage": 0
            }
        }
        
        # Calculate ROI for each campaign
        roi_percentages = []
        
        for campaign_id in campaign_ids:
            # Get time period for this campaign
            time_period = None
            if time_periods and campaign_id in time_periods:
                time_period = time_periods[campaign_id]
            
            # Get cost for this campaign
            campaign_costs = costs.get(campaign_id, {})
            
            # Get revenue metrics for this campaign
            campaign_revenue_metrics = revenue_metrics.get(campaign_id, [])
            
            try:
                # Calculate ROI
                roi_data = self.calculate_roi(
                    campaign_id=campaign_id,
                    costs=campaign_costs,
                    revenue_metrics=campaign_revenue_metrics,
                    time_period=time_period,
                    include_details=True
                )
                
                # Add to result
                result["campaigns"][campaign_id] = roi_data
                
                # Add to comparison
                roi_value = roi_data["roi"]["value"]
                roi_percentage = roi_data["roi"]["percentage"]
                total_cost = roi_data["costs"]["total"]
                total_revenue = roi_data["revenue"]["total"]
                
                # Add to list for comparison
                result["roi_comparison"]["values"].append({
                    "campaign_id": campaign_id,
                    "campaign_name": roi_data["campaign_name"],
                    "roi_value": roi_value
                })
                
                result["roi_comparison"]["percentages"].append({
                    "campaign_id": campaign_id,
                    "campaign_name": roi_data["campaign_name"],
                    "roi_percentage": roi_percentage
                })
                
                revenue_cost_ratio = total_revenue / total_cost if total_cost > 0 else 0
                result["roi_comparison"]["revenue_cost_ratios"].append({
                    "campaign_id": campaign_id,
                    "campaign_name": roi_data["campaign_name"],
                    "ratio": revenue_cost_ratio
                })
                
                # Track highest and lowest ROI
                if (result["roi_comparison"]["highest_roi"]["campaign_id"] is None or
                    roi_percentage > result["roi_comparison"]["highest_roi"]["percentage"]):
                    result["roi_comparison"]["highest_roi"] = {
                        "campaign_id": campaign_id,
                        "campaign_name": roi_data["campaign_name"],
                        "value": roi_value,
                        "percentage": roi_percentage
                    }
                
                if (result["roi_comparison"]["lowest_roi"]["campaign_id"] is None or
                    roi_percentage < result["roi_comparison"]["lowest_roi"]["percentage"]):
                    result["roi_comparison"]["lowest_roi"] = {
                        "campaign_id": campaign_id,
                        "campaign_name": roi_data["campaign_name"],
                        "value": roi_value,
                        "percentage": roi_percentage
                    }
                
                roi_percentages.append(roi_percentage)
                
            except Exception as e:
                logger.warning(f"Error calculating ROI for campaign {campaign_id}: {e}")
                continue
        
        # Sort comparison lists
        result["roi_comparison"]["values"].sort(key=lambda x: x["roi_value"], reverse=True)
        result["roi_comparison"]["percentages"].sort(key=lambda x: x["roi_percentage"], reverse=True)
        result["roi_comparison"]["revenue_cost_ratios"].sort(key=lambda x: x["ratio"], reverse=True)
        
        # Calculate average ROI percentage
        if roi_percentages:
            result["roi_comparison"]["average_roi_percentage"] = sum(roi_percentages) / len(roi_percentages)
            
        # Add statistical analysis
        if len(roi_percentages) > 1:
            result["roi_comparison"]["statistical_analysis"] = {
                "mean": np.mean(roi_percentages),
                "median": np.median(roi_percentages),
                "std_dev": np.std(roi_percentages),
                "min": np.min(roi_percentages),
                "max": np.max(roi_percentages),
                "range": np.max(roi_percentages) - np.min(roi_percentages)
            }
        
        return result
    
    def forecast_roi(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        forecast_period: int,
        forecast_unit: str = "days",
        historical_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Forecast future ROI based on historical data.
        
        Args:
            campaign_id: ID of the campaign to forecast
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            forecast_period: Number of time units to forecast
            forecast_unit: Unit for forecast period ("days", "weeks", "months")
            historical_period: Optional tuple of (start_date, end_date) for historical data
            
        Returns:
            Dictionary containing ROI forecast results
            
        Raises:
            CampaignNotFoundError: If the campaign is not found
            InvalidParameterError: If an invalid parameter is provided
            InsufficientDataError: If there's not enough data for forecasting
        """
        # Validate campaign
        campaign = self.campaign_tracker.get_campaign(campaign_id)
        
        # Validate forecast unit
        valid_units = ["days", "weeks", "months"]
        if forecast_unit not in valid_units:
            raise InvalidParameterError(f"Invalid forecast unit: {forecast_unit}. Must be one of {valid_units}")
        
        # Convert single metric to list
        if isinstance(revenue_metrics, str):
            revenue_metrics = [revenue_metrics]
            
        # Set historical period if not provided
        if historical_period is None:
            campaign_start = datetime.fromisoformat(campaign["start_date"])
            now = datetime.now()
            historical_period = (campaign_start, now)
            
        # Map forecast unit to metrics interval
        interval_map = {
            "days": "daily",
            "weeks": "weekly",
            "months": "monthly"
        }
        interval = interval_map[forecast_unit]
        
        # Get historical metrics
        metrics_data = self.campaign_tracker.get_metrics(
            campaign_id=campaign_id,
            start_time=historical_period[0],
            end_time=historical_period[1],
            group_by=interval,
            aggregation="sum"
        )
        
        # Extract revenue data
        historical_revenue = []
        time_periods = []
        
        grouped_data = metrics_data.get("grouped_data", {})
        for period, period_data in sorted(grouped_data.items()):
            period_revenue = 0
            
            # Sum revenue metrics for this period
            for metric_name in revenue_metrics:
                if metric_name in period_data:
                    period_revenue += period_data[metric_name]
                    
            historical_revenue.append(period_revenue)
            time_periods.append(period)
        
        # Check if we have enough historical data
        min_data_points = 3
        if len(historical_revenue) < min_data_points:
            raise InsufficientDataError(
                f"Insufficient historical data for forecasting. Need at least {min_data_points} data points.",
                campaign_id=campaign_id
            )
            
        # Calculate total cost
        total_cost = sum(costs.values())
        if total_cost <= 0:
            raise InvalidParameterError("Total cost must be greater than zero")
            
        # Calculate cost per period (simple distribution)
        cost_per_period = total_cost / forecast_period
            
        # Simple linear regression for revenue forecasting
        x = np.arange(len(historical_revenue)).reshape(-1, 1)
        y = np.array(historical_revenue)
        
        # Add constant for intercept
        X = np.hstack([x, np.ones_like(x)])
        
        # Fit model
        beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        slope, intercept = beta
        
        # Generate forecast
        forecast_data = []
        
        # Generate new period labels
        last_period = time_periods[-1]
        new_periods = []
        
        if interval == "daily":
            last_date = datetime.fromisoformat(last_period)
            for i in range(1, forecast_period + 1):
                new_date = last_date + timedelta(days=i)
                new_periods.append(new_date.date().isoformat())
        elif interval == "weekly":
            last_date = datetime.fromisoformat(last_period)
            for i in range(1, forecast_period + 1):
                new_date = last_date + timedelta(weeks=i)
                new_periods.append(new_date.date().isoformat())
        elif interval == "monthly":
            year, month = map(int, last_period.split("-"))
            for i in range(1, forecast_period + 1):
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                new_periods.append(f"{year}-{month:02d}")
        
        # Generate forecast values
        x_forecast = np.arange(len(historical_revenue), len(historical_revenue) + forecast_period)
        forecast_values = slope * x_forecast + intercept
        
        # Apply confidence adjustments
        confidence_level = 0.95
        n = len(historical_revenue)
        t_value = stats.t.ppf(1 - (1 - confidence_level) / 2, n - 2)
        
        mse = np.mean((y - (slope * x.flatten() + intercept))**2)
        std_error = np.sqrt(mse)
        
        # Pessimistic forecast: Lower confidence bound
        lower_forecast = forecast_values - t_value * std_error
        lower_forecast = np.maximum(lower_forecast, 0)  # Ensure non-negative values
        
        # Optimistic forecast: Upper confidence bound
        upper_forecast = forecast_values + t_value * std_error
        
        # Calculate cumulative values
        cum_cost = 0
        cum_optimistic = 0
        cum_expected = 0
        cum_pessimistic = 0
        
        for i in range(forecast_period):
            cum_cost += cost_per_period
            cum_expected += max(0, forecast_values[i])
            cum_optimistic += max(0, upper_forecast[i])
            cum_pessimistic += max(0, lower_forecast[i])
            
            # Calculate ROI
            expected_roi = (cum_expected - cum_cost) / cum_cost * 100 if cum_cost > 0 else 0
            optimistic_roi = (cum_optimistic - cum_cost) / cum_cost * 100 if cum_cost > 0 else 0
            pessimistic_roi = (cum_pessimistic - cum_cost) / cum_cost * 100 if cum_cost > 0 else 0
            
            forecast_data.append({
                "period": new_periods[i],
                "period_index": i + 1,
                "cost": cost_per_period,
                "expected_revenue": max(0, forecast_values[i]),
                "pessimistic_revenue": lower_forecast[i],
                "optimistic_revenue": upper_forecast[i],
                "cumulative_cost": cum_cost,
                "cumulative_expected_revenue": cum_expected,
                "cumulative_pessimistic_revenue": cum_pessimistic,
                "cumulative_optimistic_revenue": cum_optimistic,
                "expected_roi": expected_roi,
                "pessimistic_roi": pessimistic_roi,
                "optimistic_roi": optimistic_roi
            })
        
        # Prepare result
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "historical_period": {
                "start": historical_period[0].isoformat(),
                "end": historical_period[1].isoformat(),
                "data_points": len(historical_revenue)
            },
            "forecast": {
                "period_unit": forecast_unit,
                "periods": forecast_period,
                "data": forecast_data
            },
            "forecast_summary": {
                "total_cost": cum_cost,
                "total_expected_revenue": cum_expected,
                "final_expected_roi": (cum_expected - cum_cost) / cum_cost * 100 if cum_cost > 0 else 0,
                "confidence_level": confidence_level
            },
            "model": {
                "type": "linear_regression",
                "params": {
                    "slope": float(slope),
                    "intercept": float(intercept)
                },
                "quality": {
                    "mse": float(mse),
                    "rmse": float(np.sqrt(mse))
                }
            }
        }
        
        # Add break-even points
        for scenario in ["expected", "pessimistic", "optimistic"]:
            for i, data in enumerate(forecast_data):
                cum_revenue = data[f"cumulative_{scenario}_revenue"]
                if cum_revenue >= data["cumulative_cost"]:
                    result["forecast_summary"][f"{scenario}_break_even_index"] = i
                    result["forecast_summary"][f"{scenario}_break_even_period"] = data["period"]
                    break
            else:
                result["forecast_summary"][f"{scenario}_break_even_index"] = None
                result["forecast_summary"][f"{scenario}_break_even_period"] = None
                
        return result
    
    def calculate_channel_roi(
        self,
        campaign_id: str,
        channel_costs: Dict[str, float],
        channel_revenue_metrics: Dict[str, Union[str, List[str]]],
        time_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Calculate ROI for each channel in a campaign.
        
        Args:
            campaign_id: ID of the campaign to analyze
            channel_costs: Dictionary mapping channel names to costs
            channel_revenue_metrics: Dictionary mapping channels to revenue metrics
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            
        Returns:
            Dictionary containing channel ROI analysis
            
        Raises:
            CampaignNotFoundError: If the campaign is not found
            InvalidParameterError: If an invalid parameter is provided
        """
        # Validate campaign
        campaign = self.campaign_tracker.get_campaign(campaign_id)
        
        # Verify channels
        campaign_channels = campaign.get("channels", [])
        for channel in channel_costs.keys():
            if channel not in campaign_channels:
                logger.warning(f"Channel '{channel}' not found in campaign '{campaign_id}' channels")
                
        # Set time period if not provided
        if time_period is None:
            campaign_start = datetime.fromisoformat(campaign["start_date"])
            campaign_end = datetime.fromisoformat(campaign["end_date"]) if campaign.get("end_date") else datetime.now()
            time_period = (campaign_start, campaign_end)
            
        # Initialize result
        result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "time_period": {
                "start": time_period[0].isoformat(),
                "end": time_period[1].isoformat()
            },
            "channels": {},
            "overall": {
                "total_cost": sum(channel_costs.values()),
                "total_revenue": 0,
                "roi_value": 0,
                "roi_percentage": 0
            },
            "ranking": []
        }
        
        # Calculate ROI for each channel
        for channel, cost in channel_costs.items():
            # Get metrics for this channel
            metrics_data = self.campaign_tracker.get_metrics(
                campaign_id=campaign_id,
                start_time=time_period[0],
                end_time=time_period[1],
                channel=channel,
                group_by="metric",
                aggregation="sum"
            )
            
            # Get revenue metrics for this channel
            revenue_metrics = channel_revenue_metrics.get(channel, [])
            if isinstance(revenue_metrics, str):
                revenue_metrics = [revenue_metrics]
            
            # Calculate total revenue for this channel
            channel_revenue = 0
            revenue_breakdown = {}
            
            for metric_name in revenue_metrics:
                # Check if metric data exists
                if "grouped_data" in metrics_data and metric_name in metrics_data["grouped_data"]:
                    metric_value = metrics_data["grouped_data"][metric_name]["aggregate"]
                    revenue_breakdown[metric_name] = metric_value
                    channel_revenue += metric_value
                    
            # Calculate ROI
            roi_value = channel_revenue - cost
            roi_percentage = (roi_value / cost) * 100 if cost > 0 else 0
            
            # Add to result
            result["channels"][channel] = {
                "cost": cost,
                "revenue": {
                    "total": channel_revenue,
                    "breakdown": revenue_breakdown
                },
                "roi": {
                    "value": roi_value,
                    "percentage": roi_percentage
                }
            }
            
            # Update overall
            result["overall"]["total_revenue"] += channel_revenue
            result["ranking"].append({
                "channel": channel,
                "roi_percentage": roi_percentage,
                "roi_value": roi_value,
                "revenue": channel_revenue,
                "cost": cost,
                "revenue_cost_ratio": channel_revenue / cost if cost > 0 else 0
            })
        
        # Calculate overall ROI
        total_cost = result["overall"]["total_cost"]
        total_revenue = result["overall"]["total_revenue"]
        
        if total_cost > 0:
            result["overall"]["roi_value"] = total_revenue - total_cost
            result["overall"]["roi_percentage"] = (result["overall"]["roi_value"] / total_cost) * 100
            
        # Sort ranking
        result["ranking"].sort(key=lambda x: x["roi_percentage"], reverse=True)
        
        # Add efficiency analysis
        total_conversions = 0
        for channel in result["channels"].keys():
            channel_data = self.campaign_tracker.get_metrics(
                campaign_id=campaign_id,
                start_time=time_period[0],
                end_time=time_period[1],
                channel=channel,
                metric_name="conversions",
                aggregation="sum"
            )
            
            if channel_data.get("aggregate", {}).get("conversions", 0) > 0:
                conversions = channel_data["aggregate"]["conversions"]
                result["channels"][channel]["efficiency"] = {
                    "cost_per_acquisition": result["channels"][channel]["cost"] / conversions if conversions > 0 else float('inf'),
                    "revenue_per_acquisition": result["channels"][channel]["revenue"]["total"] / conversions if conversions > 0 else 0
                }
                total_conversions += conversions
                
        # Add overall efficiency
        if total_conversions > 0:
            result["overall"]["efficiency"] = {
                "cost_per_acquisition": total_cost / total_conversions,
                "revenue_per_acquisition": total_revenue / total_conversions
            }
            
        return result
    
    def optimize_budget_allocation(
        self,
        campaign_id: str,
        total_budget: float,
        channel_costs: Dict[str, float],
        channel_revenue_metrics: Dict[str, Union[str, List[str]]],
        constraints: Optional[Dict[str, Any]] = None,
        time_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Optimize budget allocation across channels to maximize ROI.
        
        Args:
            campaign_id: ID of the campaign to optimize
            total_budget: Total budget to allocate
            channel_costs: Dictionary mapping channel names to costs
            channel_revenue_metrics: Dictionary mapping channels to revenue metrics
            constraints: Optional constraints for optimization
            time_period: Optional tuple of (start_date, end_date) for historical data
            
        Returns:
            Dictionary containing optimized budget allocation
            
        Raises:
            CampaignNotFoundError: If the campaign is not found
            InvalidParameterError: If an invalid parameter is provided
            InsufficientDataError: If there's not enough data for optimization
        """
        # Validate campaign
        campaign = self.campaign_tracker.get_campaign(campaign_id)
        
        # Validate budget
        if total_budget <= 0:
            raise InvalidParameterError("Total budget must be greater than zero")
            
        # Set default constraints if not provided
        if constraints is None:
            constraints = {
                "min_channel_allocation": 0.05,  # Minimum 5% of budget per channel
                "max_channel_allocation": 0.5    # Maximum 50% of budget per channel
            }
        
        # Set time period if not provided
        if time_period is None:
            campaign_start = datetime.fromisoformat(campaign["start_date"])
            now = datetime.now()
            time_period = (campaign_start, now)
            
        # Calculate current ROI for each channel
        channel_roi = self.calculate_channel_roi(
            campaign_id=campaign_id,
            channel_costs=channel_costs,
            channel_revenue_metrics=channel_revenue_metrics,
            time_period=time_period
        )
        
        # Extract revenue-to-cost ratio for each channel
        channel_efficiencies = {}
        for channel, data in channel_roi["channels"].items():
            cost = data["cost"]
            revenue = data["revenue"]["total"]
            
            if cost > 0:
                revenue_cost_ratio = revenue / cost
                channel_efficiencies[channel] = revenue_cost_ratio
            else:
                channel_efficiencies[channel] = 0
                
        # Check if we have enough data
        if not channel_efficiencies:
            raise InsufficientDataError(
                "Insufficient data for optimization. No channel revenue data available.",
                campaign_id=campaign_id
            )
            
        # Define optimization function (negative because we want to maximize)
        def objective_function(allocations):
            total_revenue = 0
            for i, channel in enumerate(channel_efficiencies.keys()):
                channel_budget = allocations[i] * total_budget
                channel_revenue = channel_budget * channel_efficiencies[channel]
                total_revenue += channel_revenue
                
            return -total_revenue  # Negative because we want to maximize
        
        # Define constraints
        num_channels = len(channel_efficiencies)
        min_allocation = constraints["min_channel_allocation"]
        max_allocation = constraints["max_channel_allocation"]
        
        # Bounds for each channel allocation (min and max percentages)
        bounds = [(min_allocation, max_allocation) for _ in range(num_channels)]
        
        # Constraint: sum of allocations must equal 1
        constraint = {
            'type': 'eq',
            'fun': lambda x: sum(x) - 1.0
        }
        
        # Initial allocation (equal split)
        initial_allocation = [1.0 / num_channels] * num_channels
        
        # Run optimization
        result = minimize(
            objective_function,
            initial_allocation,
            method='SLSQP',
            bounds=bounds,
            constraints=constraint
        )
        
        # Process optimization results
        optimized_allocations = result.x
        channels = list(channel_efficiencies.keys())
        
        # Ensure allocations sum to 1
        optimized_allocations = optimized_allocations / np.sum(optimized_allocations)
        
        # Calculate optimized budget distribution
        budget_allocation = {}
        for i, channel in enumerate(channels):
            budget_allocation[channel] = optimized_allocations[i] * total_budget
            
        # Calculate expected ROI with new allocation
        expected_revenue = 0
        for channel, allocation in budget_allocation.items():
            expected_channel_revenue = allocation * channel_efficiencies[channel]
            expected_revenue += expected_channel_revenue
            
        expected_roi_value = expected_revenue - total_budget
        expected_roi_percentage = (expected_roi_value / total_budget) * 100
        
        # Calculate ROI improvement
        current_roi_percentage = channel_roi["overall"]["roi_percentage"]
        roi_improvement = expected_roi_percentage - current_roi_percentage
        
        # Prepare result
        optimization_result = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "total_budget": total_budget,
            "current_allocation": {channel: cost for channel, cost in channel_costs.items()},
            "current_roi": {
                "value": channel_roi["overall"]["roi_value"],
                "percentage": current_roi_percentage
            },
            "optimized_allocation": budget_allocation,
            "expected_roi": {
                "value": expected_roi_value,
                "percentage": expected_roi_percentage
            },
            "improvement": {
                "roi_percentage_points": roi_improvement,
                "relative_improvement": (roi_improvement / current_roi_percentage) * 100 if current_roi_percentage > 0 else float('inf')
            },
            "channel_efficiencies": {channel: efficiency for channel, efficiency in channel_efficiencies.items()},
            "constraints": constraints
        }
        
        return optimization_result
    
    def generate_roi_report(
        self,
        campaign_id: str,
        costs: Dict[str, float],
        revenue_metrics: Union[str, List[str]],
        time_period: Optional[Tuple[datetime, datetime]] = None,
        include_forecast: bool = False,
        forecast_period: int = 30,
        report_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive ROI report for a campaign.
        
        Args:
            campaign_id: ID of the campaign to analyze
            costs: Dictionary mapping cost categories to amounts
            revenue_metrics: Metric name(s) to use for revenue calculation
            time_period: Optional tuple of (start_date, end_date) to limit analysis
            include_forecast: Whether to include ROI forecast
            forecast_period: Number of days to forecast if include_forecast is True
            report_type: Type of report to generate ("summary", "detailed", "executive")
            
        Returns:
            Dictionary containing ROI report data
            
        Raises:
            CampaignNotFoundError: If the campaign is not found
            InvalidParameterError: If an invalid parameter is provided
        """
        # Validate campaign
        campaign = self.campaign_tracker.get_campaign(campaign_id)
        
        # Validate report type
        valid_report_types = ["summary", "detailed", "executive"]
        if report_type not in valid_report_types:
            raise InvalidParameterError(f"Invalid report type: {report_type}. Must be one of {valid_report_types}")
        
        # Set time period if not provided
        if time_period is None:
            campaign_start = datetime.fromisoformat(campaign["start_date"])
            campaign_end = datetime.fromisoformat(campaign["end_date"]) if campaign.get("end_date") else datetime.now()
            time_period = (campaign_start, campaign_end)
            
        # Calculate basic ROI
        roi_data = self.calculate_roi(
            campaign_id=campaign_id,
            costs=costs,
            revenue_metrics=revenue_metrics,
            time_period=time_period,
            include_details=True
        )
        
        # Initialize report
        report = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "time_period": {
                "start": time_period[0].isoformat(),
                "end": time_period[1].isoformat()
            },
            "roi_summary": roi_data
        }
        
        # Add channel analysis if detailed or executive report
        if report_type in ["detailed", "executive"]:
            # Organize cost and revenue by channel
            channels = campaign.get("channels", [])
            channel_costs = {}
            channel_revenue_metrics = {}
            
            # Split costs equally among channels if not provided by channel
            cost_per_channel = sum(costs.values()) / len(channels) if channels else 0
            
            for channel in channels:
                channel_costs[channel] = cost_per_channel
                channel_revenue_metrics[channel] = revenue_metrics
                
            # Calculate channel ROI
            try:
                channel_roi = self.calculate_channel_roi(
                    campaign_id=campaign_id,
                    channel_costs=channel_costs,
                    channel_revenue_metrics=channel_revenue_metrics,
                    time_period=time_period
                )
                report["channel_analysis"] = channel_roi
                
            except Exception as e:
                logger.warning(f"Error calculating channel ROI: {e}")
                report["channel_analysis"] = {
                    "error": str(e)
                }
            
        # Add time-based analysis for all report types
        interval = "daily" if (time_period[1] - time_period[0]).days <= 30 else "weekly"
        
        try:
            cumulative_roi = self.calculate_cumulative_roi(
                campaign_id=campaign_id,
                costs=costs,
                revenue_metrics=revenue_metrics,
                start_date=time_period[0],
                end_date=time_period[1],
                interval=interval
            )
            report["time_analysis"] = cumulative_roi
            
        except Exception as e:
            logger.warning(f"Error calculating cumulative ROI: {e}")
            report["time_analysis"] = {
                "error": str(e)
            }
            
        # Add forecast if requested
        if include_forecast:
            try:
                forecast = self.forecast_roi(
                    campaign_id=campaign_id,
                    costs=costs,
                    revenue_metrics=revenue_metrics,
                    forecast_period=forecast_period,
                    forecast_unit="days",
                    historical_period=time_period
                )
                report["forecast"] = forecast
                
            except Exception as e:
                logger.warning(f"Error forecasting ROI: {e}")
                report["forecast"] = {
                    "error": str(e)
                }
                
        # Add recommendations for detailed or executive reports
        if report_type in ["detailed", "executive"]:
            recommendations = []
            
            # Check ROI performance
            roi_percentage = roi_data["roi"]["percentage"]
            if roi_percentage < 0:
                recommendations.append({
                    "type": "warning",
                    "title": "Negative ROI",
                    "description": "The campaign currently has a negative ROI. Consider revising strategy, reducing costs, or focusing on better performing channels."
                })
            elif roi_percentage < 50:
                recommendations.append({
                    "type": "suggestion",
                    "title": "Low ROI",
                    "description": "The campaign has a positive but low ROI. Look for opportunities to improve efficiency or focus on better performing channels."
                })
            else:
                recommendations.append({
                    "type": "positive",
                    "title": "Strong ROI",
                    "description": "The campaign shows a strong ROI. Consider scaling up investment in well-performing channels."
                })
                
            # Channel-specific recommendations
            if "channel_analysis" in report and "ranking" in report["channel_analysis"]:
                # Best performing channel
                best_channel = report["channel_analysis"]["ranking"][0] if report["channel_analysis"]["ranking"] else None
                if best_channel and best_channel["roi_percentage"] > 100:
                    recommendations.append({
                        "type": "opportunity",
                        "title": f"Scale Up {best_channel['channel']}",
                        "description": f"The {best_channel['channel']} channel is performing exceptionally well with {best_channel['roi_percentage']:.1f}% ROI. Consider increasing budget allocation."
                    })
                    
                # Worst performing channel
                worst_channels = [c for c in report["channel_analysis"]["ranking"] if c["roi_percentage"] < 0]
                for channel in worst_channels:
                    recommendations.append({
                        "type": "warning",
                        "title": f"Review {channel['channel']}",
                        "description": f"The {channel['channel']} channel has a negative ROI of {channel['roi_percentage']:.1f}%. Consider reducing investment or revising strategy."
                    })
                    
            # Budget optimization recommendation
            if roi_percentage > 0:
                recommendations.append({
                    "type": "suggestion",
                    "title": "Optimize Budget Allocation",
                    "description": "Consider running budget optimization analysis to maximize overall campaign ROI by reallocating budget across channels."
                })
                
            report["recommendations"] = recommendations
            
        # Executive summary for executive report
        if report_type == "executive":
            summary_points = []
            
            # Overall ROI statement
            roi_value = roi_data["roi"]["value"]
            roi_percentage = roi_data["roi"]["percentage"]
            
            if roi_percentage >= 0:
                summary_points.append(f"The campaign generated a positive ROI of {roi_percentage:.1f}%, with {roi_value:.2f} in profit from a {roi_data['costs']['total']:.2f} investment.")
            else:
                summary_points.append(f"The campaign resulted in a negative ROI of {roi_percentage:.1f}%, with a {-roi_value:.2f} loss on a {roi_data['costs']['total']:.2f} investment.")
                
            # Best performing channels
            if "channel_analysis" in report and "ranking" in report["channel_analysis"] and report["channel_analysis"]["ranking"]:
                top_channels = report["channel_analysis"]["ranking"][:2]
                channel_names = [f"{c['channel']} ({c['roi_percentage']:.1f}% ROI)" for c in top_channels]
                
                if channel_names:
                    summary_points.append(f"Top performing channels: {', '.join(channel_names)}.")
                    
            # Break-even information
            if "time_analysis" in report and "summary" in report["time_analysis"] and "break_even_period" in report["time_analysis"]["summary"]:
                break_even = report["time_analysis"]["summary"]["break_even_period"]
                if break_even:
                    summary_points.append(f"Campaign reached break-even point on {break_even}.")
                else:
                    summary_points.append("Campaign has not yet reached break-even point.")
                    
            # Forecast highlight
            if "forecast" in report and "forecast_summary" in report["forecast"]:
                expected_roi = report["forecast"]["forecast_summary"]["final_expected_roi"]
                summary_points.append(f"Based on current trends, the campaign is projected to achieve a {expected_roi:.1f}% ROI in the next {forecast_period} days.")
                
            report["executive_summary"] = summary_points
            
        return report