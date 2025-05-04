
from api.schemas.webhook import WebhookRequest

data = {"url": "https://example.com / webhook", "events": ["invalid.event"], 
    "is_active": True}

try:
    WebhookRequest(**data)
    print("Test failed - invalid event type should be rejected")
except Exception as e:
    print("Test passed - invalid event type rejected as expected")
    print(f"Error: {str(e)}")
