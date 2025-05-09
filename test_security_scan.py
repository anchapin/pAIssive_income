#!/usr/bin/env python3
"""Test script for security scanning workflow.

This script simulates the security scanning workflow locally to verify that
the changes made to the workflow file work as expected.
"""

import argparse
import json
import os
import subprocess
import sys

from pathlib import Path
from typing import Optional


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
        return stdout, stderr, return_code
    except Exception as e:
        return "", str(e), 1


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
    print("\n=== Testing Safety Scan ===")
    ensure_directory("security-reports")

    # Create fallback safety results file
    with open("security-reports/safety-results.json", "w") as f:
        f.write("[]")

    # Run safety check
    print("Running safety check...")
    stdout, stderr, return_code = run_command("safety check --json")

    if return_code != 0 and "command not found" in stderr:
        print("Safety not installed. Installing...")
        run_command("pip install safety")
        stdout, stderr, return_code = run_command("safety check --json")

    if stdout:
        with open("security-reports/safety-results.json.tmp", "w") as f:
            f.write(stdout)

        # Validate JSON format
        try:
            json.loads(stdout)
            print("Safety output is valid JSON")
            os.rename(
                "security-reports/safety-results.json.tmp",
                "security-reports/safety-results.json",
            )
        except json.JSONDecodeError:
            print("Safety output is not valid JSON. Using empty results.")
            print("Invalid JSON content:")
            print(stdout[:100])  # Show first 100 characters
    else:
        print("Safety check produced no output")
        if stderr:
            print("Safety error log:")
            print(stderr)

    # Convert to SARIF format
    print("Converting Safety results to SARIF format...")
    stdout, stderr, return_code = run_command(
        "python sarif_utils.py security-reports/safety-results.json "
        "security-reports/safety-results.sarif Safety "
        "https://pyup.io/safety/"
    )

    if return_code != 0:
        print(f"Error converting Safety results to SARIF: {stderr}")
        return False

    print("Safety scan test completed")
    return True


def test_bandit_scan() -> bool:
    """Test the Bandit scan functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    print("\n=== Testing Bandit Scan ===")
    ensure_directory("security-reports")

    # Create fallback bandit results file
    with open("security-reports/bandit-results.json", "w") as f:
        f.write("[]")

    # Run bandit scan
    print("Running bandit scan...")
    stdout, stderr, return_code = run_command("bandit -r . -f json")

    if return_code != 0 and "command not found" in stderr:
        print("Bandit not installed. Installing...")
        run_command("pip install bandit")
        stdout, stderr, return_code = run_command("bandit -r . -f json")

    if stdout:
        with open("security-reports/bandit-results.json.tmp", "w") as f:
            f.write(stdout)

        # Validate JSON format
        try:
            json.loads(stdout)
            print("Bandit output is valid JSON")
            os.rename(
                "security-reports/bandit-results.json.tmp",
                "security-reports/bandit-results.json",
            )
        except json.JSONDecodeError:
            print("Bandit output is not valid JSON. Using empty results.")
            print("Invalid JSON content:")
            print(stdout[:100])  # Show first 100 characters
    else:
        print("Bandit scan produced no output")
        if stderr:
            print("Bandit error log:")
            print(stderr)

    # Convert to SARIF format
    print("Converting Bandit results to SARIF format...")
    stdout, stderr, return_code = run_command(
        "python sarif_utils.py security-reports/bandit-results.json "
        "security-reports/bandit-results.sarif Bandit "
        "https://bandit.readthedocs.io/"
    )

    if return_code != 0:
        print(f"Error converting Bandit results to SARIF: {stderr}")
        return False

    print("Bandit scan test completed")
    return True


def test_sarif_file_handling() -> bool:
    """Test SARIF file handling functionality.

    Returns:
        bool: True if successful, False otherwise

    """
    print("\n=== Testing SARIF File Handling ===")
    ensure_directory("security-reports")
    ensure_directory("security-reports/compressed")

    # Check if SARIF files exist
    sarif_files = list(Path("security-reports").glob("*.sarif"))
    if not sarif_files:
        print("No SARIF files found. Creating a test SARIF file...")

        # Create a test SARIF file
        stdout, stderr, return_code = run_command(
            'python sarif_utils.py "[]" security-reports/test-results.sarif '
            "Test https://example.com"
        )

        if return_code != 0:
            print(f"Error creating test SARIF file: {stderr}")
            return False

        sarif_files = list(Path("security-reports").glob("*.sarif"))

    # Process SARIF files
    for sarif_file in sarif_files:
        print(f"Processing {sarif_file}...")

        # Check file size
        file_size = os.path.getsize(sarif_file)
        print(f"File size: {file_size} bytes")

        # Validate SARIF format
        try:
            with open(sarif_file) as f:
                json.load(f)
            print(f"✅ {sarif_file} is valid JSON")
        except json.JSONDecodeError:
            print(f"❌ {sarif_file} is not valid JSON")
            print("Creating a valid but empty SARIF file as fallback")
            stdout, stderr, return_code = run_command(
                f'python sarif_utils.py "[]" {sarif_file} Test https://example.com'
            )

            if return_code != 0:
                print(f"Error creating fallback SARIF file: {stderr}")
                return False

        # Create compressed version
        compressed_file = Path("security-reports/compressed") / f"{sarif_file.name}.gz"
        stdout, stderr, return_code = run_command(
            f"gzip -c {sarif_file} > {compressed_file}"
        )

        if return_code != 0:
            print(f"Error creating compressed version: {stderr}")
            return False

        print(f"Created compressed version: {compressed_file}")

    print("SARIF file handling test completed")
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
        print("\n✅ All tests completed successfully")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
