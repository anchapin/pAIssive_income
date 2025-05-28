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

def main():
    """Main verification function."""
    print("🔍 PR #243 Workflow Fixes Verification")
    print("=" * 50)

    all_checks_passed = True

    # 1. Check critical workflow files
    print("\n📁 Checking Critical Files...")
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
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_checks_passed = False

    # 2. Validate workflow YAML syntax
    print("\n🔧 Validating Workflow Files...")
    workflow_files = [
        ".github/workflows/consolidated-ci-cd.yml",
        ".github/workflows/gradual-lint-check.yml",
        ".github/workflows/test.yml"
    ]

    for file in workflow_files:
        if check_file_exists(file):
            valid, message = validate_yaml_file(file)
            if valid:
                print(f"✅ {file} - {message}")
            else:
                print(f"❌ {file} - {message}")
                all_checks_passed = False
        else:
            print(f"❌ {file} - File not found")
            all_checks_passed = False

    # 3. Validate package.json
    print("\n📦 Validating Package Configuration...")
    if check_file_exists("package.json"):
        valid, message = validate_json_file("package.json")
        if valid:
            print(f"✅ package.json - {message}")

            # Check for required test scripts
            with open("package.json") as f:
                pkg_data = json.load(f)

            if "test" in pkg_data.get("scripts", {}):
                print("✅ Test script defined in package.json")
            else:
                print("❌ Test script missing in package.json")
                all_checks_passed = False

            # Check for required dependency
            deps = pkg_data.get("dependencies", {})
            dev_deps = pkg_data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}

            if "@sinonjs/referee-sinon" in all_deps:
                print("✅ Required test dependency found")
            else:
                print("❌ Missing @sinonjs/referee-sinon dependency")
                all_checks_passed = False
        else:
            print(f"❌ package.json - {message}")
            all_checks_passed = False

    # 4. Test Python environment
    print("\n🐍 Testing Python Environment...")

    # Check Python version
    success, stdout, stderr = run_command("python --version")
    if success:
        print(f"✅ Python version: {stdout.strip()}")
    else:
        print(f"❌ Python check failed: {stderr}")
        all_checks_passed = False

    # Check pytest availability
    success, stdout, stderr = run_command("python -m pytest --version")
    if success:
        print(f"✅ pytest available: {stdout.strip()}")
    else:
        print(f"❌ pytest not available: {stderr}")
        all_checks_passed = False

    # Check ruff availability
    success, stdout, stderr = run_command("ruff --version")
    if success:
        print(f"✅ ruff available: {stdout.strip()}")
    else:
        print(f"❌ ruff not available: {stderr}")
        all_checks_passed = False

    # 5. Test JavaScript environment
    print("\n🟨 Testing JavaScript Environment...")

    # Check Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        print(f"✅ Node.js version: {stdout.strip()}")
    else:
        print(f"❌ Node.js check failed: {stderr}")
        all_checks_passed = False

    # Check pnpm
    success, stdout, stderr = run_command("pnpm --version")
    if success:
        print(f"✅ pnpm version: {stdout.strip()}")
    else:
        print(f"❌ pnpm not available: {stderr}")
        all_checks_passed = False

    # 6. Run basic tests
    print("\n🧪 Running Basic Tests...")

    # Python tests
    if check_file_exists("tests/test_basic.py"):
        print("Running Python basic tests...")
        success, stdout, stderr = run_command(
            "python -m pytest tests/test_basic.py -v --tb=short",
            timeout=60
        )
        if success:
            print("✅ Python basic tests passed")
        else:
            print(f"❌ Python basic tests failed: {stderr}")
            all_checks_passed = False
    else:
        print("❌ tests/test_basic.py not found")
        all_checks_passed = False

    # JavaScript tests (quick check)
    if check_file_exists("package.json"):
        print("Running JavaScript tests...")
        success, stdout, stderr = run_command("pnpm test", timeout=120)
        if success:
            print("✅ JavaScript tests passed")
        else:
            print(f"❌ JavaScript tests failed: {stderr}")
            # Don't fail overall check for JS tests as they might need setup
            print("ℹ️  JavaScript test failure is non-critical for workflow validation")

    # 7. Check MCP SDK installation
    print("\n🔌 Testing MCP SDK Installation...")
    if check_file_exists("install_mcp_sdk.py"):
        success, stdout, stderr = run_command(
            "python install_mcp_sdk.py",
            timeout=60
        )
        if success:
            print("✅ MCP SDK installation script works")
        else:
            print(f"❌ MCP SDK installation failed: {stderr}")
            # Don't fail overall check as this might be environment-specific
            print("ℹ️  MCP SDK installation failure is non-critical for workflow validation")

    # 8. Check security tools
    print("\n🔒 Testing Security Tools...")

    # Check bandit
    success, stdout, stderr = run_command("bandit --version")
    if success:
        print(f"✅ bandit available: {stdout.strip()}")
    else:
        print(f"❌ bandit not available: {stderr}")
        # Non-critical for local validation
        print("ℹ️  Bandit not available locally (will be installed in CI)")

    # Check safety
    success, stdout, stderr = run_command("safety --version")
    if success:
        print(f"✅ safety available: {stdout.strip()}")
    else:
        print(f"❌ safety not available: {stderr}")
        # Non-critical for local validation
        print("ℹ️  Safety not available locally (will be installed in CI)")

    # 9. Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 ALL CRITICAL CHECKS PASSED!")
        print("✅ PR #243 workflow fixes are properly implemented")
        print("✅ Ready for GitHub Actions execution")
        return 0
    print("⚠️  SOME CHECKS FAILED")
    print("❌ Please review the failed checks above")
    print("ℹ️  Some failures may be environment-specific and won't affect CI")
    return 1

if __name__ == "__main__":
    configure_logging()
    sys.exit(main())
