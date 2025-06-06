#!/usr/bin/env python3
"""
Simple wrapper script for running tests.

This script runs pytest directly without any virtual environment checks.
"""

import os
import subprocess
import sys

# Create security-reports directory
os.makedirs("security-reports", exist_ok=True)
print("Created security-reports directory")

# Set environment variables to bypass virtual environment checks
os.environ["PYTHONNOUSERSITE"] = "1"
os.environ["SKIP_VENV_CHECK"] = "1"

# Set CI environment variable if running in GitHub Actions
if os.environ.get("GITHUB_ACTIONS"):
    os.environ["CI"] = "1"
    print("GitHub Actions environment detected")

# Get command line arguments
args = sys.argv[1:]

# Add default arguments if none provided
if not args:
    args = ["-v"]

# Run pytest directly
try:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        check=False,
        shell=False,
        timeout=3600,  # 1 hour timeout
    )
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running pytest: {e}")
    sys.exit(1)
