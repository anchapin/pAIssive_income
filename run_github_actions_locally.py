
#!/usr/bin/env python
"""
Script to run GitHub Actions workflows locally using Act.
This script helps verify that GitHub Actions workflows will pass before pushing to the repository.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def list_workflows():
    """List all available workflows in the .github/workflows directory."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("❌ No .github/workflows directory found.")
            return []

    workflows = [f for f in workflows_dir.glob("*.yml")]
        return workflows


def run_workflow(workflow_file, job=None, platform="ubuntu-latest"):
    """Run a specific workflow using Act."""
    # Check for Windows-style path
    act_path_win = Path("bin/act.exe")
    act_path = Path("bin/act")

    if act_path_win.exists():
        act_path = act_path_win
    elif not act_path.exists():
        print("❌ Act binary not found in bin/act or bin/act.exe. Please install Act first.")
        print("   Run: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash")
            return False

    command = [str(act_path)]

    # Add job parameter if specified
    if job:
        command.extend(["-j", job])

    # Add workflow file parameter
    command.extend(["-W", str(workflow_file)])

    # Add platform parameter
    command.extend(["-P", platform])

    print(f"\n🚀 Running workflow: {workflow_file}")
    print(f"   Command: {' '.join(command)}")

    try:
        subprocess.run(command, check=True)
        print(f"\n✅ Workflow {workflow_file} completed successfully!")
            return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Workflow {workflow_file} failed with exit code {e.returncode}")
            return False


def main():
    """Main function to parse args and run the script."""
    parser = argparse.ArgumentParser(description="Run GitHub Actions workflows locally using Act.")
    parser.add_argument(
        "--workflow", "-w",
        help="Specific workflow file to run (e.g., 'local-test.yml')",
    )
    parser.add_argument(
        "--job", "-j",
        help="Specific job to run within the workflow",
    )
    parser.add_argument(
        "--platform", "-p",
        default="ubuntu-latest",
        help="Platform to run the workflow on (default: ubuntu-latest)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available workflows",
    )

    args = parser.parse_args()

    if args.list:
        workflows = list_workflows()
        if workflows:
            print("\nAvailable workflows:")
            for i, workflow in enumerate(workflows, 1):
                print(f"{i}. {workflow}")
            return 0

    if args.workflow:
        workflow_path = Path(".github/workflows") / args.workflow
        if not workflow_path.exists():
            print(f"❌ Workflow file {workflow_path} not found.")
                return 1

        success = run_workflow(workflow_path, args.job, args.platform)
            return 0 if success else 1
    else:
        print("Please specify a workflow file with --workflow or list available workflows with --list")
            return 1


if __name__ == "__main__":
    sys.exit(main())