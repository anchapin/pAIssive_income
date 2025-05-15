"""Test module for common_utils.validation.core."""

import pytest
from pydantic import BaseModel, ValidationError

from common_utils.validation.core import (
    format_validation_error,
    validation_error_response,
)


class TestModel(BaseModel):
    """Test model for validation."""

    name: str
    age: int


class TestFormatValidationError:
    """Test suite for format_validation_error function."""

    def test_format_validation_error_missing_field(self):
        """Test format_validation_error with missing field."""
        try:
            TestModel(age=30)
        except ValidationError as e:
            result = format_validation_error(e)
            assert len(result) == 1
            assert result[0]["field"] == "name"
            assert "required" in result[0]["message"].lower()

    def test_format_validation_error_invalid_type(self):
        """Test format_validation_error with invalid type."""
        try:
            TestModel(name="Test User", age="invalid")
        except ValidationError as e:
            result = format_validation_error(e)
            assert len(result) == 1
            assert result[0]["field"] == "age"
            assert "integer" in result[0]["message"].lower()

    def test_format_validation_error_multiple_errors(self):
        """Test format_validation_error with multiple errors."""
        try:
            TestModel()
        except ValidationError as e:
            result = format_validation_error(e)
            assert len(result) == 2
            fields = {error["field"] for error in result}
            assert "name" in fields
            assert "age" in fields


class TestValidationErrorResponse:
    """Test suite for validation_error_response function."""

    def test_validation_error_response_with_validation_error(self):
        """Test validation_error_response with ValidationError."""
        try:
            TestModel(age=30)
        except ValidationError as e:
            response = validation_error_response(e)
            assert "errors" in response
            assert len(response["errors"]) == 1
            assert response["errors"][0]["field"] == "name"
            assert "required" in response["errors"][0]["message"].lower()

    def test_validation_error_response_with_generic_error(self):
        """Test validation_error_response with generic error."""
        error = ValueError("Test error message")
        response = validation_error_response(error)
        assert "errors" in response
        assert len(response["errors"]) == 1
        assert "message" in response["errors"][0]
        assert response["errors"][0]["message"] == "An error occurred processing the request"

    def test_validation_error_response_with_custom_message(self):
        """Test validation_error_response with custom message."""
        error = ValueError("Test error message")
        response = validation_error_response(error, message="Custom error message")
        assert "errors" in response
        assert len(response["errors"]) == 1
        assert response["errors"][0]["message"] == "Custom error message"
