"""
Script to run GitHub Actions locally using Act.
"""

import argparse
import subprocess
import sys


def main():
    """Run GitHub Actions locally using Act."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run GitHub Actions locally using Act."
    )
    parser.add_argument(
        "--workflow",
        default=".github/workflows/simple-lint.yml",
        help="Path to the workflow file",
    )
    parser.add_argument("--job", default="lint", help="Job to run")
    parser.add_argument(
        "--platform",
        default="ubuntu-latest=node:16-buster",
        help="Platform to use",
    )
    parser.add_argument(
        "--file",
        help="Specific file to lint (only works with simple-lint.yml)",
    )
    args = parser.parse_args()

    # Build the command
    cmd = ["act", "-j", args.job, "-W", args.workflow]

    if args.platform:
        cmd.extend(["-P", args.platform])

    # If a specific file is provided and we're using the simple-lint workflow,
    # modify the workflow to only lint that file
    if args.file and "simple-lint.yml" in args.workflow:
        cmd.extend(["--env", f"FILE={args.file}"])

    # Run Act
    print(f"Running Act: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        check=False,
    )

    # Return the exit code
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
