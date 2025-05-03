import sys

print("Python path:", sys.path)

try:
    from errors import NicheAnalysisError

    print("Successfully imported NicheAnalysisError")
except ImportError as e:
    print(f"Error importing NicheAnalysisError: {e}")

try:
    import pytest

    from api.schemas.webhook import WebhookEventType, WebhookRequest, WebhookUpdate

    print("Successfully imported WebhookRequest, WebhookEventType, WebhookUpdate")
except ImportError as e:
    print(f"Error importing webhook modules: {e}")
