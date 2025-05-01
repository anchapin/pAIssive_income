"""
Market Trends module for market analysis.

This module provides tools for analyzing market trends, detecting seasonal patterns,
and comparing multi-year trends.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
import uuid
import math
import statistics
from collections import defaultdict

from .errors import (
    MarketTrendError,
    InvalidDataError,
    InsufficientDataError
)

# Set up logging
logger = logging.getLogger(__name__)


class TrendDataProcessor:
    """
    Processes and prepares trend data for analysis.
    """

    def __init__(self):
        """Initialize the TrendDataProcessor."""
        self.name = "Trend Data Processor"
        self.description = "Processes and prepares trend data for analysis"

    def validate_trend_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Validate trend data format.

        Args:
            data: List of trend data points

        Raises:
            InvalidDataError: If data format is invalid
        """
        if not data:
            raise InvalidDataError("Trend data cannot be empty")
        
        for i, point in enumerate(data):
            if "timestamp" not in point:
                raise InvalidDataError(f"Missing timestamp in data point {i}")
            
            if "value" not in point:
                raise InvalidDataError(f"Missing value in data point {i}")
            
            # Try to parse timestamp
            try:
                if isinstance(point["timestamp"], str):
                    datetime.fromisoformat(point["timestamp"])
            except ValueError:
                raise InvalidDataError(f"Invalid timestamp format in data point {i}")
            
            # Check value type
            if not isinstance(point["value"], (int, float)):
                raise InvalidDataError(f"Value must be a number in data point {i}")

    def normalize_trend_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize trend data for analysis.

        Args:
            data: List of trend data points

        Returns:
            Normalized trend data
        """
        self.validate_trend_data(data)
        
        normalized_data = []
        
        for point in data:
            normalized_point = point.copy()
            
            # Ensure timestamp is datetime object
            if isinstance(point["timestamp"], str):
                normalized_point["timestamp"] = datetime.fromisoformat(point["timestamp"])
            
            normalized_data.append(normalized_point)
        
        # Sort by timestamp
        normalized_data.sort(key=lambda x: x["timestamp"])
        
        return normalized_data

    def handle_missing_data(
        self, 
        data: List[Dict[str, Any]], 
        method: str = "interpolate"
    ) -> List[Dict[str, Any]]:
        """
        Handle missing data points in trend data.

        Args:
            data: List of trend data points
            method: Method to handle missing data ("interpolate", "previous", "skip")

        Returns:
            Processed trend data with missing values handled
        """
        normalized_data = self.normalize_trend_data(data)
        
        if len(normalized_data) < 2:
            return normalized_data
        
        # Find gaps in the data
        processed_data = []
        
        for i in range(len(normalized_data)):
            current_point = normalized_data[i]
            processed_data.append(current_point)
            
            # Skip the last point
            if i == len(normalized_data) - 1:
                continue
            
            next_point = normalized_data[i + 1]
            
            # Calculate time difference
            time_diff = (next_point["timestamp"] - current_point["timestamp"]).total_seconds()
            
            # Define what constitutes a gap (e.g., more than 2x the average time difference)
            if i == 0:
                # For the first point, we don't have a previous time difference
                continue
            
            prev_point = normalized_data[i - 1]
            prev_time_diff = (current_point["timestamp"] - prev_point["timestamp"]).total_seconds()
            
            # Check if there's a significant gap
            if time_diff > 2 * prev_time_diff:
                # Handle the gap based on the specified method
                if method == "interpolate":
                    # Linear interpolation
                    num_points = int(time_diff / prev_time_diff) - 1
                    
                    for j in range(1, num_points + 1):
                        # Calculate interpolated timestamp
                        interp_time = current_point["timestamp"] + timedelta(seconds=j * prev_time_diff)
                        
                        # Calculate interpolated value
                        progress = j / (num_points + 1)
                        interp_value = current_point["value"] + progress * (next_point["value"] - current_point["value"])
                        
                        # Add interpolated point
                        processed_data.append({
                            "timestamp": interp_time,
                            "value": interp_value,
                            "interpolated": True
                        })
                
                elif method == "previous":
                    # Fill with previous value
                    num_points = int(time_diff / prev_time_diff) - 1
                    
                    for j in range(1, num_points + 1):
                        # Calculate timestamp
                        fill_time = current_point["timestamp"] + timedelta(seconds=j * prev_time_diff)
                        
                        # Add filled point with previous value
                        processed_data.append({
                            "timestamp": fill_time,
                            "value": current_point["value"],
                            "filled": True
                        })
        
        # Sort by timestamp again
        processed_data.sort(key=lambda x: x["timestamp"])
        
        return processed_data

    def resample_irregular_data(
        self, 
        data: List[Dict[str, Any]], 
        interval_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Resample irregular time series data to regular intervals.

        Args:
            data: List of trend data points
            interval_days: Desired interval in days

        Returns:
            Resampled trend data
        """
        normalized_data = self.normalize_trend_data(data)
        
        if len(normalized_data) < 2:
            return normalized_data
        
        # Determine start and end dates
        start_date = normalized_data[0]["timestamp"]
        end_date = normalized_data[-1]["timestamp"]
        
        # Create regular time points
        regular_points = []
        current_date = start_date
        
        while current_date <= end_date:
            regular_points.append(current_date)
            current_date += timedelta(days=interval_days)
        
        # Resample data
        resampled_data = []
        
        for target_date in regular_points:
            # Find nearest data points
            before_points = [p for p in normalized_data if p["timestamp"] <= target_date]
            after_points = [p for p in normalized_data if p["timestamp"] > target_date]
            
            if before_points and after_points:
                # Interpolate between nearest points
                before_point = max(before_points, key=lambda x: x["timestamp"])
                after_point = min(after_points, key=lambda x: x["timestamp"])
                
                # Calculate weights based on time difference
                total_diff = (after_point["timestamp"] - before_point["timestamp"]).total_seconds()
                if total_diff == 0:
                    # Same timestamp, use before_point
                    resampled_value = before_point["value"]
                else:
                    before_diff = (target_date - before_point["timestamp"]).total_seconds()
                    after_weight = before_diff / total_diff
                    before_weight = 1 - after_weight
                    
                    # Linear interpolation
                    resampled_value = (
                        before_weight * before_point["value"] + 
                        after_weight * after_point["value"]
                    )
            elif before_points:
                # Use last available point
                before_point = max(before_points, key=lambda x: x["timestamp"])
                resampled_value = before_point["value"]
            elif after_points:
                # Use first available point
                after_point = min(after_points, key=lambda x: x["timestamp"])
                resampled_value = after_point["value"]
            else:
                # This shouldn't happen given our logic
                continue
            
            resampled_data.append({
                "timestamp": target_date,
                "value": resampled_value,
                "resampled": True
            })
        
        return resampled_data


