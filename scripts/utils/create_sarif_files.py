#!/usr/bin/env python3


# Configure logging
logger = logging.getLogger(__name__)

"""Create SARIF files for GitHub Advanced Security."""

import json
import logging
from pathlib import Path

# Set up a dedicated logger for this module


def create_sarif_file(file_path: str, tool_name: str, tool_url: str) -> None:
    """
    Create a SARIF file with the correct structure.

    Args:
        file_path: Path to save the SARIF file
        tool_name: Name of the tool that produced the results
        tool_url: URL with information about the tool

    """
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
                        "name": tool_name,
                        "informationUri": tool_url,
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with Path(file_path).open("w") as f:
        json.dump(data, f, indent=2)

    logger.info("Created SARIF file: %s", file_path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    """Create SARIF files."""
    # Create Bandit SARIF file
    create_sarif_file(
        "security-reports/bandit-results.sarif",
        "Bandit",
        "https://bandit.readthedocs.io/",
    )

    # Create Trivy SARIF file
    create_sarif_file(
        "security-reports/trivy-results.sarif",
        "Trivy",
        "https://github.com/aquasecurity/trivy",
    )

    # Create Safety SARIF file
    create_sarif_file(
        "security-reports/safety-results.sarif", "Safety", "https://pyup.io/safety/"
    )


if __name__ == "__main__":
    main()
