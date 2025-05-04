from api.schemas.webhook import WebhookEventType, WebhookRequest

data

= {
"url": "https://example.com/webhook",
"events": [WebhookEventType.USER_CREATED],
"description": "a" * 1000,  # Very long description
"is_active": True,
}

try:
    webhook = WebhookRequest(**data)
    print("Test passed - long description accepted")
    print(f"Description length: {len(webhook.description)}")
except Exception as e:
    print("Test failed - long description should be accepted")
    print(f"Error: {str(e)}")