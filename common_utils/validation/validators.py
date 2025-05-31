"""validators - Module for common_utils/validation.validators."""

# Standard library imports
import re
from typing import Any
from urllib.parse import urlparse

# Third-party imports
from pydantic import field_validator

# Local imports
from common_utils.logging import get_logger

logger = get_logger(__name__)

# Regular expressions for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_REGEX = re.compile(
    r"^https?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or ipv4
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_email(email: str) -> bool:
    """
    Validate an email address.

    Args:
        email: The email address to validate

    Returns:
        True if the email is valid, False otherwise

    """
    if not email:
        return False

    # Check basic regex pattern
    if not EMAIL_REGEX.match(email):
        return False

    # Additional checks for common invalid patterns
    parts = email.split("@")
    if len(parts) != 2:
        return False

    domain = parts[1]
    # Check for consecutive dots in domain
    if ".." in domain:
        return False

    return True


def validate_url(url: str) -> bool:
    """
    Validate a URL.

    Args:
        url: The URL to validate

    Returns:
        True if the URL is valid, False otherwise

    """
    if not url:
        return False

    try:
        # Parse the URL
        parsed_url = urlparse(url)

        # Check scheme
        if parsed_url.scheme not in ("http", "https"):
            return False

        # Check netloc (domain)
        if not parsed_url.netloc:
            return False

        # Special case for URLs with authentication
        if "@" in parsed_url.netloc:
            # Allow URLs with username and password
            return True

        # Check if the URL matches the regex for standard URLs
        if not URL_REGEX.match(url):
            return False

        return True
    except Exception:
        return False


def validate_password_strength(password: str) -> dict[str, Any]:
    """
    Validate password strength.

    Args:
        password: The password to validate

    Returns:
        Dictionary with validation results:
        - valid: True if the password meets all requirements, False otherwise
        - errors: List of error messages if any
        - score: Password strength score (0-100)

    """
    errors = []
    score = 0

    # Check length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    else:
        score += 20

    # Check for uppercase letters
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    else:
        score += 20

    # Check for lowercase letters
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    else:
        score += 20

    # Check for digits
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    else:
        score += 20

    # Check for special characters
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")
    else:
        score += 20

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "score": score,
    }


def validate_username(username: str) -> dict[str, Any]:
    """
    Validate a username.

    Args:
        username: The username to validate

    Returns:
        Dictionary with validation results:
        - valid: True if the username meets all requirements, False otherwise
        - errors: List of error messages if any

    """
    errors = []

    # Check length
    if len(username) < 3:
        errors.append("Username must be at least 3 characters long")

    if len(username) > 30:
        errors.append("Username must be at most 30 characters long")

    # Check for valid characters
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        errors.append("Username can only contain letters, numbers, underscores, dots, and hyphens")

    # Check that username doesn't start with a special character
    if re.match(r"^[_.-]", username):
        errors.append("Username cannot start with an underscore, dot, or hyphen")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


class ValidationMixin:
    """Mixin class with common validation methods for Pydantic models."""

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        """Validate email field."""
        if not validate_email(v):
            raise ValueError("Invalid email address")
        return v

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v):
        """Validate URL field."""
        if not validate_url(v):
            raise ValueError("Invalid URL")
        return v

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v):
        """Validate username field."""
        result = validate_username(v)
        if not result["valid"]:
            raise ValueError(", ".join(result["errors"]))
        return v

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v):
        """Validate password field."""
        result = validate_password_strength(v)
        if not result["valid"]:
            raise ValueError(", ".join(result["errors"]))
        return v
