#!/usr/bin/env python3
"""Fix the PR trigger for GitHub Actions."""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        raise

def fix_pr_trigger():
    """Fix the PR trigger for GitHub Actions."""
    # Get PR information
    pr_number = os.environ.get("GITHUB_PR_NUMBER")
    if not pr_number:
        print("No PR number found in environment variables")
        sys.exit(1)

    # Get PR details
    pr_details = run_command([
        "gh", "api",
        f"/repos/{os.environ['GITHUB_REPOSITORY']}/pulls/{pr_number}"
    ])
    pr_data = json.loads(pr_details)

    # Update PR trigger
    trigger_config = {
        "trigger": {
            "pull_request": {
                "branches": ["main"],
                "types": ["opened", "synchronize", "reopened"]
            }
        }
    }

    # Write trigger configuration
    config_dir = Path(".github/workflows")
    config_dir.mkdir(parents=True, exist_ok=True)

    with open(config_dir / "pr-trigger-config.json", "w") as f:
        json.dump(trigger_config, f, indent=2)

    print("PR trigger configuration updated successfully!")

if __name__ == "__main__":
    fix_pr_trigger()
