"""
"""
Tests for webhook service error handling scenarios.
Tests for webhook service error handling scenarios.
"""
"""


from datetime import datetime, timezone
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from unittest.mock import MagicMock, patch


import httpx
import httpx
import pytest
import pytest


from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService
from api.services.webhook_service import WebhookService


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




@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_webhook_connection_error():
    async def test_webhook_connection_error():
    """Test handling of connection errors during webhook delivery."""
    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return our test webhook
    with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
    # Patch httpx.AsyncClient.post to raise a connection error
    with patch(
    "httpx.AsyncClient.post",
    side_effect=httpx.ConnectError("Connection refused"),
    ):
    # Deliver an event
    delivery = await service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )

    # Assertions
    assert delivery is not None
    assert delivery["webhook_id"] == TEST_WEBHOOK_ID
    assert delivery["status"] == WebhookDeliveryStatus.FAILED
    assert len(delivery["attempts"]) == 1
    assert delivery["attempts"][0]["status"] == WebhookDeliveryStatus.FAILED
    assert delivery["attempts"][0]["response_code"] is None
    assert "Connection refused" in delivery["attempts"][0]["error_message"]


    @pytest.mark.asyncio
    async def test_webhook_timeout_error():
    """Test handling of timeout errors during webhook delivery."""
    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return our test webhook
    with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
    # Patch httpx.AsyncClient.post to raise a timeout error
    with patch(
    "httpx.AsyncClient.post",
    side_effect=httpx.TimeoutException("Request timed out"),
    ):
    # Deliver an event
    delivery = await service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )

    # Assertions
    assert delivery is not None
    assert delivery["webhook_id"] == TEST_WEBHOOK_ID
    assert delivery["status"] == WebhookDeliveryStatus.FAILED
    assert len(delivery["attempts"]) == 1
    assert delivery["attempts"][0]["status"] == WebhookDeliveryStatus.FAILED
    assert delivery["attempts"][0]["response_code"] is None
    assert "Request timed out" in delivery["attempts"][0]["error_message"]


    @pytest.mark.asyncio
    async def test_webhook_invalid_response():
    """Test handling of invalid responses during webhook delivery."""
    # Setup mock for httpx.AsyncClient.post to return invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Not a valid JSON"

    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return our test webhook
    with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
    # Patch httpx.AsyncClient.post to return our mock response
    with patch("httpx.AsyncClient.post", return_value=mock_response):
    # Deliver an event
    delivery = await service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )

    # Assertions
    assert delivery is not None
    assert delivery["webhook_id"] == TEST_WEBHOOK_ID
    assert (
    delivery["status"] == WebhookDeliveryStatus.SUCCESS
    )  # HTTP 200 is still a success
    assert len(delivery["attempts"]) == 1
    assert delivery["attempts"][0]["status"] == WebhookDeliveryStatus.SUCCESS
    assert delivery["attempts"][0]["response_code"] == 200
    assert delivery["attempts"][0]["response_body"] == "Not a valid JSON"


    @pytest.mark.asyncio
    async def test_webhook_not_found():
    """Test handling of non-existent webhook."""
    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return None (webhook not found)
    with patch.object(service, "get_webhook", return_value=None):
    # Deliver an event to a non-existent webhook
    with pytest.raises(ValueError) as excinfo:
    await service.deliver_event(
    webhook_id="non-existent-webhook",
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )

    # Assertions
    assert "Webhook not found" in str(excinfo.value)


    @pytest.mark.asyncio
    async def test_webhook_inactive():
    """Test handling of inactive webhook."""
    # Create an inactive webhook
    inactive_webhook = TEST_WEBHOOK.copy()
    inactive_webhook["is_active"] = False

    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return our inactive webhook
    with patch.object(service, "get_webhook", return_value=inactive_webhook):
    # Deliver an event to an inactive webhook
    with pytest.raises(ValueError) as excinfo:
    await service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,
    event_data=TEST_EVENT["data"],
    )

    # Assertions
    assert "Webhook is inactive" in str(excinfo.value)


    @pytest.mark.asyncio
    async def test_webhook_event_not_subscribed():
    """Test handling of event type not subscribed to by the webhook."""
    # Create a webhook with limited event subscriptions
    limited_webhook = TEST_WEBHOOK.copy()
    limited_webhook["events"] = [
    WebhookEventType.PAYMENT_RECEIVED
    ]  # Only subscribed to payment events

    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return our limited webhook
    with patch.object(service, "get_webhook", return_value=limited_webhook):
    # Deliver an event of a type not subscribed to
    with pytest.raises(ValueError) as excinfo:
    await service.deliver_event(
    webhook_id=TEST_WEBHOOK_ID,
    event_type=WebhookEventType.USER_CREATED,  # Not subscribed to this event
    event_data=TEST_EVENT["data"],
    )

    # Assertions
    assert "Webhook is not subscribed to event type" in str(excinfo.value)
