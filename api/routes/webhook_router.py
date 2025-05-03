"""
Webhook router for the API server.

This module provides route handlers for webhook operations.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status

from ..middleware.auth import get_api_key, get_current_user
from ..models.api_key import APIKey
from ..models.user import User
from ..schemas.common import ErrorResponse, SuccessResponse
from ..schemas.webhook import (
    WebhookDeliveryList,
    WebhookDeliveryResponse,
    WebhookDeliveryStatus,
    WebhookEventType,
    WebhookList,
    WebhookRequest,
    WebhookResponse,
    WebhookUpdate,
)
from ..services.webhook_service import WebhookService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create webhook service
webhook_service = WebhookService()


# Define lifespan context manager for FastAPI lifecycle events
@asynccontextmanager
async def lifespan(app):
    # Startup: Start webhook service
    logger.info("Starting webhook service")
    await webhook_service.start()
    yield
    # Shutdown: Stop webhook service
    logger.info("Stopping webhook service")
    await webhook_service.stop()


# Create router with lifespan
router = APIRouter(lifespan=lifespan)


@router.post(
    " / ",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Webhook registered"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
)
async def register_webhook(
    request: Request,
    data: WebhookRequest = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Register a new webhook."""
    try:
        # Get client info for audit
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user - agent")

        webhook = await webhook_service.register_webhook(
            data.dict(), actor_id=current_user.id, ip_address=client_host, user_agent=user_agent
        )
        return webhook
    except Exception as e:
        logger.error(f"Error registering webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    " / ",
    response_model=WebhookList,
    responses={
        200: {"description": "List of webhooks"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def list_webhooks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """List all webhooks."""
    try:
        webhooks = await webhook_service.list_webhooks()
        total = len(webhooks)
        pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "webhooks": webhooks[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses={
        200: {"description": "Webhook details"},
        404: {"model": ErrorResponse, "description": "Webhook not found"},
    },
)
async def get_webhook(webhook_id: str = Path(...), current_user: User = Depends(get_current_user)):
    """Get webhook details."""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if webhook is None:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return webhook
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses={
        200: {"description": "Webhook updated"},
        404: {"model": ErrorResponse, "description": "Webhook not found"},
    },
)
async def update_webhook(
    request: Request,
    webhook_id: str = Path(...),
    data: WebhookUpdate = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Update a webhook."""
    try:
        # Get client info for audit
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user - agent")

        webhook = await webhook_service.update_webhook(
            webhook_id,
            data.dict(exclude_unset=True),
            actor_id=current_user.id,
            ip_address=client_host,
            user_agent=user_agent,
        )
        if webhook is None:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return webhook
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{webhook_id}",
    response_model=SuccessResponse,
    responses={
        200: {"description": "Webhook deleted"},
        404: {"model": ErrorResponse, "description": "Webhook not found"},
    },
)
async def delete_webhook(
    request: Request, webhook_id: str = Path(...), current_user: User = Depends(get_current_user)
):
    """Delete a webhook."""
    try:
        # Get client info for audit
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user - agent")

        if await webhook_service.delete_webhook(
            webhook_id, actor_id=current_user.id, ip_address=client_host, user_agent=user_agent
        ):
            return {"message": "Webhook deleted successfully"}
        raise HTTPException(status_code=404, detail="Webhook not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{webhook_id}/deliveries",
    response_model=WebhookDeliveryList,
    responses={
        200: {"description": "List of webhook deliveries"},
        404: {"model": ErrorResponse, "description": "Webhook not found"},
    },
)
async def list_webhook_deliveries(
    webhook_id: str = Path(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[WebhookDeliveryStatus] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """List deliveries for a webhook."""
    try:
        # Check if webhook exists
        webhook = await webhook_service.get_webhook(webhook_id)
        if webhook is None:
            raise HTTPException(status_code=404, detail="Webhook not found")

        # Get deliveries
        deliveries = await webhook_service.get_deliveries(webhook_id, status=status)
        total = len(deliveries)
        pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "deliveries": deliveries[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing webhook deliveries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    " / test",
    response_model=SuccessResponse,
    responses={
        200: {"description": "Test webhook sent"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
)
async def test_webhook(
    request: Request,
    url: str = Body(..., embed=True),
    event_type: WebhookEventType = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Send a test webhook to the specified URL."""
    try:
        # Create a temporary webhook
        webhook = {
            "id": "test - webhook",
            "url": url,
            "events": [event_type],
            "description": "Test webhook",
            "headers": {},
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_called_at": None,
            "secret": f"whsec_{uuid.uuid4().hex}",
        }

        # Create a test delivery
        delivery = {
            "id": f"test - delivery-{uuid.uuid4()}",
            "webhook_id": webhook["id"],
            "event_type": event_type,
            "event_data": {
                "test": True,
                "message": "This is a test webhook event",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "status": "pending",
            "attempts": 0,
            "max_attempts": 1,
            "created_at": datetime.utcnow().isoformat(),
            "next_attempt_at": datetime.utcnow().isoformat(),
        }

        # Deliver the webhook
        success = await webhook_service._deliver_webhook(webhook, delivery)

        if success:
            return {
                "message": "Test webhook sent successfully",
                "data": {
                    "delivery_id": delivery["id"],
                    "response_code": delivery.get("response_code"),
                    "response_body": delivery.get("response_body"),
                },
            }
        else:
            return {
                "message": "Test webhook failed",
                "data": {
                    "delivery_id": delivery["id"],
                    "error": delivery.get("error"),
                    "response_code": delivery.get("response_code"),
                    "response_body": delivery.get("response_body"),
                },
            }
    except Exception as e:
        logger.error(f"Error sending test webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
