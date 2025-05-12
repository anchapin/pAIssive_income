#!/usr/bin/env python
"""
verify_tracked_files.py

CI utility: Ensures only git-tracked (non-.gitignore'd) Python files are present in the repository.
Fails if any untracked or ignored Python files are found, which could otherwise be processed by scripts or tests.

Usage:
    python verify_tracked_files.py
"""

import logging
import os
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_git_tracked_files() -> set[str]:
    """Return a set of all Python files tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.py"], capture_output=True, text=True, check=True
        )
        tracked = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except subprocess.CalledProcessError:
        logging.exception("Failed to get git tracked files")
        sys.exit(1)
    else:
        return tracked


def get_all_python_files() -> set[str]:
    """Return a set of all Python files found in the repo (excluding .git directory)."""
    all_files = set()
    for root, dirs, files in os.walk("."):
        # Skip .git and common virtualenv dirs
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__"}]
        for file in files:
            if file.endswith(".py"):
                # Normalize to relative path
                relpath = os.path.relpath(os.path.join(root, file))
                all_files.add(relpath)
    return all_files


def main() -> None:
    tracked = get_git_tracked_files()
    all_found = get_all_python_files()
    untracked = sorted(f for f in all_found if f not in tracked)

    if untracked:
        logging.error(
            "The following Python files are NOT tracked by git (and may be ignored by .gitignore):"
        )
        for f in untracked:
            logging.error(f"  {f}")
        logging.error(
            "\nTo fix: either add these files to git, or remove/move them so they are not discovered by scripts/tests."
        )
        sys.exit(1)
    else:
        logging.info("All discovered Python files are tracked by git (not ignored).")
        sys.exit(0)


if __name__ == "__main__":
    main()
