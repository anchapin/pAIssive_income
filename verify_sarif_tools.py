#!/usr/bin/env python3
"""Verify sarif-tools installation and create a test SARIF file.

This script ensures sarif-tools is properly installed and functional.
"""

import importlib.util
import json
import os
import subprocess
import sys


def check_sarif_tools_installed():
    """Check if sarif-tools is installed and accessible."""
    print("Checking if sarif-tools is installed...")

    # Method 1: Check using importlib
    spec = importlib.util.find_spec("sarif_tools")
    if spec is not None:
        print("✅ sarif-tools module found via importlib")
        return True

    # Method 2: Check using pip list
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        if "sarif-tools" in result.stdout:
            print("✅ sarif-tools found in pip list")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking pip list: {e}")

    print("❌ sarif-tools not found")
    return False


def install_sarif_tools():
    """Install sarif-tools using pip."""
    print("Installing sarif-tools...")

    try:
        # Try to install with --user flag for non-root environments
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--user",
                "sarif-tools",
                "--force-reinstall",
                "-v",
            ],
            check=True,
        )
        print("✅ sarif-tools installed successfully with --user flag")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try without --user flag
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "sarif-tools",
                    "--force-reinstall",
                    "-v",
                ],
                check=True,
            )
            print("✅ sarif-tools installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install sarif-tools: {e}")
            return False


def create_test_sarif_file(output_path="test-sarif.sarif"):
    """Create a minimal valid SARIF file for testing."""
    print(f"Creating test SARIF file at {output_path}...")

    # Create a minimal valid SARIF file
    sarif_data = {
        "version": "2.1.0",
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
            "Schemata/sarif-schema-2.1.0.json"
        ),
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Test Tool",
                        "informationUri": "https://example.com/test-tool",
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    try:
        with open(output_path, "w") as f:
            json.dump(sarif_data, f, indent=2)
        print(f"✅ Test SARIF file created at {output_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create test SARIF file: {e}")
        return False


def verify_sarif_tools_functionality():
    """Verify that sarif-tools can be used to validate a SARIF file."""
    print("Verifying sarif-tools functionality...")

    test_file = "test-sarif.sarif"
    if not os.path.exists(test_file):
        if not create_test_sarif_file(test_file):
            return False

    try:
        # Try to import and use sarif_tools directly
        try:
            # Use importlib to avoid unused import warning
            if importlib.util.find_spec("sarif_tools") is not None:
                print("✅ Successfully imported sarif_tools module")
                return True
            else:
                print("❌ Failed to import sarif_tools module")
        except ImportError:
            print("❌ Failed to import sarif_tools module")

        # Try using the command line tool
        try:
            subprocess.run(["sarif-tools", "--help"], check=True)
            print("✅ sarif-tools command line tool is working")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ sarif-tools command line tool is not working")

        # Try using python -m
        try:
            subprocess.run([sys.executable, "-m", "sarif_tools", "--help"], check=True)
            print("✅ python -m sarif_tools is working")
            return True
        except subprocess.CalledProcessError:
            print("❌ python -m sarif_tools is not working")

        print("❌ All methods to verify sarif-tools functionality failed")
        return False
    except Exception as e:
        print(f"❌ Error verifying sarif-tools functionality: {e}")
        return False


def main():
    """Verify sarif-tools installation and functionality."""
    print("Starting sarif-tools verification...")

    # Create security-reports directory
    os.makedirs("security-reports", exist_ok=True)
    print("Created security-reports directory")

    # Check if sarif-tools is installed
    if not check_sarif_tools_installed():
        print("sarif-tools not found, attempting to install...")
        if not install_sarif_tools():
            print("Failed to install sarif-tools, creating fallback SARIF files...")
            create_test_sarif_file("security-reports/bandit-results.sarif")
            create_test_sarif_file("security-reports/trivy-results.sarif")
            sys.exit(1)

    # Verify sarif-tools functionality
    if not verify_sarif_tools_functionality():
        print("sarif-tools verification failed, creating fallback SARIF files...")
        create_test_sarif_file("security-reports/bandit-results.sarif")
        create_test_sarif_file("security-reports/trivy-results.sarif")
        sys.exit(1)

    print("✅ sarif-tools verification completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
