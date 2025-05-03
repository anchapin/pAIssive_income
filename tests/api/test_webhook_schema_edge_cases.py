"""
Tests for edge cases in webhook schema validation.
"""

import pytest
from pydantic import ValidationError

from api.schemas.webhook import WebhookEventType, WebhookRequest, WebhookUpdate


def test_webhook_request_empty_events():
    """Test that webhook request with empty events list is rejected."""
    invalid_data = {"url": "https://example.com / webhook", "events": [], "is_active": True}
    with pytest.raises(ValidationError) as excinfo:
        WebhookRequest(**invalid_data)
    assert "events list cannot be empty" in str(excinfo.value)


def test_webhook_request_invalid_event_type():
    """Test that webhook request with invalid event type is rejected."""
    invalid_data = {
        "url": "https://example.com / webhook",
        "events": ["invalid.event"],
        "is_active": True,
    }
    with pytest.raises(ValidationError):
        WebhookRequest(**invalid_data)


def test_webhook_request_with_max_length_description():
    """Test webhook request with very long description."""
    valid_data = {
        "url": "https://example.com / webhook",
        "events": [WebhookEventType.USER_CREATED],
        "description": "a" * 1000,  # Very long description
        "is_active": True,
    }
    webhook = WebhookRequest(**valid_data)
    assert len(webhook.description) == 1000
    assert webhook.is_active is True


def test_webhook_update_empty_payload():
    """Test that webhook update with empty payload is valid."""
    update_data = {}
    webhook_update = WebhookUpdate(**update_data)
    assert webhook_update.url is None
    assert webhook_update.events is None
    assert webhook_update.description is None
    assert webhook_update.headers is None
    assert webhook_update.is_active is None


def test_webhook_update_empty_events():
    """Test that webhook update with empty events list is rejected."""
    invalid_data = {"events": []}
    with pytest.raises(ValidationError) as excinfo:
        WebhookUpdate(**invalid_data)
    assert "events list cannot be empty" in str(excinfo.value)


def test_webhook_update_null_events():
    """Test that webhook update with null events is accepted."""
    valid_data = {"url": "https://example.com / webhook", "events": None}
    webhook_update = WebhookUpdate(**valid_data)
    assert webhook_update.events is None


def test_webhook_request_with_complex_headers():
    """Test webhook request with complex headers structure."""
    valid_data = {
        "url": "https://example.com / webhook",
        "events": [WebhookEventType.USER_CREATED],
        "headers": {
            "Authorization": "Bearer token",
            "X - Custom - Header": "custom - value",
            "Content - Type": "application / json",
            "Accept": "application / json",
        },
        "is_active": True,
    }
    webhook = WebhookRequest(**valid_data)
    assert len(webhook.headers) == 4
    assert webhook.headers["Authorization"] == "Bearer token"
    assert webhook.headers["X - Custom - Header"] == "custom - value"
