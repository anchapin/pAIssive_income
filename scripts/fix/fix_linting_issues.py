#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging

# Configure logging
logger = logging.getLogger(__name__)

"""
Script to fix common linting issues across the codebase.

This script uses Ruff to automatically fix common linting issues in Python files.
It can be run on specific files or on all Python files in the repository.
"""
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging



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
        Path: The root directory of the git repository.

    Raises:
        SystemExit: If the git command fails.

    """
    git_exe = get_executable_path("git")
    try:
        result = subprocess.run(
            [git_exe, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        logger.exception(
            "Failed to get git root directory. Are you in a git repository?"
        )
        sys.exit(1)


def should_ignore(file_path: Path, exclude_patterns: list[str]) -> bool:
    """
    Check if a file should be ignored based on exclude patterns.

    Args:
        file_path: The path to the file to check.
        exclude_patterns: List of patterns to exclude.

    Returns:
        True if the file should be ignored, False otherwise.

    """
    str_path = str(file_path)
    return any(pattern in str_path for pattern in exclude_patterns)


def _process_specific_files(
    specific_files: list[str], exclude_patterns: list[str]
) -> list[Path]:
    """
    Process a list of specific files.

    Args:
        specific_files: List of specific files to process.
        exclude_patterns: List of patterns to exclude.

    Returns:
        List of Python files to process.

    """
    files = []
    for file_path in specific_files:
        path = Path(file_path)
        if path.exists() and path.is_file() and path.suffix == ".py":
            if not should_ignore(path, exclude_patterns):
                files.append(path)
        else:
            logger.warning(
                "Skipping %s (not a Python file or doesn't exist)", file_path
            )
    return files


def _find_all_python_files(git_root: Path, exclude_patterns: list[str]) -> list[Path]:
    """
    Find all Python files in the repository.

    Args:
        git_root: Git repository root directory.
        exclude_patterns: List of patterns to exclude.

    Returns:
        List of Python files to process.

    """
    python_files = []

    for root, _, files in os.walk(git_root):
        root_path = Path(root)
        if any(pattern in str(root_path) for pattern in exclude_patterns):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = root_path / file
                if not should_ignore(file_path, exclude_patterns):
                    python_files.append(file_path)

    return python_files


def find_python_files(
    specific_files: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """
    Find Python files to process.

    Args:
        specific_files: Optional list of specific files to process.
        exclude_patterns: Optional list of patterns to exclude.

    Returns:
        List of Python files to process.

    """
    if exclude_patterns is None:
        exclude_patterns = []

    # Add common directories to exclude
    exclude_patterns.extend(
        [
            ".git/",
            "__pycache__/",
            ".venv/",
            "venv/",
            "env/",
            "node_modules/",
            "build/",
            "dist/",
            ".pytest_cache/",
        ]
    )

    if specific_files:
        return _process_specific_files(specific_files, exclude_patterns)

    # Find all Python files in the repository
    git_root = get_git_root()
    return _find_all_python_files(git_root, exclude_patterns)


def process_file(
    file_path: Path, check_only: bool, use_ruff: bool, verbose: bool
) -> tuple[Path, bool, str | None]:
    """
    Process a single file with linting tools.

    Args:
        file_path: Path to the file to process.
        check_only: Whether to only check for issues without fixing them.
        use_ruff: Whether to use Ruff for linting.
        verbose: Whether to show verbose output.

    Returns:
        Tuple of (file_path, success, error_message).

    """
    if verbose:
        logger.info("Processing %s", file_path)

    success = True
    error_message = None

    try:
        if use_ruff:
            # Run Ruff for linting and formatting
            ruff_cmd = ["ruff", "check"]
            if not check_only:
                ruff_cmd.append("--fix")
            ruff_cmd.append(str(file_path))

            # Use absolute path for ruff command
            ruff_path = get_executable_path("ruff")
            full_cmd = [ruff_path] + ruff_cmd[1:]
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                success = False
                error_message = f"Ruff errors:\n{result.stderr or result.stdout}"
                if verbose:
                    logger.error(error_message)

            # Run Ruff formatter if not in check-only mode
            if not check_only:
                # Use absolute path for ruff command
                ruff_path = get_executable_path("ruff")
                format_result = subprocess.run(
                    [ruff_path, "format", str(file_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if format_result.returncode != 0:
                    success = False
                    format_error = f"Ruff format errors:\n{format_result.stderr or format_result.stdout}"
                    error_message = (
                        error_message + "\n" + format_error
                        if error_message
                        else format_error
                    )
                    if verbose:
                        logger.error(format_error)

    except (subprocess.SubprocessError, OSError) as e:
        success = False
        error_message = f"Error processing {file_path}: {e!s}"
        logger.exception(error_message)

    return file_path, success, error_message


def _parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments.

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


def _load_exclude_patterns(args: argparse.Namespace) -> list[str]:
    """
    Load exclude patterns from arguments and exclude file.

    Args:
        args: Parsed arguments.

    Returns:
        List of exclude patterns.

    """
    # Create a new list to ensure we return list[str] and not Any
    exclude_patterns: list[str] = list(args.exclude)

    if args.exclude_file:
        exclude_file_path = Path(args.exclude_file)
        if exclude_file_path.exists():
            with exclude_file_path.open() as f:
                for line in f:
                    line_content = line.strip()
                    if line_content and not line_content.startswith("#"):
                        exclude_patterns.append(line_content)

    return exclude_patterns


def _process_files_in_parallel(
    files: list[Path], args: argparse.Namespace
) -> tuple[set[Path], dict[Path, str]]:
    """
    Process files in parallel.

    Args:
        files: List of files to process.
        args: Parsed arguments.

    Returns:
        Tuple of (failed_files, error_messages).

    """
    max_workers = args.jobs if args.jobs > 0 else None
    successful_files: set[Path] = set()
    failed_files: set[Path] = set()
    error_messages: dict[Path, str] = {}

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_file,
                file_path,
                args.check,
                not args.no_ruff,
                args.verbose,
            ): file_path
            for file_path in files
        }

        for future in as_completed(futures):
            file_path, success, error_message = future.result()
            if success:
                successful_files.add(file_path)
            else:
                failed_files.add(file_path)
                if error_message:
                    error_messages[file_path] = error_message

    # Print summary
    logger.info("Successfully processed %d files.", len(successful_files))

    return failed_files, error_messages


def main() -> None:
    """Run the script."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    args = _parse_arguments()

    # Process exclude patterns
    exclude_patterns = _load_exclude_patterns(args)

    # Find Python files to process
    files = find_python_files(
        specific_files=args.files if args.files else None,
        exclude_patterns=exclude_patterns,
    )

    if not files:
        logger.info("No Python files found to process.")
        return

    logger.info("Found %d Python files to process.", len(files))

    # Process files in parallel
    failed_files, error_messages = _process_files_in_parallel(files, args)

    # Print errors
    if failed_files:
        logger.error("Failed to process %d files:", len(failed_files))
        for file_path in failed_files:
            logger.error("  - %s", file_path)
            if args.verbose and file_path in error_messages:
                logger.error("    Error: %s", error_messages[file_path])

    sys.exit(1 if failed_files else 0)


if __name__ == "__main__":
    main()
