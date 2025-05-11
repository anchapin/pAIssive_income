#!/usr/bin/env python3
"""Test script for security scanning workflow.

This script simulates the security scanning workflow locally to verify that
the changes made to the workflow file work as expected.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def run_command(command: str, cwd: Optional[str] = None) -> tuple:
    """Run a shell command and return stdout, stderr, and return code.

    Args:
        command: Command to run
        cwd: Working directory

    Returns:
        Tuple of (stdout, stderr, return_code)

    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        return_code = process.returncode
    except Exception as e:
        return "", str(e), 1
    else:
        return stdout, stderr, return_code


def ensure_directory(directory: str) -> None:
    """Ensure a directory exists.

    Args:
        directory: Directory path

    """
    os.makedirs(directory, exist_ok=True)


def test_safety_scan() -> bool:
    """Test the Safety scan functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    logger.info("\n=== Testing Safety Scan ===")
    ensure_directory("security-reports")

    # Create fallback safety results file
    with open("security-reports/safety-results.json", "w") as f:
        f.write("[]")

    # Run safety check
    logger.info("Running safety check...")
    stdout, stderr, return_code = run_command("safety check --json")

    if return_code != 0 and "command not found" in stderr:
        logger.info("Safety not installed. Installing...")
        run_command("pip install safety")
        stdout, stderr, return_code = run_command("safety check --json")

    if stdout:
        with open("security-reports/safety-results.json.tmp", "w") as f:
            f.write(stdout)

        # Validate JSON format
        try:
            json.loads(stdout)
            logger.info("Safety output is valid JSON")
            os.rename(
                "security-reports/safety-results.json.tmp",
                "security-reports/safety-results.json",
            )
        except json.JSONDecodeError:
            logger.warning("Safety output is not valid JSON. Using empty results.")
            logger.exception("Invalid JSON content")
            logger.debug(f"First 100 characters: {stdout[:100]}")
    else:
        logger.warning("Safety check produced no output")
        if stderr:
            logger.error("Safety error log:")
            logger.error(stderr)

    # Convert to SARIF format
    logger.info("Converting Safety results to SARIF format...")
    stdout, stderr, return_code = run_command(
        "python sarif_utils.py security-reports/safety-results.json "
        "security-reports/safety-results.sarif Safety "
        "https://pyup.io/safety/"
    )

    if return_code != 0:
        logger.error(f"Error converting Safety results to SARIF: {stderr}")
        return False

    logger.info("Safety scan test completed")
    return True


def test_bandit_scan() -> bool:
    """Test the Bandit scan functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    logger.info("\n=== Testing Bandit Scan ===")
    ensure_directory("security-reports")

    # Create fallback bandit results file
    with open("security-reports/bandit-results.json", "w") as f:
        f.write("[]")

    # Run bandit scan
    logger.info("Running bandit scan...")
    stdout, stderr, return_code = run_command("bandit -r . -f json")

    if return_code != 0 and "command not found" in stderr:
        logger.info("Bandit not installed. Installing...")
        run_command("pip install bandit")
        stdout, stderr, return_code = run_command("bandit -r . -f json")

    if stdout:
        with open("security-reports/bandit-results.json.tmp", "w") as f:
            f.write(stdout)

        # Validate JSON format
        try:
            json.loads(stdout)
            logger.info("Bandit output is valid JSON")
            os.rename(
                "security-reports/bandit-results.json.tmp",
                "security-reports/bandit-results.json",
            )
        except json.JSONDecodeError:
            logger.warning("Bandit output is not valid JSON. Using empty results.")
            logger.warning("Invalid JSON content:")
            logger.warning(stdout[:100])  # Show first 100 characters
    else:
        logger.warning("Bandit scan produced no output")
        if stderr:
            logger.warning("Bandit error log:")
            logger.warning(stderr)

    # Convert to SARIF format
    logger.info("Converting Bandit results to SARIF format...")
    stdout, stderr, return_code = run_command(
        "python sarif_utils.py security-reports/bandit-results.json "
        "security-reports/bandit-results.sarif Bandit "
        "https://bandit.readthedocs.io/"
    )

    if return_code != 0:
        logger.error(f"Error converting Bandit results to SARIF: {stderr}")
        return False

    logger.info("Bandit scan test completed")
    return True


def test_sarif_file_handling() -> bool:
    """Test SARIF file handling functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    logger.info("\n=== Testing SARIF File Handling ===")
    ensure_directory("security-reports")
    ensure_directory("security-reports/compressed")

    # Check if SARIF files exist
    sarif_files = list(Path("security-reports").glob("*.sarif"))
    if not sarif_files:
        logger.info("No SARIF files found. Creating a test SARIF file...")

        # Create a test SARIF file
        stdout, stderr, return_code = run_command(
            'python sarif_utils.py "[]" security-reports/test-results.sarif '
            "Test https://example.com"
        )

        if return_code != 0:
            logger.error(f"Error creating test SARIF file: {stderr}")
            return False

        sarif_files = list(Path("security-reports").glob("*.sarif"))

    # Process SARIF files
    for sarif_file in sarif_files:
        logger.info(f"Processing {sarif_file}...")

        # Check file size
        file_size = os.path.getsize(sarif_file)
        logger.info(f"File size: {file_size} bytes")

        # Validate SARIF format
        try:
            with open(sarif_file) as f:
                json.load(f)
            logger.info(f"✅ {sarif_file} is valid JSON")
        except json.JSONDecodeError:
            logger.warning(f"❌ {sarif_file} is not valid JSON")
            logger.info("Creating a valid but empty SARIF file as fallback")
            stdout, stderr, return_code = run_command(
                f'python sarif_utils.py "[]" {sarif_file} Test https://example.com'
            )

            if return_code != 0:
                logger.exception("Error creating fallback SARIF file")
                return False

        # Create compressed version
        compressed_file = Path("security-reports/compressed") / f"{sarif_file.name}.gz"
        stdout, stderr, return_code = run_command(
            f"gzip -c {sarif_file} > {compressed_file}"
        )

        if return_code != 0:
            logger.error(f"Error creating compressed version: {stderr}")
            return False

        logger.info(f"Created compressed version: {compressed_file}")

    logger.info("SARIF file handling test completed")
    return True


def main() -> int:
    """Run security scan tests.

    Returns:
        int: Exit code

    """
    parser = argparse.ArgumentParser(description="Test security scanning workflow")
    parser.add_argument("--safety", action="store_true", help="Test Safety scan")
    parser.add_argument("--bandit", action="store_true", help="Test Bandit scan")
    parser.add_argument("--sarif", action="store_true", help="Test SARIF file handling")
    parser.add_argument("--all", action="store_true", help="Test all components")

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 1

    success = True

    # Run tests
    if args.all or args.safety:
        success = test_safety_scan() and success

    if args.all or args.bandit:
        success = test_bandit_scan() and success

    if args.all or args.sarif:
        success = test_sarif_file_handling() and success

    if success:
        logger.info("\n✅ All tests completed successfully")
        return 0
    else:
        logger.warning("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
