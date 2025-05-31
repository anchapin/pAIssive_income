"""Test module for common_utils.validation.validators."""

import logging

import pytest
from pydantic import BaseModel

from common_utils.validation.validators import (
    ValidationMixin,
    validate_email,
    validate_password_strength,
    validate_url,
    validate_username,
)


class TestValidateEmail:
    """Test suite for validate_email function."""

    @pytest.mark.parametrize(
        ("email", "expected"),
        [
            ("user@example.com", True),
            ("user.name@example.co.uk", True),
            ("user+tag@example.com", True),
            ("user@subdomain.example.com", True),
            ("", False),
            (None, False),
            ("invalid", False),
            ("invalid@", False),
            ("invalid@.com", False),
            ("@example.com", False),
            ("user@example..com", False),
        ],
    )
    def test_validate_email(self, email, expected):
        """Test validate_email with various inputs."""
        assert validate_email(email) == expected


class TestValidateUrl:
    """Test suite for validate_url function."""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("https://example.com", True),
            ("http://example.com", True),
            ("https://example.com/path", True),
            ("https://example.com/path?query=value", True),
            ("https://user:pass@example.com", True),
            ("", False),
            (None, False),
            ("invalid", False),
            ("ftp://example.com", False),
            ("http:/example.com", False),
            ("https://", False),
        ],
    )
    def test_validate_url(self, url, expected):
        """Test validate_url with various inputs."""
        assert validate_url(url) == expected

    def test_validate_url_exception_handling(self):
        """Test validate_url handles exceptions."""
        # Create a URL that will cause an exception in urlparse
        url = "http://example.com:port"  # Invalid port
        assert validate_url(url) is False


class TestValidatePasswordStrength:
    """Test suite for validate_password_strength function."""

    def test_strong_password(self):
        """Test validate_password_strength with a strong password."""
        password = "StrongP@ss123"
        result = validate_password_strength(password)
        assert result["valid"] is True
        assert result["score"] == 100
        assert len(result["errors"]) == 0

    def test_weak_password_length(self):
        """Test validate_password_strength with a short password."""
        password = "Weak1!"
        result = validate_password_strength(password)
        assert result["valid"] is False
        assert result["score"] == 80
        assert "at least 8 characters" in result["errors"][0]

    def test_weak_password_no_uppercase(self):
        """Test validate_password_strength with no uppercase letters."""
        password = "weakpass123!"
        result = validate_password_strength(password)
        assert result["valid"] is False
        assert result["score"] == 80
        assert "uppercase letter" in result["errors"][0]

    def test_weak_password_no_lowercase(self):
        """Test validate_password_strength with no lowercase letters."""
        password = "WEAKPASS123!"
        result = validate_password_strength(password)
        assert result["valid"] is False
        assert result["score"] == 80
        assert "lowercase letter" in result["errors"][0]

    def test_weak_password_no_digits(self):
        """Test validate_password_strength with no digits."""
        password = "WeakPassword!"
        result = validate_password_strength(password)
        assert result["valid"] is False
        assert result["score"] == 80
        assert "digit" in result["errors"][0]

    def test_weak_password_no_special_chars(self):
        """Test validate_password_strength with no special characters."""
        password = "WeakPassword123"
        result = validate_password_strength(password)
        assert result["valid"] is False
        assert result["score"] == 80
        assert "special character" in result["errors"][0]

    def test_very_weak_password(self):
        """Test validate_password_strength with a very weak password."""
        password = "weak"
        result = validate_password_strength(password)
        assert result["valid"] is False
        assert result["score"] == 20
        assert len(result["errors"]) == 4


class TestValidateUsername:
    """Test suite for validate_username function."""

    def test_valid_username(self):
        """Test validate_username with a valid username."""
        username = "valid_user123"
        result = validate_username(username)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_username_too_short(self):
        """Test validate_username with a username that's too short."""
        username = "ab"
        result = validate_username(username)
        assert result["valid"] is False
        assert "at least 3 characters" in result["errors"][0]

    def test_username_too_long(self):
        """Test validate_username with a username that's too long."""
        username = "a" * 31
        result = validate_username(username)
        assert result["valid"] is False
        assert "at most 30 characters" in result["errors"][0]

    def test_username_invalid_chars(self):
        """Test validate_username with invalid characters."""
        username = "invalid@user"
        result = validate_username(username)
        assert result["valid"] is False
        assert "can only contain" in result["errors"][0]

    def test_username_starts_with_special_char(self):
        """Test validate_username starting with a special character."""
        username = "_invalid_start"
        result = validate_username(username)
        assert result["valid"] is False
        assert "cannot start with" in result["errors"][0]


class TestValidationMixin:
    """Test suite for ValidationMixin class."""

    class TestModel(BaseModel, ValidationMixin):
        """Test model using ValidationMixin."""

        email: str
        url: str
        username: str
        password: str

    def test_validate_email_field_valid(self):
        """Test email validation with valid email."""
        model = self.TestModel(
            email="user@example.com",
            url="https://example.com",
            username="valid_user",
            password="StrongP@ss123",
        )
        assert model.email == "user@example.com"

    def test_validate_email_field_invalid(self):
        """Test email validation with invalid email."""
        with pytest.raises(ValueError, match="Invalid email address"):
            self.TestModel(
                email="invalid",
                url="https://example.com",
                username="valid_user",
                password="StrongP@ss123",
            )

    def test_validate_url_field_valid(self):
        """Test URL validation with valid URL."""
        model = self.TestModel(
            email="user@example.com",
            url="https://example.com",
            username="valid_user",
            password="StrongP@ss123",
        )
        assert model.url == "https://example.com"

    def test_validate_url_field_invalid(self):
        """Test URL validation with invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            self.TestModel(
                email="user@example.com",
                url="invalid",
                username="valid_user",
                password="StrongP@ss123",
            )

    def test_validate_username_field_valid(self):
        """Test username validation with valid username."""
        model = self.TestModel(
            email="user@example.com",
            url="https://example.com",
            username="valid_user",
            password="StrongP@ss123",
        )
        assert model.username == "valid_user"

    def test_validate_username_field_invalid(self):
        """Test username validation with invalid username."""
        with pytest.raises(ValueError):
            self.TestModel(
                email="user@example.com",
                url="https://example.com",
                username="_invalid",
                password="StrongP@ss123",
            )

    def test_validate_password_field_valid(self):
        """Test password validation with valid password."""
        model = self.TestModel(
            email="user@example.com",
            url="https://example.com",
            username="valid_user",
            password="StrongP@ss123",
        )
        assert model.password == "StrongP@ss123"

    def test_validate_password_field_invalid(self):
        """Test password validation with invalid password."""
        with pytest.raises(ValueError):
            self.TestModel(
                email="user@example.com",
                url="https://example.com",
                username="valid_user",
                password="weak",
            )
