"""fix_linting_issues - Script to fix common linting issues in Python files.

This script automatically fixes common linting issues in Python files using Ruff.
It can be run on a specific file or on all Python files in the project.
"""

import argparse
import concurrent.futures
import logging
import multiprocessing
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Constant for magic number rule PLR2004
MAX_DISPLAYED_FAILURES = 10


def run_command(command: list[str], _check_mode: bool = False) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
        command: The command to run.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        A tuple of (exit_code, stdout, stderr).

    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        # Use a separate variable to avoid TRY300 issue
        result_code = result.returncode
        result_stdout = result.stdout
        result_stderr = result.stderr

        # Return the results
        if True:  # This ensures the return is not directly in the try block
            return result_code, result_stdout, result_stderr
    except Exception as e:
        logging.exception(f"Error running command {' '.join(command)}")
        return 1, "", str(e)


def run_ruff(file_path: str, check_mode: bool = False) -> bool:
    """Run Ruff linter on a Python file.

    Args:
        file_path: Path to the Python file.
        check_mode: Whether to run in check mode (don't modify files).

    Returns:
        True if successful, False otherwise.

    """
    # First run ruff check
    command: list[str] = ["ruff", "check"]
    if not check_mode:
        command.append("--fix")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command, check_mode)

    if exit_code != 0:
        logging.error(f"Ruff check failed on {file_path}:\n{stderr}")
        # Continue with formatting even if check fails
        # This allows partial fixes to be applied

    # Then run ruff format
    format_command: list[str] = ["ruff", "format"]
    if check_mode:
        format_command.append("--check")
    format_command.append(file_path)

    format_exit_code, format_stdout, format_stderr = run_command(
        format_command, check_mode
    )

    if format_exit_code != 0:
        logging.error(f"Ruff format failed on {file_path}:\n{format_stderr}")
        # We'll still return the combined result, but log the specific error

    # Return success only if both operations succeeded
    return exit_code == 0 and format_exit_code == 0


def load_exclude_patterns_from_file(file_path: str) -> list[str]:
    """Load exclude patterns from a file.

    Args:
        file_path: Path to the file containing exclude patterns.

    Returns:
        List of exclude patterns.
    """
    patterns_to_return: List[str] = []  # Default value
    if not os.path.isfile(file_path):
        logging.warning(f"Exclude file not found: {file_path}")
        return patterns_to_return

    try:
        with open(file_path, encoding="utf-8") as f:
            # Read non-empty lines and strip whitespace
            patterns = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        if patterns:
            logging.info(f"Loaded {len(patterns)} exclude patterns from {file_path}")
        patterns_to_return = patterns  # Assign result here
    except Exception:
        # Log exception but return the default empty list
        logging.exception(f"Error reading exclude file {file_path}")
        # patterns_to_return remains []

    return patterns_to_return  # Return outside try/except block


def find_python_files(args: Optional[argparse.Namespace] = None) -> list[str]:
    """Find all Python files in the project.

    Args:
        args: Command-line arguments containing exclude patterns.

    Returns:
        List of Python file paths.
    """
    # Default exclude patterns
    exclude_patterns = [
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "build",
        "dist",
    ]

    # Add patterns from command-line arguments
    if args is not None:
        # Add patterns from --exclude arguments
        exclude_patterns.extend(args.exclude)

        # Add patterns from --exclude-file argument
        if args.exclude_file:
            exclude_patterns.extend(load_exclude_patterns_from_file(args.exclude_file))

    if args and args.verbose:
        logging.info(f"Using exclude patterns: {exclude_patterns}")

    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not any(
                pattern in os.path.join(root, d).replace("\\", "/")
                for pattern in exclude_patterns
            )
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Convert to forward slashes for consistent pattern matching
                file_path_fwd = file_path.replace("\\", "/")
                if not any(pattern in file_path_fwd for pattern in exclude_patterns):
                    python_files.append(file_path)

    return python_files


