#!/usr/bin/env python3
"""
health_check.py.

Orchestrates repository quality checks:
- Linting (ruff, replacing flake8)
- Formatting (ruff format)
- Static typing (pyright)
- Security (bandit)
- Dependency audit (uv pip audit)
- Documentation build (Sphinx, if configured).

Usage:
    python dev_tools/health_check.py [--all | --lint | --type |
    --security | --deps | --docs]

Requires tools: ruff, pyright, bandit, uv (with pip audit functionality),
sphinx-build (optional).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final, Literal, NoReturn

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Type aliases
CommandArg = Literal[
    "--all", "--lint", "--type", "--security", "--deps", "--docs", "--help", "-h"
]
CommandResult = subprocess.CompletedProcess[bytes]

# Constants
EXIT_SUCCESS: Final[int] = 0
EXIT_FAILURE: Final[int] = 1
DOCS_SOURCE_DIR: Final[str] = "docs_source"
DOCS_BUILD_DIR: Final[str] = "docs/_build"


def run(cmd: str, desc: str) -> None:
    """
    Run a shell command and print result.

    Args:
        cmd: The command to run
        desc: Description of the command

    Raises:
        SystemExit: If the command fails or is not found

    """
    message: str = f"\n==> {desc}"
    logger.info(message)

    try:
        # Split the command into a list for safer execution
        cmd_parts: list[str] = cmd.split()
        # Find the executable with full path
        executable: str | None = shutil.which(cmd_parts[0])
        if not executable:
            message = f"Command not found: {cmd_parts[0]}"
            logger.error(message)
            sys.exit(EXIT_FAILURE)

        # Run the command with the full path to the executable
        res = subprocess.run(
            [executable] + cmd_parts[1:], check=False, capture_output=True
        )

        if res.returncode != EXIT_SUCCESS:
            message = f"FAILED: {desc}\nOutput: {res.stderr.decode()}"
            logger.error(message)
            sys.exit(EXIT_FAILURE)
        else:
            message = f"PASSED: {desc}"
            logger.info(message)
    except (subprocess.SubprocessError, OSError) as e:
        message = f"ERROR: {desc} - {e!s}"
        logger.exception(message)
        sys.exit(EXIT_FAILURE)


def check_gitignore(_path: str) -> bool:
    """
    Skip files/directories in .gitignore (for future extension).

    Args:
        _path: Path to check against .gitignore (currently unused)

    Returns:
        bool: True if not git-ignored (placeholder)

    """
    # Skip validation for now, return True to indicate path is allowed
    return True


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
    docs_path = Path(DOCS_SOURCE_DIR)
    if docs_path.is_dir() and shutil.which("sphinx-build"):
        run(
            f"sphinx-build {DOCS_SOURCE_DIR} {DOCS_BUILD_DIR}",
            "Sphinx documentation build",
        )
    else:
        logger.warning("Sphinx not configured or not found, skipping docs build.")


def usage() -> NoReturn:
    """Print usage instructions and exit."""
    logger.info(__doc__)
    sys.exit(EXIT_SUCCESS)


def main() -> None:
    """
    Entry point for orchestrated health checks.

    Executes health checks based on command line arguments:
    - No args or --all: Run all checks
    - --lint: Run linting checks
    - --type: Run type checks
    - --security: Run security checks
    - --deps: Run dependency checks
    - --docs: Build documentation
    - --help or -h: Show usage
    """
    args: set[CommandArg] = set(sys.argv[1:])  # type: ignore[assignment]
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


if __name__ == "__main__":
    main()
