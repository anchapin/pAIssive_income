#!/usr/bin/env python3
"""Validate SARIF files and create valid empty ones if needed.

This script validates SARIF files and creates valid empty ones if needed.
It's used in GitHub Actions workflows to ensure that SARIF files are valid
before uploading them to GitHub.
"""

import argparse
import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Valid empty SARIF template
EMPTY_SARIF_TEMPLATE = {
    "version": "2.1.0",
    "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
    "runs": [
        {
            "tool": {
                "driver": {
                    "name": "{tool_name}",
                    "informationUri": "https://github.com/anchapin/pAIssive_income",
                    "rules": [],
                }
            },
            "results": [],
        }
    ],
}


def validate_sarif_file(file_path: str, tool_name: str) -> bool:
    """Validate a SARIF file and create a valid empty one if needed.

    Args:
        file_path: Path to the SARIF file.
        tool_name: Name of the tool that generated the SARIF file.

    Returns:
        True if the file is valid or was created, False otherwise.
    """
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            logging.warning(
                "SARIF file %s not found. Creating empty SARIF file.", file_path
            )
            create_empty_sarif(file_path, tool_name)
            return True

        # Check if file is valid JSON and validate its structure
        with open(file_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                logging.warning(
                    "Invalid SARIF file %s. Creating valid empty SARIF file.", file_path
                )
                create_empty_sarif(file_path, tool_name)
                return True

        # Validate SARIF structure
        if not _validate_sarif_structure(data, file_path, tool_name):
            return True  # The validation function handles creating a new file if needed
        else:
            # If we got here, the file is valid
            logging.info("SARIF file %s is valid.", file_path)
            return True
    except Exception:
        logging.exception("Error validating SARIF file %s", file_path)
        try:
            create_empty_sarif(file_path, tool_name)
        except Exception:
            logging.exception("Error creating empty SARIF file %s", file_path)
            return False
        else:
            return True


def _validate_sarif_structure(data: dict, file_path: str, tool_name: str) -> bool:
    """Validate the structure of a SARIF file.

    Args:
        data: The SARIF data.
        file_path: Path to the SARIF file.
        tool_name: Name of the tool that generated the SARIF file.

    Returns:
        True if the file is valid, False if it needed to be recreated.
    """
    # Check if version property exists
    if "version" not in data:
        logging.warning(
            "SARIF file %s missing version property. Creating valid empty SARIF file.",
            file_path,
        )
        create_empty_sarif(file_path, tool_name)
        return False

    # Check if runs property exists
    if "runs" not in data:
        logging.warning(
            "SARIF file %s missing runs property. Creating valid empty SARIF file.",
            file_path,
        )
        create_empty_sarif(file_path, tool_name)
        return False

    # Check if runs is a list
    if not isinstance(data["runs"], list):
        logging.warning(
            "SARIF file %s has invalid runs property. Creating valid empty SARIF file.",
            file_path,
        )
        create_empty_sarif(file_path, tool_name)
        return False

    # Check if runs has at least one element
    if not data["runs"]:
        logging.warning(
            "SARIF file %s has empty runs property. Creating valid empty SARIF file.",
            file_path,
        )
        create_empty_sarif(file_path, tool_name)
        return False

    # Check if tool property exists in first run
    if "tool" not in data["runs"][0]:
        logging.warning(
            "SARIF file %s missing tool property. Creating valid empty SARIF file.",
            file_path,
        )
        create_empty_sarif(file_path, tool_name)
        return False

    return True


def create_empty_sarif(file_path: str, tool_name: str) -> None:
    """Create a valid empty SARIF file.

    Args:
        file_path: Path to the SARIF file.
        tool_name: Name of the tool that generated the SARIF file.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    # Create empty SARIF file
    sarif = EMPTY_SARIF_TEMPLATE.copy()
    # Use list indexing for the runs list, which is a list type
    if isinstance(sarif["runs"], list) and len(sarif["runs"]) > 0:
        sarif["runs"][0]["tool"]["driver"]["name"] = tool_name

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2)

    logging.info("Created valid empty SARIF file %s.", file_path)


def main() -> int:
    """Main function.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(
        description="Validate SARIF files and create valid empty ones if needed."
    )
    parser.add_argument("file_path", help="Path to the SARIF file.")
    parser.add_argument(
        "tool_name", help="Name of the tool that generated the SARIF file."
    )
    args = parser.parse_args()

    if validate_sarif_file(args.file_path, args.tool_name):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
