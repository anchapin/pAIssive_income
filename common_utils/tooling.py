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
    Evaluate a mathematical expression (use with caution).

    Args:
        expression (str): A string math expression (e.g., "2 + 2 * 3").

    Returns:
        The result of the expression.

    """
    try:
        # Use ast.literal_eval instead of eval for better security
        import ast

        return ast.literal_eval(expression)
    except (SyntaxError, ValueError) as e:
        return f"Error: {e}"


# Register the example calculator tool
register_tool("calculator", calculator)
