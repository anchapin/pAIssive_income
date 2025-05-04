import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath("."))

print("Testing imports for test modules...")

# Test importing from test modules
try:

    print("Successfully imported mock_ai_model_testing_setup")
except ImportError as e:
    print(f"Error importing mock_ai_model_testing_setup: {e}")

try:

    print("Successfully imported create_mock_provider")
except ImportError as e:
    print(f"Error importing create_mock_provider: {e}")

try:

    print("Successfully imported temp_dir")
except ImportError as e:
    print(f"Error importing temp_dir: {e}")

try:
        test_workflow_with_compensating_actions,
    )

    print("Successfully imported test_workflow_with_compensating_actions")
except ImportError as e:
    print(f"Error importing test_workflow_with_compensating_actions: {e}")

print("Import tests completed.")
