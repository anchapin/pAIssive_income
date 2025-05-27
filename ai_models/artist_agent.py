"""
Minimal ARTIST-style agent wrapper for agentic tool use.

This agent can reason over a prompt, decide which tool to use, and invoke it.
This is a scaffold for further expansion.
"""

from __future__ import annotations

import logging  # Added import
import os  # Added import for os.environ check
import re
from typing import Any, Callable

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging (logger only, basicConfig in main)

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError as e:
    logger.exception(
        f"Anthropic SDK not found or import failed: {e}. Optional features depending on Anthropic will be unavailable."
    )
    anthropic = None  # type: ignore
    ANTHROPIC_AVAILABLE = False

from common_utils import tooling


class ArtistAgent:
    """Agent that selects and uses tools based on user prompts."""

    def __init__(self) -> None:
        """Initialize the agent with available tools."""
        # Discover available tools at initialization
        self.tools: dict[str, Callable[..., Any]] = tooling.list_tools()

    def decide_tool(self, prompt: str) -> str:
        """
        Select appropriate tool based on prompt keywords.

        Expand this with RL or more sophisticated reasoning as desired.

        Args:
            prompt (str): The user's input or problem description.

        Returns:
            str: Name of the tool to use.

        """
        if any(
            k in prompt.lower()
            for k in [
                "calculate",
                "add",
                "subtract",
                "multiply",
                "divide",
                "+",
                "-",
                "*",
                "/",
            ]
        ):
            return "calculator"

        # Check for text analysis keywords
        if any(
            k in prompt.lower()
            for k in [
                "analyze",
                "sentiment",
                "text",
                "phrase",
                "analyze the",
                "sentiment of",
            ]
        ):
            return "text_analyzer"

        # Add more heuristics for other tools here
        return ""

    def extract_relevant_expression(self, prompt: str, tool_name: str) -> str:
        """
        Extract the relevant expression from the prompt based on the tool.

        This is a naive implementation for the calculator tool.

        Args:
            prompt (str): The user's input or problem description.
            tool_name (str): The name of the selected tool.

        Returns:
            str: The extracted relevant expression.

        """
        if tool_name == "calculator":
            # For calculator, try to extract the mathematical expression
            # Try to find the mathematical part of the prompt
            # Look for patterns like "What is 12 * 8?" -> extract "12 * 8"
            calc_match = re.search(
                r"(?:what\s+is\s+|calculate\s+|compute\s+)?([0-9\+\-\*/\(\)\.\s%]+)",
                prompt,
                re.IGNORECASE,
            )
            if calc_match:
                expression = calc_match.group(1).strip()
                # Validate that it contains at least one operator
                if any(op in expression for op in ["+", "-", "*", "/", "%"]):
                    return expression

            # Fallback: extract any sequence of numbers and operators
            math_parts = re.findall(r"[0-9\+\-\*/\(\)\.\s%]+", prompt)
            if math_parts:
                # Take the longest match that contains operators
                for part in sorted(math_parts, key=len, reverse=True):
                    part = part.strip()
                    if (
                        any(op in part for op in ["+", "-", "*", "/", "%"])
                        and len(part) > 1
                    ):
                        return part

            # Final fallback to the entire prompt
            return prompt
        if tool_name == "text_analyzer":
            # For text analysis, try to extract the text to analyze
            # Look for patterns like "analyze this: 'text'" or "sentiment of 'text'"

            # Try to find quoted text first
            quoted_match = re.search(r"['\"]([^'\"]+)['\"]", prompt)
            if quoted_match:
                return quoted_match.group(1)

            # Try to find text after "analyze" or "sentiment of"
            analyze_match = re.search(
                r"analyze(?:\s+the)?\s+(?:sentiment\s+of\s+)?(?:this\s+)?(?:phrase:?\s*)?(.+)",
                prompt,
                re.IGNORECASE,
            )
            if analyze_match:
                return analyze_match.group(1).strip()

            sentiment_match = re.search(
                r"sentiment\s+of\s+(?:this\s+)?(?:phrase:?\s*)?(.+)",
                prompt,
                re.IGNORECASE,
            )
            if sentiment_match:
                return sentiment_match.group(1).strip()

            # Fallback to the entire prompt
            return prompt

        return prompt  # Default to returning the whole prompt if extraction logic is not defined

    def run(self, prompt: str) -> str:
        """
        Process a prompt, select a tool, and return the tool's output.

        Args:
            prompt (str): The user's input/problem.

        Returns:
            str: The tool's output, or a message if no tool found.

        """
        tool_name = self.decide_tool(prompt)
        if tool_name and tool_name in self.tools:
            tool_func = self.tools[tool_name]
            relevant_expression = self.extract_relevant_expression(prompt, tool_name)
            result = tool_func(relevant_expression)
            return str(result)  # Ensure we return a string
        return "No suitable tool found for this prompt."


def main() -> None:
    """Run example usage of ArtistAgent."""
    # logging.basicConfig is now at the start of this function
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # logger is now initialized globally

    if not ANTHROPIC_AVAILABLE:
        logger.error("Anthropic SDK not installed. Cannot run example.")
        return
    if "ANTHROPIC_API_KEY" not in os.environ:
        logger.error("ANTHROPIC_API_KEY not found in environment variables.")
        return

    agent = ArtistAgent()
    # Example usage
    logger.info("Available tools: %s", list(agent.tools.keys()))
    test_prompt = "Calculate 2 + 3 * 4"
    logger.info("Prompt: %s", test_prompt)
    logger.info("Agent output: %s", agent.run("2 + 3 * 4"))


if __name__ == "__main__":
    main()
