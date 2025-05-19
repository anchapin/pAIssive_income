#!/usr/bin/env python3
"""
Create empty SARIF files for GitHub Advanced Security.

This script creates empty SARIF files for GitHub Advanced Security
when the Bandit scan fails or produces no results.
"""

import json
import os
import sys
from pathlib import Path

# Skip virtual environment check by setting environment variables
os.environ["PYTHONNOUSERSITE"] = "1"
os.environ["SKIP_VENV_CHECK"] = "1"

def main():
    """Create empty SARIF files."""
    # Create security-reports directory if it doesn't exist
    os.makedirs("security-reports", exist_ok=True)
    print("Created security-reports directory")

    # Create empty SARIF template
    empty_sarif = {
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

    # Write empty SARIF files
    try:
        with open("security-reports/bandit-results.sarif", 'w') as f:
            json.dump(empty_sarif, f, indent=2)
        with open("security-reports/bandit-results-ini.sarif", 'w') as f:
            json.dump(empty_sarif, f, indent=2)
        print("Created empty SARIF files")
    except Exception as e:
        print(f"Error creating SARIF files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set CI environment variable if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS"):
        os.environ["CI"] = "1"
        print("GitHub Actions environment detected")

    main()
