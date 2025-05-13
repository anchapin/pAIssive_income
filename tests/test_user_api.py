"""Test the user API endpoints with the ORM/database."""

import pytest

# The app and client fixtures are imported from conftest.py


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
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

    # Authenticate the user
    response = client.post(
        "/api/users/authenticate",
        json={"username_or_email": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "testuser@example.com"
