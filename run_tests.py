"""run_tests.py - Script for the pAIssive Income project."""

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

    # Run pytest on the tests/ directory, passing through any extra arguments
    import subprocess

    cmd = ["pytest", "tests/"] + unknown
    try:
        completed = subprocess.run(cmd, check=False)
        return completed.returncode
    except FileNotFoundError:
        print("pytest is not installed or not found in PATH.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
