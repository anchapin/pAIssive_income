#!/usr/bin/env python3
"""Set up the CI environment."""

import json
import os
import platform
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

def setup_ci_environment() -> None:
    """Set up the CI environment."""
    # Create necessary directories
    directories = [
        "ci-reports",
        "ci-artifacts",
        "ci-logs",
        "ci-temp",
        "ci-cache",
        "test-results/github",
        "logs",
        "coverage",
        "playwright-report"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

    # Install dependencies
    print("Installing dependencies...")
    run_command(["pnpm", "install"])

    # Install Playwright browsers
    print("Installing Playwright browsers...")
    run_command(["pnpm", "playwright", "install"])

    # Generate environment report
    env_report = {
        "date": run_command(["date"]).strip(),
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "node_version": run_command(["node", "--version"]).strip(),
        "npm_version": run_command(["npm", "--version"]).strip(),
        "pnpm_version": run_command(["pnpm", "--version"]).strip(),
        "runner_os": os.environ.get("RUNNER_OS", "unknown"),
        "workspace": os.environ.get("GITHUB_WORKSPACE", "unknown"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "unknown"),
        "ref": os.environ.get("GITHUB_REF", "unknown"),
        "sha": os.environ.get("GITHUB_SHA", "unknown")
    }

    # Write environment report
    with open("ci-reports/ci-environment-report.json", "w") as f:
        json.dump(env_report, f, indent=2)

    # Set up environment variables
    env_vars = {
        "CI": "true",
        "NODE_ENV": "test",
        "PLAYWRIGHT_BROWSERS_PATH": "0",
        "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "0",
        "PLAYWRIGHT_SKIP_VALIDATION": "1",
        "VITEST_SEGFAULT_RETRY": "3",
        "VITEST_MAX_THREADS": "4",
        "VITEST_MIN_THREADS": "2",
        "VITEST_POOL": "threads",
        "VITEST_POOL_OPTIONS": "threads.singleThread:true",
        "VITEST_RETRY": "3",
        "VITEST_TIMEOUT": "30000",
        "VITEST_UPDATE": "false",
        "VITEST_WATCH": "false"
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set environment variable: {key}={value}")

    print("CI environment setup completed successfully!")

if __name__ == "__main__":
    setup_ci_environment()
