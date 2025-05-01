#!/usr/bin/env python
"""
Run advanced security tests for the pAIssive income platform.

This script runs the advanced security tests for authentication and authorization
edge cases as recommended in the security testing section.
"""

import unittest
import sys
from tests.security.test_advanced_authentication import TestAdvancedAuthentication
from tests.security.test_authorization_edge_cases import TestAuthorizationEdgeCases


def run_tests():
    """Run the advanced security tests."""
    print("Running advanced security tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAdvancedAuthentication))
    test_suite.addTest(unittest.makeSuite(TestAuthorizationEdgeCases))
    
    try:
        # Run tests
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        
        # Print summary
        print(f"\nTest Summary:")
        print(f"  Ran {result.testsRun} tests")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Skipped: {len(result.skipped)}")
        
        # Return exit code
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"\nError: Unexpected exception occurred during test execution:")
        print(f"  {type(e).__name__}: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
