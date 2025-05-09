#!/usr/bin/env python3
"""Test script to verify the sarif-tools installation and verification fixes.

This script simulates the GitHub Actions workflow by:
1. Setting up the environment variables
2. Installing sarif-tools
3. Running the verification script
"""

import os
import site
import subprocess
import sys


def setup_environment():
    """Set up the environment variables for sarif-tools."""
    print("Setting up environment variables...")

    # Get Python user site-packages directory
    user_site = site.getusersitepackages()
    print(f"User site-packages: {user_site}")

    # Add user site-packages to PYTHONPATH
    if user_site not in sys.path:
        print(f"Adding user site-packages to sys.path: {user_site}")
        sys.path.append(user_site)

    # Get Python user bin directory
    if os.name == "nt":  # Windows
        user_bin = os.path.join(os.path.dirname(user_site), "Scripts")
    else:
        user_bin = os.path.join(os.path.dirname(user_site), "bin")

    print(f"User bin directory: {user_bin}")

    # Add user binary directory to PATH
    if os.path.exists(user_bin):
        if user_bin not in os.environ.get("PATH", ""):
            os.environ["PATH"] = user_bin + os.pathsep + os.environ.get("PATH", "")
            print(f"Added {user_bin} to PATH")

    # Print environment for debugging
    print(f"Current PATH: {os.environ.get('PATH', '')}")
    print(f"Current sys.path: {sys.path}")


def install_sarif_tools():
    """Install sarif-tools using pip."""
    print("\nInstalling sarif-tools...")

    # Check if we're in a virtual environment
    in_virtualenv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    print(f"In virtual environment: {in_virtualenv}")

    try:
        if in_virtualenv:
            # In a virtualenv, don't use --user flag
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "sarif-tools",
                    "--force-reinstall",
                    "-v",
                ],
                check=True,
            )
        else:
            # Not in a virtualenv, use --user flag
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--user",
                    "sarif-tools",
                    "--force-reinstall",
                    "-v",
                ],
                check=True,
            )
        print("✅ sarif-tools installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install sarif-tools: {e}")
        return False


def run_verification_script():
    """Run the verify_sarif_tools.py script."""
    print("\nRunning verification script...")

    try:
        subprocess.run(
            [sys.executable, "verify_sarif_tools.py"],
            check=True,
        )
        print("✅ Verification script completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification script failed: {e}")
        return False


def main():
    """Run the test script."""
    print("=" * 80)
    print("Testing sarif-tools installation and verification fixes")
    print("=" * 80)

    # Set up environment
    setup_environment()

    # Install sarif-tools
    if not install_sarif_tools():
        print("❌ Failed to install sarif-tools")
        sys.exit(1)

    # Run verification script
    if not run_verification_script():
        print("❌ Verification script failed")
        sys.exit(1)

    print("\n✅ Test completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
