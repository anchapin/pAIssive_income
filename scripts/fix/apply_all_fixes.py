#!/usr/bin/env python3
"""Script to apply all fixes to Python files in parallel."""

from __future__ import annotations

import argparse
import logging
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Common directories to exclude
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def run_command(
    command: list[str], cwd: Optional[str] = None
) -> tuple[int, Optional[str], Optional[str]]:
    """Run a command and return its exit code and output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.exception("Error running command %s: %s", command, e)
        return 1, None, str(e)


def find_python_files() -> list[str]:
    """Find all Python files in the repository, excluding certain directories."""
    python_files = []
    for root, dirs, files in os.walk("."):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def process_file(file_path: str) -> tuple[str, bool, str]:
    """Process a single file with ruff --fix and ruff format."""
    # Add from __future__ import annotations
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("from __future__ import annotations"):
            lines = content.splitlines()
            # Find the first non-empty, non-comment line
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith("#"):
                    insert_pos = i
                    break
            # Insert the import
            lines.insert(insert_pos, "from __future__ import annotations")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\\n".join(lines))
    except Exception as e:
        logger.exception("Error adding future annotations to %s: %s", file_path, e)
        return file_path, False, str(e)

    # Run ruff --fix
    exit_code, stdout, stderr = run_command(["ruff", "check", "--fix", file_path])
    if exit_code != 0:
        return file_path, False, f"Ruff fix failed: {stderr}"

    # Run ruff format
    exit_code, stdout, stderr = run_command(["ruff", "format", file_path])
    if exit_code != 0:
        return file_path, False, f"Ruff format failed: {stderr}"

    return file_path, True, "Success"


def main() -> int:
    """Run the script."""
    parser = argparse.ArgumentParser(description="Fix Python files in parallel")
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of parallel jobs",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Find all Python files
    python_files = find_python_files()
    logger.info("Found %d Python files to process", len(python_files))

    # Process files in parallel
    success_count = 0
    error_count = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(process_file, file) for file in python_files]

        for future in as_completed(futures):
            try:
                file_path, success, message = future.result()
                if success:
                    success_count += 1
                    if args.verbose:
                        logger.info("Successfully processed %s", file_path)
                else:
                    error_count += 1
                    logger.error("Failed to process %s: %s", file_path, message)
            except Exception as e:
                error_count += 1
                logger.exception("Error processing task: %s", e)

    logger.info(
        "Completed: %d succeeded, %d failed",
        success_count,
        error_count,
    )

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
