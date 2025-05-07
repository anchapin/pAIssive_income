"""lint_check.py - Script for the pAIssive Income project."""

import argparse
import sys


def main():
    """Initialize the module."""
    parser = argparse.ArgumentParser(
        description="Script for the pAIssive Income project"
    )

    parser.parse_args()  # Parse args but ignore since not used yet

    # Run ruff and flake8 in check mode
    import subprocess

    success = True
    tools = [
        (["ruff", "."], "ruff"),
        (["flake8", "."], "flake8"),
    ]

    for tool_cmd, tool_name in tools:
        try:
            completed = subprocess.run(tool_cmd, check=False)
            if completed.returncode != 0:
                print(f"{tool_name} found linting issues.")
                success = False
        except FileNotFoundError:
            print(f"{tool_name} is not installed or not found in PATH. Skipping.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
