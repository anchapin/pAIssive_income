"""format_code.py - Script for the pAIssive Income project."""

import argparse
import sys


def main():
    """Initialize the module."""
    parser = argparse.ArgumentParser(
        description="Script for the pAIssive Income project"
    )

    # Parse arguments but ignore since functionality is not implemented yet
    # Use parse_known_args() to handle unexpected arguments gracefully
    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"Ignoring unrecognized arguments: {unknown}")

    # Format code using black and (optionally) ruff format
    import subprocess

    success = True
    formatters = [
        (["black", "."], "black"),
        (["ruff", "format", "."], "ruff format"),
    ]

    for fmt_cmd, fmt_name in formatters:
        try:
            completed = subprocess.run(fmt_cmd + unknown, check=False)
            if completed.returncode != 0:
                print(f"{fmt_name} failed to format some files.")
                success = False
        except FileNotFoundError:
            print(f"{fmt_name} is not installed or not found in PATH. Skipping.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
