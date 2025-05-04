"""
"""
Audit router for the API server.
Audit router for the API server.


This module provides route handlers for audit operations.
This module provides route handlers for audit operations.
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


from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status


from ..middleware.auth import get_current_user, require_scopes
from ..middleware.auth import get_current_user, require_scopes
from ..models.user import User
from ..models.user import User
from ..services.audit_service import AuditService
from ..services.audit_service import AuditService


(
(
AuditAction,
AuditAction,
AuditEventList,
AuditEventList,
AuditEventResponse,
AuditEventResponse,
AuditEventType,
AuditEventType,
AuditResourceType,
AuditResourceType,
AuditStatus,
AuditStatus,
)
)
# Configure logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Create audit service
# Create audit service
audit_service = AuditService()
audit_service = AuditService()


# Create router
# Create router
router = APIRouter()
router = APIRouter()




@router.get(
@router.get(
"/",
"/",
response_model=AuditEventList,
response_model=AuditEventList,
dependencies=[Depends(require_scopes(["audit:read"]))],
dependencies=[Depends(require_scopes(["audit:read"]))],
responses={
responses={
200: {"description": "List of audit events"},
200: {"description": "List of audit events"},
401: {"description": "Unauthorized"},
401: {"description": "Unauthorized"},
403: {"description": "Forbidden"},
403: {"description": "Forbidden"},
},
},
)
)
async def list_audit_events(
async def list_audit_events(
event_type: Optional[AuditEventType] = Query(
event_type: Optional[AuditEventType] = Query(
None, description="Filter by event type"
None, description="Filter by event type"
),
),
resource_type: Optional[AuditResourceType] = Query(
resource_type: Optional[AuditResourceType] = Query(
None, description="Filter by resource type"
None, description="Filter by resource type"
),
),
resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
action: Optional[AuditAction] = Query(None, description="Filter by action"),
action: Optional[AuditAction] = Query(None, description="Filter by action"),
actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
status: Optional[AuditStatus] = Query(None, description="Filter by status"),
status: Optional[AuditStatus] = Query(None, description="Filter by status"),
start_time: Optional[datetime] = Query(None, description="Filter by start time"),
start_time: Optional[datetime] = Query(None, description="Filter by start time"),
end_time: Optional[datetime] = Query(None, description="Filter by end time"),
end_time: Optional[datetime] = Query(None, description="Filter by end time"),
page: int = Query(1, ge=1, description="Page number"),
page: int = Query(1, ge=1, description="Page number"),
page_size: int = Query(10, ge=1, le=100, description="Page size"),
page_size: int = Query(10, ge=1, le=100, description="Page size"),
current_user: User = Depends(get_current_user),
current_user: User = Depends(get_current_user),
):
    ):
    """
    """
    List audit events with optional filtering.
    List audit events with optional filtering.


    This endpoint requires the "audit:read" scope.
    This endpoint requires the "audit:read" scope.
    """
    """
    # Calculate offset
    # Calculate offset
    offset = (page - 1) * page_size
    offset = (page - 1) * page_size


    # Get audit events
    # Get audit events
    events = audit_service.get_events(
    events = audit_service.get_events(
    event_type=event_type,
    event_type=event_type,
    resource_type=resource_type,
    resource_type=resource_type,
    resource_id=resource_id,
    resource_id=resource_id,
    action=action,
    action=action,
    actor_id=actor_id,
    actor_id=actor_id,
    status=status,
    status=status,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    limit=page_size,
    limit=page_size,
    offset=offset,
    offset=offset,
    )
    )


    # Get total count (for pagination)
    # Get total count (for pagination)
    total_events = len(
    total_events = len(
    audit_service.get_events(
    audit_service.get_events(
    event_type=event_type,
    event_type=event_type,
    resource_type=resource_type,
    resource_type=resource_type,
    resource_id=resource_id,
    resource_id=resource_id,
    action=action,
    action=action,
    actor_id=actor_id,
    actor_id=actor_id,
    status=status,
    status=status,
    start_time=start_time,
    start_time=start_time,
    end_time=end_time,
    end_time=end_time,
    )
    )
    )
    )


    # Calculate total pages
    # Calculate total pages
    total_pages = (total_events + page_size - 1) // page_size if total_events > 0 else 1
    total_pages = (total_events + page_size - 1) // page_size if total_events > 0 else 1


    # Create response
    # Create response
    return {
    return {
    "items": events,
    "items": events,
    "total": total_events,
    "total": total_events,
    "page": page,
    "page": page,
    "page_size": page_size,
    "page_size": page_size,
    "pages": total_pages,
    "pages": total_pages,
    }
    }




    @router.get(
    @router.get(
    "/{event_id}",
    "/{event_id}",
    response_model=AuditEventResponse,
    response_model=AuditEventResponse,
    dependencies=[Depends(require_scopes(["audit:read"]))],
    dependencies=[Depends(require_scopes(["audit:read"]))],
    responses={
    responses={
    200: {"description": "Audit event details"},
    200: {"description": "Audit event details"},
    401: {"description": "Unauthorized"},
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    403: {"description": "Forbidden"},
    404: {"description": "Audit event not found"},
    404: {"description": "Audit event not found"},
    },
    },
    )
    )
    async def get_audit_event(
    async def get_audit_event(
    event_id: str = Path(..., description="Audit event ID"),
    event_id: str = Path(..., description="Audit event ID"),
    current_user: User = Depends(get_current_user),
    current_user: User = Depends(get_current_user),
    ):
    ):
    """
    """
    Get details of a specific audit event.
    Get details of a specific audit event.


    This endpoint requires the "audit:read" scope.
    This endpoint requires the "audit:read" scope.
    """
    """
    # Get audit event
    # Get audit event
    event = audit_service.get_event_by_id(event_id)
    event = audit_service.get_event_by_id(event_id)


    # Check if event exists
    # Check if event exists
    if not event:
    if not event:
    raise HTTPException(
    raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Audit event not found"
    status_code=status.HTTP_404_NOT_FOUND, detail="Audit event not found"
    )
    )


    return event
    return event