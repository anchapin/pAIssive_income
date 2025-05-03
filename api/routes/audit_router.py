"""
Audit router for the API server.

This module provides route handlers for audit operations.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from ..middleware.auth import get_api_key, get_current_user, require_scopes
from ..models.api_key import APIKey
from ..models.user import User
from ..schemas.audit import (
    AuditAction,
    AuditActorType,
    AuditEventList,
    AuditEventResponse,
    AuditEventType,
    AuditResourceType,
    AuditStatus,
)
from ..services.audit_service import AuditService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create audit service
audit_service = AuditService()

# Create router
router = APIRouter()


@router.get(
    " / ",
    response_model=AuditEventList,
    dependencies=[Depends(require_scopes(["audit:read"]))],
    responses={
        200: {"description": "List of audit events"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def list_audit_events(
    event_type: Optional[AuditEventType] = Query(None, 
        description="Filter by event type"),
    resource_type: Optional[AuditResourceType] = Query(None, 
        description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    action: Optional[AuditAction] = Query(None, description="Filter by action"),
    actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
    status: Optional[AuditStatus] = Query(None, description="Filter by status"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
):
    """
    List audit events with optional filtering.

    This endpoint requires the "audit:read" scope.
    """
    # Calculate offset
    offset = (page - 1) * page_size

    # Get audit events
    events = audit_service.get_events(
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        actor_id=actor_id,
        status=status,
        start_time=start_time,
        end_time=end_time,
        limit=page_size,
        offset=offset,
    )

    # Get total count (for pagination)
    total_events = len(
        audit_service.get_events(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            actor_id=actor_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
        )
    )

    # Calculate total pages
    total_pages = (total_events + page_size - 1) // page_size if total_events > 0 else 1

    # Create response
    return {
        "items": events,
        "total": total_events,
        "page": page,
        "page_size": page_size,
        "pages": total_pages,
    }


@router.get(
    "/{event_id}",
    response_model=AuditEventResponse,
    dependencies=[Depends(require_scopes(["audit:read"]))],
    responses={
        200: {"description": "Audit event details"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Audit event not found"},
    },
)
async def get_audit_event(
    event_id: str = Path(..., description="Audit event ID"),
    current_user: User = Depends(get_current_user),
):
    """
    Get details of a specific audit event.

    This endpoint requires the "audit:read" scope.
    """
    # Get audit event
    event = audit_service.get_event_by_id(event_id)

    # Check if event exists
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail="Audit event not found")

    return event
