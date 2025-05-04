
from api.schemas.webhook import WebhookRequest

data = {"url": "https://example.com / webhook", "events": [], "is_active": True}

try:
    WebhookRequest(**data)
    print("Test failed - empty events list should be rejected")
except Exception as e:
    print("Test passed - empty events list rejected as expected")
    print(f"Error: {str(e)}")
