#!/usr/bin/env python3
"""
Create empty SARIF files for GitHub Advanced Security.

This script creates empty SARIF files for GitHub Advanced Security
when the Bandit scan fails or produces no results.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Create empty SARIF files.

    Returns:
        int: Exit code (0 for success, 1 for failure)

    """
    # Create security-reports directory if it doesn't exist
    reports_dir = Path("security-reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Created security-reports directory")

    # Create empty SARIF template
    empty_sarif: Dict[str, Any] = {
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
        bandit_results_path = reports_dir / "bandit-results.sarif"
        with bandit_results_path.open("w") as f:
            json.dump(empty_sarif, f, indent=2)

        bandit_results_ini_path = reports_dir / "bandit-results-ini.sarif"
        with bandit_results_ini_path.open("w") as f:
            json.dump(empty_sarif, f, indent=2)

        logger.info("Created empty SARIF files")
    except (OSError, PermissionError) as e:
        logger.exception("Error creating SARIF files")
        return 1
    else:
        return 0


if __name__ == "__main__":
    # Set CI environment variable if running in GitHub Actions
    if sys.environ.get("GITHUB_ACTIONS"):
        sys.environ["CI"] = "1"
        logger.info("GitHub Actions environment detected")

    sys.exit(main())
