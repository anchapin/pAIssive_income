"""
"""
Validation helpers for the UI module.
Validation helpers for the UI module.


This module provides helper functions for validating user input in the UI.
This module provides helper functions for validating user input in the UI.
These functions make it easy to validate requests against Pydantic schemas
These functions make it easy to validate requests against Pydantic schemas
and handle validation errors consistently.
and handle validation errors consistently.
"""
"""


import logging
import logging
from typing import Type, TypeVar
from typing import Type, TypeVar


from pydantic import BaseModel
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from pydantic import ValidationError as PydanticValidationError


from flask import request
from flask import request


from .errors import ValidationError
from .errors import ValidationError


logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)
T = TypeVar("T", bound=BaseModel)


def validate_form_data(schema_cls: Type[T]) -> T:
    def validate_form_data(schema_cls: Type[T]) -> T:
    """Validate form data against a Pydantic schema.
    """Validate form data against a Pydantic schema.


    Args:
    Args:
    schema_cls: The Pydantic schema class to validate against
    schema_cls: The Pydantic schema class to validate against


    Returns:
    Returns:
    An instance of the schema class with validated data
    An instance of the schema class with validated data


    Raises:
    Raises:
    ValidationError: If validation fails
    ValidationError: If validation fails
    """
    """
    try:
    try:
    # Convert form data to dict
    # Convert form data to dict
    form_data = request.form.to_dict(flat=False)
    form_data = request.form.to_dict(flat=False)


    # Handle single values vs lists
    # Handle single values vs lists
    cleaned_data = {}
    cleaned_data = {}
    for key, value in form_data.items():
    for key, value in form_data.items():
    cleaned_data[key] = value[0] if len(value) == 1 else value
    cleaned_data[key] = value[0] if len(value) == 1 else value


    # Validate data
    # Validate data
    validated_data = schema_cls.model_validate(cleaned_data)
    validated_data = schema_cls.model_validate(cleaned_data)
    return validated_data
    return validated_data


except PydanticValidationError as e:
except PydanticValidationError as e:
    _handle_validation_error(e)
    _handle_validation_error(e)


    def validate_json_data(schema_cls: Type[T]) -> T:
    def validate_json_data(schema_cls: Type[T]) -> T:
    """Validate JSON data against a Pydantic schema.
    """Validate JSON data against a Pydantic schema.


    Args:
    Args:
    schema_cls: The Pydantic schema class to validate against
    schema_cls: The Pydantic schema class to validate against


    Returns:
    Returns:
    An instance of the schema class with validated data
    An instance of the schema class with validated data


    Raises:
    Raises:
    ValidationError: If validation fails or if request does not contain valid JSON
    ValidationError: If validation fails or if request does not contain valid JSON
    """
    """
    try:
    try:
    # Get JSON data
    # Get JSON data
    json_data = request.get_json(silent=False)
    json_data = request.get_json(silent=False)
    if json_data is None:
    if json_data is None:
    raise ValidationError(
    raise ValidationError(
    message="No JSON data provided or invalid JSON format",
    message="No JSON data provided or invalid JSON format",
    validation_errors=[
    validation_errors=[
    {"field": "body", "error": "Invalid or missing JSON data"}
    {"field": "body", "error": "Invalid or missing JSON data"}
    ],
    ],
    )
    )


    # Validate data
    # Validate data
    validated_data = schema_cls.model_validate(json_data)
    validated_data = schema_cls.model_validate(json_data)
    return validated_data
    return validated_data


except PydanticValidationError as e:
except PydanticValidationError as e:
    _handle_validation_error(e)
    _handle_validation_error(e)


    def validate_query_params(schema_cls: Type[T]) -> T:
    def validate_query_params(schema_cls: Type[T]) -> T:
    """Validate query parameters against a Pydantic schema.
    """Validate query parameters against a Pydantic schema.


    Args:
    Args:
    schema_cls: The Pydantic schema class to validate against
    schema_cls: The Pydantic schema class to validate against


    Returns:
    Returns:
    An instance of the schema class with validated data
    An instance of the schema class with validated data


    Raises:
    Raises:
    ValidationError: If validation fails
    ValidationError: If validation fails
    """
    """
    try:
    try:
    # Convert query parameters to dict
    # Convert query parameters to dict
    query_params = request.args.to_dict(flat=True)
    query_params = request.args.to_dict(flat=True)


    # Validate data
    # Validate data
    validated_data = schema_cls.model_validate(query_params)
    validated_data = schema_cls.model_validate(query_params)
    return validated_data
    return validated_data


except PydanticValidationError as e:
except PydanticValidationError as e:
    _handle_validation_error(e)
    _handle_validation_error(e)


    def sanitize_input(input_value: str) -> str:
    def sanitize_input(input_value: str) -> str:
    """Sanitize a string input to prevent XSS attacks.
    """Sanitize a string input to prevent XSS attacks.


    Args:
    Args:
    input_value: The string to sanitize
    input_value: The string to sanitize


    Returns:
    Returns:
    A sanitized string
    A sanitized string
    """
    """
    if input_value is None:
    if input_value is None:
    return ""
    return ""


    # Strip leading/trailing whitespace
    # Strip leading/trailing whitespace
    sanitized = input_value.strip()
    sanitized = input_value.strip()


    # Replace potentially dangerous characters
    # Replace potentially dangerous characters
    replacements = {
    replacements = {
    "<": "&lt;",
    "<": "&lt;",
    ">": "&gt;",
    ">": "&gt;",
    '"': "&quot;",
    '"': "&quot;",
    "'": "&#x27;",
    "'": "&#x27;",
    "/": "&#x2F;",
    "/": "&#x2F;",
    "\\": "&#x5C;",
    "\\": "&#x5C;",
    "`": "&#96;",
    "`": "&#96;",
    }
    }


    for char, replacement in replacements.items():
    for char, replacement in replacements.items():
    sanitized = sanitized.replace(char, replacement)
    sanitized = sanitized.replace(char, replacement)


    return sanitized
    return sanitized


    def _handle_validation_error(pydantic_error: PydanticValidationError) -> None:
    def _handle_validation_error(pydantic_error: PydanticValidationError) -> None:
    """Handle Pydantic validation errors and convert them to our custom ValidationError.
    """Handle Pydantic validation errors and convert them to our custom ValidationError.


    Args:
    Args:
    pydantic_error: The Pydantic validation error
    pydantic_error: The Pydantic validation error


    Raises:
    Raises:
    ValidationError: Always raised with details from the Pydantic error
    ValidationError: Always raised with details from the Pydantic error
    """
    """
    # Format error messages
    # Format error messages
    validation_errors = []
    validation_errors = []
    for error in pydantic_error.errors():
    for error in pydantic_error.errors():
    field_path = ".".join(str(loc) for loc in error["loc"])
    field_path = ".".join(str(loc) for loc in error["loc"])
    validation_errors.append({"field": field_path, "error": error["msg"]})
    validation_errors.append({"field": field_path, "error": error["msg"]})


    # Log the validation error
    # Log the validation error
    logger.warning(f"Validation error: {validation_errors}")
    logger.warning(f"Validation error: {validation_errors}")


    # Raise our custom ValidationError
    # Raise our custom ValidationError
    raise ValidationError(
    raise ValidationError(
    message="Input validation failed", validation_errors=validation_errors
    message="Input validation failed", validation_errors=validation_errors
    )
    )

