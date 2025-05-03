from pydantic import ValidationError

from api.schemas.webhook import WebhookRequest, WebhookUpdate




# Test empty events list in WebhookRequest
def test_webhook_request_empty_events():
    data = {"url": "https://example.com/webhook", "events": [], "is_active": True}

try:
        WebhookRequest(**data)
        print("Test failed - empty events list should be rejected")
    except ValidationError as e:
        print("Test passed - empty events list rejected as expected")
        print(f"Error: {str(e)}")


# Test empty events list in WebhookUpdate
def test_webhook_update_empty_events():
    data = {"events": []}

try:
        WebhookUpdate(**data)
        print("Test failed - empty events list should be rejected")
    except ValidationError as e:
        print("Test passed - empty events list rejected as expected")
        print(f"Error: {str(e)}")


# Test null events list in WebhookUpdate (should be allowed)
def test_webhook_update_null_events():
    data = {"url": "https://example.com/webhook", "events": None}

try:
        update = WebhookUpdate(**data)
        print("Test passed - null events list accepted as expected")
        print(f"Events: {update.events}")
    except ValidationError as e:
        print("Test failed - null events list should be accepted")
        print(f"Error: {str(e)}")


# Run the tests
if __name__ == "__main__":
    print("Testing WebhookRequest with empty events list:")
    test_webhook_request_empty_events()

print("\nTesting WebhookUpdate with empty events list:")
    test_webhook_update_empty_events()

print("\nTesting WebhookUpdate with null events list:")
    test_webhook_update_null_events()