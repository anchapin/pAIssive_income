"""
String utilities for the pAIssive Income project.

This module provides common string manipulation functions used across the project.
"""

import re
import unicodedata
from typing import Optional, Union


def is_empty(s: Optional[str]) -> bool:
    """
    Check if a string is empty or None.

    Args:
        s: String to check

    Returns:
        True if the string is empty or None, False otherwise
    """
    return s is None or s == ""


def is_blank(s: Optional[str]) -> bool:
    """
    Check if a string is blank (empty, None, or only whitespace).

    Args:
        s: String to check

    Returns:
        True if the string is blank, False otherwise
    """
    return s is None or s.strip() == ""


def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated (default: "...")

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def slugify(s: str, separator: str = " - ") -> str:
    """
    Convert a string to a slug.

    Args:
        s: String to convert
        separator: Separator to use (default: " - ")

    Returns:
        Slug
    """
    # Convert to lowercase
    s = s.lower()

    # Remove accents
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

    # Replace non - alphanumeric characters with separator
    s = re.sub(r"[^a - z0 - 9] + ", separator, s)

    # Remove leading / trailing separators
    s = s.strip(separator)

    return s


def camel_to_snake(s: str) -> str:
    """
    Convert a camelCase string to snake_case.

    Args:
        s: String to convert

    Returns:
        snake_case string
    """
    # Insert underscore before uppercase letters
    s = re.sub(r"(?<!^)(?=[A - Z])", "_", s)

    # Convert to lowercase
    return s.lower()


def snake_to_camel(s: str, capitalize_first: bool = False) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        s: String to convert
        capitalize_first: Whether to capitalize the first letter (default: False)

    Returns:
        camelCase string
    """
    # Split by underscore
    parts = s.split("_")

    # Capitalize each part except the first one
    if capitalize_first:
        return "".join(part.capitalize() for part in parts)
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def format_currency(amount: Union[int, float], currency: str = "$", 
    decimal_places: int = 2) -> str:
    """
    Format a number as currency.

    Args:
        amount: Amount to format
        currency: Currency symbol (default: "$")
        decimal_places: Number of decimal places (default: 2)

    Returns:
        Formatted currency string
    """
    return f"{currency}{amount:,.{decimal_places}f}"


def format_number(
    number: Union[int, float], decimal_places: int = 0, thousands_separator: str = ","
) -> str:
    """
    Format a number with thousands separator.

    Args:
        number: Number to format
        decimal_places: Number of decimal places (default: 0)
        thousands_separator: Thousands separator (default: ",")

    Returns:
        Formatted number string
    """
    return f"{number:,.{decimal_places}f}".replace(",", thousands_separator)


def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format a number as a percentage.

    Args:
        value: Value to format (0.1 = 10%)
        decimal_places: Number of decimal places (default: 1)

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"
