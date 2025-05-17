"""Tests for the webhook service."""

import json
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

import pytest
import requests
from requests.exceptions import RequestException, Timeout

from api.services.webhook_service import WebhookService


class TestWebhookService:
    """Test suite for the WebhookService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.webhook_service = WebhookService()
        self.mock_db = MagicMock()
        self.webhook_service.db = self.mock_db

    def test_register_webhook_with_db(self):
        """Test registering a webhook with a database connection."""
        # Arrange
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "is_active": True,
        }
        expected_webhook = {
            "id": "webhook-12345678",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "is_active": True,
        }
        self.mock_db.add_webhook.return_value = expected_webhook

        # Act
        result = self.webhook_service.register_webhook(webhook_data)

        # Assert
        assert result == expected_webhook
        self.mock_db.add_webhook.assert_called_once()

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
        assert "id" in result
        assert "secret" in result
        assert result["id"].startswith("webhook-")
        assert result["secret"].startswith("whsec_")
        assert result["url"] == webhook_data["url"]

    def test_register_webhook_missing_url(self):
        """Test registering a webhook without a URL."""
        # Arrange
        webhook_data = {
            "events": ["user.created"],
            "is_active": True,
        }

        # Act/Assert
        with pytest.raises(ValueError):
            self.webhook_service.register_webhook(webhook_data)

    def test_get_webhook(self):
        """Test getting a webhook by ID."""
        # Arrange
        webhook_id = "webhook-123"
        expected_webhook = {
            "id": webhook_id,
            "url": "https://example.com/webhook",
            "events": ["user.created"],
            "is_active": True,
        }
        self.mock_db.get_webhook.return_value = expected_webhook

        # Act
        result = self.webhook_service.get_webhook(webhook_id)

        # Assert
        assert result == expected_webhook
        self.mock_db.get_webhook.assert_called_once_with(webhook_id)

    def test_get_webhook_not_found(self):
        """Test getting a webhook that doesn't exist."""
        # Arrange
        webhook_id = "webhook-nonexistent"
        self.mock_db.get_webhook.return_value = None

        # Act
        result = self.webhook_service.get_webhook(webhook_id)

        # Assert
        assert result is None
        self.mock_db.get_webhook.assert_called_once_with(webhook_id)

    def test_list_webhooks(self):
        """Test listing webhooks."""
        # Arrange
        expected_webhooks = [
            {
                "id": "webhook-123",
                "url": "https://example.com/webhook1",
                "events": ["user.created"],
                "is_active": True,
            },
            {
                "id": "webhook-456",
                "url": "https://example.com/webhook2",
                "events": ["user.updated"],
                "is_active": False,
            },
        ]
        self.mock_db.list_webhooks.return_value = expected_webhooks

        # Act
        result = self.webhook_service.list_webhooks()

        # Assert
        assert result == expected_webhooks
        self.mock_db.list_webhooks.assert_called_once_with(None)

    def test_list_webhooks_with_filters(self):
        """Test listing webhooks with filters."""
        # Arrange
        filters = {"is_active": True}
        expected_webhooks = [
            {
                "id": "webhook-123",
                "url": "https://example.com/webhook1",
                "events": ["user.created"],
                "is_active": True,
            },
        ]
        self.mock_db.list_webhooks.return_value = expected_webhooks

        # Act
        result = self.webhook_service.list_webhooks(filters)

        # Assert
        assert result == expected_webhooks
        self.mock_db.list_webhooks.assert_called_once_with(filters)

    def test_update_webhook(self):
        """Test updating a webhook."""
        # Arrange
        webhook_id = "webhook-123"
        update_data = {
            "is_active": False,
            "events": ["user.created", "user.updated"],
        }
        expected_webhook = {
            "id": webhook_id,
            "url": "https://example.com/webhook",
            "events": ["user.created", "user.updated"],
            "is_active": False,
        }
        self.mock_db.update_webhook.return_value = expected_webhook

        # Act
        result = self.webhook_service.update_webhook(webhook_id, update_data)

        # Assert
        assert result == expected_webhook
        self.mock_db.update_webhook.assert_called_once_with(webhook_id, update_data)

    def test_delete_webhook(self):
        """Test deleting a webhook."""
        # Arrange
        webhook_id = "webhook-123"
        self.mock_db.delete_webhook.return_value = True

        # Act
        result = self.webhook_service.delete_webhook(webhook_id)

        # Assert
        assert result is True
        self.mock_db.delete_webhook.assert_called_once_with(webhook_id)

    @patch("api.services.webhook_service.requests.post")
    def test_deliver_webhook_success(self, mock_post):
        """Test delivering a webhook successfully."""
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
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        assert result is True
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == webhook["url"]
        assert kwargs["data"] == json.dumps(event_data)
        assert "X-Webhook-Signature" in kwargs["headers"]
        assert kwargs["headers"]["Authorization"] == "Bearer test-token"

    @patch("api.services.webhook_service.requests.post")
    def test_deliver_webhook_failure(self, mock_post):
        """Test delivering a webhook with a failure response."""
        # Arrange
        webhook = {
            "id": "webhook-123",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
        }
        event_data = {
            "type": "user.created",
            "data": {"user_id": "user-123", "username": "testuser"},
        }
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        assert result is False
        mock_post.assert_called_once()

    @patch("api.services.webhook_service.requests.post")
    def test_deliver_webhook_exception(self, mock_post):
        """Test delivering a webhook with an exception."""
        # Arrange
        webhook = {
            "id": "webhook-123",
            "url": "https://example.com/webhook",
            "events": ["user.created"],
        }
        event_data = {
            "type": "user.created",
            "data": {"user_id": "user-123", "username": "testuser"},
        }
        
        # Mock the exception
        mock_post.side_effect = RequestException("Connection error")

        # Act
        result = self.webhook_service.deliver_webhook(webhook, event_data)

        # Assert
        assert result is False
        mock_post.assert_called_once()

    def test_process_event(self):
        """Test processing an event."""
        # Arrange
        event_type = "user.created"
        event_data = {"user_id": "123"}
        webhooks = [
            {
                "id": "webhook-123",
                "url": "https://example.com/webhook1",
                "events": ["user.created"],
            },
            {
                "id": "webhook-456",
                "url": "https://example.com/webhook2",
                "events": ["user.created", "user.updated"],
            },
        ]
        self.mock_db.find_webhooks_by_event.return_value = webhooks

        # Mock the deliver_webhook method
        self.webhook_service.deliver_webhook = MagicMock(return_value=True)

        # Act
        result = self.webhook_service.process_event(event_type, event_data)

        # Assert
        assert result == 2  # Both webhooks should be delivered successfully
        self.mock_db.find_webhooks_by_event.assert_called_once_with(event_type, active_only=True)
        assert self.webhook_service.deliver_webhook.call_count == 2
