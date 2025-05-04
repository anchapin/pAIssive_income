"""
"""
Integration tests for webhook security features.
Integration tests for webhook security features.


This module tests the integration between webhook security features and the webhook service.
This module tests the integration between webhook security features and the webhook service.
"""
"""


import asyncio
import asyncio
import json
import json
import time
import time
from datetime import datetime, timezone
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from unittest.mock import MagicMock, patch


import pytest
import pytest
from fastapi import FastAPI, Request
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.testclient import TestClient


from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService
from api.services.webhook_service import WebhookService


(
(
WebhookIPAllowlistMiddleware,
WebhookIPAllowlistMiddleware,
WebhookRateLimitMiddleware,
WebhookRateLimitMiddleware,
)
)
(
(
WebhookIPAllowlist,
WebhookIPAllowlist,
WebhookRateLimiter,
WebhookRateLimiter,
WebhookSignatureVerifier,
WebhookSignatureVerifier,
)
)
# Test data
# Test data
TEST_WEBHOOK_ID = "test-webhook-123"
TEST_WEBHOOK_ID = "test-webhook-123"
TEST_WEBHOOK = {
TEST_WEBHOOK = {
"id": TEST_WEBHOOK_ID,
"id": TEST_WEBHOOK_ID,
"url": "https://example.com/webhook",
"url": "https://example.com/webhook",
"events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
"events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
"description": "Test webhook",
"description": "Test webhook",
"headers": {"Authorization": "Bearer test-token"},
"headers": {"Authorization": "Bearer test-token"},
"is_active": True,
"is_active": True,
"created_at": datetime.now(timezone.utc),
"created_at": datetime.now(timezone.utc),
"last_called_at": None,
"last_called_at": None,
"secret": "test-secret-key",
"secret": "test-secret-key",
}
}


TEST_EVENT = {
TEST_EVENT = {
"type": WebhookEventType.USER_CREATED,
"type": WebhookEventType.USER_CREATED,
"data": {
"data": {
"user_id": "user-123",
"user_id": "user-123",
"username": "testuser",
"username": "testuser",
"email": "test@example.com",
"email": "test@example.com",
"created_at": datetime.now(timezone.utc).isoformat(),
"created_at": datetime.now(timezone.utc).isoformat(),
},
},
}
}




