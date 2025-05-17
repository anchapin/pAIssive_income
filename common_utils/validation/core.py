"""Core validation utilities for input validation and error handling.

All usage must comply with the project's standards:
See: docs/input_validation_and_error_handling_standards.md
"""

from typing import Any, Dict, List, Optional, TypeVar, Union

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


def format_validation_error(error: PydanticValidationError) -> List[Dict[str, str]]:
    """Format a Pydantic ValidationError into a standardized format.

    Args:
        error: The Pydantic ValidationError instance.

    Returns:
        List of dictionaries with field, message, and type.
    """
    formatted_errors = []
    for err in error.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        message = err.get("msg", "Invalid value")
        error_type = err.get("type", "validation_error")

        formatted_errors.append({
            "field": field,
            "message": message,
            "type": error_type
        })

    return formatted_errors


def validation_error_response(
    error: Union[PydanticValidationError, ValidationError, Exception],
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Standardized error response for validation errors.

    Args:
        error: The error instance (PydanticValidationError, ValidationError, or generic Exception).
        message: Optional custom error message.

    Returns:
        Dictionary conforming to error response standards.
    """
    formatted_errors = []
    error_message = message or "An error occurred processing the request"

    if isinstance(error, PydanticValidationError):
        formatted_errors = format_validation_error(error)
        error_message = message or "Validation error"
    elif isinstance(error, ValidationError):
        error_message = message or error.message

        if error.details and isinstance(error.details, list):
            for err in error.details:
                # Extract field and error message
                field = ".".join(str(loc) for loc in err.get("loc", []))
                err_message = err.get("msg", "Invalid value")

                formatted_errors.append({
                    "field": field,
                    "message": err_message,
                    "type": err.get("type", "validation_error")
                })

    return {
        "error_code": "validation_error",
        "message": error_message,
        "errors": formatted_errors or [{"field": "unknown", "message": error_message}],
    }
