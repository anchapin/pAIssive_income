"""run_linting.py - Script for the pAIssive Income project."""

import argparse
import sys


def main():
    """Initialize the module."""
    parser = argparse.ArgumentParser(
        description="Script for the pAIssive Income project"
    )

    # Use parse_known_args() to handle unexpected arguments gracefully
    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"Ignoring unrecognized arguments: {unknown}")

    # Run ruff, black, and flake8 (if available), passing through extra arguments
    import subprocess

    success = True
    # Prefer ruff, black, and flake8 if available
    tools = [
        (["ruff", "."], "ruff"),
        (["black", "--check", "."], "black"),
        (["flake8", "."], "flake8"),
    ]

    for tool_cmd, tool_name in tools:
        try:
            completed = subprocess.run(tool_cmd + unknown, check=False)
            if completed.returncode != 0:
                print(f"{tool_name} found issues.")
                success = False
        except FileNotFoundError:
            print(f"{tool_name} is not installed or not found in PATH. Skipping.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
