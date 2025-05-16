"""
Tool registry for agentic reasoning and integration.

This module allows registration and retrieval of callable tools (functions, APIs, etc.)
for use by agent wrappers.
"""

from typing import Callable, Dict, Any

# Global tool registry
_TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


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


def list_tools() -> Dict[str, Callable[..., Any]]:
    """
    List all registered tools.

    Returns:
        Dict[str, Callable]: Mapping of tool names to functions.
    """
    return dict(_TOOL_REGISTRY)


# Example tool: simple calculator
def calculator(expression: str) -> Any:
    """
    Evaluate a mathematical expression (use with caution).

    Args:
        expression (str): A string math expression (e.g., "2 + 2 * 3").

    Returns:
        The result of the expression.
    """
    try:
        return eval(expression, {"__builtins__": {}})
    except Exception as e:
        return f"Error: {e}"


# Register the example calculator tool
register_tool("calculator", calculator)
