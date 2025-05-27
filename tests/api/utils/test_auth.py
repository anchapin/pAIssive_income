"""test_auth - Module for tests/api/utils.test_auth."""

# Standard library imports
import logging
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Third-party imports
import pytest
from fastapi import HTTPException

# Local imports
from api.utils.auth import (
    TokenData,
    get_current_active_user,
    get_current_user,
    verify_api_key,
)


class TestTokenData(unittest.TestCase):
    """Test suite for TokenData model."""

    def test_token_data_init(self):
        """Test initializing TokenData."""
        # Test with just subject
        token_data = TokenData(sub="user123")
        assert token_data.sub == "user123"
        assert token_data.scopes == []

        # Test with subject and scopes
        token_data = TokenData(sub="user123", scopes=["read", "write"])
        assert token_data.sub == "user123"
        assert token_data.scopes == ["read", "write"]


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Test suite for get_current_user function."""

    async def test_get_current_user_success(self):
        """Test getting current user with valid token."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.verify_token.return_value = (True, {"sub": "user123"})
        mock_user_service.user_repository.find_by_id.return_value = {
            "id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "auth_hash": "hashed_password",
            "status": "active",
        }

        # Act
        result = await get_current_user("valid_token", mock_user_service)

        # Assert
        assert result["id"] == "user123"
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert "auth_hash" not in result
        mock_user_service.verify_token.assert_called_once_with("valid_token")
        mock_user_service.user_repository.find_by_id.assert_called_once_with("user123")

    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.verify_token.return_value = (False, None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", mock_user_service)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        mock_user_service.verify_token.assert_called_once_with("invalid_token")

    async def test_get_current_user_missing_subject(self):
        """Test getting current user with token missing subject claim."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.verify_token.return_value = (True, {"other": "value"})

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("token_without_sub", mock_user_service)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        mock_user_service.verify_token.assert_called_once_with("token_without_sub")

    async def test_get_current_user_no_repository(self):
        """Test getting current user when user repository is not available."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.verify_token.return_value = (True, {"sub": "user123"})
        mock_user_service.user_repository = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("valid_token", mock_user_service)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal server error"
        mock_user_service.verify_token.assert_called_once_with("valid_token")

    async def test_get_current_user_not_found(self):
        """Test getting current user when user is not found."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.verify_token.return_value = (True, {"sub": "user123"})
        mock_user_service.user_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("valid_token", mock_user_service)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"
        mock_user_service.verify_token.assert_called_once_with("valid_token")
        mock_user_service.user_repository.find_by_id.assert_called_once_with("user123")

    async def test_get_current_user_removes_sensitive_fields(self):
        """Test that sensitive fields are removed from user data."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.verify_token.return_value = (True, {"sub": "user123"})
        mock_user_service.user_repository.find_by_id.return_value = {
            "id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "auth_hash": "hashed_auth",
            "password_hash": "hashed_password",
            "credential_hash": "hashed_credential",
        }

        # Act
        result = await get_current_user("valid_token", mock_user_service)

        # Assert
        assert "auth_hash" not in result
        assert "password_hash" not in result
        assert "credential_hash" not in result


@pytest.mark.asyncio
class TestGetCurrentActiveUser:
    """Test suite for get_current_active_user function."""

    async def test_get_current_active_user_success(self):
        """Test getting current active user with active status."""
        # Arrange
        mock_current_user = {
            "id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "status": "active",
        }

        # Act
        result = await get_current_active_user(mock_current_user)

        # Assert
        assert result == mock_current_user

    async def test_get_current_active_user_inactive(self):
        """Test getting current active user with inactive status."""
        # Arrange
        mock_current_user = {
            "id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "status": "inactive",
        }

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(mock_current_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Inactive user"


@pytest.mark.asyncio
class TestVerifyApiKey:
    """Test suite for verify_api_key function."""

    async def test_verify_api_key_success(self):
        """Test verifying a valid API key."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.user_repository.find_api_key.return_value = {
            "id": "key123",
            "user_id": "user123",
            "key": "valid_api_key",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        }

        # Act
        result = await verify_api_key("valid_api_key", mock_user_service)

        # Assert
        assert result["id"] == "key123"
        assert result["user_id"] == "user123"
        mock_user_service.user_repository.find_api_key.assert_called_once_with("valid_api_key")

    async def test_verify_api_key_no_repository(self):
        """Test verifying API key when repository is not available."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.user_repository = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key("valid_api_key", mock_user_service)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal server error"

    async def test_verify_api_key_invalid(self):
        """Test verifying an invalid API key."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.user_repository.find_api_key.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key("invalid_api_key", mock_user_service)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid API key"
        mock_user_service.user_repository.find_api_key.assert_called_once_with("invalid_api_key")

    async def test_verify_api_key_expired(self):
        """Test verifying an expired API key."""
        # Arrange
        mock_user_service = MagicMock()
        mock_user_service.user_repository.find_api_key.return_value = {
            "id": "key123",
            "user_id": "user123",
            "key": "expired_api_key",
            "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        }

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key("expired_api_key", mock_user_service)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Expired API key"
        mock_user_service.user_repository.find_api_key.assert_called_once_with("expired_api_key")
