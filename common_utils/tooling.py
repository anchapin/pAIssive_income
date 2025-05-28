"""
Tool registry for agentic reasoning and integration.

This module allows registration and retrieval of callable tools (functions, APIs, etc.)
for use by agent wrappers.
"""

from __future__ import annotations

# Global tool registry
from typing import Any, Callable, Optional

# Tool registry: maps tool name to dict with 'func', optional 'keywords', optional 'input_preprocessor'
_TOOL_REGISTRY: dict[str, dict[str, Any]] = {}

def register_tool(
    name: str,
    func: Callable[..., Any],
    *,
    keywords: Optional[list[str]] = None,
    input_preprocessor: Optional[Callable[[str], Any]] = None,
) -> None:
    """
    Register a callable tool with a name and optional metadata.

    Args:
        name (str): Name of the tool.
        func (Callable): Function implementing the tool.
        keywords (list[str], optional): Keywords for heuristic selection.
        input_preprocessor (Callable, optional): Function to extract/prepare input for this tool from a task description.

    """
    _TOOL_REGISTRY[name] = {
        "func": func,
        "keywords": keywords or [],
        "input_preprocessor": input_preprocessor,
    }

def get_tool(name: str) -> Callable[..., Any]:
    """Retrieve a registered tool's main callable by name."""
    return _TOOL_REGISTRY[name]["func"]

def list_tools() -> dict[str, dict[str, Any]]:
    """List all registered tools and their metadata."""
    return dict(_TOOL_REGISTRY)

# Example input preprocessor for calculator
def calculator_input_preprocessor(description: str) -> str:
    """
    Extract a math expression from the task description for the calculator tool.
    For demo: use a simple regex, as before.
    """
    import re
    match = re.search(r"([0-9\+\-\*\/\.\s\%\(\)]+)", description)
    if match:
        return match.group(1).strip()
    return description

# Example tool: simple calculator (unchanged)
MAX_EXPONENT_VALUE = 100

def calculator(expression: str) -> object:
    # ... (same as before)
    import ast
    import operator
    import re

    operators = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "**": operator.pow,
        "%": operator.mod,
    }

    try:
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\%]+$", expression):
            return "Error: Invalid characters in expression"

        if "**" in expression and any(
            n > MAX_EXPONENT_VALUE
            for n in [float(x) for x in re.findall(r"\d+", expression) if x.isdigit()]
        ):
            return (
                f"Error: Exponentiation with values > {MAX_EXPONENT_VALUE} not allowed"
            )
        try:
            return ast.literal_eval(expression)
        except (ValueError, SyntaxError):
            class SafeExpressionEvaluator(ast.NodeVisitor):
                def visit_BinOp(self, node: ast.BinOp) -> object:
                    left = self.visit(node.left)
                    right = self.visit(node.right)
                    if isinstance(node.op, ast.Add):
                        return operators["+"](left, right)
                    if isinstance(node.op, ast.Sub):
                        return operators["-"](left, right)
                    if isinstance(node.op, ast.Mult):
                        return operators["*"](left, right)
                    if isinstance(node.op, ast.Div):
                        return operators["/"](left, right)
                    if isinstance(node.op, ast.Pow):
                        return operators["**"](left, right)
                    if isinstance(node.op, ast.Mod):
                        return operators["%"](left, right)
                    error_msg = f"Unsupported operator: {type(node.op).__name__}"
                    raise ValueError(error_msg)
                def visit_UnaryOp(self, node: ast.UnaryOp) -> object:
                    operand = self.visit(node.operand)
                    if isinstance(node.op, ast.USub):
                        return -operand
                    if isinstance(node.op, ast.UAdd):
                        return operand
                    error_msg = f"Unsupported unary operator: {type(node.op).__name__}"
                    raise ValueError(error_msg)
                def visit_Num(self, node: ast.Num) -> object:
                    return node.n
                def visit_Constant(self, node: ast.Constant) -> object:
                    return node.value
                def generic_visit(self, node: ast.AST) -> None:
                    error_msg = f"Unsupported node type: {type(node).__name__}"
                    raise ValueError(error_msg)
            parsed_expr = ast.parse(expression, mode="eval")
            evaluator = SafeExpressionEvaluator()
            return evaluator.visit(parsed_expr.body)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError, OverflowError) as e:
        return f"Error: {e}"

# Register the calculator tool with keywords and input preprocessor
register_tool(
    "calculator",
    calculator,
    keywords=["calculate", "math", "add", "subtract", "multiply", "divide", "+", "-", "*", "/", "%"],
    input_preprocessor=calculator_input_preprocessor,
)
