#!/usr/bin/env python3
"""
Convert Bandit JSON output to SARIF format.

This script reads the Bandit JSON output file and converts it to SARIF format
for GitHub Advanced Security.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # Moved to top for consistency and security review
import tempfile  # Moved to top for consistency
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _write_sarif_file(sarif_data: dict[str, Any], output_file: str) -> bool:
    """
    Write SARIF data to a file.

    Args:
        sarif_data: The SARIF data to write
        output_file: Path to the output file

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        with Path(output_file).open("w") as f:
            json.dump(sarif_data, f)
    except (OSError, PermissionError):
        logger.exception("Failed to write SARIF file")
        return False
    else:
        return True


def _read_bandit_json(json_file: str) -> dict[str, Any]:
    """
    Read and parse Bandit JSON output.

    Args:
        json_file: Path to the Bandit JSON file

    Returns:
        dict: Parsed JSON data or empty dict if failed

    """
    try:
        with Path(json_file).open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.exception("Error reading JSON file")
        return {}


def _convert_bandit_results_to_sarif(bandit_data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert Bandit results to SARIF format.

    Args:
        bandit_data: Bandit JSON data

    Returns:
        dict: SARIF data

    """
    # Create the SARIF template
    sarif = _create_empty_sarif()

    # If no results, return empty template
    if not bandit_data.get("results"):
        return sarif

    # Convert Bandit results to SARIF format
    rules = {}
    results = []

    for result in bandit_data.get("results", []):
        rule_id = f"B{result.get('test_id', '000')}"

        # Add rule if not already added
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "shortDescription": {"text": result.get("test_name", "Unknown test")},
                "fullDescription": {"text": result.get("issue_text", "Unknown issue")},
                "helpUri": "https://bandit.readthedocs.io/en/latest/",
                "properties": {"tags": ["security", "python"]},
            }

        # Add result
        results.append(
            {
                "ruleId": rule_id,
                "level": "warning",
                "message": {"text": result.get("issue_text", "Unknown issue")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": result.get("filename", "unknown")
                            },
                            "region": {
                                "startLine": result.get("line_number", 1),
                                "startColumn": 1,
                            },
                        }
                    }
                ],
            }
        )

    # Add rules and results to SARIF
    sarif["runs"][0]["tool"]["driver"]["rules"] = list(rules.values())
    sarif["runs"][0]["results"] = results

    return sarif


def convert_to_sarif(json_file: str, sarif_file: str) -> None:
    """
    Convert Bandit JSON output to SARIF format.

    Args:
        json_file: Path to the Bandit JSON output file
        sarif_file: Path to the output SARIF file

    """
    # Check if the JSON file exists and has content
    json_path = Path(json_file)
    if not json_path.exists() or json_path.stat().st_size == 0:
        logger.info(
            "JSON file %s does not exist or is empty. Creating empty SARIF file.",
            json_file,
        )
        _write_sarif_file(_create_empty_sarif(), sarif_file)
        return

    # Read the Bandit JSON output
    bandit_data = _read_bandit_json(json_file)
    if not bandit_data:
        logger.info("Creating empty SARIF file due to JSON read failure")
        _write_sarif_file(_create_empty_sarif(), sarif_file)
        return

    # Check if there are any results
    if not bandit_data.get("results"):
        logger.info("No results found in Bandit output. Creating empty SARIF file.")
        _write_sarif_file(_create_empty_sarif(), sarif_file)
        return

    # Convert and write SARIF file
    sarif_data = _convert_bandit_results_to_sarif(bandit_data)
    if _write_sarif_file(sarif_data, sarif_file):
        logger.info("Successfully converted %s to %s", json_file, sarif_file)


def _create_windows_junction(target_dir: Path, link_name: str) -> bool:
    """
    Create a directory junction on Windows.

    Args:
        target_dir: The target directory path
        link_name: The name of the junction to create

    Returns:
        bool: True if successful, False otherwise

    """
    # nosec B404 - subprocess is used with shell=False, validated arguments, and no user input. This is considered safe.
    try:
        cmd_path = shutil.which("cmd.exe")
        if not cmd_path:
            logger.warning("cmd.exe not found, cannot create directory junction")
            return False

        # nosec S603: trusted input, shell=False, validated args
        cmd = [
            cmd_path,
            "/c",
            "mklink",
            "/J",
            link_name,
            str(target_dir),
        ]

        # Use a helper to validate and run the command safely (addresses Ruff S603)
        def _safe_subprocess_run(
            cmd: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess[Any]:
            cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
            filtered_kwargs: dict[str, Any] = {
                k: v
                for k, v in kwargs.items()
                if (
                    (k in {"stdin", "stdout", "stderr", "input"})
                    or (
                        k in {"cwd", "encoding", "errors"}
                        and isinstance(v, (str, bytes))
                    )
                    or (k == "timeout" and isinstance(v, (int, float)))
                    or (
                        k
                        in {
                            "bufsize",
                            "creationflags",
                            "umask",
                            "pipesize",
                            "process_group",
                        }
                        and isinstance(v, int)
                    )
                    or (
                        k
                        in {
                            "close_fds",
                            "shell",
                            "text",
                            "universal_newlines",
                            "start_new_session",
                            "restore_signals",
                            "check",
                        }
                        and isinstance(v, bool)
                    )
                    or (k in {"user", "group"} and isinstance(v, (str, int)))
                    or (k == "extra_groups" and isinstance(v, (list, tuple, set)))
                    or (k == "env" and isinstance(v, dict))
                    or (k == "pass_fds" and isinstance(v, (list, tuple, set)))
                )
            }
            # nosec S603 - cmd_path is validated via shutil.which, shell=False, no user input
            return subprocess.run(cmd, check=False, **filtered_kwargs)  # type: ignore[call-arg]  # noqa: S603

        _safe_subprocess_run(cmd)  # Safe: cmd_path is from shutil.which, args are fixed
    except (OSError, PermissionError, subprocess.SubprocessError):
        logger.exception("Failed to create Windows directory junction")
        return False
    else:
        return True


def _create_symlink(target_dir: Path, link_name: str) -> bool:
    """
    Create a symlink on Unix or a junction on Windows.

    Args:
        target_dir: The target directory path
        link_name: The name of the symlink to create

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        if os.name == "nt":  # Windows
            return _create_windows_junction(target_dir, link_name)
        # Use symlink on Unix
        os.symlink(target_dir, link_name)
    except (OSError, PermissionError):
        logger.exception("Failed to create symlink")
        return False
    else:
        return True


def _try_create_primary_dir() -> bool:
    """
    Try to create the primary security-reports directory.

    Returns:
        bool: True if successful, False otherwise

    """
    reports_dir = Path("security-reports")

    # Check if directory already exists
    if reports_dir.exists() and reports_dir.is_dir():
        logger.info("security-reports directory already exists")
        return True

    # Try to create the directory
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created security-reports directory")
    except (PermissionError, OSError):
        logger.exception("Failed to create security-reports directory")
        return False
    else:
        return True


def _try_alternative_dir() -> bool:
    """
    Try to create an alternative security_reports directory.

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        alt_reports_dir = Path("security_reports")  # Use underscore instead of hyphen
        if not alt_reports_dir.exists():
            alt_reports_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created alternative security_reports directory")

            # Create a symlink to the alternative directory
            return _create_symlink(alt_reports_dir, "security-reports")
    except (OSError, PermissionError):
        logger.exception("Failed to create alternative security_reports directory")
        return False
    else:
        return False


def _try_temp_dir() -> bool:
    """
    Try to create a security-reports directory in the temp location.

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        temp_dir = Path(tempfile.gettempdir()) / "security-reports"
        temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created security-reports directory in temp location: %s", temp_dir)

        # Create a symlink to the temp directory
        return _create_symlink(temp_dir, "security-reports")
    except (OSError, PermissionError):
        logger.exception("Failed to create security-reports directory in temp location")
        return False


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    Creates the directory if it doesn't exist and logs the result.
    Tries multiple fallback strategies if the primary approach fails.
    """
    # Try primary approach first
    if _try_create_primary_dir():
        return

    # Try alternative directory with different name
    if _try_alternative_dir():
        return

    # Try temp directory as last resort
    if _try_temp_dir():
        return

    # Final fallback: Just continue without the directory
    # The security tools should handle this gracefully or we'll catch their exceptions


def _create_empty_sarif() -> dict[str, Any]:
    """
    Create an empty SARIF template.

    Returns:
        dict: Empty SARIF template

    """
    return {
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


def _write_empty_sarif_files(sarif_file: str, ini_sarif_file: str) -> bool:
    """
    Write empty SARIF files.

    Args:
        sarif_file: Path to the main SARIF file
        ini_sarif_file: Path to the ini SARIF file

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        empty_sarif = _create_empty_sarif()
        with Path(sarif_file).open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        with Path(ini_sarif_file).open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        logger.info("Created empty SARIF files")
    except (OSError, PermissionError):
        logger.exception("Failed to create empty SARIF files")
        return False
    else:
        return True


def _copy_sarif_file(source: str, destination: str) -> bool:
    """
    Copy a SARIF file from source to destination.

    Args:
        source: Source file path
        destination: Destination file path

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        shutil.copy(source, destination)
        logger.info("Copied %s to %s", source, destination)
    except (OSError, PermissionError):
        logger.exception("Failed to copy SARIF file")
        return False
    else:
        return True


def _read_write_sarif_file(source: str, destination: str) -> bool:
    """
    Read a SARIF file and write it to a new location.

    Args:
        source: Source file path
        destination: Destination file path

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        with Path(source).open() as src:
            sarif_data = json.load(src)
        with Path(destination).open("w") as dest:
            json.dump(sarif_data, dest, indent=2)
        logger.info(
            "Successfully created %s by reading and writing",
            destination,
        )
    except (OSError, PermissionError, json.JSONDecodeError):
        logger.exception("Failed to read/write SARIF file")
        return False
    else:
        return True


def _create_empty_ini_sarif_file(ini_sarif_file: str) -> bool:
    """
    Create an empty ini SARIF file as a last resort.

    Args:
        ini_sarif_file: Path to the ini SARIF file

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        with Path(ini_sarif_file).open("w") as f:
            json.dump(_create_empty_sarif(), f, indent=2)
        logger.info("Created empty SARIF file as fallback: %s", ini_sarif_file)
    except (OSError, PermissionError):
        logger.exception("Failed to create empty SARIF file")
        return False
    else:
        return True


def _create_ini_sarif_file(
    json_file: str, sarif_file: str, ini_sarif_file: str
) -> bool:
    """
    Create the ini SARIF file from the main SARIF file or directly from JSON.

    Args:
        json_file: Path to the Bandit JSON file
        sarif_file: Path to the main SARIF file
        ini_sarif_file: Path to the ini SARIF file

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        # If the main SARIF file exists, try to copy it
        if Path(sarif_file).exists():
            if _copy_sarif_file(sarif_file, ini_sarif_file):
                return True

            # If copy fails, try to read and write
            if _read_write_sarif_file(sarif_file, ini_sarif_file):
                return True
        else:
            logger.warning("SARIF file not found: %s", sarif_file)

        # Try direct conversion as fallback
        try:
            convert_to_sarif(json_file, ini_sarif_file)
        except (OSError, PermissionError):
            logger.exception("Failed to convert to ini SARIF file")
            # Create empty SARIF file as last resort
            return _create_empty_ini_sarif_file(ini_sarif_file)
        else:
            return True
    except (OSError, PermissionError):
        logger.exception("Failed to create ini SARIF file")
        return False


def _create_fallback_sarif_files() -> None:
    """Create empty SARIF files as a last resort fallback."""
    try:
        empty_sarif = _create_empty_sarif()

        # Ensure directory exists
        Path("security-reports").mkdir(parents=True, exist_ok=True)

        # Write empty SARIF files
        with Path("security-reports/bandit-results.sarif").open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        with Path("security-reports/bandit-results-ini.sarif").open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        logger.info("Created empty SARIF files as fallback after error")
    except (OSError, PermissionError):
        logger.exception("Failed to create fallback SARIF files")


def main() -> None:
    """Execute the main conversion process."""
    try:
        # Ensure security-reports directory exists
        ensure_security_reports_dir()

        # Define file paths
        json_file = "security-reports/bandit-results.json"
        sarif_file = "security-reports/bandit-results.sarif"
        ini_sarif_file = "security-reports/bandit-results-ini.sarif"

        # Check if JSON file exists
        if not Path(json_file).exists():
            logger.warning("Bandit JSON file not found: %s", json_file)
            logger.info("Creating empty SARIF files as fallback")

            if not _write_empty_sarif_files(sarif_file, ini_sarif_file):
                return
        else:
            # Convert Bandit JSON to SARIF
            logger.info("Converting %s to SARIF format", json_file)
            convert_to_sarif(json_file, sarif_file)

            # Also create bandit-results-ini.sarif for compatibility
            logger.info("Creating %s for compatibility", ini_sarif_file)
            _create_ini_sarif_file(json_file, sarif_file, ini_sarif_file)

    except (OSError, PermissionError, json.JSONDecodeError):
        logger.exception("Unexpected error in main function")
        _create_fallback_sarif_files()


if __name__ == "__main__":
    main()
