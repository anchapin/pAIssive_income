"""
run_github_actions_locally.py - Script to run GitHub Actions workflows locally using Act.

This script provides a convenient way to run GitHub Actions workflows locally
for testing purposes before pushing changes to the repository.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def list_workflows():
    """List all available GitHub Actions workflows."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("No workflows directory found at .github/workflows")
        return []

    workflows = [f.name for f in workflows_dir.glob("*.yml")]
    return workflows


def run_workflow(
    workflow,
    job=None,
    platform="ubuntu-latest",
    file=None,
    test_path=None,
    lint_only=False,
    test_only=False,
):
    """Run a GitHub Actions workflow locally using Act."""
    # Check if Act is installed
    act_path = "./bin/act" if os.path.exists("./bin/act") else "act"

    try:
        # Build the command
        cmd = [act_path]

        # Add job if specified:
        if job:
            cmd.extend(["-j", job])

        # Add workflow
        cmd.extend(["-W", workflow])

        # Add platform
        cmd.extend(["-P", platform])

        # Add environment variables for inputs:
        env = os.environ.copy()

        if file:
            env["INPUT_SPECIFIC_FILE"] = file

        if test_path:
            env["INPUT_TEST_PATH"] = test_path

        if lint_only:
            env["INPUT_LINT_ONLY"] = "true"

        if test_only:
            env["INPUT_TEST_ONLY"] = "true"

        # Run the command
        print(f"Running command: {' '.join(cmd)}")
        print(
            f"With environment variables: specific_file={file}, test_path={test_path}, "
            f"lint_only={lint_only}, test_only={test_only}"
        )

        result = subprocess.run(cmd, env=env)
        return result.returncode

    except FileNotFoundError:
        print("Error: Act not found. Please install Act or ensure it's in your PATH.")
        print(
            "You can install Act using: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
        )
        return 1


def main():
    """Main function to parse arguments and run the workflow."""
    parser = argparse.ArgumentParser(
        description="Run GitHub Actions workflows locally using Act"
    )

    parser.add_argument("--list", action="store_true", help="List available workflows")
    parser.add_argument(
        "--workflow", help="Workflow file to run (e.g., .github/workflows/ci.yml)"
    )
    parser.add_argument("--job", help="Specific job to run")
    parser.add_argument(
        "--platform",
        default="ubuntu-latest",
        help="Platform to run on (e.g., ubuntu-latest, windows-latest)",
    )
    parser.add_argument("--file", help="Specific file to lint or test")
    parser.add_argument("--test-path", help="Path to test directory or file")
    parser.add_argument(
        "--lint-only", action="store_true", help="Run only linting checks"
    )
    parser.add_argument("--test-only", action="store_true", help="Run only tests")

    args = parser.parse_args()

    if args.list:
        workflows = list_workflows()
        if workflows:
            print("Available workflows:")
            for workflow in workflows:
                print(f"  - {workflow}")
        return 0

    if not args.workflow:
        parser.print_help()
        return 1

    return run_workflow(
        workflow=args.workflow,
        job=args.job,
        platform=args.platform,
        file=args.file,
        test_path=args.test_path,
        lint_only=args.lint_only,
        test_only=args.test_only,
    )


if __name__ == "__main__":
    sys.exit(main())
