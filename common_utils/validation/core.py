"""
Core validation utilities for input validation and error handling.

All usage must comply with the project's standards:
See: docs/input_validation_and_error_handling_standards.md
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, details: object = None) -> None:
        """
        Initialize the ValidationError.

        Args:
            details (Any, optional): Additional error details. Defaults to None.

        """
        self.message = "Input validation failed."
        self.details = details
        super().__init__(self.message)


def validate_input(model_cls: type[T], data: object) -> T:
    """
    Validate input data using a Pydantic model.

    Args:
        model_cls: The Pydantic BaseModel subclass.
        data: The input data (dict or compatible type).

    Returns:
        An instance of model_cls.

    Raises:
        ValidationError: If validation fails.

    """
    try:
        model_instance = model_cls.model_validate(data)
        # Verify the instance is of the correct type without using assert
        if not isinstance(model_instance, model_cls):
            error_msg = (
                f"Expected {model_cls.__name__}, got {type(model_instance).__name__}"
            )
            raise TypeError(error_msg)
    except PydanticValidationError as exc:
        raise ValidationError from exc
    else:
        return model_instance


def validation_error_response(exc: ValidationError) -> dict[str, object]:
    """
    Standardized error response for validation errors.

    Args:
        exc: The ValidationError instance.

    Returns:
        Dictionary conforming to error response standards.

    """
    return {
        "error_code": "validation_error",
        "message": exc.message,
        "details": exc.details,
    }
