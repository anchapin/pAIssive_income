#!/usr/bin/env python3
"""Test script to validate SARIF file format.

This script creates a test SARIF file and validates its structure
to ensure it conforms to the expected format for GitHub Advanced Security.
"""

import json
import logging
import os
import sys

from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_test_sarif() -> str:
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

    logging.info(
        "Created test SARIF file at security-reports/test-bandit-results.sarif"
    )
    return "security-reports/test-bandit-results.sarif"


def validate_sarif_file(file_path: str) -> bool:
    """Validate that a SARIF file has the correct structure."""
    is_valid = True
    try:
        with open(file_path) as f:
            data = json.load(f)

        # Check required fields
        if "version" not in data:
            logging.error("Missing 'version' field")
            is_valid = False
        if "$schema" not in data:
            logging.error("Missing '$schema' field")
            is_valid = False
        if (
            "runs" not in data
            or not isinstance(data["runs"], list)
            or len(data["runs"]) == 0
        ):
            logging.error("Missing or invalid 'runs' field")
            is_valid = False
        else:
            run = data["runs"][0]
            if "tool" not in run or "driver" not in run["tool"]:
                logging.error("Missing 'tool.driver' field")
                is_valid = False
            else:
                driver = run["tool"]["driver"]
                if "name" not in driver:
                    logging.error("Missing 'tool.driver.name' field")
                    is_valid = False
                if "results" not in run:
                    logging.error("Missing 'results' field")
                    is_valid = False
    except json.JSONDecodeError:
        logging.exception(f"Invalid JSON in {file_path}")
        is_valid = False
    except Exception:
        logging.exception(f"Failed to validate {file_path}")
        is_valid = False
    if is_valid:
        logging.info(f"\u2705 SARIF file {file_path} is valid")
    return is_valid


def main() -> int:
    """Test SARIF file format."""
    logging.info("Testing SARIF file format...")

    # Create a test SARIF file
    test_file = create_test_sarif()

    # Validate the file
    is_valid = validate_sarif_file(test_file)

    # Check if any existing SARIF files are present
    sarif_files = list(Path("security-reports").glob("*.sarif"))
    for file in sarif_files:
        if str(file) != test_file:
            logging.info(f"\nValidating existing SARIF file: {file}")
            validate_sarif_file(str(file))

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