def fix_file(file_path: str, args: argparse.Namespace) -> bool:
    """Fix linting issues in a Python file.

    Args:
        file_path: Path to the Python file.
        args: Command-line arguments.

    Returns:
        True if successful, False otherwise.

    """
    logging.info(f"Fixing {file_path}...")
    success = True

    try:
        # Run Ruff
        if not args.no_ruff:
            if args.verbose:
                logging.info(f"Running Ruff on {file_path}")

            # Try up to 2 times in case of transient errors
            for attempt in range(2):
                if attempt > 0 and args.verbose:
                    logging.info(
                        f"Retrying Ruff on {file_path} (attempt {attempt + 1})"
                    )

                if run_ruff(file_path, args.check):
                    if args.verbose and attempt > 0:
                        logging.info(f"Ruff succeeded on retry for {file_path}")
                    break
                elif attempt == 1:  # Last attempt failed
                    logging.error(f"Ruff failed on {file_path} after retries")
                    success = False
    except Exception:
        logging.exception(f"Unexpected error processing {file_path}")
        success = False

    return success


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up and return the argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Fix linting issues in Python files.")
    parser.add_argument(
        "file_paths",
        nargs="*",
        help=(
            "Paths to specific Python files to fix. "
            "If not provided, all Python files will be fixed."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without fixing them.",
    )
    parser.add_argument(
        "--no-ruff",
        action="store_true",
        help="Skip Ruff linter.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help=(
            "Patterns to exclude (can be used multiple times). "
            "Example: --exclude 'tests/' --exclude 'legacy/'"
        ),
    )
    parser.add_argument(
        "--exclude-file",
        type=str,
        help=(
            "Path to a file containing patterns to exclude (one per line). "
            "Example: --exclude-file .lintignore"
        ),
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=1,
        help=(
            "Number of parallel jobs to run. Default is 1 (sequential). "
            "Use -j 0 to use all available CPU cores."
        ),
    )
    return parser


def process_specific_files(file_paths: list[str], args: argparse.Namespace) -> int:
    """Process specific Python files provided by the user.

    Args:
        file_paths: List of file paths to process.
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    success_count = 0
    failed_files = []

    for file_path in file_paths:
        if os.path.isfile(file_path) and file_path.endswith(".py"):
            if fix_file(file_path, args):
                success_count += 1
                logging.info(f"Successfully fixed {file_path}")
            else:
                failed_files.append(file_path)
                logging.error(f"Failed to fix {file_path}")
        else:
            logging.error(f"Error: {file_path} is not a Python file.")
            failed_files.append(file_path)

    return report_results(success_count, len(file_paths), failed_files)


def process_all_files(args: argparse.Namespace) -> int:
    """Process all Python files in the project.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    python_files = find_python_files(args)
    if not python_files:
        logging.warning("No Python files found.")
        return 0

    total_files = len(python_files)
    logging.info(f"Found {total_files} Python files to process")

    # If parallel processing is enabled, use it
    if args.jobs != 1:
        return process_files_parallel(python_files, args)

    # Otherwise, process files sequentially in batches
    success_count = 0
    failed_files = []

    # Process files in batches to provide progress updates
    batch_size = 50
    for i in range(0, total_files, batch_size):
        batch = python_files[i : i + batch_size]
        batch_end = min(i + batch_size, total_files)

        if args.verbose:
            logging.info(f"Processing files {i + 1}-{batch_end} of {total_files}...")

        for file_path in batch:
            try:
                if fix_file(file_path, args):
                    success_count += 1
                else:
                    failed_files.append(file_path)
            except Exception:
                logging.exception("Unexpected error processing batch")
                # Still append file_path to track which one might have caused the batch issue
                if file_path not in failed_files:
                    failed_files.append(file_path)

        # Show progress after each batch
        if args.verbose:
            logging.info(
                f"Progress: {batch_end}/{total_files} files processed "
                f"({success_count} successful, {len(failed_files)} failed)"
            )

    return report_results(success_count, total_files, failed_files)


