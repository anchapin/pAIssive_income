"""Test the user API endpoints with the ORM/database."""

from unittest.mock import patch

# Import constants
from tests.constants import HTTP_CREATED, HTTP_OK

# The app and client fixtures are imported from conftest.py


def test_create_and_authenticate_user(client):
    # Mock the user service to avoid database interactions
    with patch("api.routes.user_router.user_service") as mock_service:
        # Set up the mock for create_user
        mock_service.create_user.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com",
        }

        # Set up the mock for authenticate_user
        mock_service.authenticate_user.return_value = (
            True,
            {
                "id": 1,
                "username": "testuser",
                "email": "testuser@example.com",
            },
        )

        # Set up the mock for generate_token
        mock_service.generate_token.return_value = "test-token"

        # Create a user
        response = client.post(
            "/api/users/",
            json={
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpassword",
            },
        )
        assert response.status_code == HTTP_CREATED
        data = response.get_json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"

        # Authenticate the user
        response = client.post(
            "/api/users/authenticate",
            json={"username_or_email": "testuser", "password": "testpassword"},
        )
        assert response.status_code == HTTP_OK
        user_data = response.get_json()
        assert user_data["username"] == "testuser"
        assert user_data["email"] == "testuser@example.com"
