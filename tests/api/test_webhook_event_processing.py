"""
Event processing tests for webhook system.

This module tests the event processing capabilities of the webhook system:
1. Event filtering by subscription type
2. Event payload validation
3. Event correlation across multiple webhooks
4. Event batching and debouncing
5. Event transformation middleware
6. Custom header propagation
"""

import asyncio
import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService

class TestEventFiltering:
    """Tests for event filtering by subscription type."""

    @pytest.mark.asyncio
    async def test_event_filtering(self):
        """Test that events are filtered based on webhook subscriptions."""
        # Create a webhook service
        service = WebhookService()
        await service.start()

        try:
            # Register webhooks with different event subscriptions

            # Webhook 1: USER events only
            webhook1_data = {
                "url": "https://example.com / webhook1",
                "events":[
    WebhookEventType.USER_CREATED,
    WebhookEventType.USER_UPDATED
]],
                "description": "User events webhook",
                "is_active": True,
            }
            webhook1 = await service.register_webhook(webhook1_data)

            # Webhook 2: PAYMENT events only
            webhook2_data = {
                "url": "https://example.com / webhook2",
                "events": [WebhookEventType.PAYMENT_RECEIVED],
                "description": "Payment events webhook",
                "is_active": True,
            }
            webhook2 = await service.register_webhook(webhook2_data)

            # Webhook 3: All events
            webhook3_data = {
                "url": "https://example.com / webhook3",
                "events": [
                    WebhookEventType.USER_CREATED,
                    WebhookEventType.USER_UPDATED,
                    WebhookEventType.PAYMENT_RECEIVED,
                    WebhookEventType.SUBSCRIPTION_CREATED,
                ],
                "description": "All events webhook",
                "is_active": True,
            }
            webhook3 = await service.register_webhook(webhook3_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Track which webhooks receive which events
            received_events = {webhook1["id"]: [], webhook2["id"]: [], 
                webhook3["id"]: []}

            async def mock_post(*args, **kwargs):
                # Extract the URL and payload from kwargs
                url = args[0]
                payload = json.loads(kwargs.get("data", "{}"))

                # Determine which webhook received the event
                if "webhook1" in url:
                    received_events[webhook1["id"]].append(payload["type"])
                elif "webhook2" in url:
                    received_events[webhook2["id"]].append(payload["type"])
                elif "webhook3" in url:
                    received_events[webhook3["id"]].append(payload["type"])

                return success_response

            # Patch the httpx.AsyncClient.post method to track events
            with patch("httpx.AsyncClient.post", mock_post):
                # Trigger events of different types

                # USER_CREATED event
                user_data = {
                    "user_id": "user - 123",
                    "username": "testuser",
                    "email": "test @ example.com",
                }

                await service.trigger_event(
                    event_type=WebhookEventType.USER_CREATED, event_data=user_data
                )

                # PAYMENT_RECEIVED event
                payment_data = {
                    "payment_id": "payment - 123",
                    "amount": 100.00,
                    "currency": "USD",
                    "user_id": "user - 123",
                }

                await service.trigger_event(
                    event_type=WebhookEventType.PAYMENT_RECEIVED, 
                        event_data=payment_data
                )

                # SUBSCRIPTION_CREATED event
                subscription_data = {
                    "subscription_id": "sub - 123",
                    "plan": "premium",
                    "user_id": "user - 123",
                    "start_date": datetime.utcnow().isoformat(),
                }

                await service.trigger_event(
                    event_type=WebhookEventType.SUBSCRIPTION_CREATED, 
                        event_data=subscription_data
                )

                # Wait for all events to be delivered
                await asyncio.sleep(1)

                # Verify that events were filtered correctly

                # Webhook 1 should receive only USER events
                assert WebhookEventType.USER_CREATED in received_events[webhook1["id"]]
                assert WebhookEventType.PAYMENT_RECEIVED not in received_events[
    webhook1["id"]
]]
                assert WebhookEventType.SUBSCRIPTION_CREATED not in received_events[
    webhook1["id"]
]]

                # Webhook 2 should receive only PAYMENT events
                assert WebhookEventType.USER_CREATED not in received_events[
    webhook2["id"]
]]
                assert WebhookEventType.PAYMENT_RECEIVED in received_events[
    webhook2["id"]
]]
                assert WebhookEventType.SUBSCRIPTION_CREATED not in received_events[
    webhook2["id"]
]]

                # Webhook 3 should receive all events
                assert WebhookEventType.USER_CREATED in received_events[webhook3["id"]]
                assert WebhookEventType.PAYMENT_RECEIVED in received_events[
    webhook3["id"]
]]
                assert WebhookEventType.SUBSCRIPTION_CREATED in received_events[
    webhook3["id"]
]]

        finally:
            # Stop the service
            await service.stop()

