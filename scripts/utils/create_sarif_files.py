#!/usr/bin/env python3
"""Create SARIF files for GitHub Advanced Security."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, TypedDict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Set up a dedicated logger for this module
logger = logging.getLogger(__name__)


class SarifToolDriver(TypedDict):
    """Type for SARIF tool driver."""

    name: str
    informationUri: str
    rules: list[Any]


class SarifTool(TypedDict):
    """Type for SARIF tool."""

    driver: SarifToolDriver


class SarifRun(TypedDict):
    """Type for SARIF run."""

    tool: SarifTool
    results: list[Any]


class SarifFile(TypedDict):
    """Type for SARIF file."""

    version: str
    schema: str  # renamed from $schema for Python compatibility
    runs: list[SarifRun]


def create_sarif_file(
    file_path: str | Path,
    tool_name: str,
    tool_url: str,
) -> None:
    """
    Create a SARIF file with the correct structure.

    Args:
        file_path: Path to save the SARIF file
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool

    """
    data: SarifFile = {
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

    # Convert file_path to Path object if it's a string
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with file_path_obj.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info("Created SARIF file: %s", file_path)


def main() -> None:
    """Create SARIF files for security scanning tools."""
    # Create Bandit SARIF file
    create_sarif_file(
        Path("security-reports/bandit-results.sarif"),
        "Bandit",
        "https://bandit.readthedocs.io/",
    )

    # Create Trivy SARIF file
    create_sarif_file(
        Path("security-reports/trivy-results.sarif"),
        "Trivy",
        "https://github.com/aquasecurity/trivy",
    )

    # Create Safety SARIF file
    create_sarif_file(
        Path("security-reports/safety-results.sarif"),
        "Safety",
        "https://pyup.io/safety/",
    )


if __name__ == "__main__":
    main()
