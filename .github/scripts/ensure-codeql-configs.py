#!/usr/bin/env python3
"""
Script to ensure CodeQL configuration files exist.
This script creates the necessary CodeQL configuration files for security scanning.
"""

import json
import os


def ensure_directory(directory):
    """Ensure the directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")


def create_codeql_config(filename, config_name, os_name=None):
    """Create a CodeQL configuration file with the given parameters."""
    config = {
        "name": config_name,
        "queries": [
            {"uses": "security-and-quality"},
            {"uses": "security-extended"},
            {"uses": "security"},
        ],
        "disable-default-queries": False,
        "paths-ignore": [
            "node_modules",
            "**/*.test.js",
            "**/*.spec.js",
            "**/*.test.py",
            "**/*.spec.py",
            "tests/**",
            "test_mem0_integration.py",
        ],
    }

    if os_name:
        config["os"] = os_name

    with open(filename, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Created CodeQL configuration file: {filename}")


def main():
    """Main function to create CodeQL configuration files."""
    # Ensure the .github/codeql directory exists
    codeql_dir = os.path.join(".github", "codeql")
    ensure_directory(codeql_dir)

    # Create the Ubuntu configuration
    ubuntu_config = os.path.join(codeql_dir, "security-os-ubuntu.yml")
    create_codeql_config(
        ubuntu_config, "CodeQL Configuration for Ubuntu", "ubuntu-latest"
    )

    # Create the macOS configuration
    macos_config = os.path.join(codeql_dir, "security-os-macos.yml")
    create_codeql_config(macos_config, "CodeQL Configuration for macOS", "macos-latest")

    # Create the unified configuration
    unified_config = os.path.join(codeql_dir, "security-os-config.yml")
    create_codeql_config(unified_config, "Unified CodeQL Configuration")

    print("All CodeQL configuration files created successfully.")


if __name__ == "__main__":
    main()
