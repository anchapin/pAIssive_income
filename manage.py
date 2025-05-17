#!/usr/bin/env python3
"""
Unified project management script for developers.

Usage:
    python manage.py test
    python manage.py lint
    python manage.py format
    python manage.py scan --type bandit
    python manage.py integration
    python manage.py webhook
    python manage.py dashboard
    python manage.py microservices
    python manage.py help
"""

import argparse
import subprocess
import sys
import os

# Map commands to their corresponding scripts
COMMAND_MAP = {
    "test": "scripts/run/run_tests.py",
    "lint": "scripts/run/run_linting.py",
    "format": "scripts/utils/format_code.py",
    "scan_bandit": "scripts/run/run_bandit_scan.ps1",
    "scan_security": "scripts/run/run_security_tests.py",
    "scan_codeql": "scripts/run/run_security_tests_advanced.py",
    "integration": "scripts/run/run_integration_tests.py",
    "webhook": "scripts/run/run_webhook_tests.py",
    "dashboard": "scripts/run/run_dashboard.py",
    "microservices": "scripts/run/run_microservices.py",
    "local_tests": "scripts/run/run_local_tests.py",
    "mcp_tests": "scripts/run/run_mcp_tests.py",
}


def run_script(script_path, extra_args=None, shell=False):
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        sys.exit(1)
    cmd = [sys.executable, script_path] if script_path.endswith(".py") else [script_path]
    if extra_args:
        cmd.extend(extra_args)
    try:
        result = subprocess.run(cmd, check=False, shell=shell)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Failed to run script: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Project Task Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Test
    subparsers.add_parser("test", help="Run the main test suite")
    subparsers.add_parser("integration", help="Run integration tests")
    subparsers.add_parser("webhook", help="Run webhook tests")
    subparsers.add_parser("dashboard", help="Run dashboard")
    subparsers.add_parser("microservices", help="Run all microservices")
    subparsers.add_parser("local_tests", help="Run local tests")
    subparsers.add_parser("mcp_tests", help="Run MCP adapter tests")

    # Lint/Format
    subparsers.add_parser("lint", help="Run linting")
    subparsers.add_parser("format", help="Run code formatter")

    # Security/Scan
    scan_parser = subparsers.add_parser("scan", help="Run security/code quality scans")
    scan_parser.add_argument("--type", choices=["bandit", "security", "codeql"], required=True,
                             help="Type of scan to run")

    args, extra = parser.parse_known_args()

    if args.command == "test":
        run_script(COMMAND_MAP["test"], extra)
    elif args.command == "integration":
        run_script(COMMAND_MAP["integration"], extra)
    elif args.command == "webhook":
        run_script(COMMAND_MAP["webhook"], extra)
    elif args.command == "dashboard":
        run_script(COMMAND_MAP["dashboard"], extra)
    elif args.command == "microservices":
        run_script(COMMAND_MAP["microservices"], extra)
    elif args.command == "local_tests":
        run_script(COMMAND_MAP["local_tests"], extra)
    elif args.command == "mcp_tests":
        run_script(COMMAND_MAP["mcp_tests"], extra)
    elif args.command == "lint":
        run_script(COMMAND_MAP["lint"], extra)
    elif args.command == "format":
        run_script(COMMAND_MAP["format"], extra)
    elif args.command == "scan":
        scan_type = getattr(args, "type", None)
        if scan_type == "bandit":
            # PowerShell script (use shell=True for cross-platform compatibility)
            run_script(COMMAND_MAP["scan_bandit"], extra, shell=True)
        elif scan_type == "security":
            run_script(COMMAND_MAP["scan_security"], extra)
        elif scan_type == "codeql":
            run_script(COMMAND_MAP["scan_codeql"], extra)
        else:
            parser.error("Unknown scan type")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()