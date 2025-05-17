"""test_mocking_example - Example of mocking external dependencies in tests.

This module demonstrates how to use mocking to replace external dependencies
in tests, which can significantly speed up test execution by avoiding actual
network requests, database queries, or other slow operations.

Mocking is especially useful for:
1. Avoiding network requests in tests
2. Simulating different responses from external services
3. Testing error handling without actually causing errors
4. Speeding up tests by replacing slow operations with fast mocks
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
import time


# Example function that makes an external API call
def fetch_user_data(user_id):
    """Fetch user data from an external API.

    Args:
        user_id: The ID of the user to fetch

    Returns:
        dict: User data
    """
    # This would normally make a real API request
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


# Example function that uses a database
def get_user_from_database(user_id):
    """Get user data from a database.

    Args:
        user_id: The ID of the user to fetch

    Returns:
        dict: User data
    """
    # This would normally query a real database
    # Simulate a slow database query
    time.sleep(2)

    # Return dummy data for this example
    return {
        "id": user_id,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }


# Example test that mocks an HTTP request
@patch("requests.get")
def test_fetch_user_data_with_mock(mock_get):
    """Test fetch_user_data using a mock for requests.get.

    This test demonstrates how to mock an HTTP request to avoid making
    actual network calls during testing.
    """
    # Configure the mock to return a specific response
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 123, "name": "John Doe"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call the function that would normally make an HTTP request
    result = fetch_user_data(123)

    # Verify the result
    assert result == {"id": 123, "name": "John Doe"}

    # Verify that the mock was called with the expected arguments
    mock_get.assert_called_once_with("https://api.example.com/users/123")


# Example test that uses monkeypatch (an alternative to patch)
def test_fetch_user_data_with_monkeypatch(monkeypatch):
    """Test fetch_user_data using monkeypatch.

    This test demonstrates how to use pytest's monkeypatch fixture to
    replace functions or attributes during testing.
    """
    # Create a mock response
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

        def raise_for_status(self):
            pass

    # Define a replacement for requests.get
    def mock_get(url):
        return MockResponse({"id": 456, "name": "Jane Smith"})

    # Apply the monkeypatch
    monkeypatch.setattr(requests, "get", mock_get)

    # Call the function
    result = fetch_user_data(456)

    # Verify the result
    assert result == {"id": 456, "name": "Jane Smith"}


# Example test that mocks a slow database operation
def test_database_operation_with_mock():
    """Test a database operation using a mock.

    This test demonstrates how to mock a slow database operation to
    speed up test execution.
    """
    # Create a backup of the original function
    original_function = get_user_from_database

    try:
        # Replace the function with a mock
        get_user_from_database_mock = MagicMock()
        get_user_from_database_mock.return_value = {
            "id": 789,
            "name": "Alice Johnson",
            "email": "alice@example.com"
        }

        # Replace the original function with our mock
        globals()["get_user_from_database"] = get_user_from_database_mock

        # Call the function that would normally access the database
        result = get_user_from_database(789)

        # Verify the result
        assert result["id"] == 789
        assert result["name"] == "Alice Johnson"

        # Verify that the mock was called with the expected arguments
        get_user_from_database_mock.assert_called_once_with(789)
    finally:
        # Restore the original function
        globals()["get_user_from_database"] = original_function


if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-v", __file__])
