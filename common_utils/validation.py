"""Common validation utilities for input validation and error handling.

All usage must comply with the project's standards:
See: docs/input_validation_and_error_handling_standards.md
"""

from typing import Type, TypeVar, Any, Dict
from pydantic import BaseModel, ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)

class ValidationException(Exception):
    """Custom validation exception for standardized error handling."""
    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(message)

def validate_input(model_cls: Type[T], data: Any) -> T:
    """
    Validate input data using a Pydantic model.
    Args:
        model_cls: The Pydantic BaseModel subclass.
        data: The input data (dict or compatible type).
    Returns:
        An instance of model_cls.
    Raises:
        ValidationException: If validation fails.
    """
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as exc:
        raise ValidationException(
            "Input validation failed.",
            details=exc.errors()
        ) from exc

def validation_error_response(exc: ValidationException) -> Dict[str, Any]:
    """
    Standardized error response for validation errors.
    Args:
        exc: The ValidationException instance.
    Returns:
        Dictionary conforming to error response standards.
    """
    return {
        "error_code": "validation_error",
        "message": exc.message,
        "details": exc.details
    }