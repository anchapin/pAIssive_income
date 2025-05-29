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


def calculator(expression: str) -> object:  # noqa: C901
    """
    Evaluate a mathematical expression safely.

    Args:
        expression (str): A string math expression (e.g., "2 + 2 * 3").

    Returns:
        The result of the expression.

    """
    # Use a safer approach with a custom parser
    import ast
    import operator
    import re

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
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\%]+$", expression):
            return "Error: Invalid characters in expression"

        # Disallow potentially dangerous patterns
        if "**" in expression and any(
            n > MAX_EXPONENT_VALUE
            for n in [float(x) for x in re.findall(r"\d+", expression) if x.isdigit()]
        ):
            return (
                f"Error: Exponentiation with values > {MAX_EXPONENT_VALUE} not allowed"
            )

        # Try to use ast.literal_eval for simple expressions
        try:
            return ast.literal_eval(expression)
        except (ValueError, SyntaxError):
            # For expressions with operators, implement a safer alternative to eval
            # Parse the expression and evaluate it using the operators dictionary
            import ast

            # Create a custom evaluator that uses our restricted operators
            # Note: Method names must match AST node types exactly for NodeVisitor to work
            # We need to disable N802 (function name should be lowercase) for these methods
            class SafeExpressionEvaluator(ast.NodeVisitor):
                # Method names must match AST node types exactly
                def visit_BinOp(self, node: ast.BinOp) -> object:  # noqa: N802
                    """Process binary operations."""
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

                # Method names must match AST node types exactly
                def visit_UnaryOp(self, node: ast.UnaryOp) -> object:  # noqa: N802
                    """Process unary operations."""
                    operand = self.visit(node.operand)
                    if isinstance(node.op, ast.USub):
                        return -operand
                    if isinstance(node.op, ast.UAdd):
                        return operand
                    error_msg = f"Unsupported unary operator: {type(node.op).__name__}"
                    raise ValueError(error_msg)

                # Method names must match AST node types exactly
                def visit_Num(self, node: ast.Num) -> object:  # noqa: N802
                    """Process numeric nodes."""
                    return node.n

                # Method names must match AST node types exactly
                def visit_Constant(self, node: ast.Constant) -> object:  # noqa: N802
                    """Process constant nodes."""
                    return node.value

                def generic_visit(self, node: ast.AST) -> None:
                    """Handle unsupported node types."""
                    error_msg = f"Unsupported node type: {type(node).__name__}"
                    raise ValueError(error_msg)

            # Parse and evaluate the expression
            parsed_expr = ast.parse(expression, mode="eval")
            evaluator = SafeExpressionEvaluator()
            return evaluator.visit(parsed_expr.body)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError, OverflowError) as e:
        return f"Error: {e}"


# Register the example calculator tool
register_tool("calculator", calculator)


def text_analyzer(text: str) -> str:
    """
    Analyze text for basic sentiment and characteristics.

    Args:
        text (str): The text to analyze.

    Returns:
        str: Analysis results including sentiment and basic metrics.

    """
    try:
        # Basic sentiment analysis using simple keyword matching
        positive_words = [
            "good",
            "great",
            "excellent",
            "fantastic",
            "amazing",
            "wonderful",
            "love",
            "like",
            "happy",
            "positive",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "dislike",
            "sad",
            "negative",
            "horrible",
            "worst",
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Basic metrics
        word_count = len(text.split())
        char_count = len(text)

        return f"Sentiment: {sentiment} | Words: {word_count} | Characters: {char_count} | Positive indicators: {positive_count} | Negative indicators: {negative_count}"

    except Exception as e:
        return f"Error analyzing text: {e}"


# Register the text analyzer tool
register_tool("text_analyzer", text_analyzer)
