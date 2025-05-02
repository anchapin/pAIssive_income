"""
Dashboard service for the pAIssive Income API.

This module provides a service for interacting with the dashboard endpoints.
"""

from typing import Dict, Any, Optional

from .base import BaseService


class DashboardService(BaseService):
    """
    Dashboard service.
    """

    def get_overview(self) -> Dict[str, Any]:
        """
        Get dashboard overview.

        Returns:
            Dashboard overview data
        """
        return self._get("dashboard/overview")

    def get_revenue_stats(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get revenue statistics.

        Args:
            params: Optional query parameters
                - start_date: Start date for the statistics (ISO format)
                - end_date: End date for the statistics (ISO format)
                - interval: Time interval for data points (day, week, month)

        Returns:
            Revenue statistics
        """
        return self._get("dashboard/revenue", params=params)

    def get_subscriber_stats(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get subscriber statistics.

        Args:
            params: Optional query parameters
                - start_date: Start date for the statistics (ISO format)
                - end_date: End date for the statistics (ISO format)
                - interval: Time interval for data points (day, week, month)

        Returns:
            Subscriber statistics
        """
        return self._get("dashboard/subscribers", params=params)

    def get_traffic_stats(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get website traffic statistics.

        Args:
            params: Optional query parameters
                - start_date: Start date for the statistics (ISO format)
                - end_date: End date for the statistics (ISO format)
                - interval: Time interval for data points (day, week, month)

        Returns:
            Traffic statistics
        """
        return self._get("dashboard/traffic", params=params)

    def get_conversion_stats(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get conversion statistics.

        Args:
            params: Optional query parameters
                - start_date: Start date for the statistics (ISO format)
                - end_date: End date for the statistics (ISO format)
                - interval: Time interval for data points (day, week, month)

        Returns:
            Conversion statistics
        """
        return self._get("dashboard/conversions", params=params)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.

        Returns:
            Performance metrics
        """
        return self._get("dashboard/performance")
