#!/usr/bin/env python3
"""Test script to verify Bandit configuration."""

import os
import subprocess
import sys
from pathlib import Path

def test_bandit_config():
    """Test the Bandit configuration files."""
    print("Testing Bandit configuration...")

    # Check if at least one of bandit.yaml or .bandit exists
    bandit_yaml = Path("bandit.yaml")
    bandit_ini = Path(".bandit")

    if not bandit_yaml.exists() and not bandit_ini.exists():
        print("Error: Neither bandit.yaml nor .bandit found")
        return False
    # Run bandit with the available configuration
    try:
        print("Running bandit help command...")
        result = subprocess.run(
            ["bandit", "--help"],
            check=False,
            capture_output=True,
            text=True
        )
        print(f"Bandit help exit code: {result.returncode}")

        # Create security-reports directory if it doesn't exist
        os.makedirs("security-reports", exist_ok=True)
        # Test with bandit.yaml if it exists
        if bandit_yaml.exists():
            print("Running bandit with bandit.yaml...")
            result = subprocess.run(
                ["bandit", "-r", ".", "-c", "bandit.yaml", "--exclude", ".venv,node_modules,tests", "-o", "security-reports/test-results.txt", "-f", "txt"],
                check=False,
                capture_output=True,
                text=True
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
            result = subprocess.run(
                ["bandit", "-r", ".", "-c", ".bandit", "--exclude", ".venv,node_modules,tests", "-o", "security-reports/test-results-ini.txt", "-f", "txt"],
                check=False,
                capture_output=True,
                text=True
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
    try:
        subprocess.run(["bandit", "--version"], check=False, capture_output=True)
    except FileNotFoundError:
        print("Installing bandit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "bandit"], check=False)

    success = test_bandit_config()
    if success:
        print("Bandit configuration test passed!")
        sys.exit(0)
    else:
        print("Bandit configuration test failed!")
        sys.exit(1)