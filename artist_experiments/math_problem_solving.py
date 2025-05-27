"""
Mathematical problem-solving experiment using ARTIST framework.

This module implements a basic ARTIST-based agent for solving mathematical problems.
"""

from __future__ import annotations

import logging
import re
import sys  # Added sys import

logger = logging.getLogger(__name__)

try:
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    logger.exception(
        "Sympy library not found. Please install it using 'pip install sympy'"
    )
    sys.exit(1)

try:
    from ai_models.artist_agent import ArtistAgent
    from common_utils import tooling
except ImportError:
    logger.exception(
        "Failed to import local modules (ArtistAgent or tooling). Ensure they are in PYTHONPATH."
    )
    sys.exit(1)


class MathTool:
    """Mathematical tool for ARTIST experiments."""

    @staticmethod
    def solve_equation(equation_str: str) -> str:
        """
        Solve a mathematical equation.

        Args:
            equation_str (str): String representation of the equation.

        Returns:
            str: Solution to the equation.

        """
        try:
            # Extract the variable and equation parts
            match = re.match(r"([a-zA-Z])\s*=\s*(.*)", equation_str)
            if match:
                var_name = match.group(1)
                equation = match.group(2)
                var = sp.Symbol(var_name)
                expr = parse_expr(equation)
                return str(expr)

            # Handle equations with equals sign
            if "=" in equation_str:
                parts = equation_str.split("=")
                if len(parts) == 2:
                    left = parse_expr(parts[0])
                    right = parse_expr(parts[1])
                    equation = sp.Eq(left, right)

                    # Extract variables
                    variables = list(equation.free_symbols)
                    if len(variables) == 1:
                        var = variables[0]
                        solution = sp.solve(equation, var)
                        return f"{var} = {solution}"
                    solution = sp.solve(equation)
                    return str(solution)

            # If no equals sign, just evaluate the expression
            expr = parse_expr(equation_str)
            return str(expr.evalf())
        except Exception as e:
            logger.exception(f"Error solving equation: {equation_str}")
            return f"Error: {e!s}"

    @staticmethod
    def factor_expression(expr_str: str) -> str:
        """
        Factor a mathematical expression.

        Args:
            expr_str (str): String representation of the expression.

        Returns:
            str: Factored expression.

        """
        try:
            expr = parse_expr(expr_str)
            factored = sp.factor(expr)
            return str(factored)
        except Exception as e:
            logger.exception(f"Error factoring expression: {expr_str}")
            return f"Error: {e!s}"

    @staticmethod
    def expand_expression(expr_str: str) -> str:
        """
        Expand a mathematical expression.

        Args:
            expr_str (str): String representation of the expression.

        Returns:
            str: Expanded expression.

        """
        try:
            expr = parse_expr(expr_str)
            expanded = sp.expand(expr)
            return str(expanded)
        except Exception as e:
            logger.exception(f"Error expanding expression: {expr_str}")
            return f"Error: {e!s}"


class EnhancedArtistAgent(ArtistAgent):
    """Enhanced ARTIST agent for mathematical problem-solving."""

    def __init__(self) -> None:
        """Initialize the enhanced ARTIST agent."""
        super().__init__()

        # Register math tools
        math_tool = MathTool()
        tooling.register_tool("solve_equation", math_tool.solve_equation)
        tooling.register_tool("factor_expression", math_tool.factor_expression)
        tooling.register_tool("expand_expression", math_tool.expand_expression)

        # Update tools dictionary
        self.tools = tooling.list_tools()

    def decide_tool(self, prompt: str) -> str:
        """
        Select appropriate tool based on prompt keywords.

        Args:
            prompt (str): The user's input or problem description.

        Returns:
            str: Name of the tool to use.

        """
        prompt_lower = prompt.lower()

        if any(k in prompt_lower for k in ["solve", "equation", "=", "find", "value"]):
            return "solve_equation"

        if any(k in prompt_lower for k in ["factor", "factorize", "factorization"]):
            return "factor_expression"

        if any(k in prompt_lower for k in ["expand", "distribute", "multiply out"]):
            return "expand_expression"

        if any(
            k in prompt_lower
            for k in ["calculate", "compute", "evaluate", "+", "-", "*", "/"]
        ):
            return "calculator"

        return ""


def run_experiment(prompt: str) -> str:
    """
    Run the mathematical problem-solving experiment.

    Args:
        prompt (str): User prompt describing the mathematical problem.

    Returns:
        str: Result of the experiment.

    """
    agent = EnhancedArtistAgent()
    return agent.run(prompt)
