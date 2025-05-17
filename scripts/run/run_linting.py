"""run_linting - Enforce linting and formatting with Ruff.

This script runs Ruff (lint/fix and format check) on the codebase.
Intended for use in CI and pre-commit to enforce standards.
"""

import logging
import subprocess
import sys

from typing import Union

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run(cmd: Union[str, list[str]], description: str) -> None:
    logging.info(f"Running: {description} ...")
    # Convert string commands to list for security (avoid shell=True)
    cmd_list = cmd if isinstance(cmd, list) else cmd.split()
    result = subprocess.run(cmd_list, shell=False, check=False)
    if result.returncode != 0:
        logging.error(f"❌ {description} failed.")
        sys.exit(result.returncode)
    logging.info(f"✅ {description} passed.")


def main() -> None:
    # Lint and fix with Ruff
    run("ruff check --fix .", "Ruff lint and auto-fix")
    # Enforce Ruff formatting (check only, do not auto-fix in CI)
    run("ruff format --check .", "Ruff formatting check")


if __name__ == "__main__":
    main()
