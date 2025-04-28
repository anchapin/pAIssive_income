"""
API endpoints for monitoring and logging system.

This module provides API endpoints for accessing monitoring data, health status,
system metrics, and log data. It's designed to be integrated with a web framework
like Flask or FastAPI.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from common_utils.logging import get_logger
from common_utils.monitoring.metrics import get_metrics, export_metrics
from common_utils.monitoring.health import get_health_status
from common_utils.monitoring.system import get_system_metrics

logger = get_logger(__name__)


class MonitoringAPI:
    """
    API endpoints for monitoring and logging.
    
    This class provides methods that can be integrated with a web framework
    to expose monitoring and logging data through a REST API.
    """
    
    @staticmethod
    def get_metrics(format: str = "json") -> Dict[str, Any]:
        """
        Get all application metrics.
        
        Args:
            format: Output format (json or prometheus)
            
        Returns:
            Dictionary of metrics data
        """
        metrics_data = get_metrics()
        
        if format.lower() == "prometheus":
            # Convert to Prometheus format (simplified version)
            prometheus_output = []
            for name, metric_data in metrics_data.items():
                metric_type = metric_data["type"]
                description = metric_data["description"]
                value = metric_data["value"]
                labels = metric_data["labels"]
                
                # Add HELP and TYPE lines
                prometheus_output.append(f"# HELP {name} {description}")
                prometheus_output.append(f"# TYPE {name} {metric_type}")
                
                # Format labels if present
                if labels:
                    label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
                    prometheus_output.append(f"{name}{{{label_str}}} {value}")
                else:
                    prometheus_output.append(f"{name} {value}")
            
            return {"prometheus_format": "\n".join(prometheus_output)}
        
        return {"metrics": metrics_data}
    
    @staticmethod
    def get_health() -> Dict[str, Any]:
        """
        Get system health status.
        
        Returns:
            Dictionary with health status information
        """
        return get_health_status()
    
    @staticmethod
    def get_system() -> Dict[str, Any]:
        """
        Get system metrics.
        
        Returns:
            Dictionary with system resource metrics
        """
        return {"system": get_system_metrics()}
    
    @staticmethod
    def get_logs(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get application logs.
        
        Args:
            start_time: Start time for log filtering
            end_time: End time for log filtering
            level: Filter by log level
            limit: Maximum number of logs to return
            offset: Offset for pagination
            search_term: Search term to filter logs
            
        Returns:
            Dictionary with log entries and metadata
        """
        # Find log files
        log_dir = Path("logs")
        if not log_dir.exists():
            return {
                "logs": [],
                "total": 0,
                "metadata": {
                    "start_time": start_time,
                    "end_time": end_time,
                    "level": level,
                    "limit": limit,
                    "offset": offset,
                    "search_term": search_term,
                    "error": "Log directory not found"
                }
            }
        
        # Default to last 24 hours if no time range specified
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=1)
            
        # Find all log files in the logs directory
        log_files = sorted(log_dir.glob("*.log"), reverse=True)
        
        logs = []
        total_matching = 0
        
        # Process each log file
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            # Parse JSON log entry
                            log_entry = json.loads(line.strip())
                            
                            # Extract timestamp
                            log_time = datetime.fromtimestamp(log_entry.get("timestamp", 0))
                            
                            # Apply time filter
                            if log_time < start_time or log_time > end_time:
                                continue
                            
                            # Apply level filter
                            if level and log_entry.get("level", "").lower() != level.lower():
                                continue
                            
                            # Apply search term filter
                            if search_term:
                                message = log_entry.get("message", "")
                                if search_term.lower() not in message.lower():
                                    continue
                            
                            # Count total matching entries for pagination
                            total_matching += 1
                            
                            # Apply pagination
                            if total_matching <= offset:
                                continue
                            
                            if len(logs) >= limit:
                                continue
                            
                            # Add to results
                            logs.append(log_entry)
                            
                        except json.JSONDecodeError:
                            # Skip non-JSON lines
                            continue
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
        
        return {
            "logs": logs,
            "total": total_matching,
            "metadata": {
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "level": level,
                "limit": limit,
                "offset": offset,
                "search_term": search_term,
            }
        }
    
    @staticmethod
    def export_dashboard_data() -> Dict[str, Any]:
        """
        Export all monitoring data for dashboards.
        
        This method combines metrics, health status, and system metrics
        into a single response for easy consumption by dashboards.
        
        Returns:
            Dictionary with combined monitoring data
        """
        # Export metrics to update any cached values
        export_metrics()
        
        # Combine all monitoring data
        return {
            "metrics": get_metrics(),
            "health": get_health_status(),
            "system": get_system_metrics(),
            "timestamp": datetime.now().isoformat(),
        }


# Register API routes with Flask
def register_monitoring_api(app):
    """
    Register monitoring API endpoints with a Flask application.
    
    Args:
        app: Flask application instance
    """
    monitoring_api = MonitoringAPI()
    
    @app.route('/api/metrics', methods=['GET'])
    def api_metrics():
        format = app.request.args.get('format', 'json')
        return monitoring_api.get_metrics(format)
    
    @app.route('/api/health', methods=['GET'])
    def api_health():
        return monitoring_api.get_health()
    
    @app.route('/api/system', methods=['GET'])
    def api_system():
        return monitoring_api.get_system()
    
    @app.route('/api/logs', methods=['GET'])
    def api_logs():
        # Parse request parameters
        request = app.request
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        level = request.args.get('level')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        search_term = request.args.get('search')
        
        # Convert string timestamps to datetime objects
        if start_time:
            start_time = datetime.fromisoformat(start_time)
        if end_time:
            end_time = datetime.fromisoformat(end_time)
        
        return monitoring_api.get_logs(
            start_time, end_time, level, limit, offset, search_term
        )
    
    @app.route('/api/dashboard', methods=['GET'])
    def api_dashboard():
        return monitoring_api.export_dashboard_data()


# Register API routes with FastAPI
def register_fastapi_monitoring_api(app):
    """
    Register monitoring API endpoints with a FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    monitoring_api = MonitoringAPI()
    
    @app.get('/api/metrics')
    def api_metrics(format: str = "json"):
        return monitoring_api.get_metrics(format)
    
    @app.get('/api/health')
    def api_health():
        return monitoring_api.get_health()
    
    @app.get('/api/system')
    def api_system():
        return monitoring_api.get_system()
    
    @app.get('/api/logs')
    def api_logs(
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None
    ):
        # Convert string timestamps to datetime objects
        start_dt = None
        end_dt = None
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
        
        return monitoring_api.get_logs(
            start_dt, end_dt, level, limit, offset, search
        )
    
    @app.get('/api/dashboard')
    def api_dashboard():
        return monitoring_api.export_dashboard_data()