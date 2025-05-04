from api.schemas.webhook import WebhookEventType, WebhookRequest

data = {
"url": "https://example.com/webhook",
"events": [WebhookEventType.USER_CREATED],
"headers": {
"Authorization": "Bearer token",
"X-Custom-Header": "custom-value",
"Content-Type": "application/json",
"Accept": "application/json",
},
"is_active": True,
}

try:
    webhook = WebhookRequest(**data)
    print("Test passed - complex headers accepted")
    print(f"Headers count: {len(webhook.headers)}")
    print(f'Authorization header: {webhook.headers.get("Authorization")}')
    print(f'X-Custom-Header: {webhook.headers.get("X-Custom-Header")}')
except Exception as e:
    print("Test failed - complex headers should be accepted")
    print(f"Error: {str(e)}")