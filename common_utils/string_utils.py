"""
"""
String utilities for the pAIssive Income project.
String utilities for the pAIssive Income project.


This module provides common string manipulation functions used across the project.
This module provides common string manipulation functions used across the project.
"""
"""




import re
import re
import unicodedata
import unicodedata
from typing import Optional, Union
from typing import Optional, Union




def is_empty():
    def is_empty():
    (s: Optional[str]) -> bool:
    (s: Optional[str]) -> bool:
    """
    """
    Check if a string is empty or None.
    Check if a string is empty or None.


    Args:
    Args:
    s: String to check
    s: String to check


    Returns:
    Returns:
    True if the string is empty or None, False otherwise
    True if the string is empty or None, False otherwise
    """
    """
    return s is None or s == ""
    return s is None or s == ""




    def is_blank(s: Optional[str]) -> bool:
    def is_blank(s: Optional[str]) -> bool:
    """
    """
    Check if a string is blank (empty, None, or only whitespace).
    Check if a string is blank (empty, None, or only whitespace).


    Args:
    Args:
    s: String to check
    s: String to check


    Returns:
    Returns:
    True if the string is blank, False otherwise
    True if the string is blank, False otherwise
    """
    """
    return s is None or s.strip() == ""
    return s is None or s.strip() == ""




    def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """
    """
    Truncate a string to a maximum length.
    Truncate a string to a maximum length.


    Args:
    Args:
    s: String to truncate
    s: String to truncate
    max_length: Maximum length
    max_length: Maximum length
    suffix: Suffix to add if truncated (default: "...")
    suffix: Suffix to add if truncated (default: "...")


    Returns:
    Returns:
    Truncated string
    Truncated string
    """
    """
    if len(s) <= max_length:
    if len(s) <= max_length:
    return s
    return s
    return s[: max_length - len(suffix)] + suffix
    return s[: max_length - len(suffix)] + suffix




    def slugify(s: str, separator: str = "-") -> str:
    def slugify(s: str, separator: str = "-") -> str:
    """
    """
    Convert a string to a slug.
    Convert a string to a slug.


    Args:
    Args:
    s: String to convert
    s: String to convert
    separator: Separator to use (default: "-")
    separator: Separator to use (default: "-")


    Returns:
    Returns:
    Slug
    Slug
    """
    """
    # Convert to lowercase
    # Convert to lowercase
    s = s.lower()
    s = s.lower()


    # Remove accents
    # Remove accents
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


    # Replace non-alphanumeric characters with separator
    # Replace non-alphanumeric characters with separator
    s = re.sub(r"[^a-z0-9]+", separator, s)
    s = re.sub(r"[^a-z0-9]+", separator, s)


    # Remove leading/trailing separators
    # Remove leading/trailing separators
    s = s.strip(separator)
    s = s.strip(separator)


    return s
    return s




    def camel_to_snake(s: str) -> str:
    def camel_to_snake(s: str) -> str:
    """
    """
    Convert a camelCase string to snake_case.
    Convert a camelCase string to snake_case.


    Args:
    Args:
    s: String to convert
    s: String to convert


    Returns:
    Returns:
    snake_case string
    snake_case string
    """
    """
    # Insert underscore before uppercase letters
    # Insert underscore before uppercase letters
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)


    # Convert to lowercase
    # Convert to lowercase
    return s.lower()
    return s.lower()




    def snake_to_camel(s: str, capitalize_first: bool = False) -> str:
    def snake_to_camel(s: str, capitalize_first: bool = False) -> str:
    """
    """
    Convert a snake_case string to camelCase.
    Convert a snake_case string to camelCase.


    Args:
    Args:
    s: String to convert
    s: String to convert
    capitalize_first: Whether to capitalize the first letter (default: False)
    capitalize_first: Whether to capitalize the first letter (default: False)


    Returns:
    Returns:
    camelCase string
    camelCase string
    """
    """
    # Split by underscore
    # Split by underscore
    parts = s.split("_")
    parts = s.split("_")


    # Capitalize each part except the first one
    # Capitalize each part except the first one
    if capitalize_first:
    if capitalize_first:
    return "".join(part.capitalize() for part in parts)
    return "".join(part.capitalize() for part in parts)
    return parts[0] + "".join(part.capitalize() for part in parts[1:])
    return parts[0] + "".join(part.capitalize() for part in parts[1:])




    def format_currency(
    def format_currency(
    amount: Union[int, float], currency: str = "$", decimal_places: int = 2
    amount: Union[int, float], currency: str = "$", decimal_places: int = 2
    ) -> str:
    ) -> str:
    """
    """
    Format a number as currency.
    Format a number as currency.


    Args:
    Args:
    amount: Amount to format
    amount: Amount to format
    currency: Currency symbol (default: "$")
    currency: Currency symbol (default: "$")
    decimal_places: Number of decimal places (default: 2)
    decimal_places: Number of decimal places (default: 2)


    Returns:
    Returns:
    Formatted currency string
    Formatted currency string
    """
    """
    return f"{currency}{amount:,.{decimal_places}f}"
    return f"{currency}{amount:,.{decimal_places}f}"




    def format_number(
    def format_number(
    number: Union[int, float], decimal_places: int = 0, thousands_separator: str = ","
    number: Union[int, float], decimal_places: int = 0, thousands_separator: str = ","
    ) -> str:
    ) -> str:
    """
    """
    Format a number with thousands separator.
    Format a number with thousands separator.


    Args:
    Args:
    number: Number to format
    number: Number to format
    decimal_places: Number of decimal places (default: 0)
    decimal_places: Number of decimal places (default: 0)
    thousands_separator: Thousands separator (default: ",")
    thousands_separator: Thousands separator (default: ",")


    Returns:
    Returns:
    Formatted number string
    Formatted number string
    """
    """
    return f"{number:,.{decimal_places}f}".replace(",", thousands_separator)
    return f"{number:,.{decimal_places}f}".replace(",", thousands_separator)




    def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    """
    Format a number as a percentage.
    Format a number as a percentage.


    Args:
    Args:
    value: Value to format (0.1 = 10%)
    value: Value to format (0.1 = 10%)
    decimal_places: Number of decimal places (default: 1)
    decimal_places: Number of decimal places (default: 1)


    Returns:
    Returns:
    Formatted percentage string
    Formatted percentage string
    """
    """
    return f"{value * 100:.{decimal_places}f}%"
    return f"{value * 100:.{decimal_places}f}%"