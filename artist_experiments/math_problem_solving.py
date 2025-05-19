"""
Mathematical problem-solving experiment using ARTIST framework.

This module implements a basic ARTIST-based agent for solving mathematical problems.
"""

from __future__ import annotations

import logging
import re

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from ai_models.artist_agent import ArtistAgent
from common_utils import tooling

# Constants
EXPECTED_PARTS = 2
SINGLE_VARIABLE = 1
EQUATION_PATTERN = r"([a-zA-Z])\s*=\s*(.*)"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
            match = re.match(EQUATION_PATTERN, equation_str)
            if match:
                var_name = match.group(1)
                equation = match.group(2)
                var = sp.Symbol(var_name)
                expr = parse_expr(equation)
                return str(expr)

            # Handle equations with equals sign
            if "=" in equation_str:
                parts = equation_str.split("=")
                if len(parts) == EXPECTED_PARTS:
                    left = parse_expr(parts[0])
                    right = parse_expr(parts[1])
                    equation = sp.Eq(left, right)

                    # Extract variables
                    variables = list(equation.free_symbols)
                    if len(variables) == SINGLE_VARIABLE:
                        var = variables[0]
                        solution = sp.solve(equation, var)
                        return f"{var} = {solution}"
                    solution = sp.solve(equation)
                    return str(solution)

            # If no equals sign, just evaluate the expression
            expr = parse_expr(equation_str)
        except (ValueError, TypeError, AttributeError, sp.SympifyError) as e:
            logger.exception("Error solving equation")
            return f"Error: {e!s}"
        else:
            return str(expr.evalf())

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
        except (ValueError, TypeError, AttributeError, sp.SympifyError) as e:
            logger.exception("Error factoring expression")
            return f"Error: {e!s}"
        else:
            return str(factored)

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
        except (ValueError, TypeError, AttributeError, sp.SympifyError) as e:
            logger.exception("Error expanding expression")
            return f"Error: {e!s}"
        else:
            return str(expanded)


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
        # Use lowercase variable names for local variables
        solve_keywords = ["solve", "equation", "=", "find", "value"]
        factor_keywords = ["factor", "factorize", "factorization"]
        expand_keywords = ["expand", "distribute", "multiply out"]
        calculate_keywords = ["calculate", "compute", "evaluate", "+", "-", "*", "/"]

        prompt_lower = prompt.lower()

        if any(k in prompt_lower for k in solve_keywords):
            return "solve_equation"

        if any(k in prompt_lower for k in factor_keywords):
            return "factor_expression"

        if any(k in prompt_lower for k in expand_keywords):
            return "expand_expression"

        if any(k in prompt_lower for k in calculate_keywords):
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
