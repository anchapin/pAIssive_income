"""Test module for api.routes.user_router."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes.user_router import router


@pytest.fixture
def app():
    """Create a FastAPI app with the user_router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestUserRouter:
    """Test suite for user_router."""

    @patch("api.routes.user_router.get_user_by_id")
    def test_get_user(self, mock_get_user, client):
        """Test GET /users/{user_id} endpoint."""
        # Mock the get_user_by_id function
        mock_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True
        }
        mock_get_user.return_value = mock_user

        # Send request
        response = client.get("/users/1")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data == mock_user
        mock_get_user.assert_called_once_with(1)

    @patch("api.routes.user_router.get_user_by_id")
    def test_get_user_not_found(self, mock_get_user, client):
        """Test GET /users/{user_id} endpoint with non-existing user."""
        # Mock the get_user_by_id function to return None
        mock_get_user.return_value = None

        # Send request
        response = client.get("/users/999")

        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_get_user.assert_called_once_with(999)

    @patch("api.routes.user_router.get_users")
    def test_get_users(self, mock_get_users, client):
        """Test GET /users endpoint."""
        # Mock the get_users function
        mock_users = [
            {
                "id": 1,
                "username": "user1",
                "email": "user1@example.com",
                "is_active": True
            },
            {
                "id": 2,
                "username": "user2",
                "email": "user2@example.com",
                "is_active": False
            }
        ]
        mock_get_users.return_value = mock_users

        # Send request
        response = client.get("/users")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data == mock_users
        mock_get_users.assert_called_once()

    @patch("api.routes.user_router.create_user")
    def test_create_user(self, mock_create_user, client):
        """Test POST /users endpoint."""
        # Mock the create_user function
        mock_user = {
            "id": 1,
            "username": "newuser",
            "email": "newuser@example.com",
            "is_active": True
        }
        mock_create_user.return_value = mock_user

        # User data to send
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!"
        }

        # Send request
        response = client.post("/users", json=user_data)

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data == mock_user
        mock_create_user.assert_called_once_with(user_data)

    @patch("api.routes.user_router.update_user")
    def test_update_user(self, mock_update_user, client):
        """Test PUT /users/{user_id} endpoint."""
        # Mock the update_user function
        mock_user = {
            "id": 1,
            "username": "updateduser",
            "email": "updated@example.com",
            "is_active": True
        }
        mock_update_user.return_value = mock_user

        # User data to send
        user_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }

        # Send request
        response = client.put("/users/1", json=user_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data == mock_user
        mock_update_user.assert_called_once_with(1, user_data)

    @patch("api.routes.user_router.update_user")
    def test_update_user_not_found(self, mock_update_user, client):
        """Test PUT /users/{user_id} endpoint with non-existing user."""
        # Mock the update_user function to return None
        mock_update_user.return_value = None

        # User data to send
        user_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }

        # Send request
        response = client.put("/users/999", json=user_data)

        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_update_user.assert_called_once_with(999, user_data)

    @patch("api.routes.user_router.delete_user")
    def test_delete_user(self, mock_delete_user, client):
        """Test DELETE /users/{user_id} endpoint."""
        # Mock the delete_user function
        mock_delete_user.return_value = True

        # Send request
        response = client.delete("/users/1")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
        mock_delete_user.assert_called_once_with(1)

    @patch("api.routes.user_router.delete_user")
    def test_delete_user_not_found(self, mock_delete_user, client):
        """Test DELETE /users/{user_id} endpoint with non-existing user."""
        # Mock the delete_user function to return False
        mock_delete_user.return_value = False

        # Send request
        response = client.delete("/users/999")

        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_delete_user.assert_called_once_with(999)
