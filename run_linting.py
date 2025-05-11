"""run_linting - Enforce linting and formatting with Ruff and Black.

This script runs Ruff (lint/fix) and Black (check) on the codebase.
Intended for use in CI and pre-commit to enforce standards.
"""

import subprocess
import sys


def run(cmd, description):
    print(f"Running: {description} ...")
    result = subprocess.run(cmd, shell=True, check=False)
    if result.returncode != 0:
        print(f"❌ {description} failed.")
        sys.exit(result.returncode)
    print(f"✅ {description} passed.")


def main():
    # Lint and fix with Ruff
    run("ruff check --fix .", "Ruff lint and auto-fix")
    # Enforce Black formatting (check only, do not auto-fix in CI)
    run("black --check .", "Black formatting check")


if __name__ == "__main__":
    main()
