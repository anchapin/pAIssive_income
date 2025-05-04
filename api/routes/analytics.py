import logging
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import JSONResponse, StreamingResponse

from api.analytics import analytics_service

from ..schemas.common import SuccessResponse

FASTAPI_AVAILABLE

(
AlertThresholdRequest,
AlertThresholdResponse,
AnalyticsSummaryResponse,
ApiKeyStatsResponse,
EndpointStatsResponse,
RealTimeMetricsResponse,
RequestStatsResponse,
UserStatsResponse,
)
"""
"""
API routes for analytics.
API routes for analytics.


This module provides API routes for accessing analytics data.
This module provides API routes for accessing analytics data.
"""
"""


# Set up logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Try to import FastAPI
# Try to import FastAPI
try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning("FastAPI is required for analytics routes")
    logger.warning("FastAPI is required for analytics routes")
    FASTAPI_AVAILABLE = False
    FASTAPI_AVAILABLE = False


    # Create router
    # Create router
    if FASTAPI_AVAILABLE:
    if FASTAPI_AVAILABLE:
    router = APIRouter()
    router = APIRouter()
    else:
    else:
    router = None
    router = None




    @router.get(
    @router.get(
    "/summary",
    "/summary",
    response_model=AnalyticsSummaryResponse,
    response_model=AnalyticsSummaryResponse,
    summary="Get API usage summary",
    summary="Get API usage summary",
    description="Get a summary of API usage statistics",
    description="Get a summary of API usage statistics",
    )
    )
    async def get_summary(days: int = Query(30, description="Number of days to include")):
    async def get_summary(days: int = Query(30, description="Number of days to include")):
    """
    """
    Get a summary of API usage statistics.
    Get a summary of API usage statistics.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    API usage summary
    API usage summary
    """
    """
    try:
    try:
    summary = analytics_service.get_usage_summary(days)
    summary = analytics_service.get_usage_summary(days)
    return summary
    return summary
except Exception as e:
except Exception as e:
    logger.error(f"Error getting usage summary: {e}")
    logger.error(f"Error getting usage summary: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/requests",
    "/requests",
    response_model=List[RequestStatsResponse],
    response_model=List[RequestStatsResponse],
    summary="Get API request statistics",
    summary="Get API request statistics",
    description="Get detailed statistics for API requests",
    description="Get detailed statistics for API requests",
    )
    )
    async def get_requests(
    async def get_requests(
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    version: Optional[str] = Query(None, description="Filter by API version"),
    version: Optional[str] = Query(None, description="Filter by API version"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    days: int = Query(7, description="Number of days to include"),
    days: int = Query(7, description="Number of days to include"),
    limit: int = Query(100, description="Maximum number of records to return"),
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    offset: int = Query(0, description="Number of records to skip"),
    ):
    ):
    """
    """
    Get detailed statistics for API requests.
    Get detailed statistics for API requests.


    Args:
    Args:
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version
    user_id: Filter by user ID
    user_id: Filter by user ID
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID
    status_code: Filter by status code
    status_code: Filter by status code
    days: Number of days to include
    days: Number of days to include
    limit: Maximum number of records to return
    limit: Maximum number of records to return
    offset: Number of records to skip
    offset: Number of records to skip


    Returns:
    Returns:
    List of request statistics
    List of request statistics
    """
    """
    try:
    try:
    requests = analytics_service.get_requests(
    requests = analytics_service.get_requests(
    endpoint=endpoint,
    endpoint=endpoint,
    version=version,
    version=version,
    user_id=user_id,
    user_id=user_id,
    api_key_id=api_key_id,
    api_key_id=api_key_id,
    status_code=status_code,
    status_code=status_code,
    days=days,
    days=days,
    limit=limit,
    limit=limit,
    offset=offset,
    offset=offset,
    )
    )
    return requests
    return requests
except Exception as e:
except Exception as e:
    logger.error(f"Error getting request statistics: {e}")
    logger.error(f"Error getting request statistics: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/endpoints",
    "/endpoints",
    response_model=List[EndpointStatsResponse],
    response_model=List[EndpointStatsResponse],
    summary="Get endpoint statistics",
    summary="Get endpoint statistics",
    description="Get statistics for each API endpoint",
    description="Get statistics for each API endpoint",
    )
    )
    async def get_endpoint_stats(
    async def get_endpoint_stats(
    days: int = Query(30, description="Number of days to include")
    days: int = Query(30, description="Number of days to include")
    ):
    ):
    """
    """
    Get statistics for each API endpoint.
    Get statistics for each API endpoint.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    List of endpoint statistics
    List of endpoint statistics
    """
    """
    try:
    try:
    stats = analytics_service.get_endpoint_stats(days)
    stats = analytics_service.get_endpoint_stats(days)
    return stats
    return stats
