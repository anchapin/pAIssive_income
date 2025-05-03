"""
Tests for the webhook service.

This module provides comprehensive tests for the WebhookService class.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any

import pytest

from api.schemas.webhook import WebhookEventType
from api.services.webhook_service import WebhookService


class TestWebhookService:
    """Test suite for the WebhookService class."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_initialization(self, webhook_service):
        """Test that the webhook service initializes correctly."""
        assert webhook_service is not None
        assert webhook_service.webhooks == {}
        assert webhook_service.deliveries == {}
        assert webhook_service.running is False
        assert webhook_service.delivery_queue is not None
        assert webhook_service.worker_task is None
        assert webhook_service.audit_service is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_start_stop(self, webhook_service):
        """Test starting and stopping the webhook service."""
        # Start the service
        await webhook_service.start()
        assert webhook_service.running is True
        assert webhook_service.worker_task is not None
        
        # Stop the service
        await webhook_service.stop()
        assert webhook_service.running is False
        assert webhook_service.worker_task.done() is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_register_webhook(self, webhook_service, mock_audit_service):
        """Test registering a webhook."""
        # Start the service
        await webhook_service.start()
        
        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": [
                    WebhookEventType.USER_CREATED,
                    WebhookEventType.PAYMENT_RECEIVED,
                ],
                "description": "Test webhook",
                "is_active": True,
            }
            
            webhook = await webhook_service.register_webhook(webhook_data)
            
            # Check that the webhook was registered correctly
            assert webhook["id"] is not None
            assert webhook["url"] == "https://example.com/webhook"
            assert webhook["events"] == [
                WebhookEventType.USER_CREATED,
                WebhookEventType.PAYMENT_RECEIVED,
            ]
            assert webhook["description"] == "Test webhook"
            assert webhook["is_active"] is True
            assert webhook["created_at"] is not None
            assert webhook["last_called_at"] is None
            assert webhook["secret"] is not None
            assert webhook["secret"].startswith("whsec_")
            
            # Check that the webhook was stored in the service
            assert len(webhook_service.webhooks) == 1
            assert webhook_service.webhooks[webhook["id"]] == webhook
        
        finally:
            # Stop the service
            await webhook_service.stop()

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_list_webhooks(self, running_webhook_service):
        """Test listing webhooks."""
        # Register webhooks
        webhook_data1 = {
            "url": "https://example.com/webhook1",
            "events": [WebhookEventType.USER_CREATED],
            "description": "Test webhook 1",
            "is_active": True,
        }
        
        webhook_data2 = {
            "url": "https://example.com/webhook2",
            "events": [WebhookEventType.PAYMENT_RECEIVED],
            "description": "Test webhook 2",
            "is_active": False,
        }
        
        await running_webhook_service.register_webhook(webhook_data1)
        await running_webhook_service.register_webhook(webhook_data2)
        
        # List webhooks
        webhooks = await running_webhook_service.list_webhooks()
        
        # Check that both webhooks are returned
        assert len(webhooks) == 2
        assert any(w["url"] == "https://example.com/webhook1" for w in webhooks)
        assert any(w["url"] == "https://example.com/webhook2" for w in webhooks)

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_get_webhook(self, running_webhook_service):
        """Test getting a webhook by ID."""
        # Register a webhook
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": [WebhookEventType.USER_CREATED],
            "description": "Test webhook",
            "is_active": True,
        }
        
        webhook = await running_webhook_service.register_webhook(webhook_data)
        
        # Get the webhook
        retrieved_webhook = await running_webhook_service.get_webhook(webhook["id"])
        
        # Check that the webhook is returned correctly
        assert retrieved_webhook == webhook
        
        # Get a non-existent webhook
        non_existent = await running_webhook_service.get_webhook("non-existent")
        
        # Check that None is returned
        assert non_existent is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_update_webhook(self, registered_webhook, running_webhook_service):
        """Test updating a webhook."""
        # Update the webhook
        updated_data = {
            "description": "Updated test webhook",
            "is_active": False,
        }
        
        updated_webhook = await running_webhook_service.update_webhook(
            registered_webhook["id"], updated_data
        )
        
        # Check that the webhook was updated correctly
        assert updated_webhook["id"] == registered_webhook["id"]
        assert updated_webhook["url"] == registered_webhook["url"]
        assert updated_webhook["events"] == registered_webhook["events"]
        assert updated_webhook["description"] == "Updated test webhook"
        assert updated_webhook["is_active"] is False
        
        # Check that the webhook was updated in the service
        stored_webhook = await running_webhook_service.get_webhook(registered_webhook["id"])
        assert stored_webhook["description"] == "Updated test webhook"
        assert stored_webhook["is_active"] is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_delete_webhook(self, registered_webhook, running_webhook_service):
        """Test deleting a webhook."""
        # Delete the webhook
        deleted = await running_webhook_service.delete_webhook(registered_webhook["id"])
        
        # Check that the webhook was deleted
        assert deleted is True
        
        # Check that the webhook is no longer in the service
        webhooks = await running_webhook_service.list_webhooks()
        assert len(webhooks) == 0
        
        # Try to delete a non-existent webhook
        deleted = await running_webhook_service.delete_webhook("non-existent")
        
        # Check that deletion failed
        assert deleted is False

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.webhook
    async def test_deliver_event(self, registered_webhook, running_webhook_service, mock_http_client):
        """Test delivering an event to a webhook."""
        # Create event data
        event_data = {
            "user_id": "user-123",
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Deliver the event
        delivery = await running_webhook_service.deliver_event(
            webhook_id=registered_webhook["id"],
            event_type=WebhookEventType.USER_CREATED,
            event_data=event_data,
        )
        
        # Check that the delivery was created
        assert delivery["id"] is not None
        assert delivery["webhook_id"] == registered_webhook["id"]
        assert delivery["event_type"] == WebhookEventType.USER_CREATED
        assert delivery["event_data"] == event_data
        
        # Check that the delivery is stored in the service
        deliveries = await running_webhook_service.get_deliveries(registered_webhook["id"])
        assert len(deliveries) == 1
        assert deliveries[0]["id"] == delivery["id"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.webhook
    async def test_trigger_event(self, registered_webhook, running_webhook_service):
        """Test triggering an event to multiple webhooks."""
        # Register another webhook subscribed to a different event
        webhook_data2 = {
            "url": "https://example.com/webhook2",
            "events": [WebhookEventType.PAYMENT_RECEIVED],
            "description": "Test webhook 2",
            "is_active": True,
        }
        
        await running_webhook_service.register_webhook(webhook_data2)
        
        # Create event data
        event_data = {
            "user_id": "user-123",
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Trigger the USER_CREATED event (only the first webhook should receive it)
        delivery_ids = await running_webhook_service.trigger_event(
            event_type=WebhookEventType.USER_CREATED,
            event_data=event_data,
        )
        
        # Check that one delivery was created
        assert len(delivery_ids) == 1
        
        # Wait a moment for the worker to process the queue
        await asyncio.sleep(0.1)
        
        # Check deliveries
        deliveries = await running_webhook_service.get_deliveries()
        assert len(deliveries) == 1
        
        # Trigger the PAYMENT_RECEIVED event (only the second webhook should receive it)
        payment_data = {
            "payment_id": "payment-123",
            "amount": 100.0,
            "currency": "USD",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        delivery_ids = await running_webhook_service.trigger_event(
            event_type=WebhookEventType.PAYMENT_RECEIVED,
            event_data=payment_data,
        )
        
        # Check that one delivery was created
        assert len(delivery_ids) == 1
        
        # Wait a moment for the worker to process the queue
        await asyncio.sleep(0.1)
        
        # Check deliveries (should be 2 now)
        deliveries = await running_webhook_service.get_deliveries()
        assert len(deliveries) == 2