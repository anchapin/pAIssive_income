"""
Minimal ARTIST-style agent wrapper for agentic tool use.

This agent can reason over a prompt, decide which tool to use, and invoke it.
This is a scaffold for further expansion.
"""

from __future__ import annotations

from typing import Any, Callable
import logging # Added import
import os # Added import for os.environ check

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None # type: ignore
    ANTHROPIC_AVAILABLE = False

from common_utils import tooling

# Configure logging (logger only, basicConfig in main)
logger = logging.getLogger(__name__)

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
            # Naive extraction: assume the entire prompt is the expression
            # This should be improved for more complex prompts
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
