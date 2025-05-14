"""test_webhook_service - Module for tests/api.test_webhook_service."""

# Standard library imports
import json
import unittest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException, Timeout

# Third-party imports
import pytest

# Local imports
from api.services.webhook_service import WebhookService

class TestWebhookService(unittest.TestCase):
    """Test suite for the WebhookService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.webhook_service = WebhookService()
        self.mock_db = MagicMock()
        self.webhook_service.db = self.mock_db

    def test_register_webhook(self):
        """Test registering a webhook."""
        # Arrange
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["user.created", "payment.received"],
            "description": "Test webhook",
            "headers": {"Authorization": "Bearer test-token"},
            "is_active": True,
        }

        # Mock the database call
        self.mock_db.add_webhook.return_value = {
            "id": "webhook-123",
            **webhook_data,
            "secret": "whsec_test_secret",
        }

        # Act
        result = self.webhook_service.register_webhook(webhook_data)

        # Assert
        self.assertEqual(result["url"], webhook_data["url"])
        self.assertEqual(result["events"], webhook_data["events"])
        self.assertEqual(result["description"], webhook_data["description"])
        self.assertEqual(result["is_active"], webhook_data["is_active"])
        self.assertEqual(result["id"], "webhook-123")
        self.assertEqual(result["secret"], "whsec_test_secret")
        self.mock_db.add_webhook.assert_called_once_with(webhook_data)

    def test_register_webhook_without_db(self):
        """Test registering a webhook without a database connection."""
        # Arrange
        webhook_service = WebhookService(db=None)
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "is_active": True,
        }

        # Act
        result = webhook_service.register_webhook(webhook_data)

        # Assert
        self.assertIn("id", result)
        self.assertIn("secret", result)
        self.assertTrue(result["id"].startswith("webhook-"))
        self.assertTrue(result["secret"].startswith("whsec_"))
        self.assertEqual(result["url"], webhook_data["url"])

    def test_register_webhook_missing_url(self):
        """Test registering a webhook with missing URL."""
        # Arrange
        webhook_data = {
            "events": ["user.created"],
            "is_active": True,
        }

        # Act & Assert
        with self.assertRaises(ValueError):
            self.webhook_service.register_webhook(webhook_data)

    def test_get_webhook(self):
        """Test retrieving a webhook."""
        # Arrange
        webhook_id = "webhook-123"
        expected_webhook = {
            "id": webhook_id,
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "description": "Test webhook",
            "is_active": True,
        }
        self.mock_db.get_webhook.return_value = expected_webhook

        # Act
        result = self.webhook_service.get_webhook(webhook_id)

        # Assert
        self.assertEqual(result, expected_webhook)
        self.mock_db.get_webhook.assert_called_once_with(webhook_id)

    def test_get_webhook_not_found(self):
        """Test retrieving a non-existent webhook."""
        # Arrange
        webhook_id = "webhook-nonexistent"
        self.mock_db.get_webhook.return_value = None

        # Act
        result = self.webhook_service.get_webhook(webhook_id)

        # Assert
        self.assertIsNone(result)
        self.mock_db.get_webhook.assert_called_once_with(webhook_id)

    def test_list_webhooks(self):
        """Test listing webhooks."""
        # Arrange
        expected_webhooks = [
            {
                "id": "webhook-123",
                "url": "https://example.com/webhook1",
                "events": ["user.created"],
                "description": "Test webhook 1",
                "is_active": True,
            },
            {
                "id": "webhook-456",
                "url": "https://example.com/webhook2",
                "events": ["payment.received"],
                "description": "Test webhook 2",
                "is_active": False,
            },
        ]
        self.mock_db.list_webhooks.return_value = expected_webhooks

        # Act
        result = self.webhook_service.list_webhooks()

        # Assert
        self.assertEqual(result, expected_webhooks)
        self.mock_db.list_webhooks.assert_called_once()

    def test_list_webhooks_with_filters(self):
        """Test listing webhooks with filters."""
        # Arrange
        filters = {"is_active": True, "event": "user.created"}
        expected_webhooks = [{
            "id": "webhook-123",
            "url": "https://example.com/webhook1",
            "events": ["user.created"],
            "is_active": True,
        }]
        self.mock_db.list_webhooks.return_value = expected_webhooks

        # Act
        result = self.webhook_service.list_webhooks(filters)

        # Assert
        self.assertEqual(result, expected_webhooks)
        self.mock_db.list_webhooks.assert_called_once_with(filters)

    def test_update_webhook(self):
        """Test updating a webhook."""
        # Arrange
        webhook_id = "webhook-123"
        update_data = {
            "description": "Updated description",
            "is_active": False,
        }
        expected_webhook = {
            "id": webhook_id,
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "description": "Updated description",
            "is_active": False,
        }
        self.mock_db.update_webhook.return_value = expected_webhook

        # Act
        result = self.webhook_service.update_webhook(webhook_id, update_data)

        # Assert
        self.assertEqual(result, expected_webhook)
        self.mock_db.update_webhook.assert_called_once_with(webhook_id, update_data)

    def test_update_nonexistent_webhook(self):
        """Test updating a webhook that doesn't exist."""
        # Arrange
        webhook_id = "webhook-nonexistent"
        update_data = {"description": "Updated description"}
        self.mock_db.update_webhook.return_value = None

        # Act
        result = self.webhook_service.update_webhook(webhook_id, update_data)

        # Assert
        self.assertIsNone(result)
        self.mock_db.update_webhook.assert_called_once_with(webhook_id, update_data)

    def test_delete_webhook(self):
        """Test deleting a webhook."""
        # Arrange
        webhook_id = "webhook-123"
        self.mock_db.delete_webhook.return_value = True

        # Act
        result = self.webhook_service.delete_webhook(webhook_id)

        # Assert
        self.assertTrue(result)
        self.mock_db.delete_webhook.assert_called_once_with(webhook_id)

    def test_delete_nonexistent_webhook(self):
        """Test deleting a webhook that doesn't exist."""
        # Arrange
        webhook_id = "webhook-nonexistent"
        self.mock_db.delete_webhook.return_value = False

        # Act
        result = self.webhook_service.delete_webhook(webhook_id)

        # Assert
        self.assertFalse(result)
        self.mock_db.delete_webhook.assert_called_once_with(webhook_id)

    @patch("api.services.webhook_service.requests")
    def test_deliver_webhook(self, mock_requests):
        """Test delivering a webhook."""
        # Arrange
        webhook = {
            "id": "webhook-123",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "headers": {"Authorization": "Bearer test-token"},
            "secret": "whsec_test_secret",
        }
        event_data = {
            "type": "user.created",
            "data": {"user_id": "user-123", "username": "testuser"},
        }

        # Mock the requests.post response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_requests.post.return_value = mock_response

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        self.assertTrue(result)
        mock_requests.post.assert_called_once()
        # Verify the URL was correct
        self.assertEqual(mock_requests.post.call_args[0][0], webhook["url"])
        # Verify headers were passed correctly
        headers = mock_requests.post.call_args[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertIn("X-Webhook-Signature", headers)

    @patch("api.services.webhook_service.requests")
    def test_deliver_webhook_timeout(self, mock_requests):
        """Test webhook delivery with timeout."""
        # Arrange
        webhook = {
            "id": "webhook-123",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
        }
        event_data = {"type": "user.created", "data": {}}
        mock_requests.post.side_effect = Timeout("Connection timed out")

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        self.assertFalse(result)
        mock_requests.post.assert_called_once()

    @patch("api.services.webhook_service.requests")
    def test_deliver_webhook_connection_error(self, mock_requests):
        """Test webhook delivery with connection error."""
        # Arrange
        webhook = {
            "id": "webhook-123",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
        }
        event_data = {"type": "user.created", "data": {}}
        mock_requests.post.side_effect = RequestException("Connection failed")

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        self.assertFalse(result)
        mock_requests.post.assert_called_once()

    @patch("api.services.webhook_service.requests")
    def test_deliver_webhook_error_response(self, mock_requests):
        """Test webhook delivery with error response."""
        # Arrange
        webhook = {
            "id": "webhook-123",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
        }
        event_data = {"type": "user.created", "data": {}}
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests.post.return_value = mock_response

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        self.assertFalse(result)
        mock_requests.post.assert_called_once()

    def test_process_event(self):
        """Test processing an event."""
        # Arrange
        event_type = "user.created"
        event_data = {"user_id": "123", "username": "testuser"}
        webhooks = [
            {
                "id": "webhook-1",
                "url": "https://example1.com/webhook",
                "events": ["user.created"],
            },
            {
                "id": "webhook-2",
                "url": "https://example2.com/webhook",
                "events": ["user.created"],
            },
        ]
        self.mock_db.find_webhooks_by_event.return_value = webhooks

        # Mock the deliver_webhook method
        self.webhook_service.deliver_webhook = MagicMock(return_value=True)

        # Act
        result = self.webhook_service.process_event(event_type, event_data)

        # Assert
        self.assertEqual(result, 2)  # Both webhooks should be delivered successfully
        self.mock_db.find_webhooks_by_event.assert_called_once_with(event_type, active_only=True)
        self.assertEqual(self.webhook_service.deliver_webhook.call_count, 2)

    def test_process_event_partial_success(self):
        """Test processing an event with partial delivery success."""
        # Arrange
        event_type = "user.created"
        event_data = {"user_id": "123", "username": "testuser"}
        webhooks = [
            {"id": "webhook-1", "url": "https://example1.com/webhook"},
            {"id": "webhook-2", "url": "https://example2.com/webhook"},
        ]
        self.mock_db.find_webhooks_by_event.return_value = webhooks

        # Mock deliver_webhook to succeed for first webhook and fail for second
        self.webhook_service.deliver_webhook = MagicMock(side_effect=[True, False])

        # Act
        result = self.webhook_service.process_event(event_type, event_data)

        # Assert
        self.assertEqual(result, 1)  # Only one webhook should be delivered successfully
        self.assertEqual(self.webhook_service.deliver_webhook.call_count, 2)

    def test_process_event_no_webhooks(self):
        """Test processing an event with no matching webhooks."""
        # Arrange
        event_type = "user.created"
        event_data = {"user_id": "123"}
        self.mock_db.find_webhooks_by_event.return_value = []

        # Act
        result = self.webhook_service.process_event(event_type, event_data)

        # Assert
        self.assertEqual(result, 0)
        self.mock_db.find_webhooks_by_event.assert_called_once_with(event_type, active_only=True)

    def test_process_event_without_db(self):
        """Test processing an event without a database connection."""
        # Arrange
        webhook_service = WebhookService(db=None)
        event_type = "user.created"
        event_data = {"user_id": "123"}

        # Act
        result = webhook_service.process_event(event_type, event_data)

        # Assert
        self.assertEqual(result, 0)
