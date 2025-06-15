#!/usr/bin/env python3
"""
Manual workflow trigger script for PR #166.

This script helps trigger workflows that don't run automatically
when PRs are created by GitHub Actions.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30, check=False
        )
        if result.returncode == 0:
            if result.stdout.strip():
                pass
            return True
        if result.stderr.strip():
            pass
        return False
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def trigger_workflows(branch_name: Optional[str] = None) -> None:
    """Trigger the main workflows for the current branch."""
    if not branch_name:
        # Try to get current branch
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True, check=False
        )
        branch_name = result.stdout.strip() if result.returncode == 0 else "main"


    workflows = [
        ("consolidated-ci-cd.yml", "Consolidated CI/CD"),
        ("frontend-vitest.yml", "Frontend Vitest Tests"),
        ("frontend-e2e.yml", "Frontend E2E Tests"),
        ("codeql.yml", "CodeQL Analysis"),
        ("pr-166-fixes.yml", "PR 166 Fixes"),
    ]

    success_count = 0
    len(workflows)

    for workflow_file, description in workflows:
        command = f"gh workflow run {workflow_file} --ref {branch_name}"
        if run_command(command, f"Triggering {description}"):
            success_count += 1
        time.sleep(2)  # Small delay between triggers


    if success_count > 0:
        pass


def check_prerequisites() -> bool:
    """Check if required tools are available."""
    # Check if gh CLI is available
    if not run_command("gh --version", "GitHub CLI availability"):
        return False

    # Check if authenticated
    if not run_command("gh auth status", "GitHub CLI authentication"):
        return False

    # Check if in a git repository
    return Path(".git").exists()


def main() -> None:
    """Main function."""
    if not check_prerequisites():
        sys.exit(1)

    branch_name = None
    if len(sys.argv) > 1:
        branch_name = sys.argv[1]

    trigger_workflows(branch_name)



if __name__ == "__main__":
    main()
