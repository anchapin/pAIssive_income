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

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Create a dedicated logger for this module
logger = logging.getLogger(__name__)

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
    # Setup/onboarding commands
    "setup_dev": "scripts/setup/setup_dev_environment.py",
    "enhanced_setup_dev": "scripts/setup/enhanced_setup_dev_environment.py",
    "install_mcp_sdk": "scripts/setup/install_mcp_sdk.py",
    "pre_commit": "scripts/setup/setup_pre_commit.py",  # Or use install_pre_commit.py if preferred
}


def run_script(
    script_path: str, extra_args: Optional[list[str]] = None, shell: bool = False
) -> None:
    """
    Run a script with optional arguments.

    Args:
        script_path: Path to the script to run
        extra_args: Optional list of additional arguments
        shell: Whether to run the command in a shell

    """
    script_path_obj = Path(script_path)
    if not script_path_obj.exists():
        logger.error("Error: Script not found: %s", script_path)
        sys.exit(1)

    cmd = (
        [sys.executable, str(script_path_obj)]
        if script_path.endswith(".py")
        else [str(script_path_obj)]
    )
    if extra_args:
        cmd.extend(extra_args)

    try:
        # Use a more secure approach when shell=True is required
        if shell:
            # For PowerShell scripts that require shell=True, use a safer approach
            cmd_str = " ".join(cmd)
            logger.info("Running command with shell: %s", cmd_str)
            # Use PowerShell explicitly to avoid shell=True
            powershell_cmd = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                cmd_str,
            ]
            result = subprocess.run(powershell_cmd, check=False)
        else:
            result = subprocess.run(cmd, check=False, shell=False)

        sys.exit(result.returncode)
    except subprocess.SubprocessError:
        logger.exception("Failed to run script")
        sys.exit(1)


def main() -> None:
    """
    Execute the main project management functionality.

    Parses command line arguments and runs the appropriate script.
    """
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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

    # Onboarding/setup
    subparsers.add_parser(
        "setup-dev", help="Run the developer environment setup script"
    )
    subparsers.add_parser("enhanced-setup-dev", help="Run the enhanced setup script")
    subparsers.add_parser("install-mcp-sdk", help="Install the MCP SDK")
    subparsers.add_parser("pre-commit", help="Install and configure pre-commit hooks")

    # Database management
    subparsers.add_parser("db-init", help="Initialize the main database")
    subparsers.add_parser("db-init-agent", help="Initialize the agent database")
    subparsers.add_parser("db-migrate", help="Run database migrations")

    # Security/Scan
    scan_parser = subparsers.add_parser("scan", help="Run security/code quality scans")
    scan_parser.add_argument(
        "--type",
        choices=["bandit", "security", "codeql"],
        required=True,
        help="Type of scan to run",
    )

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
    elif args.command == "setup-dev":
        run_script(COMMAND_MAP["setup_dev"], extra)
    elif args.command == "enhanced-setup-dev":
        run_script(COMMAND_MAP["enhanced_setup_dev"], extra)
    elif args.command == "install-mcp-sdk":
        run_script(COMMAND_MAP["install_mcp_sdk"], extra)
    elif args.command == "pre-commit":
        run_script(COMMAND_MAP["pre_commit"], extra)
    elif args.command == "scan":
        scan_type = getattr(args, "type", None)
        if scan_type == "bandit":
            # PowerShell scripts need special handling
            ps_script = Path(COMMAND_MAP["scan_bandit"])
            if ps_script.exists():
                logger.info("Running PowerShell script: %s", ps_script)
                # Use PowerShell explicitly with the script path as an argument
                # This is safer than using shell=True with the full command
                cmd = [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ps_script),
                ]
                if extra:
                    cmd.extend(extra)
                try:
                    result = subprocess.run(cmd, check=False)
                    sys.exit(result.returncode)
                except subprocess.SubprocessError:
                    logger.exception("Failed to run PowerShell script")
                    sys.exit(1)
            else:
                logger.error("PowerShell script not found: %s", ps_script)
                sys.exit(1)
        elif scan_type == "security":
            run_script(COMMAND_MAP["scan_security"], extra)
        elif scan_type == "codeql":
            run_script(COMMAND_MAP["scan_codeql"], extra)
        else:
            parser.error("Unknown scan type")
    elif args.command == "db-init":
        run_script("scripts/db/init_db.py", extra)
    elif args.command == "db-init-agent":
        run_script("scripts/db/init_agent_db.py", extra)
    elif args.command == "db-migrate":
        run_script("scripts/db/run_migrations.py", extra)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