class TestPayloadValidation:
    """Tests for event payload validation."""

    @pytest.mark.asyncio
    async def test_payload_validation(self):
        """Test that event payloads are validated before delivery."""
        # Create a webhook service with validation enabled
        service = WebhookService(validate_payloads=True)
        await service.start()

        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com / webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True,
            }
            webhook = await service.register_webhook(webhook_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Patch the httpx.AsyncClient.post method to return success
            with patch("httpx.AsyncClient.post", return_value=success_response):
                # Valid payload
                valid_data = {
                    "user_id": "user - 123",
                    "username": "testuser",
                    "email": "test @ example.com",
                }

                # Deliver event with valid payload
                valid_delivery = await service.deliver_event(
                    webhook_id=webhook["id"],
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=valid_data,
                )

                # Verify that delivery was successful
                assert valid_delivery["status"] == WebhookDeliveryStatus.SUCCESS

                # Invalid payload (missing required fields)
                invalid_data = {"username": "testuser"}  # Missing user_id

                # Attempt to deliver event with invalid payload
                with pytest.raises(ValueError, match="Invalid payload"):
                    await service.deliver_event(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=invalid_data,
                    )

        finally:
            # Stop the service
            await service.stop()

class TestEventCorrelation:
    """Tests for event correlation across multiple webhooks."""

    @pytest.mark.asyncio
    async def test_event_correlation(self):
        """Test that related events can be correlated across multiple webhooks."""
        # Create a webhook service
        service = WebhookService()
        await service.start()

        try:
            # Register webhooks for different event types

            # Webhook 1: USER events
            webhook1_data = {
                "url": "https://example.com / webhook1",
                "events": [WebhookEventType.USER_CREATED],
                "description": "User events webhook",
                "is_active": True,
            }
            webhook1 = await service.register_webhook(webhook1_data)

            # Webhook 2: PAYMENT events
            webhook2_data = {
                "url": "https://example.com / webhook2",
                "events": [WebhookEventType.PAYMENT_RECEIVED],
                "description": "Payment events webhook",
                "is_active": True,
            }
            webhook2 = await service.register_webhook(webhook2_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Track delivered events
            delivered_events = []

            async def mock_post(*args, **kwargs):
                # Extract the payload from kwargs
                payload = json.loads(kwargs.get("data", "{}"))
                delivered_events.append(payload)
                return success_response

            # Patch the httpx.AsyncClient.post method to track events
            with patch("httpx.AsyncClient.post", mock_post):
                # Create a correlation ID to link events
                correlation_id = str(uuid.uuid4())

                # Trigger a USER_CREATED event
                user_data = {
                    "user_id": "user - 123",
                    "username": "testuser",
                    "email": "test @ example.com",
                    "correlation_id": correlation_id,
                }

                await service.trigger_event(
                    event_type=WebhookEventType.USER_CREATED, event_data=user_data
                )

                # Trigger a related PAYMENT_RECEIVED event
                payment_data = {
                    "payment_id": "payment - 123",
                    "amount": 100.00,
                    "currency": "USD",
                    "user_id": "user - 123",
                    "correlation_id": correlation_id,
                }

                await service.trigger_event(
                    event_type=WebhookEventType.PAYMENT_RECEIVED, 
                        event_data=payment_data
                )

                # Wait for all events to be delivered
                await asyncio.sleep(1)

                # Verify that events were delivered with the correlation ID
                user_events = [
                    e for e in delivered_events if e["type"] == \
                        WebhookEventType.USER_CREATED
                ]
                payment_events = [
                    e for e in delivered_events if e["type"] == \
                        WebhookEventType.PAYMENT_RECEIVED
                ]

                assert len(user_events) == 1
                assert len(payment_events) == 1

                # Verify that both events have the same correlation ID
                assert user_events[0]["data"]["correlation_id"] == correlation_id
                assert payment_events[0]["data"]["correlation_id"] == correlation_id

        finally:
            # Stop the service
            await service.stop()

class TestEventBatching:
    """Tests for event batching and debouncing."""

    @pytest.mark.asyncio
    async def test_event_batching(self):
        """Test that events can be batched for delivery."""
        # Create a webhook service with batching enabled
        service = WebhookService(enable_batching=True, batch_size=5, batch_window=1)
        await service.start()

        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com / webhook",
                "events": [WebhookEventType.USER_UPDATED],
                "description": "Test webhook",
                "is_active": True,
            }
            webhook = await service.register_webhook(webhook_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Track batched deliveries
            batched_deliveries = []

            async def mock_post(*args, **kwargs):
                # Extract the payload from kwargs
                payload = json.loads(kwargs.get("data", "{}"))
                batched_deliveries.append(payload)
                return success_response

            # Patch the httpx.AsyncClient.post method to track batched deliveries
            with patch("httpx.AsyncClient.post", mock_post):
                # Trigger multiple events in quick succession
                for i in range(10):
                    event_data = {
                        "user_id": "user - 123",
                        "username": f"testuser-{i}",
                        "email": f"test{i}@example.com",
                    }

                    await service.trigger_event(
                        event_type=WebhookEventType.USER_UPDATED, event_data=event_data
                    )

                # Wait for batching window to complete
                await asyncio.sleep(2)

                # Verify that events were batched
                assert len(batched_deliveries) <= 2  # Should be 2 batches of 5 events

                # Verify that each batch contains multiple events
                for batch in batched_deliveries:
                    assert "events" in batch
                    assert len(batch["events"]) > 1
                    assert len(batch["events"]) <= 5  # Max batch size

        finally:
            # Stop the service
            await service.stop()

    @pytest.mark.asyncio
    async def test_event_debouncing(self):
        """Test that events can be debounced for delivery."""
        # Create a webhook service with debouncing enabled
        service = WebhookService(enable_debouncing=True, debounce_window=0.5)
        await service.start()

        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com / webhook",
                "events": [WebhookEventType.USER_UPDATED],
                "description": "Test webhook",
                "is_active": True,
            }
            webhook = await service.register_webhook(webhook_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Track delivered events
            delivered_events = []

            async def mock_post(*args, **kwargs):
                # Extract the payload from kwargs
                payload = json.loads(kwargs.get("data", "{}"))
                delivered_events.append(payload)
                return success_response

            # Patch the httpx.AsyncClient.post method to track events
            with patch("httpx.AsyncClient.post", mock_post):
                # Trigger multiple updates to the same user in quick succession
                for i in range(5):
                    event_data = {
                        "user_id": "user - 123",
                        "username": f"testuser-{i}",  # Changing username each time
                        "email": "test @ example.com",
                    }

                    await service.trigger_event(
                        event_type=WebhookEventType.USER_UPDATED,
                        event_data=event_data,
                        debounce_key="user - 123",  # Use user_id as debounce key
                    )

                    # Small delay between events
                    await asyncio.sleep(0.1)

                # Wait for debouncing window to complete
                await asyncio.sleep(1)

                # Verify that only the last event was delivered
                assert len(delivered_events) == 1
                assert delivered_events[0]["data"]["username"] == "testuser - \
                    4"  # Last update

        finally:
            # Stop the service
            await service.stop()

class TestEventTransformation:
    """Tests for event transformation middleware."""

    @pytest.mark.asyncio
    async def test_event_transformation(self):
        """Test that events can be transformed before delivery."""

        # Define a transformation function
        async def transform_event(event_type, event_data):
            # Add a timestamp
            transformed_data = event_data.copy()
            transformed_data["processed_at"] = datetime.utcnow().isoformat()

            # Mask sensitive data
            if "email" in transformed_data:
                transformed_data["email"] = "***@***.com"

            return transformed_data

        # Create a webhook service with transformation
        service = WebhookService(transform_function=transform_event)
        await service.start()

        try:
            # Register a webhook
            webhook_data = {
                "url": "https://example.com / webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True,
            }
            webhook = await service.register_webhook(webhook_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Track delivered events
            delivered_events = []

            async def mock_post(*args, **kwargs):
                # Extract the payload from kwargs
                payload = json.loads(kwargs.get("data", "{}"))
                delivered_events.append(payload)
                return success_response

            # Patch the httpx.AsyncClient.post method to track events
            with patch("httpx.AsyncClient.post", mock_post):
                # Trigger an event
                event_data = {
                    "user_id": "user - 123",
                    "username": "testuser",
                    "email": "test @ example.com",
                }

                await service.trigger_event(
                    event_type=WebhookEventType.USER_CREATED, event_data=event_data
                )

                # Wait for event to be delivered
                await asyncio.sleep(1)

                # Verify that the event was transformed
                assert len(delivered_events) == 1
                assert "processed_at" in delivered_events[0]["data"]
                assert delivered_events[0]["data"]["email"] == "***@***.com"

        finally:
            # Stop the service
            await service.stop()

class TestCustomHeaders:
    """Tests for custom header propagation."""

    @pytest.mark.asyncio
    async def test_custom_header_propagation(self):
        """Test that custom headers are propagated to webhook deliveries."""
        # Create a webhook service
        service = WebhookService()
        await service.start()

        try:
            # Register a webhook with custom headers
            webhook_data = {
                "url": "https://example.com / webhook",
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "headers": {"X - API - Key": "test - api - key", 
                    "X - Custom - Header": "custom - value"},
                "is_active": True,
            }
            webhook = await service.register_webhook(webhook_data)

            # Create a successful response
            success_response = AsyncMock()
            success_response.status = 200
            success_response.text = AsyncMock(return_value="OK")

            # Track headers in requests
            request_headers = []

            async def mock_post(*args, **kwargs):
                # Extract the headers from kwargs
                headers = kwargs.get("headers", {})
                request_headers.append(headers)
                return success_response

            # Patch the httpx.AsyncClient.post method to track headers
            with patch("httpx.AsyncClient.post", mock_post):
                # Trigger an event
                event_data = {
                    "user_id": "user - 123",
                    "username": "testuser",
                    "email": "test @ example.com",
                }

                await service.trigger_event(
                    event_type=WebhookEventType.USER_CREATED, event_data=event_data
                )

                # Wait for event to be delivered
                await asyncio.sleep(1)

                # Verify that custom headers were included
                assert len(request_headers) == 1
                assert "X - API - Key" in request_headers[0]
                assert request_headers[0]["X - API - Key"] == "test - api - key"
                assert "X - Custom - Header" in request_headers[0]
                assert request_headers[0]["X - Custom - Header"] == "custom - value"

                # Verify that standard headers were also included
                assert "Content - Type" in request_headers[0]
                assert request_headers[0]["Content - Type"] == "application / json"
                assert "User - Agent" in request_headers[0]

        finally:
            # Stop the service
            await service.stop()
