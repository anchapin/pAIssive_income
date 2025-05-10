#!/usr/bin/env python3
"""Fix Black formatting issues in specific files.

This script runs Black on the files that were identified as needing reformatting
in the GitHub Actions workflow.
"""

import argparse
import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Files that need reformatting according to the GitHub Actions workflow
FILES_TO_FIX = [
    "regenerate_venv.py",
    "fix_potential_secrets.py",
    "test_security_fixes.py",
    "common_utils/secrets/secrets_manager.py",
    "fix_security_issues.py",
]


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.

    Args:
        command: Command to run

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        logger.exception(f"Error running command {' '.join(command)}")
        return 1, "", str(e)
    else:
        return result.returncode, result.stdout, result.stderr


def run_black(file_path: str, check_mode: bool = False) -> bool:
    """Run Black formatter on a Python file.

    Args:
        file_path: Path to the Python file
        check_mode: Whether to run in check mode (don't modify files)

    Returns:
        True if successful, False otherwise
    """
    command = ["black"]
    if check_mode:
        command.append("--check")
    command.append(file_path)

    exit_code, stdout, stderr = run_command(command)
    if exit_code != 0:
        logger.error(f"Black failed on {file_path}: {stderr}")
        return False

    logger.info(f"Black succeeded on {file_path}")
    return True


def fix_files(files: list[str], check_mode: bool = False) -> bool:
    """Fix formatting issues in the specified files.

    Args:
        files: List of files to fix
        check_mode: Whether to run in check mode (don't modify files)

    Returns:
        True if all files were fixed successfully, False otherwise
    """
    success = True
    for file_path in files:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            success = False
            continue

        logger.info(f"Running Black on {file_path}")
        if not run_black(file_path, check_mode):
            success = False

    return success


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fix Black formatting issues in specific files."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for issues without fixing them.",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific files to fix. If not provided, will use the predefined list.",
    )
    return parser.parse_args()


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_args()
    files_to_fix = args.files if args.files else FILES_TO_FIX

    logger.info(f"Fixing Black formatting issues in {len(files_to_fix)} files")
    if args.check:
        logger.info("Running in check mode (no changes will be made)")

    if fix_files(files_to_fix, args.check):
        logger.info("All files fixed successfully")
        return 0
    else:
        logger.error("Failed to fix all files")
        return 1


if __name__ == "__main__":
    sys.exit(main())
