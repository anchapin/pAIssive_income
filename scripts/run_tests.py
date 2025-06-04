#!/usr/bin/env python3
"""Run tests and generate reports."""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

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

def run_tests():
    """Run all tests and generate reports."""
    start_time = time.time()
    test_results = {
        "start_time": datetime.now().isoformat(),
        "unit_tests": {},
        "e2e_tests": {},
        "coverage": {},
        "errors": []
    }

    try:
        # Run unit tests
        print("Running unit tests...")
        unit_test_output = run_command(["pnpm", "test:unit"])
        test_results["unit_tests"]["output"] = unit_test_output
        test_results["unit_tests"]["status"] = "passed"

        # Run e2e tests
        print("Running e2e tests...")
        e2e_test_output = run_command(["pnpm", "test:e2e"])
        test_results["e2e_tests"]["output"] = e2e_test_output
        test_results["e2e_tests"]["status"] = "passed"

        # Generate coverage report
        print("Generating coverage report...")
        coverage_output = run_command(["pnpm", "test:coverage"])
        test_results["coverage"]["output"] = coverage_output
        test_results["coverage"]["status"] = "completed"

    except subprocess.CalledProcessError as e:
        test_results["errors"].append(str(e))
        print(f"Error during test execution: {e}")
        sys.exit(1)

    # Calculate duration
    end_time = time.time()
    test_results["duration"] = end_time - start_time
    test_results["end_time"] = datetime.now().isoformat()

    # Save test results
    results_dir = Path("ci-reports")
    results_dir.mkdir(exist_ok=True)

    with open(results_dir / "test-results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    # Upload test results to GitHub
    if os.environ.get("GITHUB_ACTIONS"):
        print("Uploading test results to GitHub...")
        run_command([
            "gh", "api",
            "-X", "POST",
            f"/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs",
            "-F", "name=Test Results",
            "-F", "head_sha=${{ github.sha }}",
            "-F", "status=completed",
            "-F", "conclusion=success",
            "-F", f"output=file://{results_dir}/test-results.json"
        ])

    print("Test execution completed successfully!")
    return test_results

if __name__ == "__main__":
    run_tests()
