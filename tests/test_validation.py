"""Tests for common_utils.validation input validation utility.

All tests and validation logic must comply with:
docs/input_validation_and_error_handling_standards.md
"""

import pytest
from pydantic import BaseModel, Field
from common_utils.validation import validate_input, ValidationException

class ExampleInputModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    age: int = Field(..., ge=0, le=120)
    email: str
    bio: str = Field(default="", max_length=150)

@pytest.mark.parametrize(
    "payload,expected_error",
    [
        # Missing required field
        ({"username": "alice", "age": 30}, "Input validation failed."),

        # Extra/unknown field
        (
            {"username": "bob", "age": 25, "email": "bob@example.com", "bio": "hi", "hacker": True},
            "Input validation failed."
        ),

        # Invalid type
        (
            {"username": "carol", "age": "not_a_number", "email": "carol@example.com"},
            "Input validation failed."
        ),

        # XSS payload
        (
            {"username": "<script>alert(1)</script>", "age": 22, "email": "xss@example.com"},
            "Input validation failed."
        ),

        # SQL injection payload
        (
            {"username": "eve'; DROP TABLE users; --", "age": 22, "email": "sql@example.com"},
            "Input validation failed."
        ),

        # Oversized payload
        (
            {"username": "a" * 100, "age": 22, "email": "big@example.com"},
            "Input validation failed."
        ),

        # Out-of-range age
        (
            {"username": "dan", "age": 999, "email": "dan@example.com"},
            "Input validation failed."
        ),
    ]
)
def test_invalid_input_cases(payload, expected_error):
    with pytest.raises(ValidationException) as exc_info:
        validate_input(ExampleInputModel, payload)
    assert expected_error in str(exc_info.value)

def test_valid_input():
    payload = {
        "username": "validuser",
        "age": 35,
        "email": "valid@example.com",
        "bio": "Hello world!"
    }
    instance = validate_input(ExampleInputModel, payload)
    assert instance.username == "validuser"
    assert instance.age == 35
    assert instance.email == "valid@example.com"
    assert instance.bio == "Hello world!"