"""
API Analytics Service.

This module provides a service for collecting, analyzing, and reporting on API usage.
"""

import os
import uuid
import json
import logging
import threading
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta, date
import csv
import io

from .database import AnalyticsDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for collecting and analyzing API usage data.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls, db_path: str = None):
        """
        Get or create a singleton instance of the analytics service.
        
        Args:
            db_path: Optional database path to use when creating the instance
            
        Returns:
            AnalyticsService instance
        """
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """
        Initialize the analytics service.
        
        Args:
            db_path: Path to the analytics database
        """
        self.db = AnalyticsDatabase(db_path)
        self._lock = threading.Lock()
        
        # Start background thread for daily metrics aggregation
        self._stop_event = threading.Event()
        self._aggregation_thread = threading.Thread(
            target=self._daily_aggregation_task,
            daemon=True
        )
        self._aggregation_thread.start()
    
    def track_request(self,
                     method: str,
                     path: str,
                     endpoint: str,
                     version: str = None,
                     status_code: int = None,
                     response_time: float = None,
                     user_id: str = None,
                     api_key_id: str = None,
                     client_ip: str = None,
                     user_agent: str = None,
                     request_size: int = None,
                     response_size: int = None,
                     query_params: Dict[str, Any] = None,
                     error_type: str = None,
                     error_message: str = None,
                     metadata: Dict[str, Any] = None) -> str:
        """
        Track an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            endpoint: Endpoint name (e.g., "/api/v1/users")
            version: API version
            status_code: HTTP status code
            response_time: Response time in seconds
            user_id: User ID
            api_key_id: API key ID
            client_ip: Client IP address
            user_agent: User agent string
            request_size: Request size in bytes
            response_size: Response size in bytes
            query_params: Query parameters
            error_type: Error type if an error occurred
            error_message: Error message if an error occurred
            metadata: Additional metadata
            
        Returns:
            Request ID
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Create request data
        request_data = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": path,
            "endpoint": endpoint,
            "version": version,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id,
            "api_key_id": api_key_id,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_size": request_size,
            "response_size": response_size,
            "query_params": query_params,
            "error_type": error_type,
            "error_message": error_message,
            "metadata": metadata
        }
        
        # Save request data
        try:
            self.db.save_request(request_data)
        except Exception as e:
            logger.error(f"Error saving request data: {e}")
        
        return request_id
    
    def get_requests(self,
                    endpoint: str = None,
                    version: str = None,
                    user_id: str = None,
                    api_key_id: str = None,
                    status_code: int = None,
                    days: int = 7,
                    limit: int = 1000,
                    offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get API requests.
        
        Args:
            endpoint: Filter by endpoint
            version: Filter by API version
            user_id: Filter by user ID
            api_key_id: Filter by API key ID
            status_code: Filter by status code
            days: Number of days to include
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of request dictionaries
        """
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_range = (start_time, end_time)
        
        return self.db.get_requests(
            endpoint=endpoint,
            version=version,
            user_id=user_id,
            api_key_id=api_key_id,
            status_code=status_code,
            time_range=time_range,
            limit=limit,
            offset=offset
        )
    
    def get_daily_metrics(self,
                         days: int = 30,
                         endpoint: str = None,
                         version: str = None) -> List[Dict[str, Any]]:
        """
        Get daily aggregated metrics.
        
        Args:
            days: Number of days to include
            endpoint: Filter by endpoint
            version: Filter by API version
            
        Returns:
            List of daily metrics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.db.get_daily_metrics(
            start_date=start_date,
            end_date=end_date,
            endpoint=endpoint,
            version=version
        )
    
    def get_user_metrics(self,
                        days: int = 30,
                        user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get user metrics.
        
        Args:
            days: Number of days to include
            user_id: Filter by user ID
            
        Returns:
            List of user metrics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.db.get_user_metrics(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
    
    def get_api_key_metrics(self,
                           days: int = 30,
                           api_key_id: str = None) -> List[Dict[str, Any]]:
        """
        Get API key metrics.
        
        Args:
            days: Number of days to include
            api_key_id: Filter by API key ID
            
        Returns:
            List of API key metrics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.db.get_api_key_metrics(
            start_date=start_date,
            end_date=end_date,
            api_key_id=api_key_id
        )
    
    def get_endpoint_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get aggregated statistics for each endpoint.
        
        Args:
            days: Number of days to include
            
        Returns:
            List of endpoint statistics dictionaries
        """
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.db.get_endpoint_stats(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get a summary of API usage.
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary with usage summary
        """
        # Get endpoint stats
        endpoint_stats = self.get_endpoint_stats(days)
        
        # Calculate totals
        total_requests = sum(stat.get("total_requests", 0) for stat in endpoint_stats)
        total_errors = sum(stat.get("total_errors", 0) for stat in endpoint_stats)
        error_rate = total_errors / total_requests if total_requests > 0 else 0
        
        # Calculate average response time
        total_response_time = sum(
            stat.get("avg_response_time", 0) * stat.get("total_requests", 0)
            for stat in endpoint_stats
        )
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
        
        # Get top endpoints
        top_endpoints = sorted(
            endpoint_stats,
            key=lambda x: x.get("total_requests", 0),
            reverse=True
        )[:5]
        
        # Get user metrics
        user_metrics = self.get_user_metrics(days)
        
        # Calculate unique users
        unique_users = len(set(metric.get("user_id") for metric in user_metrics))
        
        # Get API key metrics
        api_key_metrics = self.get_api_key_metrics(days)
        
        # Calculate unique API keys
        unique_api_keys = len(set(metric.get("api_key_id") for metric in api_key_metrics))
        
        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "unique_users": unique_users,
            "unique_api_keys": unique_api_keys,
            "top_endpoints": top_endpoints
        }
    
    def export_requests_csv(self,
                           days: int = 30,
                           endpoint: str = None,
                           version: str = None,
                           user_id: str = None,
                           api_key_id: str = None) -> str:
        """
        Export API requests to CSV.
        
        Args:
            days: Number of days to include
            endpoint: Filter by endpoint
            version: Filter by API version
            user_id: Filter by user ID
            api_key_id: Filter by API key ID
            
        Returns:
            CSV string
        """
        # Get requests
        requests = self.get_requests(
            endpoint=endpoint,
            version=version,
            user_id=user_id,
            api_key_id=api_key_id,
            days=days,
            limit=10000  # Higher limit for exports
        )
        
        if not requests:
            return "No data to export"
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id", "timestamp", "method", "path", "endpoint", "version",
                "status_code", "response_time", "user_id", "api_key_id",
                "client_ip", "request_size", "response_size", "error_type"
            ]
        )
        
        writer.writeheader()
        
        for request in requests:
            # Create a simplified row with only the fields we want
            row = {
                "id": request.get("id"),
                "timestamp": request.get("timestamp"),
                "method": request.get("method"),
                "path": request.get("path"),
                "endpoint": request.get("endpoint"),
                "version": request.get("version"),
                "status_code": request.get("status_code"),
                "response_time": request.get("response_time"),
                "user_id": request.get("user_id"),
                "api_key_id": request.get("api_key_id"),
                "client_ip": request.get("client_ip"),
                "request_size": request.get("request_size"),
                "response_size": request.get("response_size"),
                "error_type": request.get("error_type")
            }
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def export_metrics_csv(self, days: int = 30) -> str:
        """
        Export daily metrics to CSV.
        
        Args:
            days: Number of days to include
            
        Returns:
            CSV string
        """
        # Get daily metrics
        metrics = self.get_daily_metrics(days)
        
        if not metrics:
            return "No data to export"
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "date", "endpoint", "version", "request_count", "error_count",
                "avg_response_time", "min_response_time", "max_response_time",
                "p95_response_time", "total_request_size", "total_response_size",
                "unique_users", "unique_api_keys"
            ]
        )
        
        writer.writeheader()
        
        for metric in metrics:
            writer.writerow(metric)
        
        return output.getvalue()
    
    def cleanup_old_data(self, days: int = 365) -> int:
        """
        Remove data older than the specified number of days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of records deleted
        """
        return self.db.cleanup_old_data(days)
    
    def _daily_aggregation_task(self) -> None:
        """
        Background task for daily metrics aggregation.
        """
        while not self._stop_event.is_set():
            try:
                # Get current date
                today = datetime.now().strftime("%Y-%m-%d")
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                
                # Update metrics for yesterday and today
                self.db.update_daily_metrics(yesterday)
                self.db.update_daily_metrics(today)
                
                # Cleanup old data once a day
                self.db.cleanup_old_data()
                
                # Sleep for 1 hour
                self._stop_event.wait(3600)
                
            except Exception as e:
                logger.error(f"Error in daily aggregation task: {e}")
                # Sleep for 5 minutes before retrying
                self._stop_event.wait(300)
    
    def stop(self) -> None:
        """
        Stop the analytics service.
        """
        self._stop_event.set()
        if self._aggregation_thread.is_alive():
            self._aggregation_thread.join(timeout=5)
        
        self.db.close()


# Create a global instance of the analytics service
analytics_service = AnalyticsService.get_instance()
