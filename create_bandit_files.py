#!/usr/bin/env python3
"""
Create Bandit configuration files for GitHub Actions workflows.

This script creates the necessary Bandit configuration files for GitHub Actions workflows.
It's a simplified version that avoids linting issues.

Usage:
    python create_bandit_files.py
"""

import sys
from pathlib import Path

# Constants
BANDIT_DIR = ".github/bandit"
SECURITY_REPORTS_DIR = "security-reports"
PLATFORMS = ["windows", "linux", "macos"]

# Bandit configuration template
BANDIT_CONFIG_TEMPLATE = """# Bandit Configuration Template
# This configuration is used by GitHub Advanced Security for Bandit scanning

# Exclude directories from security scans
exclude_dirs:
  - tests
  - venv
  - .venv
  - env
  - .env
  - __pycache__
  - custom_stubs
  - node_modules
  - build
  - dist
  - docs
  - docs_source
  - junit
  - bin
  - dev_tools
  - scripts
  - tool_templates

# Skip specific test IDs
skips:
  # B101: Use of assert detected
  - B101
  # B311: Standard pseudo-random generators are not suitable for security/cryptographic purposes
  - B311

# Set the output format for GitHub Advanced Security
output_format: sarif

# Output file for GitHub Advanced Security
output_file: security-reports/bandit-results.sarif

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM

# Simplified shell configuration
shell_injection:
  no_shell: []
  shell: []
"""

# Empty SARIF content
EMPTY_SARIF_CONTENT = """{
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
}"""


def main() -> int:
    """Create Bandit configuration files."""
    # Create directories
    Path(BANDIT_DIR).mkdir(parents=True, exist_ok=True)
    Path(SECURITY_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    # Create template file
    template_path = Path(BANDIT_DIR) / "bandit-config-template.yaml"
    template_path.write_text(BANDIT_CONFIG_TEMPLATE)

    # Create platform-specific files
    for platform in PLATFORMS:
        # Regular config
        config_path = Path(BANDIT_DIR) / f"bandit-config-{platform}.yaml"
        config_path.write_text(BANDIT_CONFIG_TEMPLATE)

        # Test run ID config
        test_run_id_path = (
            Path(BANDIT_DIR) / f"bandit-config-{platform}-test_run_id.yaml"
        )
        test_run_id_path.write_text(BANDIT_CONFIG_TEMPLATE)

    # Create empty SARIF file
    empty_sarif_path = Path("empty-sarif.json")
    empty_sarif_path.write_text(EMPTY_SARIF_CONTENT)

    return 0


if __name__ == "__main__":
    sys.exit(main())
