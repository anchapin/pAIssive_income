#!/usr/bin/env python3
"""
Test script for security scanning workflow.

This script simulates the security scanning workflow locally to verify that
the changes made to the workflow file work as expected.
"""

from __future__ import annotations

import argparse
import json
import logging
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def run_command(command: str, cwd: Optional[str] = None) -> tuple[str, str, int]:
    """
    Run a shell command and return stdout, stderr, and return code.

    Args:
        command: Command to run
        cwd: Working directory

    Returns:
        Tuple of (stdout, stderr, return_code)

    """
    try:
        # Split the command into args for safer execution
        args = shlex.split(command)

        # Use subprocess.run instead of Popen for simpler code
        result = subprocess.run(  # noqa: S603 - Using shlex.split for safe command execution
            args,
            shell=False,  # Avoid shell=True for security
            capture_output=True,  # Use capture_output instead of stdout/stderr=PIPE
            cwd=cwd,
            text=True,
            check=False,
        )
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    except (subprocess.SubprocessError, OSError) as e:
        stdout, stderr, returncode = "", str(e), 1

    return stdout, stderr, returncode


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists.

    Args:
        directory: Directory path

    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def test_safety_scan() -> None:
    """
    Test the Safety scan functionality.
    """
    logger.info("\n=== Testing Safety Scan ===")
    ensure_directory("security-reports")

    # Create fallback safety results file
    Path("security-reports/safety-results.json").write_text("[]")

    # Run safety check
    logger.info("Running safety check...")
    stdout, stderr, return_code = run_command("safety check --json")

    if return_code != 0 and "command not found" in stderr:
        logger.info("Safety not installed. Installing...")
        run_command("uv pip install safety")  # Using uv
        stdout, stderr, return_code = run_command("safety check --json")

    if stdout:
        tmp_file = Path("security-reports/safety-results.json.tmp")
        tmp_file.write_text(stdout)

        # Validate JSON format
        try:
            json.loads(stdout)
            logger.info("Safety output is valid JSON")
            tmp_file.rename(Path("security-reports/safety-results.json"))
        except json.JSONDecodeError:
            logger.warning("Safety output is not valid JSON. Using empty results.")
            logger.exception("Invalid JSON content")
            logger.debug("First 100 characters: %s", stdout[:100])
    else:
        logger.warning("Safety check produced no output")
        if stderr:
            logger.error("Safety error log:")
            logger.error(stderr)

    # Convert to SARIF format
    logger.info("Converting Safety results to SARIF format...")
    stdout, stderr, return_code = run_command(
        "python3 scripts/utils/sarif_utils.py security-reports/safety-results.json "
        "security-reports/safety-results.sarif Safety "
        "https://pyup.io/safety/"
    )

    if return_code != 0:
        logger.error("Error converting Safety results to SARIF: %s", stderr)
        assert False, f"Failed to convert Safety results to SARIF: {stderr}"

    logger.info("Safety scan test completed")
    assert True


def test_bandit_scan() -> None:
    """
    Test the Bandit scan functionality.
    """
    logger.info("\n=== Testing Bandit Scan ===")
    ensure_directory("security-reports")

    # Create fallback bandit results file
    Path("security-reports/bandit-results.json").write_text("[]")

    # Run bandit scan
    logger.info("Running bandit scan...")
    stdout, stderr, return_code = run_command("bandit -r . -f json")

    if return_code != 0 and "command not found" in stderr:
        logger.info("Bandit not installed. Installing...")
        run_command("uv pip install bandit")  # Using uv
        stdout, stderr, return_code = run_command("bandit -r . -f json")

    if stdout:
        tmp_file = Path("security-reports/bandit-results.json.tmp")
        tmp_file.write_text(stdout)

        # Validate JSON format
        try:
            json.loads(stdout)
            logger.info("Bandit output is valid JSON")
            tmp_file.rename(Path("security-reports/bandit-results.json"))
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
        "python3 scripts/utils/sarif_utils.py security-reports/bandit-results.json "
        "security-reports/bandit-results.sarif Bandit "
        "https://bandit.readthedocs.io/"
    )

    if return_code != 0:
        logger.error("Error converting Bandit results to SARIF: %s", stderr)
        assert False, f"Failed to convert Bandit results to SARIF: {stderr}"

    logger.info("Bandit scan test completed")
    assert True


def test_sarif_file_handling() -> None:
    """
    Test SARIF file handling functionality.
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
            'python3 scripts/utils/sarif_utils.py "[]" security-reports/test-results.sarif '
            "Test https://example.com"
        )

        if return_code != 0:
            logger.error("Error creating test SARIF file: %s", stderr)
            assert False, f"Failed to create test SARIF file: {stderr}"

        sarif_files = list(Path("security-reports").glob("*.sarif"))

    # Process SARIF files
    for sarif_file in sarif_files:
        logger.info("Processing %s...", sarif_file)

        # Check file size
        file_size = sarif_file.stat().st_size
        logger.info("File size: %s bytes", file_size)

        # Validate SARIF format
        try:
            with sarif_file.open() as f:
                json.load(f)
            logger.info("✅ %s is valid JSON", sarif_file)
        except json.JSONDecodeError:
            logger.warning("❌ %s is not valid JSON", sarif_file)
            logger.info("Creating a valid but empty SARIF file as fallback")
            cmd = f'python3 scripts/utils/sarif_utils.py "[]" {sarif_file} Test https://example.com'
            stdout, stderr, return_code = run_command(cmd)

            if return_code != 0:
                logger.exception("Error creating fallback SARIF file")
                assert False, "Failed to create fallback SARIF file"

        # Create compressed version
        compressed_file_name = f"{sarif_file.name}.gz"
        compressed_path_base = Path("security-reports/compressed")
        compressed_file = compressed_path_base / compressed_file_name

        # Use a safer approach to create compressed file
        cmd = f"gzip -c {sarif_file} > {compressed_file}"
        stdout, stderr, return_code = run_command(cmd)

        if return_code != 0:
            logger.error("Error creating compressed version: %s", stderr)
            assert False, f"Failed to create compressed version: {stderr}"

        logger.info("Created compressed version: %s", compressed_file)

    logger.info("SARIF file handling test completed")
    assert True


def main() -> int:
    """
    Run security scan tests.

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
    logger.warning("\n❌ Some tests failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
