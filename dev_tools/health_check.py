#!/usr/bin/env python3
"""health_check.py.

Orchestrates repository quality checks:
- Linting (flake8, ruff)
- Formatting (black or ruff format)
- Static typing (mypy)
- Security (bandit)
- Dependency audit (pip-audit)
- Documentation build (Sphinx, if configured).

Usage:
    python dev_tools/health_check.py [--all | --lint | --type |
    --security | --deps | --docs]

Requires tools: flake8, ruff, mypy, bandit, pip-audit, black,
sphinx-build (optional).
"""

import os
import shutil
import subprocess
import sys


def run(cmd, desc):
    """Run a shell command and print result.

    Args:
        cmd (str): The command to run.
        desc (str): Description of the command.

    """
    print(f"\n\033[1m==> {desc}\033[0m")
    res = subprocess.run(cmd, shell=True, check=False)
    if res.returncode != 0:
        print(f"\033[91mFAILED: {desc}\033[0m")
        sys.exit(1)
    else:
        print(f"\033[92mPASSED: {desc}\033[0m")


def check_gitignore(path):
    """Skip files/directories in .gitignore (for future extension).

    Args:
        path (str): Path to check.

    Returns:
        bool: True if not git-ignored (placeholder).

    """
    return True  # Placeholder for future logic


def lint():
    """Run linting and formatting checks (ruff, flake8, black)."""
    if shutil.which("ruff"):
        run("ruff check .", "Ruff linting")
    if shutil.which("flake8"):
        run("flake8 .", "Flake8 linting")
    if shutil.which("black"):
        run("black --check .", "Black formatting check")


def type_check():
    """Run mypy static type checks."""
    if shutil.which("mypy"):
        run("mypy .", "Mypy static type checking")
    else:
        print("mypy not found, skipping type checks.")


def security():
    """Run bandit security scan."""
    if shutil.which("bandit"):
        run("bandit -r . -x tests", "Bandit security scan")
    else:
        print("bandit not found, skipping security checks.")


def deps():
    """Run pip-audit for dependency security."""
    if shutil.which("pip-audit"):
        run("pip-audit", "Python dependency audit")
    else:
        print("pip-audit not found, skipping dependency audit.")


def docs():
    """Build Sphinx documentation, if present."""
    if os.path.isdir("docs_source") and shutil.which("sphinx-build"):
        run(
            "sphinx-build docs_source docs/_build",
            "Sphinx documentation build",
        )
    else:
        print("Sphinx not configured or not found, skipping docs build.")


def usage():
    """Print usage instructions."""
    print(__doc__)


def main():
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
