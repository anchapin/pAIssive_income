"""
Test script for webhook service.
"""


import asyncio
from datetime import datetime, timezone

import pytest

from api.schemas.webhook import WebhookEventType
from api.services.webhook_service import WebhookService


@pytest.mark.asyncio  # Mark the test function to use pytest-asyncio
async def test_webhook_service():
    """Test the webhook service."""
    # Create a webhook service
    service = WebhookService()

# Start the service
    await service.start()

try:
        # Register a webhook
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": [
                WebhookEventType.USER_CREATED,
                WebhookEventType.PAYMENT_RECEIVED,
            ],
            "description": "Test webhook",
            "headers": {"Authorization": "Bearer test-token"},
            "is_active": True,
        }

webhook = await service.register_webhook(webhook_data)
        print(f"Registered webhook: {webhook['id']}")

# List webhooks
        webhooks = await service.list_webhooks()
        print(f"Found {len(webhooks)} webhooks")

# Get webhook
        retrieved_webhook = await service.get_webhook(webhook["id"])
        print(f"Retrieved webhook: {retrieved_webhook['id']}")

# Update webhook
        updated_data = {"description": "Updated test webhook", "is_active": False}

updated_webhook = await service.update_webhook(webhook["id"], updated_data)
        print(
            f"Updated webhook: {updated_webhook['description']}, active: {updated_webhook['is_active']}"
        )

# Reactivate webhook for delivery test
        await service.update_webhook(webhook["id"], {"is_active": True})

# Try to deliver an event
        try:
            event_data = {
                "user_id": "user-123",
                "username": "testuser",
                "email": "test@example.com",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

delivery = await service.deliver_event(
                webhook_id=webhook["id"],
                event_type=WebhookEventType.USER_CREATED,
                event_data=event_data,
            )

print(f"Delivery status: {delivery['status']}")
            print(f"Delivery attempts: {len(delivery['attempts'])}")

# Get deliveries
            deliveries = await service.get_deliveries(webhook["id"])
            print(f"Found {len(deliveries)} deliveries")

except Exception as e:
            print(f"Error delivering event: {str(e)}")

# Delete webhook
        deleted = await service.delete_webhook(webhook["id"])
        print(f"Webhook deleted: {deleted}")

finally:
        # Stop the service
        await service.stop()


if __name__ == "__main__":
    asyncio.run(test_webhook_service())