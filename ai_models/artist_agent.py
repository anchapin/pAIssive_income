"""
Minimal ARTIST-style agent wrapper for agentic tool use.

This agent can reason over a prompt, decide which tool to use, and invoke it.
This is a scaffold for further expansion.
"""

from typing import Any, Dict
from common_utils import tooling

class ArtistAgent:
    def __init__(self):
        # Discover available tools at initialization
        self.tools = tooling.list_tools()

    def decide_tool(self, prompt: str) -> str:
        """
        Naive tool selection logic based on prompt keywords.
        Expand this with RL or more sophisticated reasoning as desired.

        Args:
            prompt (str): The user's input or problem description.

        Returns:
            str: Name of the tool to use.
        """
        if any(k in prompt.lower() for k in ["calculate", "add", "subtract", "multiply", "divide", "+", "-", "*", "/"]):
            return "calculator"
        # Add more heuristics for other tools here
        return ""

    def run(self, prompt: str) -> Any:
        """
        Process a prompt, select a tool, and return the tool's output.

        Args:
            prompt (str): The user's input/problem.

        Returns:
            Any: The tool's output, or a message if no tool found.
        """
        tool_name = self.decide_tool(prompt)
        if tool_name and tool_name in self.tools:
            tool_func = self.tools[tool_name]
            # For this scaffold, assume the tool takes the prompt directly
            return tool_func(prompt)
        else:
            return "No suitable tool found for this prompt."


if __name__ == "__main__":
    agent = ArtistAgent()
    # Example usage
    print("Available tools:", list(agent.tools.keys()))
    test_prompt = "Calculate 2 + 3 * 4"
    print(f"Prompt: {test_prompt}")
    print("Agent output:", agent.run("2 + 3 * 4"))