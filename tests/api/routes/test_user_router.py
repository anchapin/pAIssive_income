"""Test module for api.routes.user_router."""

import logging
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

    @patch("users.services.UserService.get_user_by_id")
    def test_get_user(self, mock_get_user_by_id, client):
        """Test GET /users/{user_id} endpoint."""
        mock_user = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-02T12:00:00",
        }
        mock_get_user_by_id.return_value = mock_user

        response = client.get("/users/1")

        assert response.status_code == 200
        data = response.json()
        assert data == mock_user
        mock_get_user_by_id.assert_called_once_with(1)

    @patch("users.services.UserService.get_user_by_id")
    def test_get_user_not_found(self, mock_get_user_by_id, client):
        """Test GET /users/{user_id} endpoint with non-existing user."""
        mock_get_user_by_id.return_value = None

        response = client.get("/users/999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_get_user_by_id.assert_called_once_with(999)

    @patch("users.services.UserService.get_users")
    def test_get_users(self, mock_get_users, client):
        """Test GET /users endpoint."""
        mock_users = [
            {
                "id": 1,
                "username": "user1",
                "email": "user1@example.com",
                "is_active": True,
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-02T12:00:00",
            },
            {
                "id": 2,
                "username": "user2",
                "email": "user2@example.com",
                "is_active": False,
                "created_at": "2023-01-03T12:00:00",
                "updated_at": "2023-01-04T12:00:00",
            },
        ]
        mock_get_users.return_value = mock_users

        response = client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert data == mock_users
        mock_get_users.assert_called_once()

    @patch("users.services.UserService.create_user")
    def test_create_user(self, mock_create_user, client):
        """Test POST /users endpoint."""
        mock_user = {
            "id": 1,
            "username": "newuser",
            "email": "newuser@example.com",
            "is_active": True,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-02T12:00:00",
        }
        mock_create_user.return_value = mock_user

        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!",
        }

        response = client.post("/users", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data == mock_user
        mock_create_user.assert_called_once_with(user_data)

    @patch("users.services.UserService.create_user")
    @patch("api.routes.user_router.logger")
    def test_create_user_error(self, mock_logger, mock_create_user, client):
        """Test POST /users endpoint with server error."""
        mock_create_user.side_effect = Exception("Database error")

        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!",
        }

        response = client.post("/users", json=user_data)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error occurred" in data["detail"].lower()

        mock_logger.exception.assert_called_once_with("Error creating user")

    @patch("users.services.UserService.update_user")
    def test_update_user(self, mock_update_user, client):
        """Test PUT /users/{user_id} endpoint."""
        mock_user = {
            "id": 1,
            "username": "updateduser",
            "email": "updated@example.com",
            "is_active": True,
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-02T12:00:00",
        }
        mock_update_user.return_value = mock_user

        user_data = {
            "username": "updateduser",
            "email": "updated@example.com",
        }

        response = client.put("/users/1", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data == mock_user
        mock_update_user.assert_called_once_with(1, user_data)

    @patch("users.services.UserService.update_user")
    def test_update_user_not_found(self, mock_update_user, client):
        """Test PUT /users/{user_id} endpoint with non-existing user."""
        mock_update_user.return_value = None

        user_data = {
            "username": "updateduser",
            "email": "updated@example.com",
        }

        response = client.put("/users/999", json=user_data)

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_update_user.assert_called_once_with(999, user_data)

    @patch("users.services.UserService.delete_user")
    def test_delete_user(self, mock_delete_user, client):
        """Test DELETE /users/{user_id} endpoint."""
        mock_delete_user.return_value = True

        response = client.delete("/users/1")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
        mock_delete_user.assert_called_once_with(1)

    @patch("users.services.UserService.delete_user")
    def test_delete_user_not_found(self, mock_delete_user, client):
        """Test DELETE /users/{user_id} endpoint with non-existing user."""
        mock_delete_user.return_value = False

        response = client.delete("/users/999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_delete_user.assert_called_once_with(999)

    def test_invalid_user_id(self, client):
        """Test endpoints with invalid user ID."""
        response = client.get("/users/invalid")
        assert response.status_code == 422

        response = client.put("/users/invalid", json={"username": "test"})
        assert response.status_code == 422

        response = client.delete("/users/invalid")
        assert response.status_code == 422

    @patch("users.services.UserService.get_user_by_id")
    def test_get_user_by_id_special_case(self, mock_get_user_by_id, client):
        """Test get_user_by_id with special case ID 999."""
        mock_get_user_by_id.return_value = None

        response = client.get("/users/999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_get_user_by_id.assert_called_once_with(999)

    @patch("users.services.UserService.update_user")
    def test_update_user_special_case(self, mock_update_user, client):
        """Test update_user with special case ID 999."""
        user_data = {
            "username": "updateduser",
            "email": "updated@example.com",
        }

        mock_update_user.return_value = None

        response = client.put("/users/999", json=user_data)

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_update_user.assert_called_once_with(999, user_data)

    @patch("users.services.UserService.delete_user")
    def test_delete_user_special_case(self, mock_delete_user, client):
        """Test delete_user with special case ID 999."""
        mock_delete_user.return_value = False

        response = client.delete("/users/999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        mock_delete_user.assert_called_once_with(999)
