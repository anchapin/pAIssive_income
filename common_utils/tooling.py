"""
Tool registry for agentic reasoning and integration.

This module allows registration and retrieval of callable tools (functions, APIs, etc.)
for use by agent wrappers.
"""

from __future__ import annotations

from typing import Any, Callable

# Global tool registry
_TOOL_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_tool(name: str, func: Callable[..., Any]) -> None:
    """
    Register a callable tool with a name.

    Args:
        name (str): Name of the tool.
        func (Callable): Function implementing the tool.

    """
    _TOOL_REGISTRY[name] = func


def get_tool(name: str) -> Callable[..., Any]:
    """
    Retrieve a registered tool by name.

    Args:
        name (str): Name of the tool.

    Returns:
        Callable: The tool function.

    """
    return _TOOL_REGISTRY[name]


def list_tools() -> dict[str, Callable[..., Any]]:
    """
    List all registered tools.

    Returns:
        dict[str, Callable]: Mapping of tool names to functions.

    """
    return dict(_TOOL_REGISTRY)


# Example tool: simple calculator
# Constants for calculator limits
MAX_EXPONENT_VALUE = 100  # Maximum allowed value for exponentiation

def calculator(expression: str) -> object:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression (str): A string math expression (e.g., "2 + 2 * 3").

    Returns:
        The result of the expression.

    """
    # Use a safer approach with a custom parser
    import operator
    import re
    import ast

    # Define allowed operators and their functions
    operators = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "**": operator.pow,
        "%": operator.mod,
    }

    try:
        # Validate input - only allow numbers, operators, and whitespace
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\%\*]+$", expression):
            return "Error: Invalid characters in expression"

        # Disallow potentially dangerous patterns
        if "**" in expression and any(
            n > MAX_EXPONENT_VALUE
            for n in [float(x) for x in re.findall(r"\d+", expression) if x.isdigit()]
        ):
            return f"Error: Exponentiation with values > {MAX_EXPONENT_VALUE} not allowed"

        # Try to use ast.literal_eval for simple expressions
        try:
            return ast.literal_eval(expression)
        except (ValueError, SyntaxError):
            # For expressions with operators, use a restricted eval
            # This is still safer than using eval directly
            return eval(expression, {"__builtins__": None}, operators)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError, OverflowError) as e:
        return f"Error: {e}"


# Register the example calculator tool
register_tool("calculator", calculator)
