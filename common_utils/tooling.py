"""
Tool registry for agentic reasoning and integration.

This module allows registration and retrieval of callable tools (functions, APIs, etc.)
for use by agent wrappers.
"""

# ruff: noqa: C901, N802

from __future__ import annotations

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
        return match.group(1)
    return description

# Example tool: simple calculator (unchanged)
MAX_EXPONENT_VALUE = 100

def calculator(expression: str) -> object:
    """
    Evaluate a mathematical expression safely and return the result.

    Args:
        expression: A string containing a mathematical expression to evaluate

    Returns:
        The result of the calculation or an error message

    """
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



def text_analyzer(text: str) -> str:
    """
    Analyze text for basic sentiment and characteristics.

    Args:
        text (str): The text to analyze.

    Returns:
        str: Analysis results including sentiment and basic metrics.

    """
    # Basic sentiment analysis using simple keyword matching
    positive_words = ["good", "great", "excellent", "fantastic", "amazing", "wonderful", "love", "like", "happy", "positive"]
    negative_words = ["bad", "terrible", "awful", "hate", "dislike", "sad", "negative", "horrible", "worst"]

    try:
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
    except ValueError as e:
        return f"Error analyzing text: {e}"
    else:
        return f"Sentiment: {sentiment} | Words: {word_count} | Characters: {char_count} | Positive indicators: {positive_count} | Negative indicators: {negative_count}"


# Register the text analyzer tool
register_tool("text_analyzer", text_analyzer)
