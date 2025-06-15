#!/usr/bin/env python3
"""
PR #166 Workflow Fix Trigger Script.

This script helps trigger and monitor the workflow fixes for PR #166.
It can be used to manually run workflows and check their status.
"""

import subprocess
import sys
import time


def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        return subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=False
        )
    except Exception:
        return None

def check_gh_cli() -> bool:
    """Check if GitHub CLI is available."""
    result = run_command("gh --version")
    return bool(result and result.returncode == 0)

def trigger_workflow(workflow_name, branch=None) -> bool:
    """Trigger a specific workflow."""
    cmd = f"gh workflow run {workflow_name}"
    if branch:
        cmd += f" --ref {branch}"

    result = run_command(cmd)
    if result and result.returncode == 0:
        return True
    if result:
        pass
    return False

def list_workflows() -> bool:
    """List available workflows."""
    result = run_command("gh workflow list")
    return bool(result and result.returncode == 0)

def check_workflow_status() -> bool:
    """Check the status of recent workflow runs."""
    result = run_command("gh run list --limit 10")
    return bool(result and result.returncode == 0)

def trigger_pr_166_fixes(branch=None) -> None:
    """Trigger all PR #166 fix workflows."""
    workflows = [
        "pr-166-comprehensive-fix.yml",
        "test-setup-script-fixed.yml",
        "codeql-simplified.yml"
    ]


    success_count = 0
    for workflow in workflows:
        if trigger_workflow(workflow, branch):
            success_count += 1
        time.sleep(2)  # Small delay between triggers


    if success_count > 0:
        time.sleep(10)
        check_workflow_status()

def main() -> None:
    """Main function."""
    # Check if GitHub CLI is available
    if not check_gh_cli():
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        branch = sys.argv[2] if len(sys.argv) > 2 else None

        if command == "trigger":
            trigger_pr_166_fixes(branch)
        elif command == "list":
            list_workflows()
        elif command == "status":
            check_workflow_status()
        elif command == "help":
            print_help()
        else:
            print_help()
    else:
        # Interactive mode

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            branch = input("Enter branch name (or press Enter for current): ").strip()
            trigger_pr_166_fixes(branch if branch else None)
        elif choice == "2":
            list_workflows()
        elif choice == "3":
            check_workflow_status()
        elif choice == "4":
            sys.exit(0)
        else:
            pass

def print_help() -> None:
    """Print help information."""

if __name__ == "__main__":
    main()
