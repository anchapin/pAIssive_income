import pytest
from pydantic import ValidationError

from api.schemas.webhook import WebhookEventType, WebhookRequest


def test_webhook_request_schema_valid():
    valid_data = {
        "url": "https://example.com/webhook",
        "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
        "description": "Test webhook",
        "headers": {"Authorization": "Bearer token"},
        "is_active": True,
    }
    webhook = WebhookRequest(**valid_data)
    assert str(webhook.url) == "https://example.com/webhook"
    assert len(webhook.events) == 2
    assert webhook.is_active is True


def test_webhook_request_schema_invalid_url():
    invalid_data = {
        "url": "invalid-url",
        "events": [WebhookEventType.USER_CREATED],
        "is_active": True,
    }
    with pytest.raises(ValidationError):
        WebhookRequest(**invalid_data)


def test_webhook_request_schema_missing_fields():
    invalid_data = {"events": [WebhookEventType.USER_CREATED]}
    with pytest.raises(ValidationError):
        WebhookRequest(**invalid_data)
