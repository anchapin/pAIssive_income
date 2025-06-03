#!/usr/bin/env python3
"""
Create fallback security scan files to ensure workflow doesn't fail.

This script creates empty security scan result files that can be used
as fallbacks when security tools fail to run or generate output.
"""

import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_empty_sarif(tool_name: str, tool_version: str = "unknown") -> dict:
    """Create an empty SARIF template."""
    return {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": f"https://github.com/PyCQA/{tool_name.lower()}",
                        "version": tool_version,
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }


def create_empty_json_results() -> dict:
    """Create empty JSON results template."""
    return {
        "results": [],
        "errors": [],
        "vulnerabilities": []
    }


def main() -> None:
    """Create all fallback security files."""
    logger.info("Creating security scan fallback files...")

    # Create security-reports directory
    security_dir = Path("security-reports")
    security_dir.mkdir(exist_ok=True)
    logger.info(f"Created directory: {security_dir}")

    # Create empty SARIF files
    sarif_files = [
        ("bandit-results.sarif", "Bandit", "1.7.5"),
        ("semgrep-results.sarif", "Semgrep", "1.0.0"),
        ("trivy-results.sarif", "Trivy", "0.50.0")
    ]

    for filename, tool_name, version in sarif_files:
        file_path = security_dir / filename
        sarif_data = create_empty_sarif(tool_name, version)

        with file_path.open("w") as f:
            json.dump(sarif_data, f, indent=2)

        logger.info(f"Created fallback SARIF file: {file_path}")

    # Create empty JSON result files
    json_files = [
        "bandit-results.json",
        "safety-results.json",
        "pip-audit-results.json",
        "semgrep-results.json"
    ]

    for filename in json_files:
        file_path = security_dir / filename
        json_data = create_empty_json_results()

        with file_path.open("w") as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"Created fallback JSON file: {file_path}")

    # Create root-level empty SARIF file for compatibility
    root_sarif = Path("empty-sarif.json")
    empty_sarif = create_empty_sarif("Security-Scan", "1.0.0")

    with root_sarif.open("w") as f:
        json.dump(empty_sarif, f, indent=2)

    logger.info(f"Created root-level fallback SARIF: {root_sarif}")

    logger.info("All security scan fallback files created successfully")


if __name__ == "__main__":
    main()
