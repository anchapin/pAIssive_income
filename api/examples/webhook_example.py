"""
Webhook example for the pAIssive Income API.

This example demonstrates how to register webhooks and emit events.
"""


import asyncio
import json

from ..config import WebhookEventType
from ..services.event_emitter import EventEmitter
from ..services.webhook_service import WebhookService


async def register_webhook_example
    import hashlib
    import hmac

():
    """Example of registering a webhook."""

    # Get webhook service
    webhook_service = WebhookService()

    # Register a webhook
    webhook = await webhook_service.register_webhook(
        url="https://webhook.example.com/receive",
        events=[
            WebhookEventType.NICHE_ANALYSIS_CREATED,
            WebhookEventType.OPPORTUNITY_SCORED,
            WebhookEventType.MONETIZATION_PLAN_CREATED,
        ],
        description="Example webhook for niche analysis and monetization events",
        # Optional secret for signature verification
        secret="your-webhook-secret",
    )

    print("Webhook registered:")
    print(json.dumps(webhook, indent=2))

    return webhook


async def emit_event_example():
    """Example of emitting an event."""

    # Get event emitter
    event_emitter = EventEmitter()

    # Emit a niche analysis created event
    analysis_id = "na_12345"
    analysis_data = {
        "id": analysis_id,
        "name": "Example Niche Analysis",
        "niche": "AI-powered productivity tools",
        "keywords": ["AI assistant", "productivity", "automation"],
        "competition": {"level": "medium", "major_competitors": 5},
        "opportunity_score": 8.7,
        "created_at": "2025-04-28T12:00:00Z",
    }

    # Register a local event listener
    def on_niche_analysis_created(data):
        print("Local listener received niche analysis created event:")
        print(json.dumps(data, indent=2))

    # Register the listener
    unsubscribe = event_emitter.on(
        WebhookEventType.NICHE_ANALYSIS_CREATED, on_niche_analysis_created
    )

    # Emit the event
    listeners_count = await event_emitter.emit_niche_analysis_created(
        analysis_id=analysis_id, analysis_data=analysis_data
    )

    print(f"Event emitted to {listeners_count} local listeners")
    print("Event also sent to all registered webhooks subscribed to this event")

    # Unsubscribe the listener when done
    unsubscribe()


async def verify_webhook_signature_example():
    """Example of verifying a webhook signature."""

    # This would be the raw payload received by your webhook endpoint
    raw_payload = '{"event":"niche_analysis.created","timestamp":"2025-04-28T12:00:00Z","data":{"analysis_id":"na_12345"}}'

    # The signature from the X-Webhook-Signature header
    signature = (
        "abcdef1234567890"  # This would be the actual signature from the request
    )

    # Your webhook secret
    secret = "your-webhook-secret"

    # Verify the signature



    expected_signature = hmac.new(
        secret.encode("utf-8"), raw_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(signature, expected_signature)

    print(f"Signature is {'valid' if is_valid else 'invalid'}")


async def main():
    """Run the webhook examples."""

    print("=== Webhook Registration Example ===")
    await register_webhook_example()

    print("\n=== Event Emission Example ===")
    await emit_event_example()

    print("\n=== Webhook Signature Verification Example ===")
    await verify_webhook_signature_example()


if __name__ == "__main__":
    asyncio.run(main())