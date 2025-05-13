#!/usr/bin/env python3
"""
Generate Bandit configuration files for GitHub Advanced Security.

This script generates Bandit configuration files for GitHub Advanced Security
for different platforms and run IDs.
"""

import logging
import os

# Define the platforms and run IDs
PLATFORMS = ["Linux", "Windows", "macOS"]
RUN_IDS = [
    "14974236301",
    "14976101411",
    "14977094424",
    "14977626158",
    "14978521232",
    "14987452007",
    "14988964552",
]

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
    """Generate Bandit configuration files."""
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create the .github/bandit directory if it doesn't exist
    os.makedirs(".github/bandit", exist_ok=True)

    # Generate configuration files for each platform and run ID
    for platform in PLATFORMS:
        for run_id in RUN_IDS:
            config_content = CONFIG_TEMPLATE.format(platform=platform, run_id=run_id)
            config_file = (
                f".github/bandit/bandit-config-{platform.lower()}-{run_id}.yaml"
            )

            with open(config_file, "w") as f:
                f.write(config_content)

            # Log the generated file instead of using print
            logging.info(f"Generated {config_file}")


if __name__ == "__main__":
    main()
