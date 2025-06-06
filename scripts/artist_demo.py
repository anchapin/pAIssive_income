#!/usr/bin/env python3
"""
Demonstration script for the ArtistAgent's agentic tool use.

- Instantiates the ArtistAgent
- Prints available tools
- Supports example and interactive modes
- In example mode: runs prompts for calculator, text analyzer, and unhandled cases
- In interactive mode: user enters prompts in a loop
"""

import argparse
import sys
import logging
from pathlib import Path

# Add the parent directory to the path to ensure we can import modules
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ai_models.artist_agent import ArtistAgent

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    """Run the main function."""
    parser = argparse.ArgumentParser(
        description="Demo for ArtistAgent: agentic tool use (calculator, text analyzer, fallback)."
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode (enter prompts manually).",
    )
    args = parser.parse_args()

    logger.info("=== ArtistAgent Tool Use Demo ===")
    agent = ArtistAgent()

    # Print available tools
    logger.info("\nAvailable tools:")
    for tool_name in agent.tools: # SIM118: Removed .keys()
        logger.info("  - %s", tool_name)

    if args.interactive:
        logger.info(
            "\nInteractive mode. Type your prompt and press Enter. Type 'exit' to quit."
        )
        while True:
            prompt = input("\nPrompt: ")
            if prompt.strip().lower() in {"exit", "quit"}:
                logger.info("Exiting interactive mode.")
                break
            response = agent.run(prompt)
            logger.info("Agent output: %s", response)
    else:
        # Example prompts
        prompts = [
            "What is 12 * 8?",  # Should trigger calculator tool
            "Analyze the sentiment of this phrase: 'This is a fantastic development!'",  # For text analyzer
            "Translate hello to French",  # Should NOT be handled
        ]

        for prompt in prompts:
            logger.info("\n-----------------------------")
            logger.info("Prompt: %s", prompt)
            response = agent.run(prompt)
            logger.info("Agent output: %s", response)


if __name__ == "__main__":
    main()
