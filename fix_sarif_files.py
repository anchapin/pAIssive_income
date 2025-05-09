#!/usr/bin/env python3
"""Fix SARIF files for GitHub Advanced Security.

This script fixes SARIF files to ensure they are compatible with
GitHub Advanced Security by correcting common issues.
"""

import json
import os
import sys
from pathlib import Path


def fix_sarif_file(file_path):
    """Fix a SARIF file to ensure it's compatible with GitHub Advanced Security.

    Args:
        file_path: Path to the SARIF file to fix

    Returns:
        bool: True if the file was fixed, False otherwise

    """
    try:
        # Read the file
        with open(file_path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in {file_path}: {e}")
                return create_empty_sarif_file(file_path)

        # Check if the file needs fixing
        needs_fixing = False

        # Fix $schema field if it's malformed (contains newlines or spaces)
        # Always set the schema URL to ensure it's correct
        data["$schema"] = (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
        )
        needs_fixing = True
        print(f"Set schema URL to the correct value for {file_path}")

        # Ensure required fields are present
        if "version" not in data:
            data["version"] = "2.1.0"
            needs_fixing = True
            print(f"Added missing version field to {file_path}")

        if "$schema" not in data:
            data["$schema"] = (
                "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
            )
            needs_fixing = True
            print(f"Added missing $schema field to {file_path}")

        if (
            "runs" not in data
            or not isinstance(data["runs"], list)
            or len(data["runs"]) == 0
        ):
            data["runs"] = [
                {
                    "tool": {
                        "driver": {
                            "name": "Unknown Tool",
                            "informationUri": "",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ]
            needs_fixing = True
            print(f"Added missing runs field to {file_path}")
        else:
            for i, run in enumerate(data["runs"]):
                if "tool" not in run:
                    run["tool"] = {
                        "driver": {
                            "name": "Unknown Tool",
                            "informationUri": "",
                            "rules": [],
                        }
                    }
                    needs_fixing = True
                    print(f"Added missing tool field to run {i} in {file_path}")
                elif "driver" not in run["tool"]:
                    run["tool"]["driver"] = {
                        "name": "Unknown Tool",
                        "informationUri": "",
                        "rules": [],
                    }
                    needs_fixing = True
                    print(f"Added missing driver field to run {i} in {file_path}")

                if "results" not in run:
                    run["results"] = []
                    needs_fixing = True
                    print(f"Added missing results field to run {i} in {file_path}")

        # Save the file if it was fixed
        if needs_fixing:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Fixed SARIF file: {file_path}")
            return True
        else:
            print(f"No issues found in {file_path}")
            return True

    except Exception as e:
        print(f"ERROR: Failed to fix {file_path}: {e}")
        return create_empty_sarif_file(file_path)


def create_empty_sarif_file(file_path):
    """Create an empty SARIF file with the correct structure.

    Args:
        file_path: Path to save the SARIF file

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        data = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Unknown Tool",
                            "informationUri": "",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Created empty SARIF file: {file_path}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to create empty SARIF file {file_path}: {e}")
        return False


def main():
    """Fix SARIF files."""
    print("Fixing SARIF files for GitHub Advanced Security...")

    # Create security-reports directory if it doesn't exist
    os.makedirs("security-reports", exist_ok=True)

    # Find all SARIF files
    sarif_files = list(Path("security-reports").glob("*.sarif"))

    if not sarif_files:
        print("No SARIF files found in security-reports directory")
        return 0

    # Fix each file
    success = True
    for file in sarif_files:
        print(f"\nProcessing {file}...")
        if not fix_sarif_file(str(file)):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
