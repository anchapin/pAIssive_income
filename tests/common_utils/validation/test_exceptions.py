"""Test module for common_utils.validation.exceptions."""

import logging
import pytest

from common_utils.validation.exceptions import ValidationError


class TestValidationError:
    """Test suite for ValidationError class."""

    def test_validation_error_init(self):
        """Test ValidationError initialization."""
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.errors == []

    def test_validation_error_init_with_errors(self):
        """Test ValidationError initialization with errors."""
        errors = [
            {"field": "name", "message": "Field required"},
            {"field": "age", "message": "Must be an integer"},
        ]
        error = ValidationError("Test error message", errors=errors)
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.errors == errors

    def test_validation_error_add_error(self):
        """Test ValidationError add_error method."""
        error = ValidationError("Test error message")
        error.add_error("name", "Field required")
        assert len(error.errors) == 1
        assert error.errors[0]["field"] == "name"
        assert error.errors[0]["message"] == "Field required"

    def test_validation_error_add_multiple_errors(self):
        """Test ValidationError add_error method with multiple errors."""
        error = ValidationError("Test error message")
        error.add_error("name", "Field required")
        error.add_error("age", "Must be an integer")
        assert len(error.errors) == 2
        fields = {e["field"] for e in error.errors}
        assert "name" in fields
        assert "age" in fields

    def test_validation_error_to_dict(self):
        """Test ValidationError to_dict method."""
        error = ValidationError("Test error message")
        error.add_error("name", "Field required")
        error_dict = error.to_dict()
        assert "message" in error_dict
        assert "errors" in error_dict
        assert error_dict["message"] == "Test error message"
        assert len(error_dict["errors"]) == 1
        assert error_dict["errors"][0]["field"] == "name"
        assert error_dict["errors"][0]["message"] == "Field required"
