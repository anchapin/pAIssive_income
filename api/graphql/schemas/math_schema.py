"""GraphQL schema exposing math utilities as resolvers."""

from __future__ import annotations

import strawberry
from typing import List

from utils.math_utils import add, subtract, multiply, divide, average

@strawberry.type
class Query:
    """Root GraphQL query exposing math utilities."""

    @strawberry.field(description="Add two numbers")
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Sum of a and b.
        """
        return add(a, b)

    @strawberry.field(description="Subtract two numbers")
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract b from a.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Difference of a and b.
        """
        return subtract(a, b)

    @strawberry.field(description="Multiply two numbers")
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Product of a and b.
        """
        return multiply(a, b)

    @strawberry.field(description="Divide a by b")
    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Quotient of a and b.

        Raises:
            ValueError: If dividing by zero.
        """
        try:
            return divide(a, b)
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero")

    @strawberry.field(description="Average a list of numbers")
    def average(self, numbers: List[float]) -> float:
        """
        Calculate average of a list of numbers.

        Args:
            numbers: List of numbers.

        Returns:
            Average of the numbers.

        Raises:
            ValueError: If the list is empty.
        """
        return average(numbers)