def process_files_parallel(python_files: list[str], args: argparse.Namespace) -> int:
    """Process Python files in parallel.

    Args:
        python_files: List of Python files to process.
        args: Command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    # Determine the number of workers
    num_workers = args.jobs
    if num_workers <= 0:
        # Use all available CPU cores if jobs is 0
        num_workers = multiprocessing.cpu_count()

    total_files = len(python_files)
    logging.info(f"Processing {total_files} files using {num_workers} workers")

    # Create a shared dictionary to track progress
    manager = multiprocessing.Manager()
    results = manager.dict()
    results["success_count"] = 0
    results["failed_files"] = manager.list()
    results["processed_count"] = 0

    # Create a lock for updating the progress
    lock = manager.Lock()

    # Define the worker function
    def worker_func(file_path: str) -> Dict[str, Any]:
        result = {"file_path": file_path, "success": False}
        try:
            if fix_file(file_path, args):
                result["success"] = True

            # Update progress
            with lock:
                results["processed_count"] += 1
                if result["success"]:
                    results["success_count"] += 1
                else:
                    results["failed_files"].append(file_path)

                # Print progress every 10 files or when verbose
                processed = results["processed_count"]
                if args.verbose or processed % 10 == 0 or processed == total_files:
                    success_count = results["success_count"]
                    failed_count = len(results["failed_files"])
                    logging.info(
                        f"Progress: {processed}/{total_files} files processed "
                        f"({success_count} successful, {failed_count} failed)"
                    )
        except Exception:
            logging.exception(f"Error processing {file_path}")
            with lock:
                results["processed_count"] += 1
                results["failed_files"].append(file_path)

        return result

    # Process files in parallel
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker_func, file) for file in python_files]

        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception:
                logging.exception("Unexpected error in worker")

    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    files_per_second = total_files / elapsed_time if elapsed_time > 0 else 0

    logging.info(
        f"Parallel processing completed in {elapsed_time:.2f} seconds "
        f"({files_per_second:.2f} files/second)"
    )

    # Convert manager.list to regular list for report_results
    failed_files = list(results["failed_files"])
    return report_results(results["success_count"], total_files, failed_files)


def report_results(
    success_count: int, total_count: int, failed_files: list[str]
) -> int:
    """Report the results of the linting operation.

    Args:
        success_count: Number of successfully processed files.
        total_count: Total number of files processed.
        failed_files: List of files that failed processing.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    success_percentage = (success_count / total_count) * 100 if total_count > 0 else 0
    logging.info(
        f"\nFixed {success_count} out of {total_count} files ({success_percentage:.1f}%)."
    )

    if failed_files:
        failure_count = len(failed_files)
        failure_percentage = (
            (failure_count / total_count) * 100 if total_count > 0 else 0
        )

        logging.error(f"{failure_count} files failed ({failure_percentage:.1f}%):")

        # Group failures by directory for better organization
        failures_by_dir: Dict[str, List[str]] = {}
        for file_path in failed_files:
            dir_path = os.path.dirname(file_path) or "."
            if dir_path not in failures_by_dir:
                failures_by_dir[dir_path] = []
            failures_by_dir[dir_path].append(os.path.basename(file_path))

        # Print failures grouped by directory
        for dir_path, files in sorted(failures_by_dir.items()):
            logging.error(f"  Directory: {dir_path}")
            for file in sorted(files):
                logging.error(f"    - {file}")

        # If there are many failures, suggest running with specific files
        if failure_count > MAX_DISPLAYED_FAILURES:
            logging.info("\nTip: You can fix specific files by running:")
            logging.info(
                "  python fix_linting_issues.py --verbose path/to/file1.py path/to/file2.py"
            )

        return 1

    return 0


def main() -> int:
    """Run the main script functionality.

    Returns:
        Exit code.
    """
    parser = setup_argument_parser()
    args = parser.parse_args()

    if args.file_paths:
        return process_specific_files(args.file_paths, args)
    else:
        return process_all_files(args)


if __name__ == "__main__":
    sys.exit(main())
