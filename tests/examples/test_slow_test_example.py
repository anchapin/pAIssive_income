"""test_slow_test_example - Example of using the slow test marker.

This module demonstrates how to use the @pytest.mark.slow decorator to mark tests
that take a long time to run. These tests can be skipped during regular development
to speed up the test suite.

To run all tests including slow tests:
    pytest

To run tests excluding slow tests:
    pytest -m "not slow"
"""

import pytest
import time


def test_fast_function():
    """This is a fast test that should always run."""
    # This test is fast and should always run
    result = 1 + 1
    assert result == 2


@pytest.mark.slow
def test_slow_function():
    """This is a slow test that can be skipped during regular development.
    
    This test is marked with @pytest.mark.slow, which means it can be skipped
    when running tests with the -m "not slow" option.
    """
    # Simulate a slow operation (e.g., network request, database query)
    time.sleep(2)  # Sleep for 2 seconds to simulate a slow operation
    
    # Actual test logic
    result = complex_calculation()
    assert result == 42


@pytest.mark.slow
def test_another_slow_function():
    """Another example of a slow test.
    
    This test also performs a time-consuming operation and should be skipped
    during regular development.
    """
    # Simulate another slow operation
    time.sleep(1.5)  # Sleep for 1.5 seconds
    
    # Actual test logic
    result = [i for i in range(1000000)]  # Create a large list
    assert len(result) == 1000000


def complex_calculation():
    """A function that simulates a complex calculation."""
    # Simulate a complex calculation
    total = 0
    for i in range(1000000):
        total += i
    
    # Return a fixed value for testing purposes
    return 42


if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-v", __file__])
