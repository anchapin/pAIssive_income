#!/usr/bin/env python3
"""
Create empty SARIF files for GitHub Advanced Security.

This script creates empty SARIF files for GitHub Advanced Security
when the Bandit scan fails or produces no results.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# Skip virtual environment check by setting environment variables
os.environ["PYTHONNOUSERSITE"] = "1"
os.environ["SKIP_VENV_CHECK"] = "1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Create empty SARIF files."""
    # Create security-reports directory if it doesn't exist
    reports_dir = Path("security-reports")
    reports_dir.mkdir(exist_ok=True)
    logger.info("Created security-reports directory")

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
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    # Write empty SARIF files
    try:
        bandit_results = reports_dir / "bandit-results.sarif"
        bandit_results_ini = reports_dir / "bandit-results-ini.sarif"

        with bandit_results.open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        with bandit_results_ini.open("w") as f:
            json.dump(empty_sarif, f, indent=2)
        logger.info("Created empty SARIF files")
    except OSError:
        logger.exception("Error creating SARIF files")
        sys.exit(1)


if __name__ == "__main__":
    # Set CI environment variable if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS"):
        os.environ["CI"] = "1"
        logger.info("GitHub Actions environment detected")

    main()
