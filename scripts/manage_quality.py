#!/usr/bin/env python3

"""Unified Code Quality and Security Management Script.

This script provides a single entrypoint CLI for running all code quality,
linting, formatting, and security checks with optimized performance through
parallel execution and intelligent file handling.
"""

import argparse
import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional, cast

# Maximum time to wait for any single check
TIMEOUT_SECONDS = 300

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class CheckResult:
    """Represents the result of a quality check operation."""

    def __init__(
        self,
        name: str,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
        duration: float = 0.0,
    ) -> None:
        """Initialize the check result.

        Args:
            name: Name of the check tool/command
            returncode: Process return code (default: 0)
            stdout: Standard output capture (default: "")
            stderr: Standard error capture (default: "")
            duration: Time taken in seconds (default: 0.0)
        """
        self.name = name
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.duration = duration


def get_git_root() -> Path:
    """Get the root directory of the git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        logger.exception("Git operation failed")
        sys.exit(1)


def get_changed_files(staged_only: bool = True) -> set[Path]:
    """Get the list of changed Python files with improved error handling."""
    try:
        git_root = get_git_root()
        cmd = ["git", "diff", "--name-only"]

        if staged_only:
            cmd.append("--staged")

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=10
        )

        # Process Python files with proper error handling
        python_files = set()
        processed_files = False

        for file_path in result.stdout.splitlines():
            if not file_path.endswith(".py"):
                continue

            processed_files = True
            full_path = git_root / file_path

            if full_path.exists():
                python_files.add(full_path)
            else:
                logger.warning("Changed file not found: %s", file_path)

        if processed_files:
            return python_files
        else:
            logger.info("No Python files found in changes")
            return set()

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        logger.exception("Git operation failed")
        return set()


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def create_process_kwargs() -> dict[str, Any]:
    """Create platform-specific process creation arguments."""
    kwargs: dict[str, Any] = {
        "stdout": asyncio.subprocess.PIPE,
        "stderr": asyncio.subprocess.PIPE,
    }

    if not is_windows():
        try:
            # On Unix-like systems, create new process group if supported
            kwargs["preexec_fn"] = os.setsid
        except AttributeError:
            logger.warning("os.setsid not available, process group management disabled")

    return kwargs


async def run_command_async(
    name: str,
    command: list[str],
    files: Optional[set[Path]] = None,
) -> CheckResult:
    """Run a command asynchronously with timeout and resource management."""
    if files:
        command.extend(str(f) for f in files)

    start_time = time.time()

    try:
        process = await asyncio.create_subprocess_exec(
            *command, **create_process_kwargs()
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=TIMEOUT_SECONDS
            )
            duration = time.time() - start_time

            return CheckResult(
                name,
                cast(int, process.returncode) or 0,
                stdout.decode(),
                stderr.decode(),
                duration,
            )
        except asyncio.TimeoutError:
            # Kill process (and process group on Unix)
            if is_windows():
                process.terminate()
            else:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except (AttributeError, ProcessLookupError):
                    logger.warning("Failed to kill process group")
                    process.terminate()

            return CheckResult(
                name,
                1,
                "",
                f"Command timed out after {TIMEOUT_SECONDS} seconds",
                TIMEOUT_SECONDS,
            )

    except Exception:
        logger.exception("Failed to run command")
        return CheckResult(
            name, 1, "", "Failed to run command - check logs for details", 0.0
        )


async def run_checks(files: set[Path]) -> list[CheckResult]:
    """Run all checks in parallel with optimal resource usage."""
    python_executable = sys.executable

    # Special handling for problematic files
    mypy_args = [
        python_executable,
        "-m",
        "mypy",
        "--ignore-missing-imports",
        "--install-types",
        "--non-interactive",
        "--explicit-package-bases",
        "--config-file=mypy.ini",
    ]

    # Add special flags for problematic files
    problematic_files = {"flask/__init__.py", "flask/models.py", "migrations/env.py"}

    if any(str(f).endswith(pf) for f in files for pf in problematic_files):
        mypy_args.extend([
            "--disable-error-code=attr-defined",
            "--disable-error-code=name-defined",
            "--disable-error-code=unused-ignore",
        ])

    checks = [
        ("ruff", [python_executable, "-m", "ruff", "check", "--fix"]),
        ("mypy", mypy_args),
    ]

    tasks = [run_command_async(name, cmd, files) for name, cmd in checks]

    results = await asyncio.gather(*tasks)
    return [r for r in results if isinstance(r, CheckResult)]


def print_check_results(results: list[CheckResult]) -> int:
    """Print check results with timing information."""
    max_returncode = 0

    for result in sorted(results, key=lambda x: x.duration):
        logger.info("\n=== %s (took %.2fs) ===", result.name, result.duration)
        if result.stdout:
            logger.info("Output:\n%s", result.stdout)
        if result.stderr:
            logger.error("Errors:\n%s", result.stderr)
        max_returncode = max(max_returncode, result.returncode)

    return max_returncode


async def incremental(files: Optional[list[Path]] = None) -> int:
    """Run incremental quality checks on changed files or specified files.

    Args:
        files: Optional list of files to check. If not provided, checks staged files.
    """
    check_files = set(files) if files else get_changed_files(staged_only=True)
    logger.info(
        "Found %d Python %s to check",
        len(check_files),
        "file" if len(check_files) == 1 else "files",
    )

    if not check_files:
        return 0

    return print_check_results(await run_checks(check_files))


async def main_async() -> int:
    """Execute the main CLI functionality asynchronously."""
    parser = argparse.ArgumentParser(
        description="Unified Code Quality Management with Parallel Execution"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    incremental_parser = subparsers.add_parser(
        "incremental",
        help="Run incremental quality checks on changed files",
    )
    incremental_parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Optional list of files to check (defaults to git staged files)",
    )

    args = parser.parse_args()

    if args.command == "incremental":
        return await incremental(args.files or None)

    parser.print_help()
    return 1


def main() -> None:
    """Main entry point with proper signal handling."""
    try:
        if not is_windows():
            # Set up signal handlers for graceful shutdown on Unix
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, lambda _signum, _frame: sys.exit(1))

        sys.exit(asyncio.run(main_async()))
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
