#!/usr/bin/env python3
"""Utility script to verify and install sarif-tools.

This script attempts to install the sarif-tools package and creates a test SARIF file
if the installation fails. It's used in CI workflows to ensure SARIF processing tools
are available.
"""

import json
import subprocess
import sys


def install_sarif_tools():
    """Install the sarif-tools package.

    Attempts to install with --user flag first, then falls back to a global install.

    Returns:
        bool: True if installation was successful, False otherwise.

    """
    print("Attempting to install sarif-tools...")
    try:
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
        print("✅ sarif-tools installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install sarif-tools: {e}. Retrying without --user...")
        try:
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
            print("✅ sarif-tools installed successfully.")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Final failure to install sarif-tools: {e2}.")
            return False


def create_test_sarif_file(output_path="test-sarif.sarif"):
    """Create a minimal valid SARIF file for testing purposes.

    Args:
        output_path (str): Path where the SARIF file should be saved.

    Returns:
        bool: True if file creation was successful, False otherwise.

    """
    print(f"Creating test SARIF file at {output_path}...")
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
        "note": "This is a placeholder SARIF file created because sarif-tools failed.",
    }
    try:
        with open(output_path, "w") as f:
            json.dump(sarif_data, f, indent=2)
        print(f"✅ Test SARIF file created at {output_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create test SARIF file: {e}")
        return False


if __name__ == "__main__":
    if not install_sarif_tools():
        create_test_sarif_file()
