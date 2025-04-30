"""
Webhook router for the API server.

This module provides route handlers for webhook operations.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, status

from ..middleware.auth import get_current_user
from ..schemas.webhook import (
    WebhookRequest,
    WebhookUpdate,
    WebhookResponse,
    WebhookList,
    WebhookDeliveryResponse,
    WebhookDeliveryList,
    WebhookEventType,
    WebhookDeliveryStatus
)
from ..schemas.common import ErrorResponse, SuccessResponse
from ..services.webhook_service import WebhookService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create webhook service (will be started when FastAPI app starts)
webhook_service = WebhookService()

@router.on_event("startup")
async def startup_event():
    """Start webhook service when FastAPI app starts."""
    await webhook_service.start()

@router.on_event("shutdown")
async def shutdown_event():
    """Stop webhook service when FastAPI app shuts down."""
    await webhook_service.stop()

@router.post(
    "/",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Webhook registered"},
        400: {"model": ErrorResponse, "description": "Bad request"}
    }
)
async def register_webhook(data: WebhookRequest = Body(...)):
    """Register a new webhook."""
    try:
        webhook = await webhook_service.register_webhook(data.dict())
        return webhook
    except Exception as e:
        logger.error(f"Error registering webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/",
    response_model=WebhookList,
    responses={
        200: {"description": "List of webhooks"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def list_webhooks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
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
            "pages": pages
        }
    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
    responses={
        200: {"description": "Webhook details"},
        404: {"model": ErrorResponse, "description": "Webhook not found"}
    }
)
async def get_webhook(webhook_id: str = Path(...)):
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
        404: {"model": ErrorResponse, "description": "Webhook not found"}
    }
)
async def update_webhook(
    webhook_id: str = Path(...),
    data: WebhookUpdate = Body(...)
):
    """Update a webhook."""
    try:
        webhook = await webhook_service.update_webhook(webhook_id, data.dict())
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
        404: {"model": ErrorResponse, "description": "Webhook not found"}
    }
)
async def delete_webhook(webhook_id: str = Path(...)):
    """Delete a webhook."""
    try:
        if await webhook_service.delete_webhook(webhook_id):
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
        404: {"model": ErrorResponse, "description": "Webhook not found"}
    }
)
async def list_webhook_deliveries(
    webhook_id: str = Path(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[WebhookDeliveryStatus] = Query(None)
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
            "pages": pages
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing webhook deliveries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))