except Exception as e:
except Exception as e:
    logger.error(f"Error getting endpoint statistics: {e}")
    logger.error(f"Error getting endpoint statistics: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/users",
    "/users",
    response_model=List[UserStatsResponse],
    response_model=List[UserStatsResponse],
    summary="Get user statistics",
    summary="Get user statistics",
    description="Get statistics for API usage by users",
    description="Get statistics for API usage by users",
    )
    )
    async def get_user_stats(
    async def get_user_stats(
    days: int = Query(30, description="Number of days to include"),
    days: int = Query(30, description="Number of days to include"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    ):
    ):
    """
    """
    Get statistics for API usage by users.
    Get statistics for API usage by users.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include
    user_id: Filter by user ID
    user_id: Filter by user ID


    Returns:
    Returns:
    List of user statistics
    List of user statistics
    """
    """
    try:
    try:
    stats = analytics_service.get_user_metrics(days=days, user_id=user_id)
    stats = analytics_service.get_user_metrics(days=days, user_id=user_id)
    return stats
    return stats
except Exception as e:
except Exception as e:
    logger.error(f"Error getting user statistics: {e}")
    logger.error(f"Error getting user statistics: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/api-keys",
    "/api-keys",
    response_model=List[ApiKeyStatsResponse],
    response_model=List[ApiKeyStatsResponse],
    summary="Get API key statistics",
    summary="Get API key statistics",
    description="Get statistics for API usage by API keys",
    description="Get statistics for API usage by API keys",
    )
    )
    async def get_api_key_stats(
    async def get_api_key_stats(
    days: int = Query(30, description="Number of days to include"),
    days: int = Query(30, description="Number of days to include"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    ):
    ):
    """
    """
    Get statistics for API usage by API keys.
    Get statistics for API usage by API keys.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID


    Returns:
    Returns:
    List of API key statistics
    List of API key statistics
    """
    """
    try:
    try:
    stats = analytics_service.get_api_key_metrics(days=days, api_key_id=api_key_id)
    stats = analytics_service.get_api_key_metrics(days=days, api_key_id=api_key_id)
    return stats
    return stats
except Exception as e:
except Exception as e:
    logger.error(f"Error getting API key statistics: {e}")
    logger.error(f"Error getting API key statistics: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/export/requests",
    "/export/requests",
    summary="Export API requests to CSV",
    summary="Export API requests to CSV",
    description="Export detailed API request data to CSV format",
    description="Export detailed API request data to CSV format",
    )
    )
    async def export_requests_csv(
    async def export_requests_csv(
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    version: Optional[str] = Query(None, description="Filter by API version"),
    version: Optional[str] = Query(None, description="Filter by API version"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    days: int = Query(30, description="Number of days to include"),
    days: int = Query(30, description="Number of days to include"),
    ):
    ):
    """
    """
    Export detailed API request data to CSV format.
    Export detailed API request data to CSV format.


    Args:
    Args:
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version
    user_id: Filter by user ID
    user_id: Filter by user ID
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    CSV file
    CSV file
    """
    """
    try:
    try:
    csv_data = analytics_service.export_requests_csv(
    csv_data = analytics_service.export_requests_csv(
    days=days,
    days=days,
    endpoint=endpoint,
    endpoint=endpoint,
    version=version,
    version=version,
    user_id=user_id,
    user_id=user_id,
    api_key_id=api_key_id,
    api_key_id=api_key_id,
    )
    )


    # Generate filename
    # Generate filename
    date_str = datetime.now().strftime("%Y%m%d")
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"api_requests_{date_str}.csv"
    filename = f"api_requests_{date_str}.csv"


    # Return CSV file
    # Return CSV file
    return StreamingResponse(
    return StreamingResponse(
    iter([csv_data]),
    iter([csv_data]),
    media_type="text/csv",
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename={filename}"},
    headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error exporting requests to CSV: {e}")
    logger.error(f"Error exporting requests to CSV: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/export/metrics",
    "/export/metrics",
    summary="Export daily metrics to CSV",
    summary="Export daily metrics to CSV",
    description="Export daily aggregated metrics to CSV format",
    description="Export daily aggregated metrics to CSV format",
    )
    )
    async def export_metrics_csv(
    async def export_metrics_csv(
    days: int = Query(30, description="Number of days to include")
    days: int = Query(30, description="Number of days to include")
    ):
    ):
    """
    """
    Export daily aggregated metrics to CSV format.
    Export daily aggregated metrics to CSV format.


    Args:
    Args:
    days: Number of days to include
    days: Number of days to include


    Returns:
    Returns:
    CSV file
    CSV file
    """
    """
    try:
    try:
    csv_data = analytics_service.export_metrics_csv(days=days)
    csv_data = analytics_service.export_metrics_csv(days=days)


    # Generate filename
    # Generate filename
    date_str = datetime.now().strftime("%Y%m%d")
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"api_metrics_{date_str}.csv"
    filename = f"api_metrics_{date_str}.csv"


    # Return CSV file
    # Return CSV file
    return StreamingResponse(
    return StreamingResponse(
    iter([csv_data]),
    iter([csv_data]),
    media_type="text/csv",
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename={filename}"},
    headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error exporting metrics to CSV: {e}")
    logger.error(f"Error exporting metrics to CSV: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.get(
    @router.get(
    "/real-time",
    "/real-time",
    response_model=RealTimeMetricsResponse,
    response_model=RealTimeMetricsResponse,
    summary="Get real-time API metrics",
    summary="Get real-time API metrics",
    description="Get real-time metrics for API usage in the last few minutes",
    description="Get real-time metrics for API usage in the last few minutes",
    )
    )
    async def get_real_time_metrics(
    async def get_real_time_metrics(
    minutes: int = Query(5, description="Number of minutes to include")
    minutes: int = Query(5, description="Number of minutes to include")
    ):
    ):
    """
    """
    Get real-time metrics for API usage in the last few minutes.
    Get real-time metrics for API usage in the last few minutes.


    Args:
    Args:
    minutes: Number of minutes to include
    minutes: Number of minutes to include


    Returns:
    Returns:
    Real-time metrics
    Real-time metrics
    """
    """
    try:
    try:
    metrics = analytics_service.get_real_time_metrics(minutes)
    metrics = analytics_service.get_real_time_metrics(minutes)
    # Add timestamp to metrics
    # Add timestamp to metrics
    metrics["timestamp"] = datetime.now().isoformat()
    metrics["timestamp"] = datetime.now().isoformat()
    return metrics
    return metrics
except Exception as e:
except Exception as e:
    logger.error(f"Error getting real-time metrics: {e}")
    logger.error(f"Error getting real-time metrics: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.post(
    @router.post(
    "/alerts/thresholds",
    "/alerts/thresholds",
    response_model=AlertThresholdResponse,
    response_model=AlertThresholdResponse,
    summary="Set alert threshold",
    summary="Set alert threshold",
    description="Set a threshold for a specific metric that will trigger alerts when exceeded",
    description="Set a threshold for a specific metric that will trigger alerts when exceeded",
    )
    )
    async def set_alert_threshold(threshold: AlertThresholdRequest):
    async def set_alert_threshold(threshold: AlertThresholdRequest):
    """
    """
    Set a threshold for a specific metric that will trigger alerts when exceeded.
    Set a threshold for a specific metric that will trigger alerts when exceeded.


    Args:
    Args:
    threshold: Alert threshold request
    threshold: Alert threshold request


    Returns:
    Returns:
    Alert threshold response
    Alert threshold response
    """
    """
    try:
    try:
    analytics_service.set_alert_threshold(threshold.metric, threshold.threshold)
    analytics_service.set_alert_threshold(threshold.metric, threshold.threshold)
    return {
    return {
    "metric": threshold.metric,
    "metric": threshold.metric,
    "threshold": threshold.threshold,
    "threshold": threshold.threshold,
    "message": f"Alert threshold for {threshold.metric} set to {threshold.threshold}",
    "message": f"Alert threshold for {threshold.metric} set to {threshold.threshold}",
    }
    }
except Exception as e:
except Exception as e:
    logger.error(f"Error setting alert threshold: {e}")
    logger.error(f"Error setting alert threshold: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))




    @router.post(
    @router.post(
    "/cleanup",
    "/cleanup",
    response_model=SuccessResponse,
    response_model=SuccessResponse,
    summary="Clean up old analytics data",
    summary="Clean up old analytics data",
    description="Remove analytics data older than the specified number of days",
    description="Remove analytics data older than the specified number of days",
    )
    )
    async def cleanup_data(days: int = Query(365, description="Number of days to keep")):
    async def cleanup_data(days: int = Query(365, description="Number of days to keep")):
    """
    """
    Remove analytics data older than the specified number of days.
    Remove analytics data older than the specified number of days.


    Args:
    Args:
    days: Number of days to keep
    days: Number of days to keep


    Returns:
    Returns:
    Success response
    Success response
    """
    """
    try:
    try:
    count = analytics_service.cleanup_old_data(days)
    count = analytics_service.cleanup_old_data(days)
    return {
    return {
    "success": True,
    "success": True,
    "message": f"Removed {count} records older than {days} days",
    "message": f"Removed {count} records older than {days} days",
    }
    }
except Exception as e:
except Exception as e:
    logger.error(f"Error cleaning up analytics data: {e}")
    logger.error(f"Error cleaning up analytics data: {e}")
    raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))