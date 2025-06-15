"""
run_linting - Enforce linting and formatting with Ruff.

This script runs Ruff (lint/fix and format check) on the codebase.
Intended for use in CI and pre-commit to enforce standards.
"""

from __future__ import annotations

import logging
import sys
from typing import Union

from common_utils.security import SecurityError, run_command_securely

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

    # Convert string commands to list for security
    cmd_list = cmd if isinstance(cmd, list) else cmd.split()

    try:
        result = run_command_securely(cmd_list, timeout=300)
        if result.returncode != 0:
            logger.error("❌ %s failed.", description)
            if result.stderr:
                logger.error("Error: %s", result.stderr)
            sys.exit(result.returncode)
        logger.info("✅ %s completed successfully.", description)
    except SecurityError:
        logger.exception("❌ Security error running %s", description)
        sys.exit(1)
    except Exception:
        logger.exception("❌ Error running %s", description)
        sys.exit(1)


def main() -> None:
    """Run linting and formatting checks."""
    # Lint and fix with Ruff
    run("ruff check --fix .", "Ruff lint and auto-fix")
    # Enforce Ruff formatting (check only, do not auto-fix in CI)
    run("ruff format --check .", "Ruff formatting check")


if __name__ == "__main__":
    main()
