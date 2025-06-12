#!/usr/bin/env python3
"""
Generate Bandit configuration files for GitHub Actions workflows.

This script generates Bandit configuration files for different platforms and run IDs.
It ensures that the necessary directories and files exist and are properly configured.

Usage:
    python generate_bandit_config.py [run_id]
"""

from __future__ import annotations

import logging
import os
import sys

# Path is used throughout the script, so we keep this import
from pathlib import Path

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
BANDIT_DIR = ".github/bandit"
SECURITY_REPORTS_DIR = "security-reports"
PLATFORMS = ["windows", "linux", "macos"]

# Bandit configuration template
BANDIT_CONFIG_TEMPLATE = """# Bandit Configuration Template
# This configuration is used by GitHub Advanced Security for Bandit scanning

# Exclude directories from security scans
exclude_dirs:
  - tests
  - venv
  - .venv
  - env
  - .env
  - __pycache__
  - custom_stubs
  - node_modules
  - build
  - dist
  - docs
  - docs_source
  - junit
  - bin
  - dev_tools
  - scripts
  - tool_templates

# Skip specific test IDs
skips:
  # B101: Use of assert detected
  - B101
  # B311: Standard pseudo-random generators are not suitable for security/cryptographic purposes
  - B311

# Set the output format for GitHub Advanced Security
output_format: sarif

# Output file for GitHub Advanced Security
output_file: security-reports/bandit-results.sarif

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM

# Simplified shell configuration
shell_injection:
  no_shell: []
  shell: []
"""


# Define the empty SARIF content
EMPTY_SARIF = """{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Bandit",
          "informationUri": "https://github.com/PyCQA/bandit",
          "version": "1.7.5",
          "rules": []
        }
      },
      "results": []
    }
  ]
}"""

# Compact version for error recovery
COMPACT_SARIF = """{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Bandit",
          "informationUri": "https://github.com/PyCQA/bandit",
          "version": "1.7.5",
          "rules": []
        }
      },
      "results": []
    }
  ]
}"""


def create_directory(path: Path) -> None:
    """
    Create a directory if it doesn't exist.

    Args:
        path: The directory path to create

    """
    path.mkdir(parents=True, exist_ok=True)
    logger.info("Created directory: %s", path)


def write_sarif_file(path: Path, content: str) -> None:
    """
    Write SARIF content to a file.

    Args:
        path: The file path to write to
        content: The SARIF content to write

    """
    # If the file has a .json extension, use json.dump for proper formatting
    if path.suffix == ".json":
        import json

        try:
            # Parse the content as JSON
            json_content = json.loads(content)
            # Write with proper indentation
            with path.open("w") as f:
                json.dump(json_content, f, indent=2)
        except json.JSONDecodeError:
            # Fallback to direct write if parsing fails
            with path.open("w") as f:
                f.write(content)
    else:
        # For non-JSON files, write directly
        with path.open("w") as f:
            f.write(content)
    logger.info("Generated SARIF file: %s", path)


def get_run_ids(current_run_id: str) -> list[str]:
    """
    Get a list of run IDs to process.

    Args:
        current_run_id: The current run ID

    Returns:
        List of run IDs to process

    """
    return [current_run_id]


def setup_directories() -> tuple[Path, Path, bool]:
    """
    Set up directories for Bandit configuration files.

    Returns:
        Tuple[Path, Path, bool]: Bandit directory path, security reports directory path,
                                and success flag

    """
    try:
        # Handle Windows path separators
        bandit_dir_str = BANDIT_DIR.replace("/", os.sep)
        security_reports_dir_str = SECURITY_REPORTS_DIR.replace("/", os.sep)

        # Create Bandit directory
        bandit_dir = Path(bandit_dir_str)
        bandit_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created Bandit directory: %s", bandit_dir)

        # Create security reports directory
        security_reports_dir = Path(security_reports_dir_str)
        security_reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Created security reports directory: %s", security_reports_dir)
    except Exception:
        logger.exception("Failed to set up directories")
        return Path(BANDIT_DIR), Path(SECURITY_REPORTS_DIR), False
    else:
        return bandit_dir, security_reports_dir, True


def write_config_file(config_path: Path, content: str) -> bool:
    """
    Write content to a configuration file.

    Args:
        config_path: Path to the configuration file
        content: Content to write to the file

    Returns:
        bool: True if the file was written successfully, False otherwise

    """
    try:
        with config_path.open("w") as f:
            f.write(content)
        logger.info("Generated configuration file: %s", config_path)
    except Exception:
        logger.exception("Failed to write configuration file: %s", config_path)
        return False
    else:
        return True


def generate_config_files(bandit_dir: Path, run_id: str) -> bool:
    """
    Generate Bandit configuration files for all platforms with the given run ID.

    Args:
        bandit_dir: Directory to store Bandit configuration files
        run_id: Run ID for the configuration files

    Returns:
        bool: True if all files were generated successfully, False otherwise

    """
    success = True

    try:
        for platform in PLATFORMS:
            # Generate platform-specific configuration file
            config_path = bandit_dir / f"bandit-config-{platform}.yaml"
            if not write_config_file(config_path, BANDIT_CONFIG_TEMPLATE):
                success = False
                continue

            # Generate platform-specific configuration file with run ID
            config_path_with_run_id = (
                bandit_dir / f"bandit-config-{platform}-{run_id}.yaml"
            )
            if not write_config_file(config_path_with_run_id, BANDIT_CONFIG_TEMPLATE):
                success = False
                continue
    except Exception:
        logger.exception("Failed to generate configuration files")
        return False
    else:
        return success


def main() -> int:
    """
    Generate Bandit configuration files for all platforms and run IDs.

    Returns:
        int: 0 for success, 1 for failure

    """
    try:
        # Log environment information for debugging
        logger.info("Current working directory: %s", Path.cwd())
        logger.info("Python version: %s", sys.version)
        logger.info("Platform: %s", sys.platform)

        # Get the run ID from the command line arguments
        run_id = "test_run_id"  # Default to a generic test run ID
        if len(sys.argv) > 1:
            run_id = sys.argv[1]
            # Handle special case for test_run_id
            if run_id == "test_run_id":
                logger.info("Using test run ID")
            # Sanitize run_id to avoid potential issues
            run_id = "".join(c for c in run_id if c.isalnum() or c in "_-")

        logger.info("Generating Bandit configuration files for run ID: %s", run_id)

        # Set up directories
        bandit_dir, _, setup_success = setup_directories()
        if not setup_success:
            logger.error("Failed to set up directories")
            return 1

        # Generate configuration files
        if not generate_config_files(bandit_dir, run_id):
            logger.error("Some bandit configuration files could not be generated")
            return 1

        logger.info("Bandit configuration files generated successfully")
    except Exception:
        logger.exception("Unexpected error during Bandit configuration generation")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
