"""Core validation utilities for input validation and error handling.

All usage must comply with the project's standards:
See: docs/input_validation_and_error_handling_standards.md
"""

from typing import Any
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Input validation failed", details: Any = None) -> None:
        """Initialize the ValidationError.

        Args:
            message (str, optional): Error message. Defaults to "Input validation failed".
            details (Any, optional): Additional error details. Defaults to None.
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


def validate_input(model_cls: type[T], data: Any) -> T:
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
        model_instance = model_cls.model_validate(data)
        assert isinstance(model_instance, model_cls)
    except PydanticValidationError as exc:
        # Always use the standard error message for consistency in tests
        # but include the detailed errors for debugging
        raise ValidationError("Input validation failed.", exc.errors()) from exc
    except Exception as exc:
        # Handle other validation errors
        raise ValidationError("Input validation failed.", [{"loc": ["unknown"], "msg": str(exc), "type": "unknown_error"}]) from exc
    else:
        return model_instance


def validation_error_response(exc: ValidationError) -> dict[str, Any]:
    """Standardized error response for validation errors.

    Args:
        exc: The ValidationError instance.

    Returns:
        Dictionary conforming to error response standards.
    """
    # Format the error details into a more user-friendly structure
    formatted_errors = []

    if exc.details and isinstance(exc.details, list):
        for error in exc.details:
            # Extract field and error message
            field = ".".join(str(loc) for loc in error.get("loc", []))
            message = error.get("msg", "Invalid value")

            formatted_errors.append({
                "field": field,
                "message": message,
                "type": error.get("type", "validation_error")
            })

    return {
        "error_code": "validation_error",
        "message": exc.message,
        "errors": formatted_errors or [{"field": "unknown", "message": exc.message}],
    }
