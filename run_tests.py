"""
Script to run the webhook tests.
"""

import pytest
import sys

if __name__ == "__main__":
    print("Running webhook schema tests...")
    schema_result = pytest.main(["-v", "tests/api/test_webhook_schema.py"])
    
    print("\nRunning webhook schema edge case tests...")
    edge_case_result = pytest.main(["-v", "tests/api/test_webhook_schema_edge_cases.py"])
    
    print("\nRunning webhook delivery integration tests...")
    integration_result = pytest.main(["-v", "tests/api/test_webhook_delivery_integration.py"])
    
    print("\nRunning webhook error handling tests...")
    error_handling_result = pytest.main(["-v", "tests/api/test_webhook_error_handling.py"])
    
    # Summarize results
    print("\n=== Test Results Summary ===")
    print(f"Schema tests: {'PASSED' if schema_result == 0 else 'FAILED'}")
    print(f"Edge case tests: {'PASSED' if edge_case_result == 0 else 'FAILED'}")
    print(f"Integration tests: {'PASSED' if integration_result == 0 else 'FAILED'}")
    print(f"Error handling tests: {'PASSED' if error_handling_result == 0 else 'FAILED'}")
    
    # Exit with appropriate code
    if all(result == 0 for result in [schema_result, edge_case_result, integration_result, error_handling_result]):
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed. See details above.")
        sys.exit(1)
