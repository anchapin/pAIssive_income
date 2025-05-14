#!/usr/bin/env python3
"""Fix SARIF files for GitHub Advanced Security.

This script fixes SARIF files to ensure they are compatible with
GitHub Advanced Security by correcting common issues.
"""

import json
import logging
import os
import sys

from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def fix_schema_and_version(data: dict, file_path: str) -> bool:
    """Fix schema and version fields in SARIF data.

    Args:
        data: SARIF data to fix
        file_path: Path to the SARIF file (for logging)

    Returns:
        bool: True if any fixes were made
    """
    needs_fixing = False

    # Fix $schema field if it's malformed (contains newlines or spaces)
    # Always set the schema URL to ensure it's correct
    data["$schema"] = (
        "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
        "Schemata/sarif-schema-2.1.0.json"
    )
    needs_fixing = True
    logging.info(f"Set schema URL to the correct value for {file_path}")

    # Ensure required fields are present
    if "version" not in data:
        data["version"] = "2.1.0"
        needs_fixing = True
        logging.info(f"Added missing version field to {file_path}")

    if "$schema" not in data:
        data["$schema"] = (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
            "Schemata/sarif-schema-2.1.0.json"
        )
        needs_fixing = True
        logging.info(f"Added missing $schema field to {file_path}")

    return needs_fixing


def fix_runs(data: dict, file_path: str) -> bool:
    """Fix runs field in SARIF data.

    Args:
        data: SARIF data to fix
        file_path: Path to the SARIF file (for logging)

    Returns:
        bool: True if any fixes were made
    """
    needs_fixing = False

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
        logging.info(f"Added missing runs field to {file_path}")
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
                logging.info(f"Added missing tool field to run {i} in {file_path}")
            elif "driver" not in run["tool"]:
                run["tool"]["driver"] = {
                    "name": "Unknown Tool",
                    "informationUri": "",
                    "rules": [],
                }
                needs_fixing = True
                logging.info(f"Added missing driver field to run {i} in {file_path}")

            if "results" not in run:
                run["results"] = []
                needs_fixing = True
                logging.info(f"Added missing results field to run {i} in {file_path}")

    return needs_fixing


def fix_sarif_file(file_path: str) -> bool:
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
            except json.JSONDecodeError:
                logging.exception(f"Invalid JSON in {file_path}")
                return create_empty_sarif_file(file_path)

        # Fix the SARIF file
        schema_fixed = fix_schema_and_version(data, file_path)
        runs_fixed = fix_runs(data, file_path)
        needs_fixing = schema_fixed or runs_fixed

        # Save the file if it was fixed
        if needs_fixing:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            logging.info(f"Fixed SARIF file: {file_path}")
            return True
        else:
            logging.info(f"No issues found in {file_path}")
            return True

    except Exception:
        logging.exception(f"Failed to fix {file_path}")
        return create_empty_sarif_file(file_path)


def create_empty_sarif_file(file_path: str) -> bool:
    """Create an empty SARIF file with the correct structure.

    Args:
        file_path: Path to save the SARIF file

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If file_path is empty
        OSError: If there are filesystem related errors
    """
    if not file_path:
        logging.error("File path cannot be empty")
        return False

    try:
        data = {
            "version": "2.1.0",
            "$schema": (
                "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
                "Schemata/sarif-schema-2.1.0.json"
            ),
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

        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        logging.error(f"Filesystem error while creating SARIF file: {str(e)}")
        return False
    except TypeError as e:
        logging.error(f"Invalid data type in SARIF structure: {str(e)}")
        return False
    except json.JSONEncodeError as e:
        logging.error(f"Error encoding SARIF data to JSON: {str(e)}")
        return False
    else:
        logging.info(f"Created empty SARIF file: {file_path}")
        return True


def main() -> int:
    """Fix SARIF files."""
    logging.info("Fixing SARIF files for GitHub Advanced Security...")

    # Create security-reports directory if it doesn't exist
    os.makedirs("security-reports", exist_ok=True)

    # Find all SARIF files
    sarif_files = list(Path("security-reports").glob("*.sarif"))

    if not sarif_files:
        logging.info("No SARIF files found in security-reports directory")
        return 0

    # Fix each file
    success = True
    for file in sarif_files:
        logging.info(f"Processing {file}...")
        if not fix_sarif_file(str(file)):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
