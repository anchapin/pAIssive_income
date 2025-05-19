#!/usr/bin/env python3
"""
Artist Agent Demo Script.

This script demonstrates the use of the ArtistAgent with various tools.
It shows how the agent can select and use tools based on user prompts.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.resolve() / ".."))

from ai_models.artist_agent import ArtistAgent
from common_utils import tooling


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.

    Args:
        verbose (bool): Whether to enable verbose logging.

    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def register_custom_tools() -> None:
    """Register additional custom tools for the demo."""

    # Example of registering a custom tool for the demo
    def word_counter(text: str) -> int:
        """Count the number of words in a text."""
        return len(text.split())

    # Register the custom tool
    tooling.register_tool("word_counter", word_counter)


def run_interactive_demo(agent: ArtistAgent) -> None:
    """
    Run an interactive demo where the user can input prompts.

    Args:
        agent (ArtistAgent): The agent to use for processing prompts.

    """
    logger = logging.getLogger(__name__)
    logger.info("=== Interactive Artist Agent Demo ===")
    logger.info("Available tools: %s", list(agent.tools.keys()))
    logger.info("Type 'exit' or 'quit' to end the demo.")
    logger.info("Example prompts:")
    logger.info("  - Calculate 2 + 3 * 4")
    logger.info("  - Analyze this text: The quick brown fox jumps over the lazy dog.")
    logger.info("")

    while True:
        try:
            user_input = input("Enter your prompt: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            result = agent.run(user_input)
            logger.info("\nResult:\n%s\n", result)
        except KeyboardInterrupt:
            logger.info("\nExiting demo...")
            break
        except (ValueError, TypeError, KeyError):
            logger.exception("Error processing prompt")


def run_example_prompts(
    agent: ArtistAgent, prompts: Optional[List[str]] = None
) -> None:
    """
    Run a set of example prompts through the agent.

    Args:
        agent (ArtistAgent): The agent to use for processing prompts.
        prompts (Optional[List[str]]): List of prompts to process. If None, uses default examples.

    """
    logger = logging.getLogger(__name__)
    logger.info("=== Artist Agent Demo with Example Prompts ===")
    logger.info("Available tools: %s", list(agent.tools.keys()))

    # Default example prompts if none provided
    if not prompts:
        prompts = [
            "Calculate 2 + 3 * 4",
            "What is 10 / 2 + 5?",
            "Analyze this text: The quick brown fox jumps over the lazy dog.",
            "Count words in: Python is a programming language that lets you work quickly and integrate systems effectively.",
            "This is a prompt with no specific tool request.",
        ]

    # Process each prompt
    for i, prompt in enumerate(prompts, 1):
        logger.info("\nExample %d:", i)
        logger.info("Prompt: %s", prompt)
        result = agent.run(prompt)
        logger.info("Result:\n%s", result)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.

    """
    parser = argparse.ArgumentParser(description="Artist Agent Demo")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--prompts",
        "-p",
        nargs="+",
        help="Custom prompts to run (use with non-interactive mode)",
    )
    return parser.parse_args()


def main() -> int:
    """
    Run the Artist Agent demo.

    Returns:
        int: Exit code (0 for success).

    """
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Register any additional custom tools
        register_custom_tools()

        # Create the agent
        agent = ArtistAgent()

        if args.interactive:
            run_interactive_demo(agent)
        else:
            run_example_prompts(agent, args.prompts)
    except (ValueError, TypeError, KeyError):
        logger.exception("Error in Artist Agent demo")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
