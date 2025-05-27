#!/usr/bin/env python3
"""
Script to ensure CodeQL configuration files exist.

This script creates the necessary CodeQL configuration files for security scanning.
"""

from __future__ import annotations

import json
from pathlib import Path


def ensure_directory(directory: str) -> None:
    """Ensure the directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def create_codeql_config(filename: str, config_name: str, os_name: str | None = None) -> None:
    """Create a CodeQL configuration file with the given parameters."""
    config = {
        "name": config_name,
        "queries": [
            {"uses": "security-and-quality"},
            {"uses": "security-extended"},
            {"uses": "security"}
        ],
        "disable-default-queries": False,
        "paths-ignore": [
            "node_modules",
            "**/*.test.js",
            "**/*.spec.js",
            "**/*.test.py",
            "**/*.spec.py",
            "tests/**",
            "test_mem0_integration.py"
        ]
    }

    if os_name:
        config["os"] = os_name

    Path(filename).write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    """Create CodeQL configuration files."""
    # Ensure the .github/codeql directory exists
    codeql_dir = Path(".github") / "codeql"
    ensure_directory(str(codeql_dir))

    # Create the Ubuntu configuration
    ubuntu_config = codeql_dir / "security-os-ubuntu.yml"
    create_codeql_config(str(ubuntu_config), "CodeQL Configuration for Ubuntu", "ubuntu-latest")

    # Create the macOS configuration
    macos_config = codeql_dir / "security-os-macos.yml"
    create_codeql_config(str(macos_config), "CodeQL Configuration for macOS", "macos-latest")

    # Create the unified configuration
    unified_config = codeql_dir / "security-os-config.yml"
    create_codeql_config(str(unified_config), "Unified CodeQL Configuration")


if __name__ == "__main__":
    main()
