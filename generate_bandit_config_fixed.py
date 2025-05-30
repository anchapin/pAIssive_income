#!/usr/bin/env python3
from __future__ import annotations

import logging
import sys

# Configure logging
logger = logging.getLogger(__name__)

"""
Generate Bandit Configuration Files for GitHub Actions.

This script generates Bandit configuration files for all platforms and run IDs.
It is used by the GitHub Actions workflow to create the necessary configuration
files for Bandit security scanning.

Usage:
    python generate_bandit_config.py [run_id]
"""

try:
    from pathlib import Path

# Configure logging


# Configure logging


# Configure logging


# Configure logging



# Configure logging
except ImportError:

    print("Error: pathlib module not found. Please install it.")
    sys.exit(1)


# Define the base configuration template
CONFIG_TEMPLATE = """# Bandit Configuration for {platform} (Run ID: {run_id})
# This configuration is used by GitHub Advanced Security for Bandit scanning on {platform}

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

# Set the output file for GitHub Advanced Security
output_file: security-reports/bandit-results.sarif

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM

# Per-test configurations
any_other_function_with_shell_equals_true:
  no_shell: [os.execl, os.execle, os.execlp, os.execlpe, os.execv, os.execve, os.execvp,
    os.execvpe, os.spawnl, os.spawnle, os.spawnlp, os.spawnlpe, os.spawnv, os.spawnve,
    os.spawnvp, os.spawnvpe, os.startfile]
  shell: [os.system, os.popen, os.popen2, os.popen3, os.popen4, popen2.popen2, popen2.popen3,
    popen2.popen4, popen2.Popen3, popen2.Popen4, commands.getoutput, commands.getstatusoutput]
  subprocess: [subprocess.Popen, subprocess.call, subprocess.check_call, subprocess.check_output,
    subprocess.run]
"""


def create_directory(directory_path: Path) -> bool:
    """
    Create a directory if it doesn't exist.

    Args:
        directory_path: Path to the directory to create

    Returns:
        True if the directory was created or already exists, False otherwise

    """
    try:
        # Try to create the directory with parents
        directory_path.mkdir(parents=True, exist_ok=True)
        logger.info("Directory created or already exists: %s", directory_path)
    except OSError:
        logger.exception("Failed to create directory %s", directory_path)
        return False
    else:
        return True


def write_config_file(config_file: Path, content: str) -> bool:
    """
    Write content to a configuration file.

    Args:
        config_file: Path to the configuration file
        content: Content to write to the file

    Returns:
        True if the file was written successfully, False otherwise

    """
    try:
        # Try to write the file
        with config_file.open("w") as f:
            f.write(content)
        logger.info("Generated %s", config_file)
    except OSError:
        logger.exception("Failed to write config file %s", config_file)
        return False
    else:
        return True


def setup_directories() -> tuple[Path, Path, bool]:
    """
    Set up the necessary directories for Bandit configuration files.

    Returns:
        tuple: (bandit_dir, security_reports_dir, success)

    """
    # Create the .github/bandit directory if it doesn't exist
    bandit_dir = Path(".github/bandit")
    if not create_directory(bandit_dir):
        # Try alternative path with backslashes for Windows
        bandit_dir = Path(".github\\bandit")
        if not create_directory(bandit_dir):
            logger.error("Failed to create bandit directory")
            return bandit_dir, Path(), False

    # Create the security-reports directory if it doesn't exist
    security_reports_dir = Path("security-reports")
    if not create_directory(security_reports_dir):
        # Try alternative path with backslashes for Windows
        security_reports_dir = Path("security-reports")
        if not create_directory(security_reports_dir):
            logger.error("Failed to create security-reports directory")
            return bandit_dir, security_reports_dir, False

    return bandit_dir, security_reports_dir, True


def generate_config_files(bandit_dir: Path, run_id: str) -> bool:
    """
    Generate Bandit configuration files for all platforms.

    Args:
        bandit_dir: Directory to store Bandit configuration files
        run_id: Run ID for the configuration files

    Returns:
        bool: True if all files were generated successfully, False otherwise

    """
    success = True
    platforms = ["Windows", "Linux", "macOS"]

    # Generate configuration files for each platform with specific run ID
    for platform in platforms:
        config_content = CONFIG_TEMPLATE.format(platform=platform, run_id=run_id)
        config_file = bandit_dir / f"bandit-config-{platform.lower()}-{run_id}.yaml"

        if not write_config_file(config_file, config_content):
            success = False

    # Also create generic platform configuration files
    for platform in platforms:
        config_content = CONFIG_TEMPLATE.format(platform=platform, run_id="generic")
        config_file = bandit_dir / f"bandit-config-{platform.lower()}.yaml"

        if not write_config_file(config_file, config_content):
            success = False

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
        run_id = "default"
        if len(sys.argv) > 1:
            run_id = sys.argv[1]

        logger.info("Generating Bandit configuration files for run ID: %s", run_id)

        # Set up directories
        bandit_dir, _, setup_success = setup_directories()
        if not setup_success:
            result = 1
        # Generate configuration files
        elif generate_config_files(bandit_dir, run_id):
            logger.info("Bandit configuration files generated successfully")
            result = 0
        else:
            logger.error("Some bandit configuration files could not be generated")
            result = 1
    except Exception:
        logger.exception("Unexpected error during Bandit configuration generation")
        return 1
    else:
        return result


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    sys.exit(main())
