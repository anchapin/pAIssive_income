#!/usr/bin/env python
"""
Script to install the MCP SDK from GitHub.
This script is used by the CI/CD pipeline to install the MCP SDK.
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None


def install_mcp_sdk():
    """Install the MCP SDK from GitHub."""
    print("Installing MCP SDK from GitHub...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Clone the repository
        print(f"Cloning MCP SDK repository to {temp_dir}...")
        result = run_command(
            "git clone --depth 1 https://github.com/modelcontextprotocol/python-sdk.git .",
            cwd=temp_dir,
        )
        
        if result is None:
            print("Failed to clone MCP SDK repository")
            return False
        
        # Install the package
        print("Installing MCP SDK...")
        result = run_command(
            f"{sys.executable} -m pip install -e .",
            cwd=temp_dir,
        )
        
        if result is None:
            print("Failed to install MCP SDK")
            return False
        
        print("MCP SDK installed successfully")
        return True
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Main entry point."""
    success = install_mcp_sdk()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
