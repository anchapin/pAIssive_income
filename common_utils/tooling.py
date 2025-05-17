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
def calculator(expression: str) -> object:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression (str): A string math expression (e.g., "2 + 2 * 3").

    Returns:
        The result of the expression.

    """
    try:
        # Use a safer approach with a custom parser
        import re
        import operator

        # Define allowed operators and their functions
        operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            '%': operator.mod
        }

        # Validate input - only allow numbers, operators, and whitespace
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.\%\*]+$', expression):
            return "Error: Invalid characters in expression"

        # Disallow potentially dangerous patterns
        if '**' in expression and any(n > 1000 for n in [
            float(x) for x in re.findall(r'\d+', expression) if x.isdigit()
        ]):
            return "Error: Exponentiation with large numbers not allowed"

        # Use Python's built-in eval with a restricted namespace
        # This is safer than using ast.literal_eval for expressions
        result = eval(expression, {"__builtins__": {}}, operators)
        return result
    except Exception as e:
        return f"Error: {e}"


# Register the example calculator tool
register_tool("calculator", calculator)