class SeasonalPatternDetector:
    """
    Detects seasonal patterns in market trend data.
    """

    def __init__(self):
        """Initialize the SeasonalPatternDetector."""
        self.name = "Seasonal Pattern Detector"
        self.description = "Detects seasonal patterns in market trend data"
        self.data_processor = TrendDataProcessor()

    def detect_seasonal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect seasonal patterns in trend data.

        Args:
            data: List of trend data points

        Returns:
            Analysis of seasonal patterns
        """
        if not data or len(data) < 12:
            raise InsufficientDataError("At least 12 data points are required for seasonal pattern detection")
        
        # Normalize data
        normalized_data = self.data_processor.normalize_trend_data(data)
        
        # Group data by month
        monthly_data = defaultdict(list)
        
        for point in normalized_data:
            month = point["timestamp"].month
            monthly_data[month].append(point["value"])
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, values in monthly_data.items():
            monthly_averages[month] = sum(values) / len(values)
        
        # Calculate overall average
        overall_avg = sum(monthly_averages.values()) / len(monthly_averages)
        
        # Calculate seasonal indices
        seasonal_indices = {}
        for month, avg in monthly_averages.items():
            seasonal_indices[month] = avg / overall_avg if overall_avg > 0 else 1.0
        
        # Identify peaks and troughs
        sorted_indices = sorted(seasonal_indices.items(), key=lambda x: x[1], reverse=True)
        peak_months = [month for month, index in sorted_indices[:3]]
        trough_months = [month for month, index in sorted_indices[-3:]]
        
        # Calculate seasonal strength
        if len(seasonal_indices) >= 6:
            max_index = max(seasonal_indices.values())
            min_index = min(seasonal_indices.values())
            seasonal_strength = max_index - min_index
        else:
            seasonal_strength = 0.0
        
        # Determine if seasonality exists
        has_seasonality = seasonal_strength > 0.1  # 10% variation threshold
        
        return {
            "has_seasonality": has_seasonality,
            "seasonal_strength": seasonal_strength,
            "seasonal_indices": seasonal_indices,
            "peak_months": peak_months,
            "trough_months": trough_months,
            "monthly_averages": monthly_averages,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def detect_seasonal_patterns_irregular(
        self, 
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect seasonal patterns in irregular trend data.

        Args:
            data: List of trend data points with irregular intervals

        Returns:
            Analysis of seasonal patterns
        """
        if not data or len(data) < 8:
            raise InsufficientDataError("At least 8 data points are required for irregular seasonal pattern detection")
        
        # Normalize data
        normalized_data = self.data_processor.normalize_trend_data(data)
        
        # Resample to regular monthly intervals
        resampled_data = self.data_processor.resample_irregular_data(normalized_data, interval_days=30)
        
        # Group data by month
        monthly_data = defaultdict(list)
        
        for point in resampled_data:
            month = point["timestamp"].month
            monthly_data[month].append(point["value"])
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, values in monthly_data.items():
            monthly_averages[month] = sum(values) / len(values)
        
        # Calculate overall average
        overall_avg = sum(monthly_averages.values()) / len(monthly_averages)
        
        # Calculate seasonal indices
        seasonal_indices = {}
        for month, avg in monthly_averages.items():
            seasonal_indices[month] = avg / overall_avg if overall_avg > 0 else 1.0
        
        # Identify peaks and troughs
        sorted_indices = sorted(seasonal_indices.items(), key=lambda x: x[1], reverse=True)
        peak_months = [month for month, index in sorted_indices[:3] if len(sorted_indices) >= 3]
        trough_months = [month for month, index in sorted_indices[-3:] if len(sorted_indices) >= 3]
        
        # Calculate seasonal strength
        if len(seasonal_indices) >= 6:
            max_index = max(seasonal_indices.values())
            min_index = min(seasonal_indices.values())
            seasonal_strength = max_index - min_index
        else:
            seasonal_strength = 0.0
        
        # Determine if seasonality exists
        has_seasonality = seasonal_strength > 0.1  # 10% variation threshold
        
        # Calculate confidence score based on data quality
        coverage = len(monthly_data) / 12  # How many months are covered
        sample_size = sum(len(values) for values in monthly_data.values()) / len(monthly_data) if monthly_data else 0
        
        # Confidence score formula (simplified)
        confidence_score = min(1.0, (coverage * 0.5 + min(1.0, sample_size / 3) * 0.5))
        
        # Adjust confidence based on seasonal strength
        if seasonal_strength < 0.05:
            confidence_score *= 0.5
        elif seasonal_strength < 0.1:
            confidence_score *= 0.8
        
        return {
            "seasonal_patterns": has_seasonality,
            "confidence_score": confidence_score,
            "seasonal_strength": seasonal_strength,
            "period_length": "monthly",  # Assuming monthly seasonality
            "peak_months": peak_months,
            "trough_months": trough_months,
            "seasonal_indices": seasonal_indices,
            "monthly_averages": monthly_averages,
            "data_coverage_percent": coverage * 100,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def analyze_with_missing_data(
        self, 
        data: List[Dict[str, Any]], 
        missing_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze seasonal patterns with handling for missing data.

        Args:
            data: List of trend data points
            missing_threshold: Maximum acceptable proportion of missing data

        Returns:
            Analysis of seasonal patterns with missing data handling
        """
        if not data or len(data) < 8:
            raise InsufficientDataError("At least 8 data points are required for analysis with missing data")
        
        # Normalize data
        normalized_data = self.data_processor.normalize_trend_data(data)
        
        # Check for missing months
        months_present = set()
        for point in normalized_data:
            months_present.add(point["timestamp"].month)
        
        missing_months = set(range(1, 13)) - months_present
        missing_ratio = len(missing_months) / 12
        
        # Handle missing data if below threshold
        if missing_ratio <= missing_threshold:
            # Process data with interpolation
            processed_data = self.data_processor.handle_missing_data(normalized_data, method="interpolate")
            
            # Detect seasonal patterns
            seasonal_analysis = self.detect_seasonal_patterns_irregular(processed_data)
            
            # Add missing data information
            seasonal_analysis["missing_months"] = sorted(list(missing_months))
            seasonal_analysis["missing_data_ratio"] = missing_ratio
            seasonal_analysis["missing_data_handled"] = True
            seasonal_analysis["handling_method"] = "interpolate"
            
            return seasonal_analysis
        else:
            # Too much missing data
            raise InsufficientDataError(
                f"Too much missing data ({missing_ratio:.1%}) exceeds threshold ({missing_threshold:.1%})"
            )


class MultiYearTrendComparator:
    """
    Compares market trends across multiple years.
    """

    def __init__(self):
        """Initialize the MultiYearTrendComparator."""
        self.name = "Multi-Year Trend Comparator"
        self.description = "Compares market trends across multiple years"
        self.data_processor = TrendDataProcessor()
        self.seasonal_detector = SeasonalPatternDetector()

    def compare_yearly_seasonality(
        self, 
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare seasonal patterns across multiple years.

        Args:
            data: List of trend data points spanning multiple years

        Returns:
            Analysis of multi-year seasonal patterns
        """
        if not data or len(data) < 24:
            raise InsufficientDataError("At least 24 data points spanning multiple years are required")
        
        # Normalize data
        normalized_data = self.data_processor.normalize_trend_data(data)
        
        # Group data by year
        yearly_data = defaultdict(list)
        
        for point in normalized_data:
            year = point["timestamp"].year
            yearly_data[year].append(point)
        
        # Need at least 2 years
        if len(yearly_data) < 2:
            raise InsufficientDataError("Data must span at least 2 years")
        
        # Analyze each year
        yearly_analyses = {}
        for year, year_data in yearly_data.items():
            try:
                # Skip years with insufficient data
                if len(year_data) < 8:
                    continue
                
                yearly_analyses[year] = self.seasonal_detector.detect_seasonal_patterns_irregular(year_data)
            except (InvalidDataError, InsufficientDataError):
                # Skip years with analysis errors
                continue
        
        # Need at least 2 years with valid analyses
        if len(yearly_analyses) < 2:
            raise InsufficientDataError("Not enough years with sufficient data")
        
        # Compare seasonal patterns across years
        years = sorted(yearly_analyses.keys())
        
        # Calculate year-over-year changes in seasonal strength
        yoy_changes = {}
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            
            prev_strength = yearly_analyses[prev_year]["seasonal_strength"]
            curr_strength = yearly_analyses[curr_year]["seasonal_strength"]
            
            yoy_changes[f"{prev_year}-{curr_year}"] = curr_strength - prev_strength
        
        # Calculate seasonal stability
        seasonal_strengths = [analysis["seasonal_strength"] for analysis in yearly_analyses.values()]
        
        if len(seasonal_strengths) >= 2:
            # Use coefficient of variation as stability measure (inverted)
            mean_strength = statistics.mean(seasonal_strengths)
            if mean_strength > 0:
                stdev_strength = statistics.stdev(seasonal_strengths)
                cv = stdev_strength / mean_strength
                seasonal_stability = 1.0 - min(1.0, cv)  # Higher value means more stable
            else:
                seasonal_stability = 0.0
        else:
            seasonal_stability = 0.0
        
        # Compare peak and trough months across years
        peak_month_consistency = self._calculate_month_consistency(
            [set(analysis["peak_months"]) for analysis in yearly_analyses.values()]
        )
        
        trough_month_consistency = self._calculate_month_consistency(
            [set(analysis["trough_months"]) for analysis in yearly_analyses.values()]
        )
        
        # Determine if seasonality is strengthening or weakening
        recent_years = sorted(years)[-2:]
        if len(recent_years) >= 2:
            prev_year = recent_years[0]
            curr_year = recent_years[1]
            
            prev_strength = yearly_analyses[prev_year]["seasonal_strength"]
            curr_strength = yearly_analyses[curr_year]["seasonal_strength"]
            
            if curr_strength > prev_strength * 1.1:
                trend_direction = "strengthening"
            elif curr_strength < prev_strength * 0.9:
                trend_direction = "weakening"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "unknown"
        
        return {
            "years_analyzed": years,
            "seasonal_stability": seasonal_stability,
            "year_over_year_changes": yoy_changes,
            "seasonal_strength_by_year": {year: analysis["seasonal_strength"] for year, analysis in yearly_analyses.items()},
            "peak_month_consistency": peak_month_consistency,
            "trough_month_consistency": trough_month_consistency,
            "trend_direction": trend_direction,
            "yearly_analyses": yearly_analyses,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _calculate_month_consistency(self, month_sets: List[set]) -> float:
        """
        Calculate consistency of months across years.

        Args:
            month_sets: List of sets containing months

        Returns:
            Consistency score between 0 and 1
        """
        if not month_sets:
            return 0.0
        
        # Count occurrences of each month
        month_counts = defaultdict(int)
        for month_set in month_sets:
            for month in month_set:
                month_counts[month] += 1
        
        # Calculate consistency
        max_count = len(month_sets)
        consistency_scores = [count / max_count for count in month_counts.values()]
        
        # Average consistency
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0


class MarketTrendAnalyzer:
    """
    Main class for market trend analysis functionality.
    """

    def __init__(self):
        """Initialize the MarketTrendAnalyzer class."""
        self.data_processor = TrendDataProcessor()
        self.seasonal_detector = SeasonalPatternDetector()
        self.multi_year_comparator = MultiYearTrendComparator()
        self.name = "Market Trend Analyzer"
        self.description = "Analyzes market trends and seasonal patterns"

    def detect_seasonal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect seasonal patterns in market trend data.

        Args:
            data: List of trend data points

        Returns:
            Analysis of seasonal patterns
        """
        try:
            return self.seasonal_detector.detect_seasonal_patterns(data)
        except Exception as e:
            logger.error(f"Error in seasonal pattern detection: {str(e)}")
            raise MarketTrendError(f"Seasonal pattern detection failed: {str(e)}")

    def detect_seasonal_patterns_irregular(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect seasonal patterns in irregular market trend data.

        Args:
            data: List of trend data points with irregular intervals

        Returns:
            Analysis of seasonal patterns
        """
        try:
            return self.seasonal_detector.detect_seasonal_patterns_irregular(data)
        except Exception as e:
            logger.error(f"Error in irregular seasonal pattern detection: {str(e)}")
            raise MarketTrendError(f"Irregular seasonal pattern detection failed: {str(e)}")

    def analyze_with_missing_data(
        self, 
        data: List[Dict[str, Any]], 
        missing_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze seasonal patterns with handling for missing data.

        Args:
            data: List of trend data points
            missing_threshold: Maximum acceptable proportion of missing data

        Returns:
            Analysis of seasonal patterns with missing data handling
        """
        try:
            return self.seasonal_detector.analyze_with_missing_data(data, missing_threshold)
        except Exception as e:
            logger.error(f"Error in analysis with missing data: {str(e)}")
            raise MarketTrendError(f"Analysis with missing data failed: {str(e)}")

    def compare_multi_year_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare market trends across multiple years.

        Args:
            data: List of trend data points spanning multiple years

        Returns:
            Analysis of multi-year trends
        """
        try:
            return self.multi_year_comparator.compare_yearly_seasonality(data)
        except Exception as e:
            logger.error(f"Error in multi-year trend comparison: {str(e)}")
            raise MarketTrendError(f"Multi-year trend comparison failed: {str(e)}")
