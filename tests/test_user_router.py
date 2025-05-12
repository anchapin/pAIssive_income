"""test_user_router - Test module for user router."""

import json
from typing import Any
from unittest.mock import patch

import pytest

from api.routes.user_router import user_bp
from flask import Flask
from users.services import UserExistsError


@pytest.fixture
def app() -> Flask:
    """Create a Flask app for testing.

    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    return app


@pytest.fixture
def client(app: Flask) -> Flask.test_client:
    """Create a test client.

    Args:
        app: Flask application

    Returns:
        Flask.test_client: Test client for the Flask application
    """
    return app.test_client()


def test_create_user_success(client):
    """Test creating a user successfully."""
    # Mock the UserService
    with patch("api.routes.user_router.user_service") as mock_service:
        # Set up the mock
        mock_service.create_user.return_value = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
        }

        # Make the request
        response = client.post(
            "/api/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        # Assertions
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        mock_service.create_user.assert_called_once_with(
            "testuser", "test@example.com", "password123"
        )


def test_create_user_already_exists(client):
    """Test creating a user that already exists."""
    # Mock the UserService
    with patch("api.routes.user_router.user_service") as mock_service:
        # Set up the mock to raise an exception
        mock_service.create_user.side_effect = UserExistsError("User already exists")

        # Make the request
        response = client.post(
            "/api/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        # Assertions
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "User already exists"


def test_create_user_server_error(client):
    """Test creating a user with a server error."""
    # Mock the UserService
    with patch("api.routes.user_router.user_service") as mock_service:
        # Set up the mock to raise an exception
        mock_service.create_user.side_effect = Exception("Database error")

        # Make the request
        response = client.post(
            "/api/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        # Assertions
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "An error occurred while creating the user"


def test_authenticate_user_success(client):
    """Test authenticating a user successfully."""
    # Mock the UserService
    with patch("api.routes.user_router.user_service") as mock_service:
        # Set up the mock
        mock_service.authenticate_user.return_value = (
            True,
            {"id": 1, "username": "testuser", "email": "test@example.com"},
        )

        # Make the request
        response = client.post(
            "/api/users/authenticate",
            json={"username_or_email": "testuser", "password": "password123"},
        )

        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        mock_service.authenticate_user.assert_called_once_with(
            "testuser", "password123"
        )


def test_authenticate_user_failure(client):
    """Test authenticating a user with invalid credentials."""
    # Mock the UserService
    with patch("api.routes.user_router.user_service") as mock_service:
        # Set up the mock
        mock_service.authenticate_user.return_value = (False, None)

        # Make the request
        response = client.post(
            "/api/users/authenticate",
            json={"username_or_email": "testuser", "password": "wrong_password"},
        )

        # Assertions
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "Invalid credentials"
