#!/usr/bin/env python3
"""
Test script to verify that security reports are properly created.

This script checks that:
1. The security-reports directory exists
2. The bandit-results.json and bandit-results-ini.json files exist
3. The JSON files are valid
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# Helper for safe subprocess execution (addresses Ruff S603)
def _safe_subprocess_run(
    cmd: list[str],
    **kwargs: Any,  # noqa: ANN401
) -> subprocess.CompletedProcess[str]:
    """Safely run a subprocess command, only allowing trusted binaries."""
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    allowed_binaries = {sys.executable}
    if not cmd or (
        cmd[0] not in allowed_binaries and not str(cmd[0]).endswith("pytest")
    ):
        msg = f"Untrusted or unsupported command: {cmd}"
        raise ValueError(msg)
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
    return subprocess.run(cmd, check=False, shell=False, **filtered_kwargs)  # nosec B603  # noqa: S603


def check_security_reports_dir() -> bool:
    """
    Check if the security-reports directory exists.

    Returns:
        bool: True if the directory exists, False otherwise

    """
    reports_dir = Path("security-reports")
    if reports_dir.exists():
        logger.info("security-reports directory exists")
        return True
    logger.error("security-reports directory does not exist")
    return False


def check_json_files() -> bool:
    """
    Check if the bandit-results.json and bandit-results-ini.json files exist.

    Returns:
        bool: True if both files exist, False otherwise

    """
    bandit_results = Path("security-reports/bandit-results.json")
    bandit_results_ini = Path("security-reports/bandit-results-ini.json")

    if bandit_results.exists():
        logger.info("bandit-results.json exists")
    else:
        logger.error("bandit-results.json does not exist")
        return False

    if bandit_results_ini.exists():
        logger.info("bandit-results-ini.json exists")
    else:
        logger.error("bandit-results-ini.json does not exist")
        return False

    return True


def validate_json_files() -> bool:
    """
    Validate that the JSON files are valid.

    Returns:
        bool: True if both files are valid JSON, False otherwise

    """
    bandit_results = Path("security-reports/bandit-results.json")
    bandit_results_ini = Path("security-reports/bandit-results-ini.json")

    try:
        with bandit_results.open() as f:
            json.load(f)
        logger.info("bandit-results.json is valid JSON")
    except (json.JSONDecodeError, Exception):
        logger.exception("bandit-results.json is not valid JSON")
        return False

    try:
        with bandit_results_ini.open() as f:
            json.load(f)
        logger.info("bandit-results-ini.json is valid JSON")
    except (json.JSONDecodeError, Exception):
        logger.exception("bandit-results-ini.json is not valid JSON")
        return False

    return True


def main() -> int:
    """Run all security report checks and return exit code."""
    # Check if the security-reports directory exists
    if not check_security_reports_dir():
        # Try to create the directory
        try:
            Path("security-reports").mkdir(parents=True, exist_ok=True)
            logger.info("Created security-reports directory")
        except Exception:
            logger.exception("Failed to create security-reports directory")
            return 1

    # Check if the JSON files exist
    if not check_json_files():
        # Try to run the test_bandit_config.py script
        try:
            _safe_subprocess_run(
                [str(Path("test_bandit_config.py"))], check=False, shell=False
            )
            logger.info("Ran test_bandit_config.py")
        except Exception:
            logger.exception("Failed to run test_bandit_config.py")
            return 1

        # Check again
        if not check_json_files():
            logger.error(
                "JSON files still do not exist after running test_bandit_config.py"
            )
            return 1

    # Validate the JSON files
    if not validate_json_files():
        logger.error("JSON files are not valid")
        return 1

    logger.info("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
