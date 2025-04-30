"""
Webhook router for the API server.

This module provides endpoints for webhook registration and management.
"""

import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
    from fastapi.security.api_key import APIKeyHeader
    from ..schemas.webhook import (
        WebhookCreate,
        WebhookUpdate,
        WebhookResponse,
        WebhookList,
        WebhookEventType,
        WebhookDeliveryStatus,
        WebhookDeliveryResponse,
        WebhookDeliveryList,
    )
    from ..services.webhook_service import WebhookService

    # Create router
    webhook_router = APIRouter()
    webhook_service = WebhookService()

    # API Key auth
    api_key_header = APIKeyHeader(name="X-API-Key")

    # Helper function to get the webhook service
    async def get_webhook_service() -> WebhookService:
        return webhook_service

    # Define endpoints
    @webhook_router.post(
        "/",
        response_model=WebhookResponse,
        summary="Register a webhook",
        description="Register a new webhook for event notifications.",
    )
    async def create_webhook(
        webhook_data: WebhookCreate,
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        Register a webhook for event notifications.

        Args:
            webhook_data: Webhook data
            webhook_service: Webhook service

        Returns:
            Created webhook
        """
        try:
            webhook = await webhook_service.register_webhook(
                url=webhook_data.url,
                events=webhook_data.events,
                description=webhook_data.description,
                active=webhook_data.active,
                secret=webhook_data.secret,
            )

            return webhook
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error creating webhook: {str(e)}"
            )

    @webhook_router.get(
        "/",
        response_model=WebhookList,
        summary="List webhooks",
        description="Get a list of registered webhooks.",
    )
    async def list_webhooks(
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        List webhooks.

        Args:
            webhook_service: Webhook service

        Returns:
            List of webhooks
        """
        try:
            webhooks = await webhook_service.get_webhooks()
            return {"webhooks": webhooks}
        except Exception as e:
            logger.error(f"Error listing webhooks: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error listing webhooks: {str(e)}"
            )

    @webhook_router.get(
        "/{webhook_id}",
        response_model=WebhookResponse,
        summary="Get webhook details",
        description="Get details for a specific webhook.",
    )
    async def get_webhook(
        webhook_id: str = Path(..., description="Webhook ID"),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        Get webhook details.

        Args:
            webhook_id: Webhook ID
            webhook_service: Webhook service

        Returns:
            Webhook details
        """
        try:
            webhook = await webhook_service.get_webhook(webhook_id)

            if not webhook:
                raise HTTPException(
                    status_code=404, detail=f"Webhook {webhook_id} not found"
                )

            return webhook
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting webhook {webhook_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error getting webhook: {str(e)}"
            )

    @webhook_router.patch(
        "/{webhook_id}",
        response_model=WebhookResponse,
        summary="Update webhook",
        description="Update an existing webhook.",
    )
    async def update_webhook(
        webhook_data: WebhookUpdate,
        webhook_id: str = Path(..., description="Webhook ID"),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        Update webhook.

        Args:
            webhook_data: Updated webhook data
            webhook_id: Webhook ID
            webhook_service: Webhook service

        Returns:
            Updated webhook
        """
        try:
            webhook = await webhook_service.update_webhook(
                webhook_id=webhook_id,
                url=webhook_data.url,
                description=webhook_data.description,
                events=webhook_data.events,
                active=webhook_data.active,
                secret=webhook_data.secret,
            )

            return webhook
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating webhook {webhook_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error updating webhook: {str(e)}"
            )

    @webhook_router.delete(
        "/{webhook_id}", summary="Delete webhook", description="Delete a webhook."
    )
    async def delete_webhook(
        webhook_id: str = Path(..., description="Webhook ID"),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        Delete webhook.

        Args:
            webhook_id: Webhook ID
            webhook_service: Webhook service

        Returns:
            Success message
        """
        try:
            deleted = await webhook_service.delete_webhook(webhook_id)

            if not deleted:
                raise HTTPException(
                    status_code=404, detail=f"Webhook {webhook_id} not found"
                )

            return {"message": f"Webhook {webhook_id} deleted"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting webhook {webhook_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error deleting webhook: {str(e)}"
            )

    @webhook_router.get(
        "/{webhook_id}/deliveries",
        response_model=WebhookDeliveryList,
        summary="List webhook deliveries",
        description="Get delivery history for a webhook.",
    )
    async def list_webhook_deliveries(
        webhook_id: str = Path(..., description="Webhook ID"),
        page: int = Query(1, description="Page number"),
        page_size: int = Query(20, description="Items per page"),
        status: Optional[WebhookDeliveryStatus] = Query(
            None, description="Filter by status"
        ),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        List webhook deliveries.

        Args:
            webhook_id: Webhook ID
            page: Page number
            page_size: Items per page
            status: Optional status filter
            webhook_service: Webhook service

        Returns:
            List of webhook deliveries
        """
        try:
            # Verify webhook exists
            webhook = await webhook_service.get_webhook(webhook_id)

            if not webhook:
                raise HTTPException(
                    status_code=404, detail=f"Webhook {webhook_id} not found"
                )

            result = await webhook_service.get_deliveries(
                webhook_id=webhook_id, page=page, page_size=page_size, status=status
            )

            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing deliveries for webhook {webhook_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error listing deliveries: {str(e)}"
            )

    @webhook_router.get(
        "/deliveries",
        response_model=WebhookDeliveryList,
        summary="List all webhook deliveries",
        description="Get delivery history for all webhooks.",
    )
    async def list_all_deliveries(
        page: int = Query(1, description="Page number"),
        page_size: int = Query(20, description="Items per page"),
        status: Optional[WebhookDeliveryStatus] = Query(
            None, description="Filter by status"
        ),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        List all webhook deliveries.

        Args:
            page: Page number
            page_size: Items per page
            status: Optional status filter
            webhook_service: Webhook service

        Returns:
            List of webhook deliveries
        """
        try:
            result = await webhook_service.get_deliveries(
                page=page, page_size=page_size, status=status
            )

            return result
        except Exception as e:
            logger.error(f"Error listing all deliveries: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error listing deliveries: {str(e)}"
            )

    @webhook_router.get(
        "/deliveries/{delivery_id}",
        response_model=WebhookDeliveryResponse,
        summary="Get delivery details",
        description="Get details for a specific webhook delivery.",
    )
    async def get_delivery(
        delivery_id: str = Path(..., description="Delivery ID"),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        Get delivery details.

        Args:
            delivery_id: Delivery ID
            webhook_service: Webhook service

        Returns:
            Delivery details
        """
        try:
            delivery = await webhook_service.get_delivery(delivery_id)

            if not delivery:
                raise HTTPException(
                    status_code=404, detail=f"Delivery {delivery_id} not found"
                )

            return delivery
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting delivery {delivery_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error getting delivery: {str(e)}"
            )

    @webhook_router.post(
        "/deliveries/{delivery_id}/retry",
        response_model=WebhookDeliveryResponse,
        summary="Retry delivery",
        description="Retry a failed webhook delivery.",
    )
    async def retry_delivery(
        delivery_id: str = Path(..., description="Delivery ID"),
        webhook_service: WebhookService = Depends(get_webhook_service),
    ) -> Dict[str, Any]:
        """
        Retry webhook delivery.

        Args:
            delivery_id: Delivery ID
            webhook_service: Webhook service

        Returns:
            Updated delivery
        """
        try:
            delivery = await webhook_service.retry_delivery(delivery_id)
            return delivery
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error retrying delivery {delivery_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error retrying delivery: {str(e)}"
            )

    @webhook_router.get(
        "/events",
        summary="List available event types",
        description="Get a list of all available webhook event types.",
    )
    async def list_event_types() -> Dict[str, Any]:
        """
        List available event types.

        Returns:
            List of event types
        """
        events = [{"name": e.name, "value": e.value} for e in WebhookEventType]
        return {"events": events}

except ImportError:
    # FastAPI not available
    webhook_router = None
    logger.warning("FastAPI is required for webhook router")
