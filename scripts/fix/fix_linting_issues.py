#!/usr/bin/env python3

"""
Script to fix common linting issues across the codebase.

This script uses Ruff to automatically fix common linting issues in Python files.
It can be run on specific files or on all Python files in the repository.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from subprocess import CompletedProcess
from typing import Optional, Sequence, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_executable_path(name: str) -> str:
    """
    Get the full path to an executable.

    Args:
        name: Name of the executable

    Returns:
        Full path to the executable or just the name if not found

    """
    exe_path = shutil.which(name)
    if exe_path:
        logger.debug("Found %s at: %s", name, exe_path)
        return str(exe_path)  # Ensure we return a string
    logger.warning(
        "Could not find %s executable, using '%s' and relying on PATH", name, name
    )
    return name


def get_git_root() -> Path:
    """
    Get the root directory of the git repository.

    Returns:
        The root directory of the git repository.

    Raises:
        SystemExit: If the git command fails.

    """
    git_exe = get_executable_path("git")
    try:
        result = cast(
            "CompletedProcess[str]",
            subprocess.run(
                [git_exe, "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
            ),
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        logger.exception(
            "Failed to get git root directory. Are you in a git repository?"
        )
        sys.exit(1)


def should_ignore(
    file_path: Path, exclude_patterns: Optional[Sequence[str]] = None
) -> bool:
    """
    Check if a file should be ignored based on exclude patterns.

    Args:
        file_path: The path to the file to check.
        exclude_patterns: List of patterns to exclude, or None to exclude nothing.

    Returns:
        True if the file should be ignored, False otherwise.

    """
    if not exclude_patterns:
        return False
    str_path = str(file_path)
    return any(pattern in str_path for pattern in exclude_patterns)


def _process_specific_files(
    specific_files: Sequence[str], exclude_patterns: Optional[Sequence[str]] = None
) -> list[Path]:
    """
    Process a list of specific files.

    Args:
        specific_files: List of specific files to process.
        exclude_patterns: List of patterns to exclude, or None to exclude nothing.

    Returns:
        List of valid file paths to process.

    Raises:
        SystemExit: If any file does not exist or is not a Python file.

    """
    files: list[Path] = []
    for file_str in specific_files:
        path = Path(file_str)
        if not path.exists():
            logger.error("File not found: %s", path)
            sys.exit(1)
        if path.suffix != ".py":
            logger.error("Not a Python file: %s", path)
            sys.exit(1)
        if not should_ignore(path, exclude_patterns):
            files.append(path)
    return files


def fix_file(file_path: Path) -> tuple[Path, bool]:
    """
    Fix linting issues in a single file.

    Args:
        file_path: Path to the file to fix.

    Returns:
        Tuple of (file_path, success_status).

    """
    ruff_exe = get_executable_path("ruff")
    try:
        cast(
            "CompletedProcess[str]",
            subprocess.run(
                [ruff_exe, "check", "--fix", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            ),
        )
        return file_path, True
    except subprocess.CalledProcessError as e:
        logger.exception("Failed to fix %s: %s", file_path, e.stderr)
        return file_path, False


def find_python_files(
    root_dir: Path, exclude_patterns: Optional[Sequence[str]] = None
) -> list[Path]:
    """
    Find all Python files in the repository.

    Args:
        root_dir: Root directory to search from.
        exclude_patterns: List of patterns to exclude, or None to exclude nothing.

    Returns:
        List of Python file paths.

    """
    python_files: list[Path] = []
    for path in root_dir.rglob("*.py"):
        rel_path = path.relative_to(root_dir)
        if not should_ignore(rel_path, exclude_patterns):
            python_files.append(path)
    return python_files


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed command line arguments.

    """
    parser = argparse.ArgumentParser(
        description="Fix common linting issues in Python files."
    )
    parser.add_argument("files", nargs="*", help="Specific files to process (optional)")
    parser.add_argument(
        "--check", action="store_true", help="Check for issues without fixing them"
    )
    parser.add_argument("--no-ruff", action="store_true", help="Skip Ruff linter")
    parser.add_argument(
        "--exclude", action="append", default=[], help="Patterns to exclude"
    )
    parser.add_argument(
        "--exclude-file", help="File containing patterns to exclude (one per line)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show verbose output"
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=os.cpu_count(),
        help="Number of parallel jobs (default: number of CPU cores)",
    )

    return parser.parse_args()


def main() -> int:
    """
    Run the main entry point for the script.

    Returns:
        Exit code: 0 for success, 1 for failure

    """
    args = parse_args()

    # Get exclude patterns
    exclude_patterns = args.exclude if args.exclude else []

    # Determine files to process
    files_to_process: list[Path] = []
    if args.files:
        files_to_process = _process_specific_files(args.files, exclude_patterns)
    else:
        root_dir = get_git_root()
        files_to_process = find_python_files(root_dir, exclude_patterns)

    if not files_to_process:
        logger.warning("No Python files found to process")
        return 0

    # Process files in parallel
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(fix_file, path): path for path in files_to_process}
        success = True
        for future in as_completed(futures):
            file_path, result = future.result()
            if not result:
                success = False
                logger.error("Failed to fix %s", file_path)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
