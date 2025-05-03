"""
Integration tests for webhook delivery functionality.
"""


from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes.webhook_router import router as webhook_router
from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService



# Test data
TEST_WEBHOOK_ID = "test-webhook-123"
TEST_WEBHOOK = {
    "id": TEST_WEBHOOK_ID,
    "url": "https://example.com/webhook",
    "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer test-token"},
    "is_active": True,
    "created_at": datetime.now(timezone.utc),
    "last_called_at": None,
    "secret": "test-secret-key",
}

TEST_EVENT = {
    "type": WebhookEventType.USER_CREATED,
    "data": {
        "user_id": "user-123",
        "username": "testuser",
        "email": "test@example.com",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
}


@pytest.fixture
def app():
    """Create a FastAPI test application."""
    app = FastAPI()
    app.include_router(webhook_router, prefix="/webhooks")
            return app


@pytest.fixture
def client(app):
    """Create a test client."""
            return TestClient(app)


@pytest.fixture
def mock_webhook_service():
    """Mock the webhook service."""
    with patch("api.routes.webhook_router.webhook_service") as mock_service:
        # Setup mock methods
        mock_service.register_webhook = MagicMock(return_value=TEST_WEBHOOK)
        mock_service.list_webhooks = MagicMock(return_value=[TEST_WEBHOOK])
        mock_service.get_webhook = MagicMock(return_value=TEST_WEBHOOK)
        mock_service.update_webhook = MagicMock(return_value=TEST_WEBHOOK)
        mock_service.delete_webhook = MagicMock(return_value=True)

        # Setup delivery methods
        mock_delivery = {
            "id": "delivery-123",
            "webhook_id": TEST_WEBHOOK_ID,
            "status": WebhookDeliveryStatus.SUCCESS,
            "timestamp": datetime.now(timezone.utc),
            "attempts": [
                {
                    "id": "attempt-123",
                    "webhook_id": TEST_WEBHOOK_ID,
                    "event_type": WebhookEventType.USER_CREATED,
                    "status": WebhookDeliveryStatus.SUCCESS,
                    "request_url": TEST_WEBHOOK["url"],
                    "request_headers": TEST_WEBHOOK["headers"],
                    "request_body": TEST_EVENT,
                    "response_code": 200,
                    "response_body": '{"status":"ok"}',
                    "error_message": None,
                    "timestamp": datetime.now(timezone.utc),
                    "retries": 0,
                    "next_retry": None,
                }
            ],
        }
        mock_service.get_deliveries = MagicMock(return_value=[mock_delivery])
        mock_service.deliver_event = MagicMock(return_value=mock_delivery)

        yield mock_service


@pytest.mark.asyncio
async def test_webhook_delivery_success(mock_webhook_service):
    """Test successful webhook delivery."""
    # Setup mock for httpx.AsyncClient.post
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"status":"ok"}'

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        # Create a real webhook service instance for testing
        service = WebhookService()

        # Patch the get_webhook method to return our test webhook
        with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
            # Deliver an event
            delivery = await service.deliver_event(
                webhook_id=TEST_WEBHOOK_ID,
                event_type=WebhookEventType.USER_CREATED,
                event_data=TEST_EVENT["data"],
            )

            # Assertions
            assert delivery is not None
            assert delivery["webhook_id"] == TEST_WEBHOOK_ID
            assert delivery["status"] == WebhookDeliveryStatus.SUCCESS
            assert len(delivery["attempts"]) == 1
            assert delivery["attempts"][0]["status"] == WebhookDeliveryStatus.SUCCESS
            assert delivery["attempts"][0]["response_code"] == 200


@pytest.mark.asyncio
async def test_webhook_delivery_failure(mock_webhook_service):
    """Test webhook delivery failure."""
    # Setup mock for httpx.AsyncClient.post to simulate a failure
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Server error",
            request=httpx.Request("POST", TEST_WEBHOOK["url"]),
            response=mock_response,
        )
    )

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        # Create a real webhook service instance for testing
        service = WebhookService()

        # Patch the get_webhook method to return our test webhook
        with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
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
            assert delivery["attempts"][0]["response_code"] == 500
            assert "Internal Server Error" in delivery["attempts"][0]["error_message"]


@pytest.mark.asyncio
async def test_webhook_delivery_retry(mock_webhook_service):
    """Test webhook delivery retry mechanism."""
    # Setup sequence of responses: first failure, then success
    mock_failure = MagicMock()
    mock_failure.status_code = 503
    mock_failure.text = "Service Unavailable"
    mock_failure.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Service Unavailable",
            request=httpx.Request("POST", TEST_WEBHOOK["url"]),
            response=mock_failure,
        )
    )

    mock_success = MagicMock()
    mock_success.status_code = 200
    mock_success.text = '{"status":"ok"}'

    # Create a sequence of responses
    responses = [mock_failure, mock_success]

    # Create a real webhook service instance for testing
    service = WebhookService()

    # Patch the get_webhook method to return our test webhook
    with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
        # Patch the httpx.AsyncClient.post to return our sequence of responses
        with patch("httpx.AsyncClient.post", side_effect=responses):
            # Deliver an event with retry
            delivery = await service.deliver_event(
                webhook_id=TEST_WEBHOOK_ID,
                event_type=WebhookEventType.USER_CREATED,
                event_data=TEST_EVENT["data"],
                retry_count=1,  # Allow one retry
                retry_delay=0.1,  # Short delay for testing
            )

            # Assertions
            assert delivery is not None
            assert delivery["webhook_id"] == TEST_WEBHOOK_ID
            assert delivery["status"] == WebhookDeliveryStatus.SUCCESS
            assert len(delivery["attempts"]) == 2
            assert delivery["attempts"][0]["status"] == WebhookDeliveryStatus.FAILED
            assert delivery["attempts"][0]["response_code"] == 503
            assert delivery["attempts"][1]["status"] == WebhookDeliveryStatus.SUCCESS
            assert delivery["attempts"][1]["response_code"] == 200


@pytest.mark.asyncio
async def test_webhook_delivery_max_retries_exceeded(mock_webhook_service):
    """Test webhook delivery with maximum retries exceeded."""
    # Setup mock for httpx.AsyncClient.post to always fail
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Server error",
            request=httpx.Request("POST", TEST_WEBHOOK["url"]),
            response=mock_response,
        )
    )

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        # Create a real webhook service instance for testing
        service = WebhookService()

        # Patch the get_webhook method to return our test webhook
        with patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
            # Deliver an event with multiple retries
            delivery = await service.deliver_event(
                webhook_id=TEST_WEBHOOK_ID,
                event_type=WebhookEventType.USER_CREATED,
                event_data=TEST_EVENT["data"],
                retry_count=3,  # Allow three retries
                retry_delay=0.1,  # Short delay for testing
            )

            # Assertions
            assert delivery is not None
            assert delivery["webhook_id"] == TEST_WEBHOOK_ID
            assert delivery["status"] == WebhookDeliveryStatus.MAX_RETRIES_EXCEEDED
            assert len(delivery["attempts"]) == 4  # Initial attempt + 3 retries
            for attempt in delivery["attempts"]:
                assert attempt["status"] == WebhookDeliveryStatus.FAILED
                assert attempt["response_code"] == 500