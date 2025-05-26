#!/usr/bin/env python3


# Configure logging
logger = logging.getLogger(__name__)

"""
Fix GitHub Actions Bandit Configuration Issues.

This script fixes issues with the Bandit configuration in GitHub Actions workflows.
It ensures that the necessary directories and files exist and are properly configured.

Usage:
    python scripts/fix/fix_github_actions_bandit.py
"""

import logging
import shutil
import sys
from pathlib import Path



def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        bool: True if the directory exists or was created, False otherwise

    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.info("Directory exists or was created: %s", directory_path)
    except OSError:
        logger.exception("Failed to create directory %s", directory_path)
        return False
    else:
        return True


def copy_template_file(source_path: str, dest_path: str) -> bool:
    """
    Copy a template file to a destination path.

    Args:
        source_path: Path to the source file
        dest_path: Path to the destination file

    Returns:
        bool: True if the file was copied successfully, False otherwise

    """
    try:
        shutil.copy2(source_path, dest_path)
        logger.info("Copied template file from %s to %s", source_path, dest_path)
    except OSError:
        logger.exception(
            "Failed to copy template file from %s to %s", source_path, dest_path
        )
        return False
    else:
        return True


def create_empty_sarif_file(file_path: str) -> bool:
    """
    Create an empty SARIF file at the specified path.

    Args:
        file_path: Path to the SARIF file

    Returns:
        bool: True if the file was created successfully, False otherwise

    """
    try:
        empty_sarif_content = """{
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
        path = Path(file_path)
        with path.open("w") as f:
            f.write(empty_sarif_content)
        logger.info("Created empty SARIF file at %s", file_path)
    except OSError:
        logger.exception("Failed to create empty SARIF file at %s", file_path)
        return False
    else:
        return True


def setup_directories() -> bool:
    """
    Set up necessary directories for Bandit configuration.

    Returns:
        bool: True if successful, False otherwise

    """
    directories = [
        ".github/bandit",
        "security-reports",
    ]
    for directory in directories:
        if not ensure_directory_exists(directory):
            logger.error("Failed to create directory: %s", directory)
            return False
    return True


def setup_empty_sarif() -> bool:
    """
    Set up empty SARIF file if it doesn't exist.

    Returns:
        bool: True if successful, False otherwise

    """
    empty_sarif_path = "empty-sarif.json"
    empty_sarif_file = Path(empty_sarif_path)
    if not empty_sarif_file.exists() and not create_empty_sarif_file(empty_sarif_path):
        logger.error("Failed to create empty SARIF file")
        return False
    return True


def create_platform_configs(template_path: str) -> bool:
    """
    Create Bandit configuration files for all platforms.

    Args:
        template_path: Path to the template file

    Returns:
        bool: True if successful, False otherwise

    """
    template_file = Path(template_path)
    if not template_file.exists():
        logger.error("Template file not found: %s", template_path)
        return False

    platforms = ["windows", "linux", "macos"]
    for platform in platforms:
        dest_path = f".github/bandit/bandit-config-{platform}.yaml"
        if not copy_template_file(template_path, dest_path):
            logger.error("Failed to create configuration file for %s", platform)
            return False

        # Also create a test_run_id version
        test_run_id_path = f".github/bandit/bandit-config-{platform}-test_run_id.yaml"
        if not copy_template_file(template_path, test_run_id_path):
            logger.error(
                "Failed to create test_run_id configuration file for %s", platform
            )
            return False
    return True


def main() -> int:
    """
    Fix GitHub Actions Bandit configuration issues.

    Returns:
        int: 0 for success, 1 for failure

    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    exit_code = 1

    try:
        # Set up directories
        if setup_directories():
            # Set up empty SARIF file
            if setup_empty_sarif():
                # Create bandit configuration files for all platforms
                template_path = ".github/bandit/bandit-config-template.yaml"
                if create_platform_configs(template_path):
                    logger.info(
                        "Successfully fixed GitHub Actions Bandit configuration issues"
                    )
                    exit_code = 0
                else:
                    logger.error("Failed to create platform configurations")
            else:
                logger.error("Failed to set up empty SARIF file")
        else:
            logger.error("Failed to set up directories")
    except Exception:
        logger.exception("Unexpected error during Bandit configuration fix")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
