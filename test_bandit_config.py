#!/usr/bin/env python3
"""Test script to verify Bandit configuration."""

import os
import subprocess
import sys
from pathlib import Path

def test_bandit_config():
    """Test the Bandit configuration files."""
    print("Testing Bandit configuration...")
    
    # Check if bandit.yaml exists
    bandit_yaml = Path("bandit.yaml")
    if not bandit_yaml.exists():
        print("Error: bandit.yaml not found")
        return False
    
    # Check if .bandit exists
    bandit_ini = Path(".bandit")
    if not bandit_ini.exists():
        print("Error: .bandit not found")
        return False
    
    # Run bandit with the bandit.yaml configuration
    try:
        print("Running bandit with bandit.yaml...")
        result = subprocess.run(
            ["bandit", "--help"],
            check=False,
            capture_output=True,
            text=True
        )
        print(f"Bandit help exit code: {result.returncode}")
        
        # Create security-reports directory if it doesn't exist
        os.makedirs("security-reports", exist_ok=True)
        
        # Run bandit with the bandit.yaml configuration
        result = subprocess.run(
            ["bandit", "-r", ".", "-c", "bandit.yaml", "--exclude", ".venv,node_modules,tests", "-o", "security-reports/test-results.txt", "-f", "txt"],
            check=False,
            capture_output=True,
            text=True
        )
        print(f"Bandit with bandit.yaml exit code: {result.returncode}")
        if result.returncode != 0:
            print("Error output:")
            print(result.stderr)
            return False
        
        # Run bandit with the .bandit configuration
        result = subprocess.run(
            ["bandit", "-r", ".", "-c", ".bandit", "--exclude", ".venv,node_modules,tests", "-o", "security-reports/test-results-ini.txt", "-f", "txt"],
            check=False,
            capture_output=True,
            text=True
        )
        print(f"Bandit with .bandit exit code: {result.returncode}")
        if result.returncode != 0:
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
