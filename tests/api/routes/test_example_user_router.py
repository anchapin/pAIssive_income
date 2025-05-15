"""test_example_user_router - Module for tests/api/routes.test_example_user_router."""

# Standard library imports
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Third-party imports
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

# Local imports
from api.routes.example_user_router import router, CreateUserModel
from common_utils.validation.core import ValidationError


@pytest.fixture
def test_client():
    """Create a test client for the router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestCreateUserModel:
    """Test suite for the CreateUserModel."""

    def test_valid_model(self):
        """Test that a valid model passes validation."""
        # Valid data
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "age": 30
        }

        # Create model
        model = CreateUserModel(**valid_data)

        # Verify fields
        assert model.username == valid_data["username"]
        assert model.email == valid_data["email"]
        assert model.age == valid_data["age"]

    def test_invalid_username(self):
        """Test that invalid usernames fail validation."""
        # Username too short
        with pytest.raises(ValueError):
            CreateUserModel(username="ab", email="test@example.com", age=30)

        # Username too long
        with pytest.raises(ValueError):
            CreateUserModel(
                username="a" * 33,  # 33 characters
                email="test@example.com",
                age=30
            )

    def test_invalid_email(self):
        """Test that invalid emails fail validation."""
        with pytest.raises(ValueError):
            CreateUserModel(username="testuser", email="not_an_email", age=30)

    def test_invalid_age(self):
        """Test that invalid ages fail validation."""
        # Age too low
        with pytest.raises(ValueError):
            CreateUserModel(username="testuser", email="test@example.com", age=-1)

        # Age too high
        with pytest.raises(ValueError):
            CreateUserModel(username="testuser", email="test@example.com", age=121)


class TestCreateUserEndpoint:
    """Test suite for the create_user endpoint."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, test_client):
        """Test successful user creation."""
        # Valid user data
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "age": 30
        }

        # Send request
        response = test_client.post("/api/v1/example_users/", json=user_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User created"
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["age"] == user_data["age"]

    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, test_client):
        """Test validation error handling."""
        # Invalid user data (missing required fields)
        user_data = {
            "username": "testuser"
            # Missing email and age
        }

        # Send request
        response = test_client.post("/api/v1/example_users/", json=user_data)

        # Verify response
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data
        assert "errors" in data["detail"]
        assert len(data["detail"]["errors"]) > 0

    @pytest.mark.asyncio
    async def test_create_user_invalid_json(self, test_client):
        """Test handling of invalid JSON."""
        # Send request with invalid JSON
        response = test_client.post(
            "/api/v1/example_users/",
            headers={"Content-Type": "application/json"},
            content="not valid json"
        )

        # Verify response
        assert response.status_code == 500  # Internal Server Error

    @patch("api.routes.example_user_router.validate_input")
    @pytest.mark.asyncio
    async def test_create_user_validation_error_response(self, mock_validate_input, test_client):
        """Test validation error response handling."""
        # Mock validation error
        validation_error = ValidationError("Validation failed")
        validation_error.details = {"field": "error message"}
        mock_validate_input.side_effect = validation_error

        # Send request
        response = test_client.post(
            "/api/v1/example_users/",
            json={"username": "testuser", "email": "test@example.com", "age": 30}
        )

        # Verify response
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data
        assert "errors" in data["detail"]

    @patch("api.routes.example_user_router.validate_input")
    @patch("api.routes.example_user_router.logger")
    @pytest.mark.asyncio
    async def test_create_user_unexpected_error(self, mock_logger, mock_validate_input, test_client):
        """Test handling of unexpected errors."""
        # Mock unexpected error
        mock_validate_input.side_effect = Exception("Unexpected error")

        # Send request
        response = test_client.post(
            "/api/v1/example_users/",
            json={"username": "testuser", "email": "test@example.com", "age": 30}
        )

        # Verify response
        assert response.status_code == 500  # Internal Server Error
        assert response.json()["detail"] == "Internal server error"

        # Verify logging
        mock_logger.error.assert_called_once_with(
            "An unexpected error occurred",
            exc_info=True
        )

    @pytest.mark.asyncio
    async def test_create_user_empty_payload(self, test_client):
        """Test handling of empty payload."""
        # Send request with empty JSON
        response = test_client.post(
            "/api/v1/example_users/",
            json={}
        )

        # Verify response
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data
        assert "errors" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_user_invalid_types(self, test_client):
        """Test handling of invalid data types."""
        # Send request with invalid data types
        response = test_client.post(
            "/api/v1/example_users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "age": "thirty"  # String instead of int
            }
        )

        # Verify response
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_user_json_decode_error(self, test_client):
        """Test handling of JSON decode error."""
        # Send request with invalid JSON
        response = test_client.post(
            "/api/v1/example_users/",
            headers={"Content-Type": "application/json"},
            content="not valid json"
        )

        # Verify response
        assert response.status_code == 500  # Internal Server Error
