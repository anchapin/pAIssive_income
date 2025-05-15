"""Tests for common_utils.validation input validation utility.

All tests and validation logic must comply with:
docs/input_validation_and_error_handling_standards.md
"""

import json
from typing import Any, Dict, List, Optional, Union

import pytest
from pydantic import BaseModel, EmailStr, Field, ValidationError as PydanticValidationError

from common_utils.validation.core import ValidationError, validate_input, validation_error_response
from common_utils.validation.decorators import validate_request_body
from common_utils.validation.validators import validate_email, validate_url


class ExampleInputModel(BaseModel):
    """Example input model for validation testing.

    This model includes various validation rules to test different validation scenarios.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_-]+$",  # Only allow alphanumeric, underscore, and hyphen
    )
    age: int = Field(..., ge=0, le=120)
    email: str
    bio: str = Field(default="", max_length=150)

    model_config = {
        "extra": "forbid",  # Forbid extra fields
        "strict": True,  # Enable strict mode for type validation
    }


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        # Missing required field
        ({"username": "alice", "age": 30}, "Input validation failed."),
        # Extra/unknown field
        (
            {
                "username": "bob",
                "age": 25,
                "email": "bob@example.com",
                "bio": "hi",
                "hacker": True,
            },
            "Input validation failed.",
        ),
        # Invalid type
        (
            {"username": "carol", "age": "not_a_number", "email": "carol@example.com"},
            "Input validation failed.",
        ),
        # XSS payload
        (
            {
                "username": "<script>alert(1)</script>",
                "age": 22,
                "email": "xss@example.com",
            },
            "Input validation failed.",
        ),
        # SQL injection payload
        (
            {
                "username": "eve'; DROP TABLE users; --",
                "age": 22,
                "email": "sql@example.com",
            },
            "Input validation failed.",
        ),
        # Oversized payload
        (
            {"username": "a" * 100, "age": 22, "email": "big@example.com"},
            "Input validation failed.",
        ),
        # Out-of-range age
        (
            {"username": "dan", "age": 999, "email": "dan@example.com"},
            "Input validation failed.",
        ),
    ],
)
def test_invalid_input_cases(payload: dict, expected_error: str) -> None:
    """Test that invalid inputs raise ValidationError with the expected message.

    Args:
        payload: The input data to validate
        expected_error: The expected error message

    """
    with pytest.raises(ValidationError) as exc_info:
        validate_input(ExampleInputModel, payload)
    assert expected_error in str(exc_info.value)


def test_valid_input() -> None:
    """Test that valid input is correctly validated and returned as a model instance."""
    payload = {
        "username": "validuser",
        "age": 35,
        "email": "valid@example.com",
        "bio": "Hello world!",
    }
    instance = validate_input(ExampleInputModel, payload)
    assert instance.username == "validuser"
    assert instance.age == 35
    assert instance.email == "valid@example.com"
    assert instance.bio == "Hello world!"


def test_validation_error_response() -> None:
    """Test that validation_error_response returns the expected error response."""
    # Create a ValidationError with multiple errors
    validation_error = ValidationError(
        "Input validation failed.",
        [
            {
                "loc": ["username"],
                "msg": "String should have at least 3 characters",
                "type": "string_too_short",
            },
            {
                "loc": ["age"],
                "msg": "Input should be greater than or equal to 0",
                "type": "greater_than_equal",
            },
            {
                "loc": ["email"],
                "msg": "Invalid email format",
                "type": "value_error",
            },
        ],
    )

    # Get the error response
    response = validation_error_response(validation_error)

    # Check the response structure
    assert "errors" in response
    assert isinstance(response["errors"], list)
    assert len(response["errors"]) == 3

    # Check that each error has the expected fields
    for error in response["errors"]:
        assert "field" in error
        assert "message" in error

    # Check that specific errors are included
    error_fields = [error["field"] for error in response["errors"]]
    assert "username" in error_fields
    assert "age" in error_fields
    assert "email" in error_fields


class MockRequest:
    """Mock request class for testing decorators."""

    def __init__(self, json_data: Dict[str, Any]):
        self._json = json_data

    async def get_json(self) -> Dict[str, Any]:
        return self._json


class TestValidateRequestBodyDecorator:
    """Test suite for the validate_request_body decorator."""

    @pytest.mark.asyncio
    async def test_valid_request(self) -> None:
        """Test that a valid request passes validation."""
        # Define a test function with the decorator
        @validate_request_body(ExampleInputModel)
        async def test_func(request, model_instance):
            return {"success": True, "data": model_instance.model_dump()}

        # Create a mock request with valid data
        request = MockRequest({
            "username": "validuser",
            "age": 35,
            "email": "valid@example.com",
            "bio": "Hello world!",
        })

        # Call the function
        result = await test_func(request)

        # Check the result
        assert result["success"] is True
        assert result["data"]["username"] == "validuser"
        assert result["data"]["age"] == 35
        assert result["data"]["email"] == "valid@example.com"
        assert result["data"]["bio"] == "Hello world!"

    @pytest.mark.asyncio
    async def test_invalid_request(self) -> None:
        """Test that an invalid request returns a validation error response."""
        # Define a test function with the decorator
        @validate_request_body(ExampleInputModel)
        async def test_func(request, model_instance):
            return {"success": True, "data": model_instance.model_dump()}

        # Create a mock request with invalid data
        request = MockRequest({
            "username": "a",  # Too short
            "age": -1,  # Out of range
            "email": "invalid-email",  # Invalid email
        })

        # Call the function
        result = await test_func(request)

        # Check the result
        assert "errors" in result
        assert isinstance(result["errors"], list)
        assert len(result["errors"]) > 0


class TestValidators:
    """Test suite for the validation utility functions."""

    @pytest.mark.parametrize(
        ("email", "expected_valid"),
        [
            ("valid@example.com", True),
            ("user.name+tag@example.co.uk", True),
            ("user@subdomain.example.com", True),
            ("", False),
            ("invalid", False),
            ("invalid@", False),
            ("invalid@.com", False),
            ("@example.com", False),
            ("user@example..com", False),
        ],
    )
    def test_validate_email(self, email: str, expected_valid: bool) -> None:
        """Test email validation."""
        assert validate_email(email) == expected_valid

    @pytest.mark.parametrize(
        ("url", "expected_valid"),
        [
            ("https://example.com", True),
            ("http://example.com", True),
            ("https://example.com/path", True),
            ("https://example.com/path?query=value", True),
            ("https://user:pass@example.com", True),
            ("", False),
            ("invalid", False),
            ("ftp://example.com", False),  # Not HTTP/HTTPS
            ("http:/example.com", False),  # Missing slash
            ("https://", False),  # Missing domain
        ],
    )
    def test_validate_url(self, url: str, expected_valid: bool) -> None:
        """Test URL validation."""
        assert validate_url(url) == expected_valid