@pytest.fixture
@pytest.fixture
def webhook_service():
    def webhook_service():
    """Create a webhook service for testing."""
    service = WebhookService()
    return service


    @pytest.fixture
    def ip_allowlist():
    """Create an IP allowlist for testing."""
    allowlist = WebhookIPAllowlist()
    # Add some test IPs and networks
    allowlist.add_ip("192.168.1.1")
    allowlist.add_network("10.0.0.0/8")
    return allowlist


    @pytest.fixture
    def rate_limiter():
    """Create a rate limiter for testing."""
    return WebhookRateLimiter(limit=5, window_seconds=1)


    @pytest.fixture
    def app(webhook_service, ip_allowlist, rate_limiter):
    """Create a FastAPI app with webhook security middleware."""
    app = FastAPI()

    # Add middleware
    app.add_middleware(
    WebhookIPAllowlistMiddleware,
    allowlist=ip_allowlist,
    webhook_path_prefix="/webhooks",
    )
    app.add_middleware(
    WebhookRateLimitMiddleware,
    rate_limiter=rate_limiter,
    webhook_path_prefix="/webhooks",
    )

    # Add test routes
    @app.post("/webhooks/test")
    async def test_webhook(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    return {"status": "success", "client_ip": client_ip}

    @app.post("/api/other")
    async def other_endpoint(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    return {"status": "success", "client_ip": client_ip}

    return app


    @pytest.fixture
    def client(app):
    """Create a test client."""
    return TestClient(app)


    class TestWebhookSecurityIntegration:

    def test_ip_allowlist_middleware_allowed(self, client):
    """Test that allowed IPs can access webhook endpoints."""
    # Set client IP to an allowed IP
    client.app.user_middleware[0].allowlist.add_ip("testclient")

    response = client.post("/webhooks/test", json={"test": "data"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    def test_ip_allowlist_middleware_blocked(self, client):
    """Test that disallowed IPs are blocked from webhook endpoints."""
    # Clear the allowlist and add a different IP
    client.app.user_middleware[0].allowlist.allowlisted_ips.clear()
    client.app.user_middleware[0].allowlist.add_ip("192.168.1.2")

    response = client.post("/webhooks/test", json={"test": "data"})
    assert response.status_code == 403
    assert "IP address not allowed" in response.json()["detail"]

    def test_ip_allowlist_middleware_non_webhook_path(self, client):
    """Test that non-webhook paths are not affected by IP allowlisting."""
    # Clear the allowlist
    client.app.user_middleware[0].allowlist.allowlisted_ips.clear()

    # This should work even though the IP is not allowlisted
    response = client.post("/api/other", json={"test": "data"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    def test_rate_limit_middleware(self, client):
    """Test that rate limiting is applied to webhook endpoints."""
    # Make requests up to the limit
    for _ in range(5):
    response = client.post("/webhooks/test", json={"test": "data"})
    assert response.status_code == 200
    assert "X-RateLimit-Remaining" in response.headers

    # Next request should be rate limited
    response = client.post("/webhooks/test", json={"test": "data"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
    assert "Retry-After" in response.headers

    def test_rate_limit_middleware_non_webhook_path(self, client):
    """Test that non-webhook paths are not affected by rate limiting."""
    # Make many requests to a non-webhook path
    for _ in range(10):
    response = client.post("/api/other", json={"test": "data"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    def test_signature_verification_with_webhook_service(self, webhook_service):
    """Test signature verification with the webhook service."""
    # Create a webhook
    webhook_data = {
    "url": "https://example.com/webhook",
    "events": [WebhookEventType.USER_CREATED],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer test-token"},
    "is_active": True,
    }

    # Mock the register_webhook method to return a test webhook
    with patch.object(
    webhook_service, "register_webhook", return_value=TEST_WEBHOOK
    ):
    webhook = asyncio.run(webhook_service.register_webhook(webhook_data))

    # Create a payload
    payload = json.dumps(
    {
    "id": "evt-123",
    "type": WebhookEventType.USER_CREATED,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "data": {"user_id": "user-123", "username": "testuser"},
    }
    )

    # Create a signature
    signature = WebhookSignatureVerifier.create_signature(
    webhook["secret"], payload
    )

    # Verify the signature
    assert WebhookSignatureVerifier.verify_signature(
    webhook["secret"], payload, signature
    )

    # Verify with headers
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}
    assert WebhookSignatureVerifier.verify_request_signature(
    webhook["secret"], payload, headers
    )

    def test_webhook_delivery_with_security(self, webhook_service):
    """Test webhook delivery with security features."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.raise_for_status = MagicMock()

    # Create a mock for httpx.AsyncClient.post
    async def mock_post(url, headers=None, json=None, **kwargs):
    # Verify that the signature header is present
    assert "X-Webhook-Signature" in headers

    # Verify the signature
    payload = json_dumps(json)
    signature = headers["X-Webhook-Signature"]
    assert WebhookSignatureVerifier.verify_signature(
    TEST_WEBHOOK["secret"], payload, signature
    )

    return mock_response

    # Helper function to match json.dumps behavior in the service
    def json_dumps(obj):
    return json.dumps(obj)

    # Patch the httpx.AsyncClient.post method
    with patch("httpx.AsyncClient.post", mock_post):
    # Patch the get_webhook method to return our test webhook
    with patch.object(
    webhook_service, "get_webhook", return_value=TEST_WEBHOOK
    ):
    # Deliver an event
    delivery = asyncio.run(
    webhook_service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )
    )

    # Check delivery status
    assert delivery["status"] == WebhookDeliveryStatus.SUCCESS
    assert len(delivery["attempts"]) == 1
    assert (
    delivery["attempts"][0]["status"] == WebhookDeliveryStatus.SUCCESS
    )

    def test_end_to_end_webhook_flow(self, webhook_service, ip_allowlist, rate_limiter):
    """Test the end-to-end webhook flow with security features."""
    # Create a FastAPI app to receive webhooks
    receiver_app = FastAPI()
    received_webhooks = []

    @receiver_app.post("/webhook")
    async def receive_webhook(request: Request):
    # Get the payload
    payload = await request.json()

    # Get the signature
    signature = request.headers.get("X-Webhook-Signature")

    # Store the received webhook
    received_webhooks.append(
    {
    "payload": payload,
    "signature": signature,
    "headers": dict(request.headers),
    }
    )

    return {"status": "success"}

    # Start the receiver app in a separate thread
    with TestClient(receiver_app) as receiver_client:
    # Create a webhook pointing to the receiver
    webhook_data = {
    "url": f"http://{receiver_client.base_url.host}:{receiver_client.base_url.port}/webhook",
    "events": [WebhookEventType.USER_CREATED],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer test-token"},
    "is_active": True,
    }

    # Register the webhook
    with patch.object(
    webhook_service, "register_webhook", return_value=TEST_WEBHOOK
    ):
    asyncio.run(webhook_service.register_webhook(webhook_data))

    # Allow the receiver's IP
    ip_allowlist.add_ip(receiver_client.base_url.host)

    # Deliver an event
    with patch.object(
    webhook_service, "get_webhook", return_value=TEST_WEBHOOK
    ):
    # Use the real httpx.AsyncClient.post to make an actual HTTP request
    asyncio.run(
    webhook_service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )
    )

    # Check that the webhook was received
    assert len(received_webhooks) == 1
    assert "X-Webhook-Signature" in received_webhooks[0]["headers"]

    # Verify the signature
    payload_str = json.dumps(received_webhooks[0]["payload"])
    signature = received_webhooks[0]["signature"]
    assert WebhookSignatureVerifier.verify_signature(
    TEST_WEBHOOK["secret"], payload_str, signature
    )


    @pytest.mark.asyncio
    async def test_webhook_service_with_rate_limiting():
    """Test webhook service with rate limiting."""
    # Create services
    webhook_service = WebhookService()
    rate_limiter = WebhookRateLimiter(limit=3, window_seconds=1)

    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.raise_for_status = MagicMock()

    # Patch the httpx.AsyncClient.post method
    with patch("httpx.AsyncClient.post", return_value=mock_response):
    # Patch the get_webhook method to return our test webhook
    with patch.object(webhook_service, "get_webhook", return_value=TEST_WEBHOOK):
    # Make requests up to the limit
    for _ in range(3):
    # Check if rate limited
    if rate_limiter.is_rate_limited(TEST_WEBHOOK["url"]):
    break

    # Add request to rate limiter
    rate_limiter.add_request(TEST_WEBHOOK["url"])

    # Deliver an event
    await webhook_service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )

    # Next request should be rate limited
    assert rate_limiter.is_rate_limited(TEST_WEBHOOK["url"])

    # Get remaining requests
    remaining = rate_limiter.get_remaining_requests(TEST_WEBHOOK["url"])
    assert remaining == 0

    # Get reset time
    reset_time = rate_limiter.get_reset_time(TEST_WEBHOOK["url"])
    assert reset_time is not None