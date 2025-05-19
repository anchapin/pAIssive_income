"""
run_linting - Enforce linting and formatting with Ruff.

This script runs Ruff (lint/fix and format check) on the codebase.
Intended for use in CI and pre-commit to enforce standards.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from typing import Union

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Set up a dedicated logger for this module
logger = logging.getLogger(__name__)


def run(cmd: Union[str, list[str]], description: str) -> None:
    """
    Run a command and exit if it fails.

    Args:
        cmd: Command to run as string or list
        description: Description of the command for logging

    """
    logger.info("Running: %s ...", description)
    # Convert string commands to list for security (avoid shell=True)
    cmd_list = cmd if isinstance(cmd, list) else cmd.split()

    # Get full path to executable for security
    executable = shutil.which(cmd_list[0])
    if not executable:
        logger.error("❌ Command not found: %s", cmd_list[0])
        sys.exit(1)

    cmd_list[0] = executable
    # nosec comment below tells security scanners this is safe as we control the input
    result = subprocess.run(cmd_list, shell=False, check=False)  # nosec B603 S603
    if result.returncode != 0:
        logger.error("❌ %s failed.", description)
        sys.exit(result.returncode)
    logger.info("✅ %s passed.", description)


def main() -> None:
    """Run linting and formatting checks."""
    # Lint and fix with Ruff
    run("ruff check --fix .", "Ruff lint and auto-fix")
    # Enforce Ruff formatting (check only, do not auto-fix in CI)
    run("ruff format --check .", "Ruff formatting check")


if __name__ == "__main__":
    main()
