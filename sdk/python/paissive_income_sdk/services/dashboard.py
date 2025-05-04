"""
"""
Dashboard service for the pAIssive Income API.
Dashboard service for the pAIssive Income API.


This module provides a service for interacting with the dashboard endpoints.
This module provides a service for interacting with the dashboard endpoints.
"""
"""




from typing import Any, Dict, Optional
from typing import Any, Dict, Optional


from .base import BaseService
from .base import BaseService




class DashboardService:
    class DashboardService:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Dashboard service.
    Dashboard service.
    """
    """


    def get_overview(self) -> Dict[str, Any]:
    def get_overview(self) -> Dict[str, Any]:
    """
    """
    Get dashboard overview.
    Get dashboard overview.


    Returns:
    Returns:
    Dashboard overview data
    Dashboard overview data
    """
    """
    return self._get("dashboard/overview")
    return self._get("dashboard/overview")


    def get_revenue_stats(
    def get_revenue_stats(
    self, params: Optional[Dict[str, Any]] = None
    self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get revenue statistics.
    Get revenue statistics.


    Args:
    Args:
    params: Optional query parameters
    params: Optional query parameters
    - start_date: Start date for the statistics (ISO format)
    - start_date: Start date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - interval: Time interval for data points (day, week, month)
    - interval: Time interval for data points (day, week, month)


    Returns:
    Returns:
    Revenue statistics
    Revenue statistics
    """
    """
    return self._get("dashboard/revenue", params=params)
    return self._get("dashboard/revenue", params=params)


    def get_subscriber_stats(
    def get_subscriber_stats(
    self, params: Optional[Dict[str, Any]] = None
    self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get subscriber statistics.
    Get subscriber statistics.


    Args:
    Args:
    params: Optional query parameters
    params: Optional query parameters
    - start_date: Start date for the statistics (ISO format)
    - start_date: Start date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - interval: Time interval for data points (day, week, month)
    - interval: Time interval for data points (day, week, month)


    Returns:
    Returns:
    Subscriber statistics
    Subscriber statistics
    """
    """
    return self._get("dashboard/subscribers", params=params)
    return self._get("dashboard/subscribers", params=params)


    def get_traffic_stats(
    def get_traffic_stats(
    self, params: Optional[Dict[str, Any]] = None
    self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get website traffic statistics.
    Get website traffic statistics.


    Args:
    Args:
    params: Optional query parameters
    params: Optional query parameters
    - start_date: Start date for the statistics (ISO format)
    - start_date: Start date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - interval: Time interval for data points (day, week, month)
    - interval: Time interval for data points (day, week, month)


    Returns:
    Returns:
    Traffic statistics
    Traffic statistics
    """
    """
    return self._get("dashboard/traffic", params=params)
    return self._get("dashboard/traffic", params=params)


    def get_conversion_stats(
    def get_conversion_stats(
    self, params: Optional[Dict[str, Any]] = None
    self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Get conversion statistics.
    Get conversion statistics.


    Args:
    Args:
    params: Optional query parameters
    params: Optional query parameters
    - start_date: Start date for the statistics (ISO format)
    - start_date: Start date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - end_date: End date for the statistics (ISO format)
    - interval: Time interval for data points (day, week, month)
    - interval: Time interval for data points (day, week, month)


    Returns:
    Returns:
    Conversion statistics
    Conversion statistics
    """
    """
    return self._get("dashboard/conversions", params=params)
    return self._get("dashboard/conversions", params=params)


    def get_performance_metrics(self) -> Dict[str, Any]:
    def get_performance_metrics(self) -> Dict[str, Any]:
    """
    """
    Get performance metrics.
    Get performance metrics.


    Returns:
    Returns:
    Performance metrics
    Performance metrics
    """
    """
    return self._get("dashboard/performance")
    return self._get("dashboard/performance")