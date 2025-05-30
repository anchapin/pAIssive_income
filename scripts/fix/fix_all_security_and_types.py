#!/usr/bin/env python3
"""
Master security and code quality fixer.

This script runs all the fix scripts in the correct order to address:
1. Security issues (Bandit)
2. Type checking issues (Pyright)
3. Linting issues (Ruff)
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fix security, type checking, and linting issues"
    )

    parser.add_argument(
        "--security-only", action="store_true", help="Only fix security issues"
    )

    parser.add_argument(
        "--types-only", action="store_true", help="Only fix type checking issues"
    )

    parser.add_argument(
        "--lint-only", action="store_true", help="Only fix linting issues"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode - don't modify files, just report issues",
    )

    parser.add_argument(
        "--directory",
        "-d",
        help="Directory to fix (default: current directory)",
        default=".",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def run_script(
    script_path: str, script_args: list[str], check_mode: bool = False
) -> tuple[int, str, str]:
    """
    Run a Python script securely.

    Args:
        script_path: Path to the script
        script_args: Arguments to pass to the script
        check_mode: Whether to add --check to the command

    Returns:
        Tuple of (exit_code, stdout, stderr)

    """
    cmd = [sys.executable, script_path]

    if check_mode:
        cmd.append("--check")

    cmd.extend(script_args)

    script_name = Path(script_path).name
    logger.info(f"Running {script_name}...")

    try:
        # Run command with safe defaults
        result = subprocess.run(
            cmd,
            check=False,
            shell=False,  # Never use shell=True for security
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            logger.warning(
                "{script_name} exited with code ",
                extra={"result.returncode": result.returncode},
            )
            if result.stdout:
                logger.debug("stdout: ", extra={"result.stdout": result.stdout})
            if result.stderr:
                logger.error("stderr: ", extra={"result.stderr": result.stderr})
        else:
            logger.info(f"{script_name} completed successfully")

        return result.returncode, result.stdout, result.stderr

    except Exception as e:
        logger.exception("Error running {script_name}: ", extra={"e": e})
        return 1, "", str(e)


def fix_security_issues(directory: str, check_mode: bool) -> bool:
    """
    Fix security issues in the codebase.

    Args:
        directory: Directory to fix
        check_mode: Whether to use check mode

    Returns:
        bool: Whether operation was successful

    """
    logger.info("Fixing security issues...")

    # 1. Run the fix_security_issues.py script
    security_script = Path("scripts/fix/fix_security_issues.py")
    if not security_script.exists():
        logger.error(
            "Security fix script not found: ",
            extra={"security_script": security_script},
        )
        return False

    security_args = ["--directory", directory]
    if check_mode:
        security_args.append("--scan-only")

    code, _, _ = run_script(str(security_script), security_args)
    if code != 0:
        logger.warning("Security fix script returned non-zero code")

    # 2. Run the fix_bandit_security_scan.py script
    bandit_script = Path("scripts/fix/fix_bandit_security_scan.py")
    if bandit_script.exists():
        bandit_args = []
        code, _, _ = run_script(str(bandit_script), bandit_args, check_mode)
        if code != 0:
            logger.warning("Bandit fix script returned non-zero code")

    # 3. Run the fix_duplicate_logging.py script
    logging_script = Path("scripts/fix/fix_duplicate_logging.py")
    if logging_script.exists():
        logging_args = ["--directory", directory]
        code, _, _ = run_script(str(logging_script), logging_args, check_mode)
        if code != 0:
            logger.warning("Logging fix script returned non-zero code")

    logger.info("Security fixes completed")
    return True


def fix_type_issues(directory: str, check_mode: bool) -> bool:
    """
    Fix type checking issues in the codebase.

    Args:
        directory: Directory to fix
        check_mode: Whether to use check mode

    Returns:
        bool: Whether operation was successful

    """
    logger.info("Fixing type checking issues...")

    pyright_script = Path("scripts/fix/fix_pyright_type_errors.py")
    if not pyright_script.exists():
        logger.error(
            "Type fix script not found: ", extra={"pyright_script": pyright_script}
        )
        return False

    type_args = ["--directory", directory]
    code, _, _ = run_script(str(pyright_script), type_args, check_mode)
    if code != 0:
        logger.warning("Type fix script returned non-zero code")

    logger.info("Type fixes completed")
    return True


def fix_lint_issues(directory: str, check_mode: bool) -> bool:
    """
    Fix linting issues in the codebase.

    Args:
        directory: Directory to fix
        check_mode: Whether to use check mode

    Returns:
        bool: Whether operation was successful

    """
    logger.info("Fixing linting issues...")

    lint_script = Path("scripts/fix/fix_all_issues_final.py")
    if not lint_script.exists():
        logger.error(
            "Linting fix script not found: ", extra={"lint_script": lint_script}
        )
        return False

    lint_args = []
    if directory != ".":
        lint_args.extend(["--dir", directory])

    code, _, _ = run_script(str(lint_script), lint_args, check_mode)
    if code != 0:
        logger.warning("Lint fix script returned non-zero code")

    logger.info("Linting fixes completed")
    return True


def main() -> int:
    """Run the main function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    directory = args.directory
    check_mode = args.check

    # Validate directory
    if not Path(directory).exists():
        logger.error("Directory not found: ", extra={"directory": directory})
        return 1

    # Run the fix scripts based on arguments
    success_count = 0
    total_count = 0

    # Fix security issues if requested or if no specific fixes requested
    if args.security_only or not any(
        [args.security_only, args.types_only, args.lint_only]
    ):
        total_count += 1
        if fix_security_issues(directory, check_mode):
            success_count += 1

    # Fix type checking issues if requested or if no specific fixes requested
    if args.types_only or not any(
        [args.security_only, args.types_only, args.lint_only]
    ):
        total_count += 1
        if fix_type_issues(directory, check_mode):
            success_count += 1

    # Fix linting issues if requested or if no specific fixes requested
    if args.lint_only or not any([args.security_only, args.types_only, args.lint_only]):
        total_count += 1
        if fix_lint_issues(directory, check_mode):
            success_count += 1

    # Summary
    if check_mode:
        logger.info(
            f"Check complete: {success_count}/{total_count} scripts ran successfully"
        )
    else:
        logger.info(
            f"Fixes complete: {success_count}/{total_count} fix scripts ran successfully"
        )

    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
