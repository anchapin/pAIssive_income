"""test_webhook_service - Module for testing webhook service functionality."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests

from api.services.webhook_service import WebhookService


class MockDB:
    """Mock database for testing."""

    def __init__(self):
        self.webhooks = {}

    def add_webhook(self, webhook_data):
        webhook_id = webhook_data.get("id", f"webhook-{len(self.webhooks) + 1}")
        self.webhooks[webhook_id] = webhook_data
        return webhook_data

    def get_webhook(self, webhook_id):
        return self.webhooks.get(webhook_id)

    def list_webhooks(self, filters=None):
        return list(self.webhooks.values())

    def update_webhook(self, webhook_id, update_data):
        if webhook_id in self.webhooks:
            self.webhooks[webhook_id].update(update_data)
            return self.webhooks[webhook_id]
        return None

    def delete_webhook(self, webhook_id):
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            return True
        return False

    def find_webhooks_by_event(self, event_type, active_only=True):
        return [
            webhook for webhook in self.webhooks.values()
            if event_type in webhook.get("events", [])
            and (not active_only or webhook.get("is_active", True))
        ]


@pytest.fixture
def webhook_service():
    """Create a webhook service instance with a mock database."""
    db = MockDB()
    return WebhookService(db)


@pytest.fixture
def sample_webhook_data():
    """Sample webhook data for testing."""
    return {
        "url": "https://example.com/webhook",
        "events": ["user.created", "user.updated"],
        "description": "Test webhook",
        "headers": {"X-Custom-Header": "test"},
        "is_active": True,
    }


def test_register_webhook(webhook_service, sample_webhook_data):
    """Test registering a new webhook."""
    webhook = webhook_service.register_webhook(sample_webhook_data)

    assert webhook["url"] == sample_webhook_data["url"]
    assert webhook["events"] == sample_webhook_data["events"]
    assert webhook["description"] == sample_webhook_data["description"]
    assert webhook["headers"] == sample_webhook_data["headers"]
    assert webhook["is_active"] == sample_webhook_data["is_active"]
    assert "id" in webhook
    assert "secret" in webhook
    assert "created_at" in webhook


def test_register_webhook_missing_url(webhook_service):
    """Test registering a webhook without a URL."""
    with pytest.raises(ValueError):
        webhook_service.register_webhook({"events": ["user.created"]})


def test_get_webhook(webhook_service, sample_webhook_data):
    """Test retrieving a webhook by ID."""
    webhook = webhook_service.register_webhook(sample_webhook_data)
    retrieved = webhook_service.get_webhook(webhook["id"])

    assert retrieved == webhook


def test_get_nonexistent_webhook(webhook_service):
    """Test retrieving a non-existent webhook."""
    assert webhook_service.get_webhook("nonexistent") is None


def test_list_webhooks(webhook_service, sample_webhook_data):
    """Test listing all webhooks."""
    webhook1 = webhook_service.register_webhook(sample_webhook_data)
    webhook2 = webhook_service.register_webhook({
        **sample_webhook_data,
        "url": "https://example.com/webhook2"
    })

    webhooks = webhook_service.list_webhooks()
    assert len(webhooks) == 2
    assert webhook1 in webhooks
    assert webhook2 in webhooks


def test_update_webhook(webhook_service, sample_webhook_data):
    """Test updating a webhook."""
    webhook = webhook_service.register_webhook(sample_webhook_data)
    update_data = {
        "description": "Updated description",
        "is_active": False
    }

    updated = webhook_service.update_webhook(webhook["id"], update_data)
    assert updated["description"] == update_data["description"]
    assert updated["is_active"] == update_data["is_active"]


def test_delete_webhook(webhook_service, sample_webhook_data):
    """Test deleting a webhook."""
    webhook = webhook_service.register_webhook(sample_webhook_data)
    assert webhook_service.delete_webhook(webhook["id"]) is True
    assert webhook_service.get_webhook(webhook["id"]) is None


@patch("requests.post")
def test_deliver_webhook_success(mock_post, webhook_service, sample_webhook_data):
    """Test successful webhook delivery."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    webhook = webhook_service.register_webhook(sample_webhook_data)
    event_data = {"user_id": "123", "action": "created"}

    assert webhook_service.deliver_webhook(webhook, event_data) is True
    mock_post.assert_called_once()


@patch("requests.post")
def test_deliver_webhook_failure(mock_post, webhook_service, sample_webhook_data):
    """Test failed webhook delivery."""
    mock_post.side_effect = requests.RequestException()

    webhook = webhook_service.register_webhook(sample_webhook_data)
    event_data = {"user_id": "123", "action": "created"}

    assert webhook_service.deliver_webhook(webhook, event_data) is False


def test_process_event(webhook_service, sample_webhook_data):
    """Test processing an event and delivering to matching webhooks."""
    webhook = webhook_service.register_webhook(sample_webhook_data)
    event_type = "user.created"
    event_data = {"user_id": "123", "action": "created"}

    with patch.object(webhook_service, "deliver_webhook", return_value=True):
        success_count = webhook_service.process_event(event_type, event_data)
        assert success_count == 1


def test_process_event_no_matching_webhooks(webhook_service):
    """Test processing an event with no matching webhooks."""
    event_type = "nonexistent.event"
    event_data = {"user_id": "123", "action": "created"}

    success_count = webhook_service.process_event(event_type, event_data)
    assert success_count == 0
