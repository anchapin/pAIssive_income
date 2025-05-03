"""
Script to run the webhook tests individually.
"""

import sys
import unittest
from datetime import datetime, timezone
from unittest import mock

import httpx
import pytest

from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService

# Test data
TEST_WEBHOOK_ID = "test - webhook - 123"
TEST_WEBHOOK = {
    "id": TEST_WEBHOOK_ID,
    "url": "https://example.com / webhook",
    "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
    "description": "Test webhook",
    "headers": {"Authorization": "Bearer test - token"},
    "is_active": True,
    "created_at": datetime.now(timezone.utc),
    "last_called_at": None,
    "secret": "test - secret - key",
}

TEST_EVENT = {
    "type": WebhookEventType.USER_CREATED,
    "data": {
        "user_id": "user - 123",
        "username": "testuser",
        "email": "test @ example.com",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
}


class WebhookDeliveryTest(unittest.TestCase):
    """Test webhook delivery functionality."""

    async def test_webhook_delivery_success(self):
        """Test successful webhook delivery."""
        # Setup mock for httpx.AsyncClient.post
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status":"ok"}'

        with mock.patch("httpx.AsyncClient.post", return_value=mock_response):
            # Create a real webhook service instance for testing
            service = WebhookService()

            # Patch the get_webhook method to return our test webhook
            with mock.patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
                # Deliver an event
                delivery = await service.deliver_event(
                    webhook_id=TEST_WEBHOOK_ID,
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=TEST_EVENT["data"],
                )

                # Assertions
                self.assertIsNotNone(delivery)
                self.assertEqual(delivery["webhook_id"], TEST_WEBHOOK_ID)
                self.assertEqual(delivery["status"], WebhookDeliveryStatus.SUCCESS)
                self.assertEqual(len(delivery["attempts"]), 1)
                self.assertEqual(delivery["attempts"][0]["status"], 
                    WebhookDeliveryStatus.SUCCESS)
                self.assertEqual(delivery["attempts"][0]["response_code"], 200)

    async def test_webhook_delivery_failure(self):
        """Test webhook delivery failure."""
        # Setup mock for httpx.AsyncClient.post to simulate a failure
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status = mock.MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request("POST", TEST_WEBHOOK["url"]),
                response=mock_response,
            )
        )

        with mock.patch("httpx.AsyncClient.post", return_value=mock_response):
            # Create a real webhook service instance for testing
            service = WebhookService()

            # Patch the get_webhook method to return our test webhook
            with mock.patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
                # Deliver an event
                delivery = await service.deliver_event(
                    webhook_id=TEST_WEBHOOK_ID,
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=TEST_EVENT["data"],
                )

                # Assertions
                self.assertIsNotNone(delivery)
                self.assertEqual(delivery["webhook_id"], TEST_WEBHOOK_ID)
                self.assertEqual(delivery["status"], WebhookDeliveryStatus.FAILED)
                self.assertEqual(len(delivery["attempts"]), 1)
                self.assertEqual(delivery["attempts"][0]["status"], 
                    WebhookDeliveryStatus.FAILED)
                self.assertEqual(delivery["attempts"][0]["response_code"], 500)
                self.assertIn("Internal Server Error", 
                    delivery["attempts"][0]["error_message"])

    async def test_webhook_connection_error(self):
        """Test handling of connection errors during webhook delivery."""
        # Create a real webhook service instance for testing
        service = WebhookService()

        # Patch the get_webhook method to return our test webhook
        with mock.patch.object(service, "get_webhook", return_value=TEST_WEBHOOK):
            # Patch httpx.AsyncClient.post to raise a connection error
            with mock.patch(
                "httpx.AsyncClient.post", 
                    side_effect=httpx.ConnectError("Connection refused")
            ):
                # Deliver an event
                delivery = await service.deliver_event(
                    webhook_id=TEST_WEBHOOK_ID,
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=TEST_EVENT["data"],
                )

                # Assertions
                self.assertIsNotNone(delivery)
                self.assertEqual(delivery["webhook_id"], TEST_WEBHOOK_ID)
                self.assertEqual(delivery["status"], WebhookDeliveryStatus.FAILED)
                self.assertEqual(len(delivery["attempts"]), 1)
                self.assertEqual(delivery["attempts"][0]["status"], 
                    WebhookDeliveryStatus.FAILED)
                self.assertIsNone(delivery["attempts"][0]["response_code"])
                self.assertIn("Connection refused", 
                    delivery["attempts"][0]["error_message"])


if __name__ == "__main__":
    # Run the tests
    unittest.main()
