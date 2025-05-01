"""
Script to run tests locally with the correct Python path.
"""

import os
import sys
import subprocess
import argparse

def main():
    """Run tests with the correct Python path."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run tests locally with the correct Python path.")
    parser.add_argument("--test-path", default="tests", help="Path to the tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    args = parser.parse_args()

    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Add the current directory to the Python path
    sys.path.insert(0, current_dir)

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = current_dir

    # Build the command
    cmd = ["python", "-m", "pytest", args.test_path, "--import-mode=importlib"]

    if args.verbose:
        cmd.append("-v")

    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])

    # Run the tests
    print(f"Running tests: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        env=env,
        check=False,
    )

    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
