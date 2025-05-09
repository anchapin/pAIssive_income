#!/usr/bin/env python3
"""Create SARIF files for GitHub Advanced Security."""

import json
import os


def create_sarif_file(file_path, tool_name, tool_url):
    """Create a SARIF file with the correct structure.

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

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Created SARIF file: {file_path}")


def main():
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
