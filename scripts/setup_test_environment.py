#!/usr/bin/env python3
"""Set up the test environment for CI/CD."""

import json
import os
import platform
import subprocess
from pathlib import Path


def create_directory(path) -> None:
    """Create a directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {path}")

def create_dummy_file(path, content="") -> None:
    """Create a dummy file if it doesn't exist."""
    if not Path(path).exists():
        Path(path).write_text(content)
        print(f"Created dummy file: {path}")

def setup_test_environment() -> None:
    """Set up the test environment."""
    # Create necessary directories
    directories = [
        "tests/unit",
        "tests/e2e",
        "tests/mock-api",
        "tests/__mocks__",
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
        create_directory(directory)

    # Create dummy test files
    dummy_files = {
        "tests/unit/dummy.test.js": """
import { describe, it, expect } from 'vitest';

describe('Dummy test', () => {
  it('should pass', () => {
    expect(true).toBe(true);
  });
});
""",
        "tests/e2e/dummy.spec.js": """
import { test, expect } from '@playwright/test';

test('dummy test', async ({ page }) => {
  expect(true).toBe(true);
});
""",
        "tests/mock-api/dummy.test.js": """
import { describe, it, expect } from 'vitest';

describe('Dummy mock API test', () => {
  it('should pass', () => {
    expect(true).toBe(true);
  });
});
""",
        "tests/__mocks__/dummy.js": """
export const dummyMock = {
  mockFunction: () => true
};
"""
    }

    for file_path, content in dummy_files.items():
        create_dummy_file(file_path, content)

    # Generate environment report
    env_report = {
        "date": subprocess.check_output(["date"]).decode().strip(),
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "node_version": subprocess.check_output(["node", "--version"]).decode().strip(),
        "npm_version": subprocess.check_output(["npm", "--version"]).decode().strip(),
        "pnpm_version": subprocess.check_output(["pnpm", "--version"]).decode().strip(),
        "runner_os": os.environ.get("RUNNER_OS", "unknown"),
        "workspace": os.environ.get("GITHUB_WORKSPACE", "unknown"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "unknown"),
        "ref": os.environ.get("GITHUB_REF", "unknown"),
        "sha": os.environ.get("GITHUB_SHA", "unknown")
    }

    # Write environment report
    with open("ci-reports/test-environment-report.json", "w") as f:
        json.dump(env_report, f, indent=2)

    print("Test environment setup completed successfully!")

if __name__ == "__main__":
    setup_test_environment()
