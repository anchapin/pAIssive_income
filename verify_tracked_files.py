#!/usr/bin/env python
"""
verify_tracked_files.py

CI utility: Ensures only git-tracked (non-.gitignore'd) Python files are present in the repository.
Fails if any untracked or ignored Python files are found, which could otherwise be processed by scripts or tests.

Usage:
    python verify_tracked_files.py
"""

import os
import sys

def get_git_tracked_files():
    """Return a set of all Python files tracked by git."""
    output = os.popen("git ls-files '*.py'").read()
    tracked = set(line.strip() for line in output.splitlines() if line.strip())
    return tracked

def get_all_python_files():
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

def main():
    tracked = get_git_tracked_files()
    all_found = get_all_python_files()
    untracked = sorted(f for f in all_found if f not in tracked)

    if untracked:
        print("ERROR: The following Python files are NOT tracked by git (and may be ignored by .gitignore):")
        for f in untracked:
            print(f"  {f}")
        print("\nTo fix: either add these files to git, or remove/move them so they are not discovered by scripts/tests.")
        sys.exit(1)
    else:
        print("All discovered Python files are tracked by git (not ignored).")
        sys.exit(0)

if __name__ == "__main__":
    main()