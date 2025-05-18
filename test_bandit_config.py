#!/usr/bin/env python3
"""Test script to verify Bandit configuration."""

import os
import subprocess  # nosec B404 - subprocess is used with proper security controls
import sys
import shutil
from pathlib import Path

# Find the full path to the bandit executable
def get_bandit_path() -> str:
    """Get the full path to the bandit executable."""
    bandit_path = shutil.which("bandit")
    if not bandit_path:
        # If bandit is not in PATH, default to just "bandit"
        # It will be installed later if needed
        return "bandit"
    return bandit_path

def test_bandit_config():
    """Test the Bandit configuration files."""
    print("Testing Bandit configuration...")

    # Check if at least one of bandit.yaml or .bandit exists
    bandit_yaml = Path("bandit.yaml")
    bandit_ini = Path(".bandit")

    if not bandit_yaml.exists() and not bandit_ini.exists():
        print("Error: Neither bandit.yaml nor .bandit found")
        return False

    # Get the full path to bandit
    bandit_path = get_bandit_path()

    # Run bandit with the available configuration
    try:
        print("Running bandit help command...")
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        result = subprocess.run(  # nosec B603
            [bandit_path, "--help"],
            check=False,
            capture_output=True,
            text=True,
            shell=False  # Explicitly set shell=False for security
        )
        print(f"Bandit help exit code: {result.returncode}")

        # Create security-reports directory if it doesn't exist
        os.makedirs("security-reports", exist_ok=True)

        # Test with bandit.yaml if it exists
        if bandit_yaml.exists():
            print("Running bandit with bandit.yaml...")
            # nosec B603 - subprocess call is used with shell=False and validated arguments
            result = subprocess.run(  # nosec B603
                [bandit_path, "-r", ".", "-c", "bandit.yaml", "--exclude", ".venv,node_modules,tests",
                 "-o", "security-reports/test-results.txt", "-f", "txt"],
                check=False,
                capture_output=True,
                text=True,
                shell=False  # Explicitly set shell=False for security
            )
            print(f"Bandit with bandit.yaml exit code: {result.returncode}")
            # Bandit returns non-zero exit code for warnings, but we can still consider this a success
            # as long as the output file was created
            if result.returncode != 0:
                print("Warning: Bandit returned non-zero exit code, but this might be due to warnings.")
                print("Checking if output file was created...")
                if Path("security-reports/test-results.txt").exists():
                    print("Output file exists, continuing...")
                else:
                    print("Error: Output file was not created.")
                    print("Error output:")
                    print(result.stderr)
                    return False

        # Test with .bandit if it exists
        if bandit_ini.exists():
            print("Running bandit with .bandit...")
            # nosec B603 - subprocess call is used with shell=False and validated arguments
            result = subprocess.run(  # nosec B603
                [bandit_path, "-r", ".", "-c", ".bandit", "--exclude", ".venv,node_modules,tests",
                 "-o", "security-reports/test-results-ini.txt", "-f", "txt"],
                check=False,
                capture_output=True,
                text=True,
                shell=False  # Explicitly set shell=False for security
            )
            print(f"Bandit with .bandit exit code: {result.returncode}")
            # Bandit returns non-zero exit code for warnings, but we can still consider this a success
            # as long as the output file was created
            if result.returncode != 0:
                print("Warning: Bandit returned non-zero exit code, but this might be due to warnings.")
                print("Checking if output file was created...")
                if Path("security-reports/test-results-ini.txt").exists():
                    print("Output file exists, continuing...")
                else:
                    print("Error: Output file was not created.")
                    print("Error output:")
                    print(result.stderr)
                    return False
        return True
    except Exception as e:
        print(f"Error running bandit: {e}")
        return False

if __name__ == "__main__":
    # Install bandit if not already installed
    bandit_path = get_bandit_path()
    try:
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        subprocess.run(  # nosec B603
            [bandit_path, "--version"],
            check=False,
            capture_output=True,
            shell=False  # Explicitly set shell=False for security
        )
    except FileNotFoundError:
        print("Installing bandit...")
        # nosec B603 - subprocess call is used with shell=False and validated arguments
        subprocess.run(  # nosec B603
            [sys.executable, "-m", "pip", "install", "bandit"],
            check=False,
            shell=False  # Explicitly set shell=False for security
        )

    success = test_bandit_config()
    if success:
        print("Bandit configuration test passed!")
        sys.exit(0)
    else:
        print("Bandit configuration test failed!")
        sys.exit(1)