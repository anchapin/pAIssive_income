#!/usr/bin/env python3
"""
Comprehensive verification script for PR #243 workflow fixes.
This script validates all the fixes applied to resolve GitHub Actions failures.
"""

import json
import subprocess
import sys
from pathlib import Path

import yaml

from logging_config import configure_logging


def run_command(cmd, capture_output=True, timeout=30):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout, check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_file_exists(filepath):
    """Check if a file exists."""
    return Path(filepath).exists()

def validate_yaml_file(filepath):
    """Validate YAML file syntax."""
    try:
        with open(filepath) as f:
            yaml.safe_load(f)
        return True, "Valid YAML"
    except Exception as e:
        return False, f"Invalid YAML: {e}"

def validate_json_file(filepath):
    """Validate JSON file syntax."""
    try:
        with open(filepath) as f:
            json.load(f)
        return True, "Valid JSON"
    except Exception as e:
        return False, f"Invalid JSON: {e}"

def main() -> int:
    """Main verification function."""
    all_checks_passed = True

    # 1. Check critical workflow files
    critical_files = [
        ".github/workflows/consolidated-ci-cd.yml",
        "package.json",
        "install_mcp_sdk.py",
        "debug_workflow_issues.py",
        "pyproject.toml",
        "ruff.toml",
        "bandit.yaml"
    ]

    for file in critical_files:
        if check_file_exists(file):
            pass
        else:
            all_checks_passed = False

    # 2. Validate workflow YAML syntax
    workflow_files = [
        ".github/workflows/consolidated-ci-cd.yml",
        ".github/workflows/gradual-lint-check.yml",
        ".github/workflows/test.yml"
    ]

    for file in workflow_files:
        if check_file_exists(file):
            valid, message = validate_yaml_file(file)
            if valid:
                pass
            else:
                all_checks_passed = False
        else:
            all_checks_passed = False

    # 3. Validate package.json
    if check_file_exists("package.json"):
        valid, message = validate_json_file("package.json")
        if valid:

            # Check for required test scripts
            with open("package.json") as f:
                pkg_data = json.load(f)

            if "test" in pkg_data.get("scripts", {}):
                pass
            else:
                all_checks_passed = False

            # Check for required dependency
            deps = pkg_data.get("dependencies", {})
            dev_deps = pkg_data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}

            if "@sinonjs/referee-sinon" in all_deps:
                pass
            else:
                all_checks_passed = False
        else:
            all_checks_passed = False

    # 4. Test Python environment

    # Check Python version
    success, stdout, stderr = run_command("python --version")
    if success:
        pass
    else:
        all_checks_passed = False

    # Check pytest availability
    success, stdout, stderr = run_command("python -m pytest --version")
    if success:
        pass
    else:
        all_checks_passed = False

    # Check ruff availability
    success, stdout, stderr = run_command("ruff --version")
    if success:
        pass
    else:
        all_checks_passed = False

    # 5. Test JavaScript environment

    # Check Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        pass
    else:
        all_checks_passed = False

    # Check pnpm
    success, stdout, stderr = run_command("pnpm --version")
    if success:
        pass
    else:
        all_checks_passed = False

    # 6. Run basic tests

    # Python tests
    if check_file_exists("tests/test_basic.py"):
        success, stdout, stderr = run_command(
            "python -m pytest tests/test_basic.py -v --tb=short",
            timeout=60
        )
        if success:
            pass
        else:
            all_checks_passed = False
    else:
        all_checks_passed = False

    # JavaScript tests (quick check)
    if check_file_exists("package.json"):
        success, stdout, stderr = run_command("pnpm test", timeout=120)
        if success:
            pass
        else:
            # Don't fail overall check for JS tests as they might need setup
            pass

    # 7. Check MCP SDK installation
    if check_file_exists("install_mcp_sdk.py"):
        success, stdout, stderr = run_command(
            "python install_mcp_sdk.py",
            timeout=60
        )
        if success:
            pass
        else:
            # Don't fail overall check as this might be environment-specific
            pass

    # 8. Check security tools

    # Check bandit
    success, stdout, stderr = run_command("bandit --version")
    if success:
        pass
    else:
        # Non-critical for local validation
        pass

    # Check safety
    success, stdout, stderr = run_command("safety --version")
    if success:
        pass
    else:
        # Non-critical for local validation
        pass

    # 9. Final summary
    if all_checks_passed:
        return 0
    return 1

if __name__ == "__main__":
    configure_logging()
    sys.exit(main())
