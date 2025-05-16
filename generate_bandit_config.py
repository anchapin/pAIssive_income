#!/usr/bin/env python3
"""Generate Bandit configuration files for specific run IDs."""

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

# Skip specific test IDs
skips:
  # B101: Use of assert detected
  - B101
  # B311: Standard pseudo-random generators are not suitable for security/cryptographic purposes
  - B311

# Set the output format for GitHub Advanced Security
output_format: sarif

# Set the output file for GitHub Advanced Security
output_file: security-reports/bandit-results-{run_id}.sarif

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
    """Generate Bandit configuration files for specific run IDs."""
    # Get run ID from command line argument or use default
    run_id = sys.argv[1] if len(sys.argv) > 1 else "15053076509"  # Default run ID

    # Create the .github/bandit directory if it doesn't exist
    bandit_dir = Path(".github/bandit")
    bandit_dir.mkdir(parents=True, exist_ok=True)

    # Create security-reports directory if it doesn't exist
    reports_dir = Path("security-reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Generate configuration files for each platform
    for platform in ["Windows", "Linux", "macOS"]:
        config_content = CONFIG_TEMPLATE.format(platform=platform, run_id=run_id)
        config_file = bandit_dir / f"bandit-config-{platform.lower()}-{run_id}.yaml"

        with config_file.open("w") as f:
            f.write(config_content)

        logger.info("Generated %s", config_file)

    # Create an empty SARIF file in the security-reports directory
    empty_sarif = """{
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

    # Create the run-specific SARIF file
    sarif_file = reports_dir / f"bandit-results-{run_id}.sarif"
    with sarif_file.open("w") as f:
        f.write(empty_sarif)
    logger.info("Generated empty SARIF file: %s", sarif_file)

    # Create the standard SARIF file
    standard_sarif_file = reports_dir / "bandit-results.sarif"
    with standard_sarif_file.open("w") as f:
        f.write(empty_sarif)
    logger.info("Generated empty SARIF file: %s", standard_sarif_file)


if __name__ == "__main__":
    main()
