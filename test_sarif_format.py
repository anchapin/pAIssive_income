#!/usr/bin/env python3
"""Test script to validate SARIF file format.

This script creates a test SARIF file and validates its structure
to ensure it conforms to the expected format for GitHub Advanced Security.
"""

import json
import os
import sys

from pathlib import Path


def create_test_sarif():
    """Create a test SARIF file with the correct structure."""
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
                        "name": "Bandit",
                        "informationUri": "https://bandit.readthedocs.io/",
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    # Create directory if it doesn't exist
    os.makedirs("security-reports", exist_ok=True)

    # Save the file
    with open("security-reports/test-bandit-results.sarif", "w") as f:
        json.dump(sarif_data, f, indent=2)

    print("Created test SARIF file at security-reports/test-bandit-results.sarif")
    return "security-reports/test-bandit-results.sarif"


def validate_sarif_file(file_path):
    """Validate that a SARIF file has the correct structure."""
    try:
        with open(file_path) as f:
            data = json.load(f)

        # Check required fields
        if "version" not in data:
            print("ERROR: Missing 'version' field")
            return False

        if "$schema" not in data:
            print("ERROR: Missing '$schema' field")
            return False

        if (
            "runs" not in data
            or not isinstance(data["runs"], list)
            or len(data["runs"]) == 0
        ):
            print("ERROR: Missing or invalid 'runs' field")
            return False

        run = data["runs"][0]
        if "tool" not in run or "driver" not in run["tool"]:
            print("ERROR: Missing 'tool.driver' field")
            return False

        driver = run["tool"]["driver"]
        if "name" not in driver:
            print("ERROR: Missing 'tool.driver.name' field")
            return False

        if "results" not in run:
            print("ERROR: Missing 'results' field")
            return False

        print(f"✅ SARIF file {file_path} is valid")
        return True

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to validate {file_path}: {e}")
        return False


def main():
    """Test SARIF file format."""
    print("Testing SARIF file format...")

    # Create a test SARIF file
    test_file = create_test_sarif()

    # Validate the file
    is_valid = validate_sarif_file(test_file)

    # Check if any existing SARIF files are present
    sarif_files = list(Path("security-reports").glob("*.sarif"))
    for file in sarif_files:
        if str(file) != test_file:
            print(f"\nValidating existing SARIF file: {file}")
            validate_sarif_file(str(file))

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
