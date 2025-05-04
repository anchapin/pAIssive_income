import sys

print("Python path:", sys.path)

try:

    print("Successfully imported NicheAnalysisError")
except ImportError as e:
    print(f"Error importing NicheAnalysisError: {e}")

try:

    print("Successfully imported WebhookRequest, WebhookEventType, WebhookUpdate")
except ImportError as e:
    print(f"Error importing webhook modules: {e}")
