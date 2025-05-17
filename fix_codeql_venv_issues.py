#!/usr/bin/env python3
"""
Script to fix CodeQL issues in virtual environment files.

This script addresses issues in the virtual environment files that are causing
the CodeQL scan to fail. It removes the virtual environment directories to
prevent them from being scanned.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Directories to remove
VENV_DIRS = {
    ".venv",
    "venv",
    "env",
    ".env",
    "virtualenv",
}

# Directories to exclude from scanning
DIRS_TO_EXCLUDE = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}


def remove_venv_dirs(root_dir: str) -> list[str]:
    """
    Remove virtual environment directories.

    Args:
        root_dir: Root directory to scan

    Returns:
        List[str]: List of removed directories

    """
    removed_dirs = []

    for dirpath, dirnames, _ in os.walk(root_dir, topdown=True):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in DIRS_TO_EXCLUDE]

        for dirname in dirnames[:]:  # Create a copy to avoid modifying during iteration
            if dirname in VENV_DIRS:
                venv_path = Path(dirpath) / dirname
                logger.info("Removing virtual environment directory: %s", venv_path)
                try:
                    shutil.rmtree(venv_path)
                    removed_dirs.append(str(venv_path))
                    dirnames.remove(
                        dirname
                    )  # Remove from list to avoid descending into it
                except Exception:
                    logger.exception("Error removing %s", venv_path)

    return removed_dirs


def create_gitignore_entry(_: list[str]) -> None:
    """
    Create or update .gitignore file with entries for removed directories.

    Args:
        _: Unused parameter (kept for backward compatibility)

    """
    gitignore_path = ".gitignore"
    gitignore_entries = set()

    # Read existing .gitignore file
    if Path(gitignore_path).exists():
        with Path(gitignore_path).open(encoding="utf-8") as f:
            gitignore_entries = {line.strip() for line in f if line.strip()}

    # Add entries for removed directories
    for venv_dir in VENV_DIRS:
        gitignore_entries.add(f"{venv_dir}/")
        gitignore_entries.add(f"**/{venv_dir}/")

    # Add entries for site-packages and dist-packages
    gitignore_entries.add("**/site-packages/")
    gitignore_entries.add("**/dist-packages/")

    # Write updated .gitignore file
    with Path(gitignore_path).open("w", encoding="utf-8") as f:
        for entry in sorted(gitignore_entries):
            f.write(f"{entry}\n")

    logger.info(
        "Updated %s with entries for virtual environment directories", gitignore_path
    )


def create_codeqlignore_entry() -> None:
    """Create or update .codeqlignore file with entries for virtual environment directories."""
    codeqlignore_path = ".codeqlignore"
    codeqlignore_entries = set()

    # Read existing .codeqlignore file
    if Path(codeqlignore_path).exists():
        with Path(codeqlignore_path).open(encoding="utf-8") as f:
            codeqlignore_entries = {line.strip() for line in f if line.strip()}

    # Add entries for virtual environment directories
    for venv_dir in VENV_DIRS:
        codeqlignore_entries.add(f"{venv_dir}/**")
        codeqlignore_entries.add(f"**/{venv_dir}/**")

    # Add entries for site-packages and dist-packages
    codeqlignore_entries.add("**/site-packages/**")
    codeqlignore_entries.add("**/dist-packages/**")

    # Write updated .codeqlignore file
    with Path(codeqlignore_path).open("w", encoding="utf-8") as f:
        for entry in sorted(codeqlignore_entries):
            f.write(f"{entry}\n")

    logger.info(
        "Updated %s with entries for virtual environment directories", codeqlignore_path
    )


def main() -> None:
    """Execute the main function to fix CodeQL issues in virtual environment files."""
    parser = argparse.ArgumentParser(
        description="Fix CodeQL issues in virtual environment files"
    )
    parser.add_argument("--root-dir", default=".", help="Root directory to scan")
    parser.add_argument(
        "--update-gitignore", action="store_true", help="Update .gitignore file"
    )
    parser.add_argument(
        "--update-codeqlignore", action="store_true", help="Update .codeqlignore file"
    )
    parser.add_argument(
        "--remove-venv",
        action="store_true",
        help="Remove virtual environment directories",
    )
    args = parser.parse_args()

    if args.remove_venv:
        removed_dirs = remove_venv_dirs(args.root_dir)
        logger.info("Removed %d virtual environment directories", len(removed_dirs))

    if args.update_gitignore:
        create_gitignore_entry([])

    if args.update_codeqlignore:
        create_codeqlignore_entry()

    # If no actions specified, perform all actions
    if not (args.remove_venv or args.update_gitignore or args.update_codeqlignore):
        removed_dirs = remove_venv_dirs(args.root_dir)
        logger.info("Removed %d virtual environment directories", len(removed_dirs))
        create_gitignore_entry(removed_dirs)
        create_codeqlignore_entry()


if __name__ == "__main__":
    main()
