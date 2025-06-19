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
