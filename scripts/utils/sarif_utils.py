#!/usr/bin/env python3


# Configure logging
logger = logging.getLogger(__name__)

"""
SARIF utilities for security scanning workflows.

This module provides utilities for creating and manipulating SARIF files
without any external dependencies. It's designed to be used in CI/CD workflows
where installing additional packages might be problematic.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional



def create_empty_sarif(tool_name: str, tool_url: str = "") -> dict[str, Any]:
    """
    Create an empty SARIF file structure.

    Args:
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool

    Returns:
        Dict containing a valid empty SARIF structure

    Raises:
        ValueError: If tool_name is invalid
        TypeError: If tool_name is not a string

    """
    if not isinstance(tool_name, str):
        raise TypeError
    if not tool_name or tool_name.isspace():
        raise ValueError

    # Return the SARIF structure directly - no need for try/except here
    # as the structure is static and won't raise exceptions
    return {
        "version": "2.1.0",
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
            "Schemata/sarif-schema-2.1.0.json"
        ),
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": tool_url,
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }


def save_sarif_file(sarif_data: dict[str, Any], output_file: str) -> bool:
    """
    Save SARIF data to a file.

    Args:
        sarif_data: SARIF data structure
        output_file: Path to save the SARIF file

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If output path is invalid
        OSError: If there are filesystem related errors
        TypeError: If data is invalid

    """
    if not output_file:
        raise ValueError
    if not isinstance(sarif_data, dict):
        raise TypeError

    try:
        # Create directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w") as f:
            json.dump(sarif_data, f, indent=2)
    except OSError:
        logger.exception("Filesystem error")
        return False
    except TypeError:
        logger.exception("Invalid data type in SARIF")
        return False
    except json.JSONDecodeError:
        logger.exception("JSON encoding error")
        return False
    except Exception:
        logger.exception("Error saving SARIF file")
        return False
    else:
        return True


def add_result(
    sarif_data: dict[str, Any],
    rule_id: str,
    message: str,
    file_path: str,
    line_number: int,
    level: str = "warning",
    rule_name: str = "",
    rule_description: str = "",
) -> dict[str, Any]:
    """
    Add a result to a SARIF data structure.

    Args:
        sarif_data: SARIF data structure
        rule_id: ID of the rule that was violated
        message: Description of the issue
        file_path: Path to the file where the issue was found
        line_number: Line number where the issue was found
        level: Severity level (note, warning, error)
        rule_name: Short name of the rule
        rule_description: Longer description of the rule

    Returns:
        Updated SARIF data structure

    """
    # Create rule if it doesn't exist
    rules = sarif_data["runs"][0]["tool"]["driver"]["rules"]
    rule_exists = any(r.get("id") == rule_id for r in rules)

    if not rule_exists:
        rule = {"id": rule_id, "shortDescription": {"text": rule_name or rule_id}}

        if rule_description:
            rule["fullDescription"] = {"text": rule_description}

        if level:
            rule["defaultConfiguration"] = {"level": level}

        rules.append(rule)

    # Add result
    result = {
        "ruleId": rule_id,
        "level": level,
        "message": {"text": message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": file_path},
                    "region": {"startLine": line_number, "startColumn": 1},
                }
            }
        ],
    }

    sarif_data["runs"][0]["results"].append(result)
    return sarif_data


def convert_json_to_sarif(
    json_data: dict[str, object] | list[dict[str, object]] | None,
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[dict[str, str]] = None,
) -> dict[str, object]:
    """
    Convert generic JSON data to SARIF format.

    Args:
        json_data: Tool-specific JSON data (can be a list or dict)
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool
        result_mapping: Mapping from tool-specific fields to SARIF fields

    Returns:
        Dict containing SARIF data

    """
    sarif_data = create_empty_sarif(tool_name, tool_url)

    # Default mapping if none provided
    if result_mapping is None:
        result_mapping = {
            "rule_id": "id",
            "message": "message",
            "file_path": "file",
            "line_number": "line",
            "level": "severity",
            "rule_name": "name",
            "rule_description": "description",
        }

    # Ensure we have a list of results to process
    if isinstance(json_data, dict):
        results = json_data.get("results", [])
    elif isinstance(json_data, list):
        results = json_data  # Assume the list itself contains results
    else:
        # Define a more specific error message
        error_msg = "Unsupported JSON data type. Expected dict or list."
        raise TypeError(error_msg)

    if isinstance(results, list):
        for result in results:
            # Extract fields using mapping
            rule_id = str(result.get(result_mapping.get("rule_id", "id"), "unknown"))
            message = str(result.get(result_mapping.get("message", "message"), ""))
            file_path = str(result.get(result_mapping.get("file_path", "file"), ""))

            # Handle line number which might be an int or string
            line_raw = result.get(result_mapping.get("line_number", "line"), 1)
            line_number = int(line_raw) if line_raw else 1

            level = str(
                result.get(result_mapping.get("level", "severity"), "warning")
            ).lower()
            rule_name = str(result.get(result_mapping.get("rule_name", "name"), ""))
            rule_description = str(
                result.get(result_mapping.get("rule_description", "description"), "")
            )

            # Map severity levels if needed
            if level not in ["note", "warning", "error"]:
                if level.upper() in ["HIGH", "CRITICAL"]:
                    level = "error"
                elif level.upper() in ["MEDIUM"]:
                    level = "warning"
                else:
                    level = "note"

            # Add to SARIF
            add_result(
                sarif_data,
                rule_id,
                message,
                file_path,
                line_number,
                level,
                rule_name,
                rule_description,
            )

    return sarif_data


def convert_file(
    input_file: str,
    output_file: str,
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[dict[str, str]] = None,
) -> bool:
    """
    Convert a JSON file to SARIF format.

    Args:
        input_file: Path to the input JSON file
        output_file: Path to save the SARIF file
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool
        result_mapping: Optional mapping of JSON keys to SARIF fields

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        # Check if input file exists and has content
        input_path = Path(input_file)
        if not input_path.exists() or input_path.stat().st_size == 0:
            logger.warning("Input file [%s] is empty or does not exist", input_file)
            logger.info("Creating an empty SARIF file at %s", output_file)
            empty_sarif = create_empty_sarif(tool_name, tool_url)
            return save_sarif_file(empty_sarif, output_file)

        # Input file exists and has content, try to parse it
        try:
            with input_path.open() as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            logger.exception("Error parsing JSON from %s", input_file)
            logger.info("Creating an empty SARIF file at %s", output_file)
            empty_sarif = create_empty_sarif(tool_name, tool_url)
            return save_sarif_file(empty_sarif, output_file)

        # Convert to SARIF
        sarif_data = convert_json_to_sarif(
            json_data, tool_name, tool_url, result_mapping
        )

        # Save SARIF file
        return save_sarif_file(sarif_data, output_file)
    except Exception:
        logger.exception("Error converting file")
        # Ensure we always create a valid SARIF file even on error
        try:
            empty_sarif = create_empty_sarif(tool_name, tool_url)
            save_sarif_file(empty_sarif, output_file)
            logger.info("Created fallback empty SARIF file at %s", output_file)
        except (OSError, TypeError, ValueError) as e:
            logger.critical(
                "Critical error: Failed to create fallback SARIF file: %s", e
            )
            return False
        else:
            return True  # Return success since we created a valid SARIF file


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # Simple command-line interface
    MIN_ARGS = 4  # input_file, output_file, tool_name are required
    if len(sys.argv) < MIN_ARGS:
        logger.error(
            "Usage: python sarif_utils.py <input_file> <output_file> <tool_name> "
            "[tool_url]"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    tool_name = sys.argv[3]
    tool_url = sys.argv[4] if len(sys.argv) > MIN_ARGS else ""

    # Check if input_file is a JSON string (starts with '[' or '{')
    if input_file.strip().startswith(("[", "{")):
        logger.info("Detected JSON string input, creating SARIF directly")
        try:
            json_data = json.loads(input_file)
            sarif_data = convert_json_to_sarif(json_data, tool_name, tool_url)
            success = save_sarif_file(sarif_data, output_file)
        except json.JSONDecodeError:
            logger.exception("Error parsing JSON string")
            empty_sarif = create_empty_sarif(tool_name, tool_url)
            success = save_sarif_file(empty_sarif, output_file)
    else:
        # Process as file path
        success = convert_file(input_file, output_file, tool_name, tool_url)

    sys.exit(0 if success else 1)
