#!/usr/bin/env python3
"""
Generate Bandit Configuration Files for GitHub Actions.

This script generates Bandit configuration files for all platforms and run IDs.
It is used by the GitHub Actions workflow to create the necessary configuration
files for Bandit security scanning.

Usage:
    python generate_bandit_config.py [run_id]
"""

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define the base configuration template
CONFIG_TEMPLATE = """# Bandit Configuration for {platform} (Run ID: {run_id})
# This configuration is used by GitHub Advanced Security for Bandit scanning on {platform}

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

# Set the output file for GitHub Advanced Security
output_file: security-reports/bandit-results.sarif

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM

# Per-test configurations
any_other_function_with_shell_equals_true:
  no_shell: [os.execl, os.execle, os.execlp, os.execlpe, os.execv, os.execve, os.execvp,
    os.execvpe, os.spawnl, os.spawnle, os.spawnlp, os.spawnlpe, os.spawnv, os.spawnve,
    os.spawnvp, os.spawnvpe, os.startfile]
  shell: [os.system, os.popen, os.popen2, os.popen3, os.popen4, popen2.popen2, popen2.popen3,
    popen2.popen4, popen2.Popen3, popen2.Popen4, commands.getoutput, commands.getstatusoutput]
  subprocess: [subprocess.Popen, subprocess.call, subprocess.check_call, subprocess.check_output,
    subprocess.run]
"""


def main() -> None:
    """Generate Bandit configuration files for all platforms and run IDs."""
    # Get the run ID from the command line arguments
    run_id = "default"
    if len(sys.argv) > 1:
        run_id = sys.argv[1]

    logger.info("Generating Bandit configuration files for run ID: %s", run_id)

    # Create the .github/bandit directory if it doesn't exist
    bandit_dir = Path(".github/bandit")
    bandit_dir.mkdir(parents=True, exist_ok=True)

    # Create the security-reports directory if it doesn't exist
    security_reports_dir = Path("security-reports")
    security_reports_dir.mkdir(parents=True, exist_ok=True)

    # Generate configuration files for each platform
    for platform in ["Windows", "Linux", "macOS"]:
        config_content = CONFIG_TEMPLATE.format(platform=platform, run_id=run_id)
        config_file = bandit_dir / f"bandit-config-{platform.lower()}-{run_id}.yaml"

        with config_file.open("w") as f:
            f.write(config_content)

        logger.info("Generated %s", config_file)

    # Also create generic platform configuration files
    for platform in ["Windows", "Linux", "macOS"]:
        config_content = CONFIG_TEMPLATE.format(platform=platform, run_id="generic")
        config_file = bandit_dir / f"bandit-config-{platform.lower()}.yaml"

        with config_file.open("w") as f:
            f.write(config_content)

        logger.info("Generated %s", config_file)

    logger.info("Bandit configuration files generated successfully")


if __name__ == "__main__":
    main()
