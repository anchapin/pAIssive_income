#!/usr/bin/env python3
"""
Convert Bandit JSON output to SARIF format.

This script reads the Bandit JSON output file and converts it to SARIF format
for GitHub Advanced Security.
"""

import json
import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def convert_to_sarif(json_file, sarif_file):
    """
    Convert Bandit JSON output to SARIF format.

    Args:
        json_file: Path to the Bandit JSON output file
        sarif_file: Path to the output SARIF file
    """
    # Create the SARIF template
    sarif = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "informationUri": "https://github.com/PyCQA/bandit",
                        "version": "1.7.5",
                        "rules": []
                    }
                },
                "results": []
            }
        ]
    }

    # Check if the JSON file exists and has content
    json_path = Path(json_file)
    if not json_path.exists() or json_path.stat().st_size == 0:
        logger.info(f"JSON file {json_file} does not exist or is empty. Creating empty SARIF file.")
        try:
            with open(sarif_file, 'w') as f:
                json.dump(sarif, f)
            return
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create SARIF file: {e}")
            return

    # Read the Bandit JSON output
    try:
        with open(json_file, 'r') as f:
            bandit_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading JSON file: {e}. Creating empty SARIF file.")
        try:
            with open(sarif_file, 'w') as f:
                json.dump(sarif, f)
            return
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create SARIF file: {e}")
            return

    # Check if there are any results
    if not bandit_data.get('results'):
        logger.info("No results found in Bandit output. Creating empty SARIF file.")
        try:
            with open(sarif_file, 'w') as f:
                json.dump(sarif, f)
            return
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create SARIF file: {e}")
            return

    # Convert Bandit results to SARIF format
    rules = {}
    results = []

    for result in bandit_data.get('results', []):
        rule_id = f"B{result.get('test_id', '000')}"

        # Add rule if not already added
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "shortDescription": {
                    "text": result.get('test_name', 'Unknown test')
                },
                "fullDescription": {
                    "text": result.get('issue_text', 'Unknown issue')
                },
                "helpUri": "https://bandit.readthedocs.io/en/latest/",
                "properties": {
                    "tags": ["security", "python"]
                }
            }

        # Add result
        results.append({
            "ruleId": rule_id,
            "level": "warning",
            "message": {
                "text": result.get('issue_text', 'Unknown issue')
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": result.get('filename', 'unknown')
                        },
                        "region": {
                            "startLine": result.get('line_number', 1),
                            "startColumn": 1
                        }
                    }
                }
            ]
        })

    # Add rules and results to SARIF
    sarif['runs'][0]['tool']['driver']['rules'] = list(rules.values())
    sarif['runs'][0]['results'] = results

    # Write SARIF file
    try:
        with open(sarif_file, 'w') as f:
            json.dump(sarif, f)
        logger.info(f"Successfully converted {json_file} to {sarif_file}")
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to write SARIF file: {e}")


def ensure_security_reports_dir() -> None:
    """
    Ensure the security-reports directory exists.

    Creates the directory if it doesn't exist and logs the result.
    """
    reports_dir = Path("security-reports")
    if not reports_dir.exists():
        try:
            reports_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created security-reports directory")
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to create security-reports directory: {e}")
            # Try to create in a temp location as fallback
            try:
                import tempfile
                temp_dir = Path(tempfile.gettempdir()) / "security-reports"
                temp_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created security-reports directory in temp location: {temp_dir}")
            except (PermissionError, OSError) as e:
                logger.error(f"Failed to create security-reports directory in temp location: {e}")


def main():
    """Main function."""
    # Ensure security-reports directory exists
    ensure_security_reports_dir()

    # Convert Bandit JSON to SARIF
    json_file = "security-reports/bandit-results.json"
    sarif_file = "security-reports/bandit-results.sarif"
    convert_to_sarif(json_file, sarif_file)

    # Also create bandit-results-ini.sarif for compatibility
    ini_sarif_file = "security-reports/bandit-results-ini.sarif"
    try:
        if os.path.exists(sarif_file):
            shutil.copy(sarif_file, ini_sarif_file)
            logger.info(f"Copied {sarif_file} to {ini_sarif_file}")
        else:
            convert_to_sarif(json_file, ini_sarif_file)
    except (OSError, PermissionError) as e:
        logger.error(f"Failed to create ini SARIF file: {e}")
        # Try to convert directly as fallback
        convert_to_sarif(json_file, ini_sarif_file)


if __name__ == "__main__":
    main()
