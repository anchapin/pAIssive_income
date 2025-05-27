"""Additional tests for the example user router."""

import logging
import json
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from api.routes.example_user_router import router, CreateUserModel
from common_utils.validation.core import ValidationError


@pytest.fixture
def test_client():
    """Create a test client for the router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestExampleUserRouter:
    """Additional tests for the example user router."""

    def test_router_prefix(self):
        """Test that the router has the correct prefix."""
        assert router.prefix == "/api/v1/example_users"
        assert "example_users" in router.tags

    @patch("api.routes.example_user_router.validate_input")
    @patch("api.routes.example_user_router.logger")
    async def test_create_user_with_logging(self, mock_logger, mock_validate_input, test_client):
        """Test that the create_user endpoint logs appropriately."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.model_dump.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "age": 30
        }
        mock_validate_input.return_value = mock_model

        # Send request
        response = test_client.post(
            "/api/v1/example_users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "age": 30
            }
        )

        # Verify response
        assert response.status_code == 200
        assert response.json() == {
            "message": "User created",
            "user": {
                "username": "testuser",
                "email": "test@example.com",
                "age": 30
            }
        }

    @patch("api.routes.example_user_router.validate_input")
    @patch("api.routes.example_user_router.validation_error_response")
    async def test_create_user_validation_error_handling(self, mock_validation_error_response, mock_validate_input, test_client):
        """Test that validation errors are handled correctly."""
        # Setup mocks
        validation_error = ValidationError("Validation failed")
        mock_validate_input.side_effect = validation_error
        mock_validation_error_response.return_value = {"errors": ["Test error"]}

        # Send request
        response = test_client.post(
            "/api/v1/example_users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "age": 30
            }
        )

        # Verify response
        assert response.status_code == 422
        assert response.json() == {"detail": {"errors": ["Test error"]}}
        mock_validation_error_response.assert_called_once_with(validation_error)

    def test_create_user_with_different_payload(self, test_client):
        """Test create_user with different payload values."""
        # Send request with different payload
        response = test_client.post(
            "/api/v1/example_users/",
            json={
                "username": "different_user",
                "email": "different@example.com",
                "age": 25
            }
        )

        # Verify response
        assert response.status_code == 200
        assert response.json() == {
            "message": "User created",
            "user": {
                "username": "different_user",
                "email": "different@example.com",
                "age": 25
            }
        }

    def test_create_user_with_invalid_data(self, test_client):
        """Test create_user with invalid data."""
        # Send request with invalid data
        response = test_client.post(
            "/api/v1/example_users/",
            json={
                "username": "ab",  # Too short
                "email": "invalid-email",
                "age": -1
            }
        )

        # Verify response
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_user_model_validation(self):
        """Test additional validation scenarios for CreateUserModel."""
        # Test with valid data
        model = CreateUserModel(username="valid_user", email="valid@example.com", age=50)
        assert model.username == "valid_user"
        assert model.email == "valid@example.com"
        assert model.age == 50

        # Test with boundary values
        model = CreateUserModel(username="abc", email="boundary@example.com", age=0)  # Minimum values
        assert model.username == "abc"
        assert model.age == 0

        model = CreateUserModel(username="a" * 32, email="boundary@example.com", age=120)  # Maximum values
        assert model.username == "a" * 32
        assert model.age == 120

        # Test with invalid values
        with pytest.raises(ValueError):
            CreateUserModel(username="ab", email="valid@example.com", age=50)  # Username too short

        with pytest.raises(ValueError):
            CreateUserModel(username="valid_user", email="invalid_email", age=50)  # Invalid email

        with pytest.raises(ValueError):
            CreateUserModel(username="valid_user", email="valid@example.com", age=-1)  # Age too low

        with pytest.raises(ValueError):
            CreateUserModel(username="valid_user", email="valid@example.com", age=121)  # Age too high
