#!/usr/bin/env python3
from __future__ import annotations

import logging
import shutil
import subprocess
import sys

# Configure logging
logger = logging.getLogger(__name__)

"""
health_check.py.

Orchestrates repository quality checks:
- Linting (ruff, replacing flake8)
- Formatting (ruff format)
- Static typing (mypy)
- Security (bandit)
- Dependency audit (uv pip audit)
- Documentation build (Sphinx, if configured).

Usage:
    python dev_tools/health_check.py [--all | --lint | --type |
    --security | --deps | --docs]

Requires tools: ruff, mypy, bandit, uv (with pip audit functionality),
sphinx-build (optional).
"""

try:
    from pathlib import Path
except ImportError as e:
    logger.exception("Failed to import pathlib", exc_info=e)
    sys.exit(1)

# Third-party imports would go here if needed
# Currently no third-party imports are required for health check


def run(cmd: str, desc: str) -> None:
    """
    Run a command and print result.

    Args:
        cmd (str): The command to run.
        desc (str): Description of the command.

    """
    logger.info("\n==> %s", desc)
    # Convert string command to list for security (avoid shell=True)
    cmd_list = cmd.split()

    # Validate command for security - only allow specific commands
    allowed_commands = {"ruff", "mypy", "bandit", "uv", "sphinx-build"}

    if cmd_list[0] not in allowed_commands:
        logger.error("Security: Command '%s' not in allowed list", cmd_list[0])
        sys.exit(1)

    # Use a list of validated commands for security
    # Command has been validated against allowed_commands list
    res = subprocess.run(  # noqa: S603
        cmd_list, shell=False, check=False, capture_output=True, text=True
    )
    if res.returncode != 0:
        logger.error("FAILED: %s", desc)
        if res.stderr:
            logger.error("Error output: %s", res.stderr)
        sys.exit(1)
    else:
        logger.info("PASSED: %s", desc)


def check_gitignore(_path: str) -> bool:
    """
    Skip files/directories in .gitignore (for future extension).

    Args:
        path (str): Path to check.

    Returns:
        bool: True if not git-ignored (placeholder).

    """
    return True  # Placeholder for future logic


def lint() -> None:
    """Run linting and formatting checks with Ruff."""
    if shutil.which("ruff"):
        run("ruff check .", "Ruff linting")
        run("ruff format --check .", "Ruff formatting check")
    else:
        logger.warning("ruff not found, skipping linting and formatting checks.")


def type_check() -> None:
    """Run mypy static type checks."""
    if shutil.which("mypy"):
        run("mypy .", "Mypy static type checking")
    else:
        logger.warning("mypy not found, skipping type checks.")


def security() -> None:
    """Run bandit security scan."""
    if shutil.which("bandit"):
        run("bandit -r . -x tests", "Bandit security scan")
    else:
        logger.warning("bandit not found, skipping security checks.")


def deps() -> None:
    """Run uv pip audit for dependency security."""
    if shutil.which("uv"):
        run("uv pip audit", "Python dependency audit")
    else:
        logger.warning("uv not found, skipping dependency audit.")


def docs() -> None:
    """Build Sphinx documentation, if present."""
    if Path("docs_source").is_dir() and shutil.which("sphinx-build"):
        run(
            "sphinx-build docs_source docs/_build",
            "Sphinx documentation build",
        )
    else:
        logger.warning("Sphinx not configured or not found, skipping docs build.")


def usage() -> None:
    """Print usage instructions."""
    logger.info(__doc__)


def main() -> None:
    """Entry point for orchestrated health checks."""
    try:
        args = set(sys.argv[1:])
        if not args or "--all" in args:
            lint()
            type_check()
            security()
            deps()
            docs()
        else:
            if "--lint" in args:
                lint()
            if "--type" in args:
                type_check()
            if "--security" in args:
                security()
            if "--deps" in args:
                deps()
            if "--docs" in args:
                docs()
            if "--help" in args or "-h" in args:
                usage()
    except Exception as e:
        logger.exception("An error occurred in main_health_check", exc_info=e)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
