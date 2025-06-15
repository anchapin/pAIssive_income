#!/usr/bin/env python3
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
from typing import (
    Any,
    Dict,
    Final,
    Literal,
    NoReturn,
    Optional,
    TypedDict,
    Union,
    overload,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Type aliases and constants
SARIF_VERSION: Final[str] = "2.1.0"
SARIF_SCHEMA_URL: Final[str] = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
    "Schemata/sarif-schema-2.1.0.json"
)

# Command line argument constants
MIN_ARGS: Final[int] = 4
ARG_INPUT_FILE: Final[int] = 1
ARG_OUTPUT_FILE: Final[int] = 2
ARG_TOOL_NAME: Final[int] = 3
ARG_TOOL_URL: Final[int] = 4


class SarifRule(TypedDict):
    """Type definition for a SARIF rule."""

    id: str
    shortDescription: dict[str, str]
    fullDescription: dict[str, str]
    help: dict[str, str]
    defaultConfiguration: dict[str, Union[str, int, float, bool]]
    properties: dict[str, Any]


class SarifLocation(TypedDict):
    """Type definition for a SARIF location."""

    physicalLocation: dict[str, Any]
    logicalLocations: list[dict[str, str]]


class SarifResult(TypedDict):
    """Type definition for a SARIF result."""

    ruleId: str
    level: Literal["none", "note", "warning", "error"]
    message: dict[str, str]
    locations: list[SarifLocation]
    partialFingerprints: dict[str, str]


class SarifToolDriver(TypedDict):
    """Type definition for a SARIF tool driver."""

    name: str
    informationUri: str
    rules: list[SarifRule]


class SarifTool(TypedDict):
    """Type definition for a SARIF tool."""

    driver: SarifToolDriver


class SarifRun(TypedDict):
    """Type definition for a SARIF run."""

    tool: SarifTool
    results: list[SarifResult]


class SarifFile(TypedDict):
    """Type definition for a complete SARIF file."""

    version: Literal["2.1.0"]
    schema: str  # Note: This represents the $schema field
    runs: list[SarifRun]


