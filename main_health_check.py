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
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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
    allowed_commands = {"ruff", "pyright", "bandit", "uv", "sphinx-build"}

    if cmd_list[0] not in allowed_commands:
        logger.error("Security: Command '%s' not in allowed list", cmd_list[0])
        sys.exit(1)

    # Use a helper to validate and run the command safely (addresses Ruff S603)
    def _safe_subprocess_run(
        cmd: list[str],
        **kwargs: Any,  # noqa: ANN401
    ) -> subprocess.CompletedProcess:
        cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
        if "cwd" in kwargs and isinstance(kwargs["cwd"], Path):
            kwargs["cwd"] = str(kwargs["cwd"])
        return subprocess.run(cmd, check=False, **kwargs)  # noqa: S603

    res = _safe_subprocess_run(cmd_list)  # Safe: command is validated and shell=False
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
    """Run pyright static type checks."""
    if shutil.which("pyright"):
        run("pyright .", "Pyright static type checking")
    else:
        logger.warning("pyright not found, skipping type checks.")


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


if __name__ == "__main__":
    main()
