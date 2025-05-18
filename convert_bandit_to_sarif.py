#!/usr/bin/env python3
"""
Convert Bandit JSON output to SARIF format.

This script reads the Bandit JSON output file and converts it to SARIF format
for GitHub Advanced Security.
"""

import json
import os
from pathlib import Path


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
        print(f"JSON file {json_file} does not exist or is empty. Creating empty SARIF file.")
        with open(sarif_file, 'w') as f:
            json.dump(sarif, f)
        return

    # Read the Bandit JSON output
    try:
        with open(json_file, 'r') as f:
            bandit_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading JSON file: {e}. Creating empty SARIF file.")
        with open(sarif_file, 'w') as f:
            json.dump(sarif, f)
        return

    # Check if there are any results
    if not bandit_data.get('results'):
        print("No results found in Bandit output. Creating empty SARIF file.")
        with open(sarif_file, 'w') as f:
            json.dump(sarif, f)
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
    with open(sarif_file, 'w') as f:
        json.dump(sarif, f)

    print(f"Successfully converted {json_file} to {sarif_file}")


def main():
    """Main function."""
    # Ensure security-reports directory exists
    reports_dir = Path("security-reports")
    if not reports_dir.exists():
        reports_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created security-reports directory")

    # Convert Bandit JSON to SARIF
    json_file = "security-reports/bandit-results.json"
    sarif_file = "security-reports/bandit-results.sarif"
    convert_to_sarif(json_file, sarif_file)

    # Also create bandit-results-ini.sarif for compatibility
    ini_sarif_file = "security-reports/bandit-results-ini.sarif"
    if os.path.exists(sarif_file):
        shutil.copy(sarif_file, ini_sarif_file)
        print(f"Copied {sarif_file} to {ini_sarif_file}")
    else:
        convert_to_sarif(json_file, ini_sarif_file)


if __name__ == "__main__":
    import shutil
    main()
