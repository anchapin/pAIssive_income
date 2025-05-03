"""
Script to run the data consistency tests.
"""


import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test classes
from tests.common_utils.db.test_concurrent_operations import (
    test_parallel_updates_consistency,
    test_transaction_prevents_race_conditions,
    test_transaction_isolation_levels,
    test_deadlock_prevention,
    test_concurrent_batch_operations
)

from tests.common_utils.db.test_cache_coherency import (
    test_cache_invalidation_timing,
    test_cache_update_propagation,
    test_cache_hit_miss_ratios,
    test_concurrent_cache_access,
    test_cache_invalidation_propagation,
    test_cache_persistence,
    test_cache_eviction_policy
)


def run_tests():
    """Run the data consistency tests."""
    print("Running data consistency tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add concurrent operation test cases
    test_loader = unittest.TestLoader()
    concurrent_ops_module = __import__('tests.common_utils.db.test_concurrent_operations', fromlist=['*'])
    concurrent_ops_tests = test_loader.loadTestsFromModule(concurrent_ops_module)
    test_suite.addTests(concurrent_ops_tests)
    
    # Add cache coherency test cases
    cache_coherency_module = __import__('tests.common_utils.db.test_cache_coherency', fromlist=['*'])
    cache_coherency_tests = test_loader.loadTestsFromModule(cache_coherency_module)
    test_suite.addTests(cache_coherency_tests)
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())