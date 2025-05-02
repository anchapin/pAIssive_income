"""
Exceptions for validation errors.

This module provides custom exceptions to handle validation errors.
"""

from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """
    Exception raised when validation fails.
    """

    def __init__(
        self,
        message: str,
        validation_errors: Optional[List[Dict[str, str]]] = None,
        http_status: int = 400,
    ):
        """
        Initialize a ValidationError.

        Args:
            message: Error message
            validation_errors: List of validation errors
            http_status: HTTP status code
        """
        self.message = message
        self.validation_errors = validation_errors or []
        self.http_status = http_status
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary for JSON responses.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "error": "Validation Error",
            "message": self.message,
            "details": self.validation_errors,
        }

    def __str__(self) -> str:
        """
        Get a string representation of the exception.

        Returns:
            String representation
        """
        if self.validation_errors:
            error_details = ", ".join(f"{e['field']}: {e['error']}" for e in self.validation_errors)
            return f"{self.message}: {error_details}"
        return self.message
