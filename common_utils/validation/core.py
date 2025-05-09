"""Core validation utilities for input validation and error handling.

All usage must comply with the project's standards:
See: docs/input_validation_and_error_handling_standards.md
"""

from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import cast

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationError(Exception):
    """Custom validation error for standardized error handling."""

    def __init__(self, message: str, details: Any = None):
        """Initialize the ValidationError.

        Args:
            message (str): The error message.
            details (Any, optional): Additional error details. Defaults to None.

        """
        self.message = message
        self.details = details
        super().__init__(message)


def validate_input(model_cls: Type[T], data: Any) -> T:
    """Validate input data using a Pydantic model.

    Args:
        model_cls: The Pydantic BaseModel subclass.
        data: The input data (dict or compatible type).

    Returns:
        An instance of model_cls.

    Raises:
        ValidationError: If validation fails.

    """
    try:
        return cast(T, model_cls.model_validate(data))
    except PydanticValidationError as exc:
        raise ValidationError("Input validation failed.", details=exc.errors()) from exc


def validation_error_response(exc: ValidationError) -> Dict[str, Any]:
    """Standardized error response for validation errors.

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
