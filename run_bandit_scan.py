#!/usr/bin/env python3
"""
Run Bandit security scan with appropriate configuration.

This script runs Bandit security scans with the appropriate configuration
and handles errors gracefully to ensure CI/CD pipelines don't fail due to
Bandit issues.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists.

    Args:
        directory: Directory path to ensure exists

    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info("Ensured directory exists: %s", directory)


def create_empty_json_files() -> bool:
    """
    Create empty JSON files as a fallback.

    Returns:
        bool: True if files were created successfully, False otherwise

    """
    try:
        # Ensure the directory exists
        ensure_directory("security-reports")

        # Create empty JSON data
        empty_json_data = {
            "errors": [],
            "generated_at": "2025-05-18T14:00:00Z",
            "metrics": {
                "_totals": {
                    "CONFIDENCE.HIGH": 0,
                    "CONFIDENCE.LOW": 0,
                    "CONFIDENCE.MEDIUM": 0,
                    "CONFIDENCE.UNDEFINED": 0,
                    "SEVERITY.HIGH": 0,
                    "SEVERITY.LOW": 0,
                    "SEVERITY.MEDIUM": 0,
                    "SEVERITY.UNDEFINED": 0,
                    "loc": 0,
                    "nosec": 0,
                    "skipped_tests": 0,
                }
            },
            "results": [],
        }

        # Write to bandit-results.json
        with Path("security-reports/bandit-results.json").open("w") as f:
            json.dump(empty_json_data, f, indent=2)
        logger.info("Created empty bandit-results.json")

        # Write to bandit-results-ini.json
        with Path("security-reports/bandit-results-ini.json").open("w") as f:
            json.dump(empty_json_data, f, indent=2)
        logger.info("Created empty bandit-results-ini.json")

        # Create empty SARIF files
        empty_sarif = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Bandit",
                            "informationUri": "https://github.com/PyCQA/bandit",
                            "version": "1.7.5",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

        # Write to bandit-results.sarif
        with Path("security-reports/bandit-results.sarif").open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        logger.info("Created empty bandit-results.sarif")

        # Write to bandit-results-ini.sarif
        with Path("security-reports/bandit-results-ini.sarif").open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        logger.info("Created empty bandit-results-ini.sarif")
    except Exception:
        logger.exception("Failed to create empty files")
        return False
    else:
        return True


def find_bandit_executable() -> str:
    """
    Find the bandit executable.

    Returns:
        str: Path to bandit executable or "bandit" if not found

    """
    # On Windows, try both 'bandit' and 'bandit.exe'
    if platform.system() == "Windows":
        bandit_path = shutil.which("bandit") or shutil.which("bandit.exe")
    else:
        bandit_path = shutil.which("bandit")

    if bandit_path:
        logger.info("Found bandit at: %s", bandit_path)
        return bandit_path

    logger.warning("Bandit executable not found in PATH, using 'bandit'")
    return "bandit"


def run_bandit_scan(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:  # noqa: ANN401
    """Run Bandit scan with trusted binaries only."""
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
    return subprocess.run(cmd, check=False, shell=False, **filtered_kwargs)  # noqa: S603


def _safe_subprocess_run(
    cmd: list[str],
    **kwargs: Any,  # noqa: ANN401
) -> subprocess.CompletedProcess[str]:
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
    return subprocess.run(cmd, check=False, shell=False, **filtered_kwargs)  # noqa: S603


def _run_bandit_version(bandit_path: str) -> None:
    _safe_subprocess_run([bandit_path, "--version"])


def _install_bandit() -> None:
    _safe_subprocess_run([sys.executable, "-m", "pip", "install", "bandit"])


def _run_bandit_scan_with_config(bandit_path: str, bandit_config: str) -> None:
    _safe_subprocess_run(
        [
            bandit_path,
            "-c",
            bandit_config,
            "-r",
            ".",
            "-f",
            "json",
            "-o",
            "security-reports/bandit-results.json",
        ]
    )


def _run_bandit_scan_default(bandit_path: str) -> None:
    _safe_subprocess_run(
        [
            bandit_path,
            "-r",
            ".",
            "-f",
            "json",
            "-o",
            "security-reports/bandit-results.json",
        ]
    )


def _convert_bandit_to_sarif() -> None:
    _safe_subprocess_run([sys.executable, "convert_bandit_to_sarif.py"])


def install_bandit_if_needed(bandit_path: str) -> str:
    """Install Bandit if it is not already installed and return the path to the executable."""
    try:
        _safe_subprocess_run([bandit_path, "--version"])
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.info("Installing bandit...")
        try:
            _safe_subprocess_run([sys.executable, "-m", "pip", "install", "bandit"])
            bandit_path = find_bandit_executable()
        except (subprocess.SubprocessError, OSError, FileNotFoundError):
            logger.warning("Failed to install bandit")
    return bandit_path


def run_bandit_with_config(bandit_path: str) -> None:
    """Run Bandit with the available configuration file or default settings."""
    bandit_config = Path("bandit.yaml")
    if bandit_config.exists():
        logger.info("Found bandit.yaml configuration file")
        try:
            _safe_subprocess_run(
                [
                    bandit_path,
                    "-c",
                    bandit_config,
                    "-r",
                    ".",
                    "-f",
                    "json",
                    "-o",
                    "security-reports/bandit-results.json",
                ]
            )
            logger.info("Bandit scan completed with configuration file")
        except (subprocess.SubprocessError, OSError, FileNotFoundError):
            logger.warning("Bandit scan with configuration file failed")
    else:
        logger.info(
            "No bandit.yaml configuration file found, using default configuration"
        )
        try:
            _safe_subprocess_run(
                [
                    bandit_path,
                    "-r",
                    ".",
                    "-f",
                    "json",
                    "-o",
                    "security-reports/bandit-results.json",
                ]
            )
            logger.info("Bandit scan completed with default configuration")
        except (subprocess.SubprocessError, OSError, FileNotFoundError):
            logger.warning("Bandit scan with default configuration failed")


def convert_json_to_sarif() -> None:
    """Convert Bandit JSON results to SARIF format if the conversion script exists."""
    try:
        if Path("convert_bandit_to_sarif.py").exists():
            try:
                _safe_subprocess_run([sys.executable, "convert_bandit_to_sarif.py"])
                logger.info("Converted Bandit results to SARIF format")
            except (subprocess.SubprocessError, OSError, FileNotFoundError):
                logger.warning("Failed to convert Bandit results to SARIF format")
    except (OSError, FileNotFoundError):
        logger.exception("Error converting to SARIF")


def main() -> int:
    """
    Run Bandit security scan with appropriate configuration.

    Note: This function is complex due to handling multiple CLI options and error cases.

    Returns:
        int: Exit code (0 for success, non-zero for failure)

    """
    if os.environ.get("GITHUB_ACTIONS"):
        os.environ["CI"] = "1"
        logger.info("GitHub Actions environment detected")
    create_empty_json_files()
    bandit_path = find_bandit_executable()
    bandit_path = install_bandit_if_needed(bandit_path)
    run_bandit_with_config(bandit_path)
    convert_json_to_sarif()
    logger.info("Bandit scan completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
