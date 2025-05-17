"""
Example of using the slow test marker.

This module demonstrates how to use the @pytest.mark.slow decorator to mark tests
that take a long time to run. These tests can be skipped during regular development
to speed up the test suite.

To run all tests including slow tests:
    pytest

To run tests excluding slow tests:
    pytest -m "not slow"
"""

import time

import pytest


def test_fast_function():
    """Run a fast test that should always execute."""
    # This test is fast and should always run
    expected_result = 2
    result = 1 + 1
    assert result == expected_result


@pytest.mark.slow
def test_slow_function():
    """
    Run a slow test that can be skipped during regular development.

    This test is marked with @pytest.mark.slow, which means it can be skipped
    when running tests with the -m "not slow" option.
    """
    # Simulate a slow operation (e.g., network request, database query)
    time.sleep(2)  # Sleep for 2 seconds to simulate a slow operation

    # Actual test logic
    expected_result = 42
    result = complex_calculation()
    assert result == expected_result


@pytest.mark.slow
def test_another_slow_function():
    """
    Run another example of a slow test.

    This test also performs a time-consuming operation and should be skipped
    during regular development.
    """
    # Simulate another slow operation
    time.sleep(1.5)  # Sleep for 1.5 seconds

    # Actual test logic
    list_size = 1000000
    result = list(range(list_size))  # Create a large list
    assert len(result) == list_size


def complex_calculation():
    """Simulate a complex calculation."""
    # Simulate a complex calculation
    total = 0
    iterations = 1000000
    for i in range(iterations):
        total += i

    # Return a fixed value for testing purposes
    return 42


if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-v", __file__])
