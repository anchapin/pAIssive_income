"""
Validation helpers for the UI module.

This module provides helper functions for validating user input in the UI.
These functions make it easy to validate requests against Pydantic schemas
and handle validation errors consistently.
"""

import logging
from typing import Type, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from flask import request

from .errors import ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def validate_form_data(schema_cls: Type[T]) -> T:
    """
    Validate form data against a Pydantic schema.
    
    Args:
        schema_cls: The Pydantic schema class to validate against
        
    Returns:
        An instance of the schema class with validated data
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Convert form data to dict
        form_data = request.form.to_dict(flat=False)
        
        # Handle single values vs lists
        cleaned_data = {}
        for key, value in form_data.items():
            cleaned_data[key] = value[0] if len(value) == 1 else value
        
        # Validate data
        validated_data = schema_cls.model_validate(cleaned_data)
        return validated_data
    
    except PydanticValidationError as e:
        _handle_validation_error(e)


def validate_json_data(schema_cls: Type[T]) -> T:
    """
    Validate JSON data against a Pydantic schema.
    
    Args:
        schema_cls: The Pydantic schema class to validate against
        
    Returns:
        An instance of the schema class with validated data
        
    Raises:
        ValidationError: If validation fails or if request does not contain valid JSON
    """
    try:
        # Get JSON data
        json_data = request.get_json(silent=False)
        if json_data is None:
            raise ValidationError(
                message="No JSON data provided or invalid JSON format",
                validation_errors=[{"field": "body", "error": "Invalid or missing JSON data"}]
            )
        
        # Validate data
        validated_data = schema_cls.model_validate(json_data)
        return validated_data
    
    except PydanticValidationError as e:
        _handle_validation_error(e)


def validate_query_params(schema_cls: Type[T]) -> T:
    """
    Validate query parameters against a Pydantic schema.
    
    Args:
        schema_cls: The Pydantic schema class to validate against
        
    Returns:
        An instance of the schema class with validated data
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Convert query parameters to dict
        query_params = request.args.to_dict(flat=True)
        
        # Validate data
        validated_data = schema_cls.model_validate(query_params)
        return validated_data
    
    except PydanticValidationError as e:
        _handle_validation_error(e)


def sanitize_input(input_value: str) -> str:
    """
    Sanitize a string input to prevent XSS attacks.
    
    Args:
        input_value: The string to sanitize
        
    Returns:
        A sanitized string
    """
    if input_value is None:
        return ""
    
    # Strip leading/trailing whitespace
    sanitized = input_value.strip()
    
    # Replace potentially dangerous characters
    replacements = {
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
        "\\": "&#x5C;",
        "`": "&#96;"
    }
    
    for char, replacement in replacements.items():
        sanitized = sanitized.replace(char, replacement)
    
    return sanitized


def _handle_validation_error(pydantic_error: PydanticValidationError) -> None:
    """
    Handle Pydantic validation errors and convert them to our custom ValidationError.
    
    Args:
        pydantic_error: The Pydantic validation error
        
    Raises:
        ValidationError: Always raised with details from the Pydantic error
    """
    # Format error messages
    validation_errors = []
    for error in pydantic_error.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field_path,
            "error": error["msg"]
        })
    
    # Log the validation error
    logger.warning(f"Validation error: {validation_errors}")
    
    # Raise our custom ValidationError
    raise ValidationError(
        message="Input validation failed",
        validation_errors=validation_errors
    )