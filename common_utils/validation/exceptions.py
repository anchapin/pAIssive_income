"""exceptions - Module for common_utils/validation.exceptions."""

# Standard library imports
from typing import Any, Optional

# Third-party imports

# Local imports


class ValidationError(Exception):
    """
    Exception raised for validation errors.

    Provides structured error information for validation failures.
    """

    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[list[dict[str, Any]]] = None
    ) -> None:
        """
        Initialize ValidationError with message and optional errors.

        Args:
            message: Human-readable error message
            errors: List of error details, each containing field and message

        """
        self.message = message
        self.errors = errors or []
        super().__init__(message)

    def add_error(self, field: str, message: str, error_type: str = "validation_error") -> None:
        """
        Add a new error to the errors list.

        Args:
            field: The field that failed validation
            message: The error message
            error_type: The type of validation error

        """
        self.errors.append({
            "field": field,
            "message": message,
            "type": error_type
        })

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the error to a dictionary representation.

        Returns:
            Dictionary with message and errors

        """
        return {
            "message": self.message,
            "errors": self.errors
        }
