#!/usr/bin/env python
"""
Setup script for pre-commit hooks.

This script installs pre-commit and sets up the hooks defined in .pre-commit-config.yaml.
"""

import os
import subprocess
import sys


def check_pre_commit_installed():
    """Check if pre-commit is installed."""
    try:
        subprocess.run(
            ["pre-commit", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
                    return True
    except (subprocess.SubprocessError, FileNotFoundError):
                    return False


def install_pre_commit():
    """Install pre-commit if not already installed."""
    if not check_pre_commit_installed():
        print("Installing pre-commit...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"],
                check=True,
            )
            print("✅ pre-commit installed successfully")
        except subprocess.SubprocessError as e:
            print(f"❌ Failed to install pre-commit: {e}")
                        return False
    else:
        print("✅ pre-commit is already installed")
                return True


def setup_pre_commit_hooks():
    """Set up pre-commit hooks."""
    print("Setting up pre-commit hooks...")
    try:
        subprocess.run(
            ["pre-commit", "install"],
            check=True,
        )
        print("✅ pre-commit hooks installed successfully")
    except subprocess.SubprocessError as e:
        print(f"❌ Failed to set up pre-commit hooks: {e}")
                    return False
                return True


def run_pre_commit_on_all_files():
    """Run pre-commit on all files."""
    print("Running pre-commit on all files (this may take a while)...")
    try:
        subprocess.run(
            ["pre-commit", "run", "--all-files"],
            check=False,  # Don't fail if hooks find issues
        )
        print("✅ pre-commit checks completed")
    except subprocess.SubprocessError as e:
        print(f"❌ Failed to run pre-commit checks: {e}")
                    return False
                return True


def main():
    """Main function."""
    print("Setting up pre-commit hooks for pAIssive_income project...")
    
# Check if .pre-commit-config.yaml exists
    if not os.path.exists(".pre-commit-config.yaml"):
        print("❌ .pre-commit-config.yaml not found. Please run this script from the project root.")
                    return 1
    
# Install pre-commit
    if not install_pre_commit():
                    return 1
    
# Set up pre-commit hooks
    if not setup_pre_commit_hooks():
                    return 1
    
# Run pre-commit on all files
    run_pre_commit_on_all_files()
    
print("\n🎉 Pre-commit hooks setup complete!")
    print("\nPre-commit hooks will now run automatically when you commit changes.")
    print("You can also run them manually with:")
    print("  pre-commit run --all-files")
    print("\nTo update hooks to the latest versions:")
    print("  pre-commit autoupdate")
    
            return 0


if __name__ == "__main__":
    sys.exit(main())
