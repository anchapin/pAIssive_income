import pytest

from api.schemas.webhook import WebhookEventType, WebhookRequest, WebhookUpdate

data = {}  # Empty update payload

try:
    webhook_update = WebhookUpdate(**data)
    print("Test passed - empty update payload accepted")
    print(f"URL: {webhook_update.url}")
    print(f"Events: {webhook_update.events}")
    print(f"Description: {webhook_update.description}")
    print(f"Headers: {webhook_update.headers}")
    print(f"Is active: {webhook_update.is_active}")
except Exception as e:
    print("Test failed - empty update payload should be accepted")
    print(f"Error: {str(e)}")
