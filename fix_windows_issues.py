#!/usr/bin/env python3
"""Fix Windows-specific issues in Python files."""

import argparse
import logging
import os
import subprocess
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Constants
MAX_DEBUG_FILES = 5

# Directories to ignore
DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

# File patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dylib",
    "*.dll",
    "*.exe",
]


def normalize_paths(specific_files: list[str]) -> list[str]:
    """Normalize a list of file paths for Windows."""
    normalized_files = []
    for file_path in specific_files:
        try:
            # Convert to absolute path and normalize
            abs_path = os.path.abspath(file_path)
            norm_path = os.path.normpath(abs_path)
            if os.path.isfile(norm_path):
                normalized_files.append(norm_path)
        except Exception:
            continue
    return normalized_files


def should_ignore_directory(root: str, ignore_dirs: set) -> bool:
    """Check if a directory should be ignored."""
    norm_root = os.path.normpath(root)
    return any(ignore_dir in norm_root.split(os.sep) for ignore_dir in ignore_dirs)


def get_windows_ignore_patterns(patterns: list[str]) -> list[str]:
    """Convert ignore patterns to Windows-style paths."""
    windows_patterns = patterns.copy()
    for pattern in patterns:
        windows_patterns.append(os.path.normpath(f".\\{pattern}"))
    return windows_patterns


def parse_arguments() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fix code quality issues in Python files on Windows."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "Specific files to fix. "
            "If not provided, all Python files will be processed."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without fixing them.",
    )
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="Fix only syntax errors.",
    )
    parser.add_argument(
        "--format-only",
        action="store_true",
        help="Fix only formatting issues.",
    )
    parser.add_argument(
        "--no-black",
        action="store_true",
        help="Skip Black formatting.",
    )
    parser.add_argument(
        "--no-isort",
        action="store_true",
        help="Skip isort import sorting.",
    )
    parser.add_argument(
        "--no-ruff",
        action="store_true",
        help="Skip Ruff linting.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser.parse_args()


def find_python_files(specific_files: Optional[list[str]] = None) -> list[str]:
    """Find Python files to process, with Windows-specific path handling."""
    if specific_files:
        return normalize_paths(specific_files)

    python_files: list[str] = []
    ignore_patterns = get_windows_ignore_patterns(DEFAULT_IGNORE_PATTERNS)

    logger.info("Ignore patterns: %s", ignore_patterns)
    logger.info("Platform: %s", sys.platform)

    for root, _dirs, files in os.walk("."):
        # Debug output for the first few directories
        if len(python_files) < MAX_DEBUG_FILES:
            logger.debug("Checking directory: %s", root)

        # Check if this directory should be ignored
        if should_ignore_directory(root, DEFAULT_IGNORE_DIRS):
            if len(python_files) < MAX_DEBUG_FILES:
                logger.debug("Skipping ignored directory: %s", root)
            continue

        # Process Python files
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.normpath(os.path.join(root, file))
                python_files.append(file_path)
                if len(python_files) <= MAX_DEBUG_FILES:
                    logger.debug("Found Python file: %s", file_path)

    logger.info("Total Python files found: %d", len(python_files))
    return python_files


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr with Windows handling."""
    try:
        # Log command for debugging
        cmd_str = " ".join(command)
        logger.debug("Running command: %s", cmd_str)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )
        except Exception as run_error:
            logger.warning(
                "subprocess.run failed: %s, falling back to Popen", run_error
            )
            # Fall back to Popen if run fails
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        else:
            return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.exception("Error running command %s", " ".join(command))
        return 1, "", str(e)


def fix_syntax_errors(file_path: str) -> bool:
    """Fix syntax errors in a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            compile(content, file_path, "exec")
        except SyntaxError:
            # File has syntax errors, attempt to fix
            # For now, just return False
            return False
        else:
            return True  # No syntax errors
    except Exception:
        logger.exception("Error fixing syntax errors in %s", file_path)
        return False


def process_files(python_files: list[str]) -> tuple[int, list[str]]:
    """Process a list of Python files and return success count and failed files."""
    success_count = 0
    failed_files = []

    for i, file_path in enumerate(python_files):
        logger.info("Processing file %d/%d: %s", i + 1, len(python_files), file_path)
        try:
            # For now, just fix syntax errors
            if fix_syntax_errors(file_path):
                success_count += 1
                logger.info("✓ Successfully processed %s", file_path)
            else:
                failed_files.append(file_path)
                logger.warning("✗ Failed to process %s", file_path)
        except Exception:
            logger.exception("Error processing %s", file_path)
            failed_files.append(file_path)

    return success_count, failed_files


def print_summary(
    success_count: int, total_files: int, failed_files: list[str]
) -> None:
    """Print a summary of the processing results."""
    logger.info("=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)
    logger.info(
        "Successfully processed %d out of %d files.",
        success_count,
        total_files,
    )

    if failed_files:
        logger.warning("Failed files:")
        for file_path in failed_files:
            logger.warning("  - %s", file_path)


def main() -> int:
    """Run the main program to fix code quality issues on Windows."""
    try:
        logger.info("Running fix_windows_issues.py on platform: %s", sys.platform)
        logger.info("Python version: %s", sys.version)
        logger.info("Current working directory: %s", os.getcwd())

        args = parse_arguments()
        logger.debug("Arguments: %s", args)

        # Find Python files to process
        logger.info("Finding Python files to process...")
        python_files = find_python_files(args.files)

        if not python_files:
            logger.info("No Python files found to process.")
            return 0

        logger.info("Processing %d Python files...", len(python_files))

        # Process files and get results
        success_count, failed_files = process_files(python_files)

        # Print summary
        print_summary(success_count, len(python_files), failed_files)

        return 0 if success_count == len(python_files) else 1
    except Exception:
        logger.exception("Error in main function")
        return 1


if __name__ == "__main__":
    sys.exit(main())
