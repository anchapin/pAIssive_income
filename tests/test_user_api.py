"""Test the user API endpoints with the ORM/database."""

# The app and client fixtures are imported from conftest.py

# Import constants
from tests.constants import HTTP_CREATED, HTTP_OK


def test_create_and_authenticate_user(client):
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
