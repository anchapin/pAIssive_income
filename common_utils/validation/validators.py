"""
Basic validation functions for common data types.

This module provides validation functions for basic data types such as strings,
numbers, dates, and more complex structures like lists and dictionaries.
"""

import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


def validate_string(
    value: Any, min_length: int = None, max_length: int = None, strip: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a string and optionally check its length.

    Args:
        value: The value to validate
        min_length: Minimum length of the string
        max_length: Maximum length of the string
        strip: Whether to strip whitespace before checking length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, "Value must be a string"

    if strip:
        value = value.strip()

    if min_length is not None and len(value) < min_length:
        return False, f"String must be at least {min_length} characters long"

    if max_length is not None and len(value) > max_length:
        return False, f"String must be at most {max_length} characters long"

    return True, None


def validate_email(value: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a valid email address.

    Args:
        value: The value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First check if it's a string
    is_string, error = validate_string(value)
    if not is_string:
        return is_string, error

    # Use a simple regex for email validation
    pattern = r"^[a - zA - Z0 - 9._%+-]+@[a - zA - Z0 - 9.-]+\.[a - zA - Z]{2,}$"
    if not re.match(pattern, value):
        return False, "Invalid email address format"

    return True, None


def validate_number(
    value: Any, min_value: float = None, max_value: float = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a number and optionally check its range.

    Args:
        value: The value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, "Value must be a number"

    if min_value is not None and value < min_value:
        return False, f"Value must be at least {min_value}"

    if max_value is not None and value > max_value:
        return False, f"Value must be at most {max_value}"

    return True, None


def validate_integer(
    value: Any, min_value: int = None, max_value: int = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is an integer and optionally check its range.

    Args:
        value: The value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int) or isinstance(value, bool):
        return False, "Value must be an integer"

    return validate_number(value, min_value, max_value)


def validate_boolean(value: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a boolean.

    Args:
        value: The value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, bool):
        return False, "Value must be a boolean"

    return True, None


def validate_list(
    value: Any,
    min_length: int = None,
    max_length: int = None,
    item_validator: Callable = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a list and optionally check its length and items.

    Args:
        value: The value to validate
        min_length: Minimum length of the list
        max_length: Maximum length of the list
        item_validator: Function to validate each item in the list

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, list):
        return False, "Value must be a list"

    if min_length is not None and len(value) < min_length:
        return False, f"List must have at least {min_length} items"

    if max_length is not None and len(value) > max_length:
        return False, f"List must have at most {max_length} items"

    if item_validator is not None:
        for i, item in enumerate(value):
            is_valid, error = item_validator(item)
            if not is_valid:
                return False, f"Item at index {i} is invalid: {error}"

    return True, None


def validate_dict(
    value: Any,
    required_keys: List[str] = None,
    key_validators: Dict[str, Callable] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a dictionary and optionally check its keys and values.

    Args:
        value: The value to validate
        required_keys: List of keys that must be present
        key_validators: Dictionary of key -> validator function

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, dict):
        return False, "Value must be a dictionary"

    if required_keys is not None:
        for key in required_keys:
            if key not in value:
                return False, f"Required key '{key}' is missing"

    if key_validators is not None:
        for key, validator in key_validators.items():
            if key in value:
                is_valid, error = validator(value[key])
                if not is_valid:
                    return False, f"Value for key '{key}' is invalid: {error}"

    return True, None


def validate_date(
    value: Any,
    min_date: datetime = None,
    max_date: datetime = None,
    format_str: str = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a valid date.

    Args:
        value: The value to validate (string or datetime)
        min_date: Minimum allowed date
        max_date: Maximum allowed date
        format_str: Format string for parsing date strings

    Returns:
        Tuple of (is_valid, error_message)
    """
    date_obj = None

    if isinstance(value, datetime):
        date_obj = value
    elif isinstance(value, str) and format_str is not None:
        try:
            date_obj = datetime.strptime(value, format_str)
        except ValueError:
            return False, f"Date format must be {format_str}"
    else:
        return False, "Value must be a datetime object or a string with a valid format"

    if min_date is not None and date_obj < min_date:
        return (
            False,
            f"Date must be on or after {min_date.strftime(format_str or ' % Y-%m-%d')}",
        )

    if max_date is not None and date_obj > max_date:
        return (
            False,
            f"Date must be on or before {max_date.strftime(format_str or ' % Y-%m-%d')}",
                
        )

    return True, None


def validate_choice(value: Any, choices: List[Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is one of the allowed choices.

    Args:
        value: The value to validate
        choices: List of allowed values

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value not in choices:
        choices_str = ", ".join(str(c) for c in choices)
        return False, f"Value must be one of: {choices_str}"

    return True, None


def validate_regex(
    value: Any, pattern: str, error_message: str = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a string matches a regular expression pattern.

    Args:
        value: The value to validate
        pattern: Regular expression pattern to match
        error_message: Custom error message

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First check if it's a string
    is_string, error = validate_string(value)
    if not is_string:
        return is_string, error

    if not re.match(pattern, value):
        return False, error_message or f"Value doesn't match the required pattern"

    return True, None
