"""
API routes for analytics.

This module provides API routes for accessing analytics data.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response
    from fastapi.responses import JSONResponse, StreamingResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI is required for analytics routes")
    FASTAPI_AVAILABLE = False

# Import analytics service
from api.analytics import analytics_service

# Import schemas
from ..schemas.analytics import (
    RequestStatsResponse,
    EndpointStatsResponse,
    UserStatsResponse,
    ApiKeyStatsResponse,
    AnalyticsSummaryResponse
)
from ..schemas.common import ErrorResponse, SuccessResponse

# Create router
if FASTAPI_AVAILABLE:
    router = APIRouter()
else:
    router = None


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get API usage summary",
    description="Get a summary of API usage statistics"
)
async def get_summary(days: int = Query(30, description="Number of days to include")):
    """
    Get a summary of API usage statistics.
    
    Args:
        days: Number of days to include
        
    Returns:
        API usage summary
    """
    try:
        summary = analytics_service.get_usage_summary(days)
        return summary
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/requests",
    response_model=List[RequestStatsResponse],
    summary="Get API request statistics",
    description="Get detailed statistics for API requests"
)
async def get_requests(
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    version: Optional[str] = Query(None, description="Filter by API version"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    days: int = Query(7, description="Number of days to include"),
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Number of records to skip")
):
    """
    Get detailed statistics for API requests.
    
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
        List of request statistics
    """
    try:
        requests = analytics_service.get_requests(
            endpoint=endpoint,
            version=version,
            user_id=user_id,
            api_key_id=api_key_id,
            status_code=status_code,
            days=days,
            limit=limit,
            offset=offset
        )
        return requests
    except Exception as e:
        logger.error(f"Error getting request statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/endpoints",
    response_model=List[EndpointStatsResponse],
    summary="Get endpoint statistics",
    description="Get statistics for each API endpoint"
)
async def get_endpoint_stats(days: int = Query(30, description="Number of days to include")):
    """
    Get statistics for each API endpoint.
    
    Args:
        days: Number of days to include
        
    Returns:
        List of endpoint statistics
    """
    try:
        stats = analytics_service.get_endpoint_stats(days)
        return stats
    except Exception as e:
        logger.error(f"Error getting endpoint statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/users",
    response_model=List[UserStatsResponse],
    summary="Get user statistics",
    description="Get statistics for API usage by users"
)
async def get_user_stats(
    days: int = Query(30, description="Number of days to include"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get statistics for API usage by users.
    
    Args:
        days: Number of days to include
        user_id: Filter by user ID
        
    Returns:
        List of user statistics
    """
    try:
        stats = analytics_service.get_user_metrics(days=days, user_id=user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/api-keys",
    response_model=List[ApiKeyStatsResponse],
    summary="Get API key statistics",
    description="Get statistics for API usage by API keys"
)
async def get_api_key_stats(
    days: int = Query(30, description="Number of days to include"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID")
):
    """
    Get statistics for API usage by API keys.
    
    Args:
        days: Number of days to include
        api_key_id: Filter by API key ID
        
    Returns:
        List of API key statistics
    """
    try:
        stats = analytics_service.get_api_key_metrics(days=days, api_key_id=api_key_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting API key statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/export/requests",
    summary="Export API requests to CSV",
    description="Export detailed API request data to CSV format"
)
async def export_requests_csv(
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    version: Optional[str] = Query(None, description="Filter by API version"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    api_key_id: Optional[str] = Query(None, description="Filter by API key ID"),
    days: int = Query(30, description="Number of days to include")
):
    """
    Export detailed API request data to CSV format.
    
    Args:
        endpoint: Filter by endpoint
        version: Filter by API version
        user_id: Filter by user ID
        api_key_id: Filter by API key ID
        days: Number of days to include
        
    Returns:
        CSV file
    """
    try:
        csv_data = analytics_service.export_requests_csv(
            days=days,
            endpoint=endpoint,
            version=version,
            user_id=user_id,
            api_key_id=api_key_id
        )
        
        # Generate filename
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"api_requests_{date_str}.csv"
        
        # Return CSV file
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting requests to CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/export/metrics",
    summary="Export daily metrics to CSV",
    description="Export daily aggregated metrics to CSV format"
)
async def export_metrics_csv(days: int = Query(30, description="Number of days to include")):
    """
    Export daily aggregated metrics to CSV format.
    
    Args:
        days: Number of days to include
        
    Returns:
        CSV file
    """
    try:
        csv_data = analytics_service.export_metrics_csv(days=days)
        
        # Generate filename
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"api_metrics_{date_str}.csv"
        
        # Return CSV file
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting metrics to CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/cleanup",
    response_model=SuccessResponse,
    summary="Clean up old analytics data",
    description="Remove analytics data older than the specified number of days"
)
async def cleanup_data(days: int = Query(365, description="Number of days to keep")):
    """
    Remove analytics data older than the specified number of days.
    
    Args:
        days: Number of days to keep
        
    Returns:
        Success response
    """
    try:
        count = analytics_service.cleanup_old_data(days)
        return {
            "success": True,
            "message": f"Removed {count} records older than {days} days"
        }
    except Exception as e:
        logger.error(f"Error cleaning up analytics data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
