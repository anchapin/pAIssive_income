"""
Schema validation for structured data.

This module provides utilities for validating structured data against schemas,
particularly useful for API request validation.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from flask import Request


@dataclass
class ValidationResult:
    """
    Result of a validation operation.
    """

    valid: bool
    errors: List[Dict[str, str]] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """
        Check if validation has any errors.

        Returns:
            True if there are validation errors, False otherwise
        """
        return len(self.errors) > 0

    def add_error(self, field_name: str, error: str) -> None:
        """
        Add an error to the validation result.

        Args:
            field_name: Name of the field with the error
            error: Error message
        """
        self.valid = False
        self.errors.append({"field": field_name, "error": error})


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
    """
    Validate data against a schema.

    Args:
        data: Data to validate
        schema: Schema to validate against

    Returns:
        ValidationResult with validation status and errors
    """
    result = ValidationResult(valid=True)

    # Check for required fields
    for field_name, field_schema in schema.items():
        if field_schema.get("required", False) and field_name not in data:
            result.add_error(field_name, f"Field '{field_name}' is required")

    # Validate fields in data
    for field_name, value in data.items():
        if field_name not in schema:
            if schema.get("strict", False):
                result.add_error(field_name, f"Unknown field '{field_name}'")
            continue

        field_schema = schema[field_name]
        validator = field_schema.get("validator")

        if validator:
            is_valid, error = validator(value)
            if not is_valid:
                result.add_error(field_name, error)

    return result


def validate_api_request(request: Request, schema: Dict[str, Any]) -> ValidationResult:
    """
    Validate a Flask request against a schema.

    Args:
        request: Flask request object
        schema: Schema to validate against

    Returns:
        ValidationResult with validation status and errors
    """
    result = ValidationResult(valid=True)

    # Ensure request has JSON data
    if not request.is_json:
        result.add_error("request", "Request must be JSON")
        return result

    # Get JSON data
    try:
        data = request.get_json()
    except Exception as e:
        result.add_error("request", f"Invalid JSON: {str(e)}")
        return result

    # Validate data against schema
    schema_result = validate_schema(data, schema)
    if not schema_result.valid:
        result.valid = False
        result.errors.extend(schema_result.errors)

    return result
