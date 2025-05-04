"""
"""
Logging router for the API server.
Logging router for the API server.


This module provides route handlers for log operations.
This module provides route handlers for log operations.
"""
"""


import logging
import logging
import time
import time
from datetime import datetime
from datetime import datetime
from typing import Optional
from typing import Optional


from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import APIRouter, Depends, HTTPException, Query


from ..middleware.auth import get_current_user, require_scopes
from ..middleware.auth import get_current_user, require_scopes
from ..models.user import User
from ..models.user import User
from ..services.logging_service import LoggingService
from ..services.logging_service import LoggingService


# Configure logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Create logging service
# Create logging service
logging_service = LoggingService()
logging_service = LoggingService()


# Create router
# Create router
router = APIRouter()
router = APIRouter()




@router.get(
@router.get(
"/api",
"/api",
dependencies=[Depends(require_scopes(["logs:read"]))],
dependencies=[Depends(require_scopes(["logs:read"]))],
responses={
responses={
200: {"description": "API logs"},
200: {"description": "API logs"},
401: {"description": "Unauthorized"},
401: {"description": "Unauthorized"},
403: {"description": "Forbidden"},
403: {"description": "Forbidden"},
},
},
)
)
async def get_api_logs(
async def get_api_logs(
level: Optional[str] = Query(None, description="Filter by log level"),
level: Optional[str] = Query(None, description="Filter by log level"),
start_time: Optional[datetime] = Query(None, description="Filter by start time"),
start_time: Optional[datetime] = Query(None, description="Filter by start time"),
end_time: Optional[datetime] = Query(None, description="Filter by end time"),
end_time: Optional[datetime] = Query(None, description="Filter by end time"),
user_id: Optional[str] = Query(None, description="Filter by user ID"),
user_id: Optional[str] = Query(None, description="Filter by user ID"),
path: Optional[str] = Query(None, description="Filter by path"),
path: Optional[str] = Query(None, description="Filter by path"),
method: Optional[str] = Query(None, description="Filter by HTTP method"),
method: Optional[str] = Query(None, description="Filter by HTTP method"),
status_code: Optional[int] = Query(None, description="Filter by status code"),
status_code: Optional[int] = Query(None, description="Filter by status code"),
limit: int = Query(
limit: int = Query(
100, ge=1, le=1000, description="Maximum number of logs to return"
100, ge=1, le=1000, description="Maximum number of logs to return"
),
),
offset: int = Query(0, ge=0, description="Number of logs to skip"),
offset: int = Query(0, ge=0, description="Number of logs to skip"),
current_user: User = Depends(get_current_user),
current_user: User = Depends(get_current_user),
):
    ):
    """
    """
    Get API logs.
    Get API logs.


    This endpoint requires the "logs:read" scope.
    This endpoint requires the "logs:read" scope.
    """
    """
    # Create filters
    # Create filters
    filters = {}
    filters = {}
    if user_id:
    if user_id:
    filters["user_id"] = user_id
    filters["user_id"] = user_id
    if path:
    if path:
    filters["path"] = path
    filters["path"] = path
    if method:
    if method:
    filters["method"] = method
    filters["method"] = method
    if status_code:
    if status_code:
    filters["status_code"] = status_code
    filters["status_code"] = status_code


    # Get logs
    # Get logs
    logs = logging_service.get_logs(
    logs = logging_service.get_logs(
    log_type="api",
    log_type="api",
    level=level,
    level=level,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    limit=limit,
    limit=limit,
    offset=offset,
    offset=offset,
    filters=filters,
    filters=filters,
    )
    )


    return {"logs": logs, "total": len(logs), "limit": limit, "offset": offset}
    return {"logs": logs, "total": len(logs), "limit": limit, "offset": offset}




    @router.get(
    @router.get(
    "/security",
    "/security",
    dependencies=[Depends(require_scopes(["logs:read:security"]))],
    dependencies=[Depends(require_scopes(["logs:read:security"]))],
    responses={
    responses={
    200: {"description": "Security logs"},
    200: {"description": "Security logs"},
    401: {"description": "Unauthorized"},
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    403: {"description": "Forbidden"},
    },
    },
    )
    )
    async def get_security_logs(
    async def get_security_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    security_level: Optional[str] = Query(None, description="Filter by security level"),
    security_level: Optional[str] = Query(None, description="Filter by security level"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    action: Optional[str] = Query(None, description="Filter by action"),
    status: Optional[str] = Query(None, description="Filter by status"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(
    limit: int = Query(
    100, ge=1, le=1000, description="Maximum number of logs to return"
    100, ge=1, le=1000, description="Maximum number of logs to return"
    ),
    ),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    current_user: User = Depends(get_current_user),
    current_user: User = Depends(get_current_user),
    ):
    ):
    """
    """
    Get security logs.
    Get security logs.


    This endpoint requires the "logs:read:security" scope.
    This endpoint requires the "logs:read:security" scope.
    """
    """
    # Check if user is admin
    # Check if user is admin
    if not current_user.is_admin:
    if not current_user.is_admin:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Only administrators can access security logs",
    detail="Only administrators can access security logs",
    )
    )


    # Create filters
    # Create filters
    filters = {}
    filters = {}
    if security_level:
    if security_level:
    filters["security_level"] = security_level
    filters["security_level"] = security_level
    if event_type:
    if event_type:
    filters["event_type"] = event_type
    filters["event_type"] = event_type
    if user_id:
    if user_id:
    filters["user_id"] = user_id
    filters["user_id"] = user_id
    if resource_type:
    if resource_type:
    filters["resource_type"] = resource_type
    filters["resource_type"] = resource_type
    if action:
    if action:
    filters["action"] = action
    filters["action"] = action
    if status:
    if status:
    filters["status"] = status
    filters["status"] = status


    # Get logs
    # Get logs
    logs = logging_service.get_logs(
    logs = logging_service.get_logs(
    log_type="security",
    log_type="security",
    level=level,
    level=level,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    limit=limit,
    limit=limit,
    offset=offset,
    offset=offset,
    filters=filters,
    filters=filters,
    )
    )


    return {"logs": logs, "total": len(logs), "limit": limit, "offset": offset}
    return {"logs": logs, "total": len(logs), "limit": limit, "offset": offset}




    @router.get(
    @router.get(
    "/webhook",
    "/webhook",
    dependencies=[Depends(require_scopes(["logs:read"]))],
    dependencies=[Depends(require_scopes(["logs:read"]))],
    responses={
    responses={
    200: {"description": "Webhook logs"},
    200: {"description": "Webhook logs"},
    401: {"description": "Unauthorized"},
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    403: {"description": "Forbidden"},
    },
    },
    )
    )
    async def get_webhook_logs(
    async def get_webhook_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    webhook_id: Optional[str] = Query(None, description="Filter by webhook ID"),
    webhook_id: Optional[str] = Query(None, description="Filter by webhook ID"),
    delivery_id: Optional[str] = Query(None, description="Filter by delivery ID"),
    delivery_id: Optional[str] = Query(None, description="Filter by delivery ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    success: Optional[bool] = Query(None, description="Filter by success"),
    success: Optional[bool] = Query(None, description="Filter by success"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    limit: int = Query(
    limit: int = Query(
    100, ge=1, le=1000, description="Maximum number of logs to return"
    100, ge=1, le=1000, description="Maximum number of logs to return"
    ),
    ),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    current_user: User = Depends(get_current_user),
    current_user: User = Depends(get_current_user),
    ):
    ):
    """
    """
    Get webhook logs.
    Get webhook logs.


    This endpoint requires the "logs:read" scope.
    This endpoint requires the "logs:read" scope.
    """
    """
    # Create filters
    # Create filters
    filters = {}
    filters = {}
    if webhook_id:
    if webhook_id:
    filters["webhook_id"] = webhook_id
    filters["webhook_id"] = webhook_id
    if delivery_id:
    if delivery_id:
    filters["delivery_id"] = delivery_id
    filters["delivery_id"] = delivery_id
    if event_type:
    if event_type:
    filters["event_type"] = event_type
    filters["event_type"] = event_type
    if success is not None:
    if success is not None:
    filters["success"] = success
    filters["success"] = success


    # Get logs
    # Get logs
    logs = logging_service.get_logs(
    logs = logging_service.get_logs(
    log_type="webhook",
    log_type="webhook",
    level=level,
    level=level,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    limit=limit,
    limit=limit,
    offset=offset,
    offset=offset,
    filters=filters,
    filters=filters,
    )
    )


    return {"logs": logs, "total": len(logs), "limit": limit, "offset": offset}
    return {"logs": logs, "total": len(logs), "limit": limit, "offset": offset}