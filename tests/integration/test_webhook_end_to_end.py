"""
End-to-end tests for the webhook system.

This module tests the complete webhook flow from registration to delivery,
including security features.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import FastAPI, Request, Response, status
from fastapi.testclient import TestClient

from api.middleware.webhook_security import WebhookIPAllowlistMiddleware, WebhookRateLimitMiddleware
from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_security import (
    WebhookIPAllowlist,
    WebhookRateLimiter,
    WebhookSignatureVerifier,
)
from api.services.webhook_service import WebhookService

# Test data
TEST_SECRET = "test-webhook-secret-key"
TEST_EVENT_DATA = {
    "user_id": "user-123",
    "username": "testuser",
    "email": "test@example.com",
    "created_at": datetime.now(timezone.utc).isoformat(),
}


@pytest.fixture
def webhook_service():
    """Create a webhook service for testing."""
    service = WebhookService()
    asyncio.run(service.start())
    yield service
    asyncio.run(service.stop())


@pytest.fixture
def webhook_receiver_app():
    """Create a FastAPI app that receives webhooks."""
    app = FastAPI()
    app.received_webhooks = []
    app.webhook_secret = TEST_SECRET

    @app.post("/webhook")
    async def receive_webhook(request: Request):
        # Get the payload
        payload_bytes = await request.body()
        payload = payload_bytes.decode()

        # Get the signature
        signature = request.headers.get("X-Webhook-Signature")

        # Verify the signature
        is_valid = WebhookSignatureVerifier.verify_signature(app.webhook_secret, payload, signature)

        # Store the received webhook
        app.received_webhooks.append(
            {
                "payload": json.loads(payload),
                "signature": signature,
                "headers": dict(request.headers),
                "is_valid": is_valid,
            }
        )

        if not is_valid:
            return Response(
                content=json.dumps({"error": "Invalid signature"}),
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
            )

        return {"status": "success", "received_at": datetime.now(timezone.utc).isoformat()}

    return app


@pytest.fixture
def webhook_sender_app(webhook_service):
    """Create a FastAPI app that sends webhooks."""
    app = FastAPI()

    @app.post("/webhooks")
    async def register_webhook(request: Request):
        data = await request.json()
        webhook = await webhook_service.register_webhook(data)
        return webhook

    @app.post("/send-event/{webhook_id}")
    async def send_event(webhook_id: str, request: Request):
        data = await request.json()
        event_type = data.get("event_type", WebhookEventType.USER_CREATED)
        event_data = data.get("event_data", TEST_EVENT_DATA)

        delivery = await webhook_service.deliver_event(
            webhook_id=webhook_id, event_type=event_type, event_data=event_data
        )

        return delivery

    return app


class TestWebhookEndToEnd:
    """End-to-end tests for the webhook system."""

    def test_webhook_registration_and_delivery(self, webhook_sender_app, webhook_receiver_app):
        """Test the complete webhook flow from registration to delivery."""
        # Start both apps
        with (
            TestClient(webhook_sender_app) as sender_client,
            TestClient(webhook_receiver_app) as receiver_client,
        ):

            # Get the receiver URL
            receiver_url = (
                f"http://{receiver_client.base_url.host}:"
                f"{receiver_client.base_url.port}/webhook"
            )

            # Register a webhook
            webhook_data = {
                "url": receiver_url,
                "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
                "description": "Test webhook",
                "headers": {"Authorization": "Bearer test-token"},
                "is_active": True,
            }

            # Mock the secret generation to use our test secret
            with patch.object(
                webhook_sender_app.app.state.webhook_service,
                "_generate_secret",
                return_value=TEST_SECRET,
            ):
                response = sender_client.post("/webhooks", json=webhook_data)

            assert response.status_code == 200
            webhook = response.json()
            assert webhook["url"] == receiver_url
            assert webhook["events"] == webhook_data["events"]
            assert webhook["description"] == webhook_data["description"]

            # Send an event
            event_data = {
                "event_type": WebhookEventType.USER_CREATED,
                "event_data": TEST_EVENT_DATA,
            }

            response = sender_client.post(f"/send-event/{webhook['id']}", json=event_data)
            assert response.status_code == 200
            delivery = response.json()
            assert delivery["status"] == WebhookDeliveryStatus.SUCCESS

            # Check that the webhook was received
            assert len(webhook_receiver_app.received_webhooks) == 1
            received = webhook_receiver_app.received_webhooks[0]
            assert received["is_valid"]
            assert received["payload"]["type"] == WebhookEventType.USER_CREATED
            assert received["payload"]["data"] == TEST_EVENT_DATA

    def test_webhook_signature_verification(self, webhook_sender_app, webhook_receiver_app):
        """Test that webhook signatures are properly verified."""
        # Start both apps
        with (
            TestClient(webhook_sender_app) as sender_client,
            TestClient(webhook_receiver_app) as receiver_client,
        ):

            # Get the receiver URL
            receiver_url = (
                f"http://{receiver_client.base_url.host}:"
                f"{receiver_client.base_url.port}/webhook"
            )

            # Register a webhook
            webhook_data = {
                "url": receiver_url,
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True,
            }

            # Mock the secret generation to use our test secret
            with patch.object(
                webhook_sender_app.app.state.webhook_service,
                "_generate_secret",
                return_value=TEST_SECRET,
            ):
                response = sender_client.post("/webhooks", json=webhook_data)

            webhook = response.json()

            # Create a payload
            payload = {
                "id": str(uuid.uuid4()),
                "type": WebhookEventType.USER_CREATED,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "data": TEST_EVENT_DATA,
            }

            # Create a valid signature
            valid_signature = WebhookSignatureVerifier.create_signature(
                TEST_SECRET, json.dumps(payload)
            )

            # Create an invalid signature
            invalid_signature = WebhookSignatureVerifier.create_signature(
                "wrong-secret", json.dumps(payload)
            )

            # Send a request with a valid signature
            headers = {"Content-Type": "application/json", "X-Webhook-Signature": valid_signature}
            response = receiver_client.post("/webhook", json=payload, headers=headers)
            assert response.status_code == 200

            # Send a request with an invalid signature
            headers = {"Content-Type": "application/json", "X-Webhook-Signature": invalid_signature}
            response = receiver_client.post("/webhook", json=payload, headers=headers)
            assert response.status_code == 401

    def test_webhook_with_ip_allowlist(self, webhook_sender_app, webhook_receiver_app):
        """Test webhook delivery with IP allowlisting."""
        # Create an IP allowlist
        ip_allowlist = WebhookIPAllowlist()

        # Add middleware to the sender app
        webhook_sender_app.add_middleware(
            WebhookIPAllowlistMiddleware, allowlist=ip_allowlist, webhook_path_prefix="/webhooks"
        )

        # Start both apps
        with (
            TestClient(webhook_sender_app) as sender_client,
            TestClient(webhook_receiver_app) as receiver_client,
        ):

            # Get the receiver URL
            receiver_url = (
                f"http://{receiver_client.base_url.host}:"
                f"{receiver_client.base_url.port}/webhook"
            )

            # Try to register a webhook without allowlisting the IP
            webhook_data = {
                "url": receiver_url,
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True,
            }

            response = sender_client.post("/webhooks", json=webhook_data)
            assert response.status_code == 403

            # Allowlist the client IP
            ip_allowlist.add_ip("testclient")

            # Now registration should succeed
            response = sender_client.post("/webhooks", json=webhook_data)
            assert response.status_code == 200

    def test_webhook_with_rate_limiting(self, webhook_sender_app, webhook_receiver_app):
        """Test webhook delivery with rate limiting."""
        # Create a rate limiter with a low limit
        rate_limiter = WebhookRateLimiter(limit=2, window_seconds=1)

        # Add middleware to the sender app
        webhook_sender_app.add_middleware(
            WebhookRateLimitMiddleware, rate_limiter=rate_limiter, webhook_path_prefix="/webhooks"
        )

        # Start both apps
        with (
            TestClient(webhook_sender_app) as sender_client,
            TestClient(webhook_receiver_app) as receiver_client,
        ):

            # Get the receiver URL
            receiver_url = (
                f"http://{receiver_client.base_url.host}:"
                f"{receiver_client.base_url.port}/webhook"
            )

            # Register a webhook
            webhook_data = {
                "url": receiver_url,
                "events": [WebhookEventType.USER_CREATED],
                "description": "Test webhook",
                "is_active": True,
            }

            # First request should succeed
            response = sender_client.post("/webhooks", json=webhook_data)
            assert response.status_code == 200
            assert "X-RateLimit-Remaining" in response.headers

            # Second request should succeed
            response = sender_client.post("/webhooks", json=webhook_data)
            assert response.status_code == 200
            assert "X-RateLimit-Remaining" in response.headers
            assert int(response.headers["X-RateLimit-Remaining"]) == 0

            # Third request should be rate limited
            response = sender_client.post("/webhooks", json=webhook_data)
            assert response.status_code == 429
            assert "Retry-After" in response.headers
