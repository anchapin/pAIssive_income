#!/usr/bin/env python3
"""health_check.py.

Orchestrates repository quality checks:
- Linting (flake8, ruff)
- Formatting (ruff format)
- Static typing (mypy)
- Security (bandit)
- Dependency audit (uv pip audit)
- Documentation build (Sphinx, if configured).

Usage:
    python dev_tools/health_check.py [--all | --lint | --type |
    --security | --deps | --docs]

Requires tools: flake8, ruff, mypy, bandit, uv (with pip audit functionality),
sphinx-build (optional).
"""

import logging
import os
import shutil
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run(cmd: str, desc: str) -> None:
    """Run a shell command and print result.

    Args:
        cmd (str): The command to run.
        desc (str): Description of the command.

    """
    logging.info(f"\n==> {desc}")
    res = subprocess.run(cmd, shell=True, check=False)
    if res.returncode != 0:
        logging.error(f"FAILED: {desc}")
        sys.exit(1)
    else:
        logging.info(f"PASSED: {desc}")


def check_gitignore(_path: str) -> bool:
    """Skip files/directories in .gitignore (for future extension).

    Args:
        path (str): Path to check.

    Returns:
        bool: True if not git-ignored (placeholder).

    """
    return True  # Placeholder for future logic


def lint() -> None:
    """Run linting and formatting checks (ruff, flake8)."""
    if shutil.which("ruff"):
        run("ruff check .", "Ruff linting")
        run("ruff format --check .", "Ruff formatting check")
    if shutil.which("flake8"):
        run("flake8 .", "Flake8 linting")


def type_check() -> None:
    """Run mypy static type checks."""
    if shutil.which("mypy"):
        run("mypy .", "Mypy static type checking")
    else:
        logging.warning("mypy not found, skipping type checks.")


def security() -> None:
    """Run bandit security scan."""
    if shutil.which("bandit"):
        run("bandit -r . -x tests", "Bandit security scan")
    else:
        logging.warning("bandit not found, skipping security checks.")


def deps() -> None:
    """Run uv pip audit for dependency security."""
    if shutil.which("uv"):
        run("uv pip audit", "Python dependency audit")
    else:
        logging.warning("uv not found, skipping dependency audit.")


def docs() -> None:
    """Build Sphinx documentation, if present."""
    if os.path.isdir("docs_source") and shutil.which("sphinx-build"):
        run(
            "sphinx-build docs_source docs/_build",
            "Sphinx documentation build",
        )
    else:
        logging.warning("Sphinx not configured or not found, skipping docs build.")


def usage() -> None:
    """Print usage instructions."""
    logging.info(__doc__)


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
