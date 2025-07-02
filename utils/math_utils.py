"""Utility functions for mathematical operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b

    """
    return a + b


def subtract(a: float, b: float) -> float:
    """
    Subtract b from a.

    Args:
        a: First number
        b: Second number

    Returns:
        Difference of a and b

    """
    return a - b


def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b

    """
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide a by b.

    Args:
        a: First number
        b: Second number

    Returns:
        Quotient of a and b

    Raises:
        ZeroDivisionError: If b is zero

    """
    if b == 0:
        msg = "Cannot divide by zero"
        raise ZeroDivisionError(msg)
    return a / b


def average(numbers: Sequence[float]) -> float:
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        Average of the numbers

    Raises:
        ValueError: If the list is empty

    """
    if not numbers:
        msg = "Cannot calculate average of empty list"
        raise ValueError(msg)
    return sum(numbers) / len(numbers)


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage of part from whole.

    Args:
        part: The part value
        whole: The whole value

    Returns:
        Percentage value

    Raises:
        ZeroDivisionError: If whole is zero
    """
    if whole == 0:
        msg = "Cannot calculate percentage with zero whole"
        raise ZeroDivisionError(msg)
    return round((part / whole) * 100, 2)


def validate_number(value) -> bool:
    """
    Validate if a value is a number.

    Args:
        value: Value to validate

    Returns:
        True if value is a number, False otherwise
    """
    if value is None:
        return False
    try:
        float(value)
    except (ValueError, TypeError):
        return False
    else:
        return True


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Format a number as currency.

    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use

    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"
