#!/usr/bin/env python3
"""SARIF utilities for security scanning workflows.

This module provides utilities for creating and manipulating SARIF files
without any external dependencies. It's designed to be used in CI/CD workflows
where installing additional packages might be problematic.
"""

import json
import os
import sys
from typing import Any, Dict, Optional


def create_empty_sarif(tool_name: str, tool_url: str = "") -> Dict[str, Any]:
    """Create an empty SARIF file structure.

    Args:
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool

    Returns:
        Dict containing a valid empty SARIF structure

    """
    return {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
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


def save_sarif_file(sarif_data: Dict[str, Any], output_file: str) -> bool:
    """Save SARIF data to a file.

    Args:
        sarif_data: SARIF data structure
        output_file: Path to save the SARIF file

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(sarif_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving SARIF file: {e}")
        return False


def add_result(
    sarif_data: Dict[str, Any],
    rule_id: str,
    message: str,
    file_path: str,
    line_number: int,
    level: str = "warning",
    rule_name: str = "",
    rule_description: str = "",
) -> Dict[str, Any]:
    """Add a result to a SARIF data structure.

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
    json_data: Dict[str, Any],
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Convert generic JSON data to SARIF format.

    Args:
        json_data: Tool-specific JSON data
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

    # Process results if they exist
    results = json_data.get("results", [])
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
    result_mapping: Optional[Dict[str, str]] = None,
) -> bool:
    """Convert a JSON file to SARIF format.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output SARIF file
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool
        result_mapping: Mapping from tool-specific fields to SARIF fields

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        # Create empty SARIF file first as fallback
        empty_sarif = create_empty_sarif(tool_name, tool_url)
        save_sarif_file(empty_sarif, output_file)

        # Check if input file exists and has content
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            print(f"Warning: Input file {input_file} is empty or does not exist")
            return False

        # Load input JSON
        with open(input_file) as f:
            json_data = json.load(f)

        # Convert to SARIF
        sarif_data = convert_json_to_sarif(
            json_data, tool_name, tool_url, result_mapping
        )

        # Save SARIF file
        return save_sarif_file(sarif_data, output_file)
    except Exception as e:
        print(f"Error converting file: {e}")
        return False


if __name__ == "__main__":
    # Simple command-line interface
    if len(sys.argv) < 4:
        print(
            "Usage: python sarif_utils.py <input_file> <output_file> <tool_name> "
            "[tool_url]"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    tool_name = sys.argv[3]
    tool_url = sys.argv[4] if len(sys.argv) > 4 else ""

    success = convert_file(input_file, output_file, tool_name, tool_url)
    sys.exit(0 if success else 1)