def create_empty_sarif(tool_name: str, tool_url: str = "") -> SarifFile:
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
        msg = "tool_name must be a string"
        raise TypeError(msg)
    if not tool_name or tool_name.isspace():
        msg = "tool_name cannot be empty or whitespace"
        raise ValueError(msg)

    return {
        "version": SARIF_VERSION,
        "$schema": SARIF_SCHEMA_URL,
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


@overload
def save_sarif_file(sarif_data: SarifFile, output_file: str) -> bool: ...


@overload
def save_sarif_file(sarif_data: SarifFile, output_file: Path) -> bool: ...


def save_sarif_file(sarif_data: SarifFile, output_file: Union[str, Path]) -> bool:
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
        msg = "output_file cannot be empty"
        raise ValueError(msg)
    if not isinstance(sarif_data, dict):
        msg = "sarif_data must be a dict"
        raise TypeError(msg)

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


# Type aliases for the mapping dictionary
FieldMapping = Dict[
    Literal[
        "rule_id",
        "message",
        "file_path",
        "line_number",
        "level",
        "rule_name",
        "rule_description",
    ],
    str,
]

# Constants for severity levels
SeverityLevel = Literal["none", "note", "warning", "error"]
DEFAULT_LEVEL: Final[SeverityLevel] = "warning"
DEFAULT_LINE_NUMBER: Final[int] = 1

# Default field mapping
DEFAULT_FIELD_MAPPING: Final[FieldMapping] = {
    "rule_id": "id",
    "message": "message",
    "file_path": "file",
    "line_number": "line",
    "level": "severity",
    "rule_name": "name",
    "rule_description": "description",
}


def add_result(
    sarif_data: SarifFile,
    rule_id: str,
    message: str,
    file_path: str,
    line_number: int,
    level: SeverityLevel = DEFAULT_LEVEL,
    rule_name: str = "",
    rule_description: str = "",
) -> SarifFile:
    """
    Add a result to a SARIF data structure.

    Args:
        sarif_data: SARIF data structure
        rule_id: ID of the rule that was violated
        message: Description of the issue
        file_path: Path to the file where the issue was found
        line_number: Line number where the issue was found
        level: Severity level (none, note, warning, error)
        rule_name: Short name of the rule
        rule_description: Longer description of the rule

    Returns:
        Updated SARIF data structure

    """
    # Create rule if it doesn't exist
    rules = sarif_data["runs"][0]["tool"]["driver"]["rules"]
    rule_exists = any(r.get("id") == rule_id for r in rules)

    if not rule_exists:
        rule: SarifRule = {
            "id": rule_id,
            "shortDescription": {"text": rule_name or rule_id},
            "fullDescription": {"text": rule_description}
            if rule_description
            else {"text": ""},
            "help": {"text": ""},
            "defaultConfiguration": {"level": level},
            "properties": {},
        }

        rules.append(rule)

    # Add result
    result: SarifResult = {
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
        "partialFingerprints": {},
    }

    sarif_data["runs"][0]["results"].append(result)
    return sarif_data


def convert_json_to_sarif(
    json_data: Union[dict[str, Any], list[dict[str, Any]], None],
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[FieldMapping] = None,
) -> SarifFile:
    """
    Convert generic JSON data to SARIF format.

    Args:
        json_data: Tool-specific JSON data (can be a list or dict)
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool
        result_mapping: Mapping from tool-specific fields to SARIF fields

    Returns:
        Dict containing SARIF data

    Raises:
        TypeError: If json_data is not a dict or list
        ValueError: If required fields are missing or invalid

    """
    sarif_data = create_empty_sarif(tool_name, tool_url)

    # Use default mapping if none provided
    mapping = result_mapping if result_mapping is not None else DEFAULT_FIELD_MAPPING

    # Ensure we have a list of results to process
    if isinstance(json_data, dict):
        results = json_data.get("results", [])
    elif isinstance(json_data, list):
        results = json_data  # Assume the list itself contains results
    else:
        msg = "Unsupported JSON data type. Expected dict or list."
        raise TypeError(msg)

    if isinstance(results, list):
        for result in results:
            # Extract fields using mapping
            rule_id = str(result.get(mapping.get("rule_id", "id"), "unknown"))
            message = str(result.get(mapping.get("message", "message"), ""))
            file_path = str(result.get(mapping.get("file_path", "file"), ""))

            # Handle line number which might be an int or string
            line_raw = result.get(
                mapping.get("line_number", "line"), DEFAULT_LINE_NUMBER
            )
            line_number = int(line_raw) if line_raw else DEFAULT_LINE_NUMBER

            # Convert severity to SARIF level
            raw_level = str(
                result.get(mapping.get("level", "severity"), DEFAULT_LEVEL)
            ).lower()
            level: SeverityLevel = (
                "error"
                if raw_level in ("error", "high", "critical")
                else "warning"
                if raw_level in ("warning", "medium")
                else "note"
                if raw_level in ("note", "low", "info")
                else "none"
            )

            rule_name = str(result.get(mapping.get("rule_name", "name"), ""))
            rule_description = str(
                result.get(mapping.get("rule_description", "description"), "")
            )

            # Add the result to SARIF data
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


@overload
def convert_file(
    input_file: str,
    output_file: str,
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[FieldMapping] = None,
) -> bool: ...


@overload
def convert_file(
    input_file: Path,
    output_file: Union[str, Path],
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[FieldMapping] = None,
) -> bool: ...


def convert_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    tool_name: str,
    tool_url: str = "",
    result_mapping: Optional[FieldMapping] = None,
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

    Raises:
        OSError: On filesystem-related errors
        TypeError: If arguments have invalid types
        ValueError: If paths are invalid

    """
    try:
        # Check if input file exists and has content
        input_path = Path(input_file)
        if not input_path.exists() or input_path.stat().st_size == 0:
            logger.warning("Input file [%s] is empty or does not exist", input_file)
            logger.info("Creating an empty SARIF file at %s", output_file)
            empty_sarif: SarifFile = create_empty_sarif(tool_name, tool_url)
            return save_sarif_file(empty_sarif, output_file)

        # Input file exists and has content, try to parse it
        try:
            with input_path.open() as f:
                json_data: Union[dict[str, Any], list[dict[str, Any]], None] = (
                    json.load(f)
                )
        except json.JSONDecodeError:
            logger.exception("Error parsing JSON from %s", input_file)
            logger.info("Creating an empty SARIF file at %s", output_file)
            empty_sarif = create_empty_sarif(tool_name, tool_url)
            return save_sarif_file(empty_sarif, output_file)

        # Convert to SARIF
        sarif_data: SarifFile = convert_json_to_sarif(
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


def main() -> NoReturn:
    """
    Command line interface for SARIF conversion.

    Usage:
        python sarif_utils.py input.json output.sarif "Tool Name" [tool_url]

    Raises:
        SystemExit: Always exits with status code

    """
    if len(sys.argv) < MIN_ARGS:
        print(
            "Usage: python sarif_utils.py input.json output.sarif"
            ' "Tool Name" [tool_url]'
        )
        sys.exit(1)

    input_file: str = sys.argv[ARG_INPUT_FILE]
    output_file: str = sys.argv[ARG_OUTPUT_FILE]
    tool_name: str = sys.argv[ARG_TOOL_NAME]
    tool_url: str = sys.argv[ARG_TOOL_URL] if len(sys.argv) > MIN_ARGS else ""

    success: bool = convert_file(input_file, output_file, tool_name, tool_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
