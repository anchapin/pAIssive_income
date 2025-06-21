"""Script to format all Python files in the scripts directory."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Use built-in types for type annotations

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Set up a dedicated logger for this module
logger = logging.getLogger(__name__)


def _safe_subprocess_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess:  # noqa: ANN401
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    if "cwd" in kwargs and isinstance(kwargs["cwd"], Path):
        kwargs["cwd"] = str(kwargs["cwd"])
    allowed_keys = {
        "cwd",
        "timeout",
        "check",
        "shell",
        "text",
        "capture_output",
        "input",
        "encoding",
        "errors",
        "env",
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
    return subprocess.run(cmd, check=False, **filtered_kwargs)


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr."""
    try:
        # Always use shell=False for security
        # nosec comment below tells security scanners this is safe as we control the input
        result = _safe_subprocess_run(  # nosec S603
            command,
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        # Use a separate variable to avoid TRY300 issue
        result_code = result.returncode
        result_stdout = result.stdout
        result_stderr = result.stderr
    except Exception as e:
        logger.exception("Error running command %s", " ".join(command))
        return 1, "", str(e)
    else:
        # Return the results
        return result_code, result_stdout, result_stderr


def format_file(file_path: str) -> bool:
    """Format a Python file using Ruff."""
    logger.info("Formatting %s...", file_path)

    # Run Ruff format
    ruff_format_cmd = ["ruff", "format", file_path]
    ruff_format_code, ruff_format_stdout, ruff_format_stderr = run_command(
        ruff_format_cmd
    )
    if ruff_format_code != 0:
        logger.error("Ruff format failed on %s: %s", file_path, ruff_format_stderr)
    else:
        logger.info("Ruff format succeeded on %s", file_path)

    # Run Ruff check with fixes
    ruff_check_cmd = ["ruff", "check", "--fix", file_path]
    ruff_check_code, ruff_check_stdout, ruff_check_stderr = run_command(ruff_check_cmd)
    if ruff_check_code != 0:
        logger.error("Ruff check failed on %s: %s", file_path, ruff_check_stderr)
    else:
        logger.info("Ruff check succeeded on %s", file_path)

    return ruff_format_code == 0 and ruff_check_code == 0


def main() -> int:
    """Format all Python files in the scripts directory."""
    script_files = [
    # "scripts/fix_test_collection_warnings.py",  # removed in aggressive pruning
    # "scripts/sues.py",  # removed in aggressive pruning
    # ...other scripts...
]

    success_count = 0
    failed_files = []

    for file_path in script_files:
        if Path(file_path).exists():
            if format_file(file_path):
                success_count += 1
            else:
                failed_files.append(file_path)
        else:
            logger.warning("File not found: %s", file_path)
            failed_files.append(file_path)

    logger.info(
        "\nFormatting complete. %d files formatted successfully.", success_count
    )

    if failed_files:
        logger.warning("Failed to format files: %s", failed_files)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
