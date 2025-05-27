#!/usr/bin/env python3
"""
Debug script to identify potential workflow issues.

This script checks for common issues that might cause GitHub Actions workflows to fail.
"""

import json
import os
import sys
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report the result."""
    exists = Path(file_path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists


def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists and report the result."""
    exists = Path(dir_path).exists() and Path(dir_path).is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dir_path}")
    return exists


def check_python_imports() -> None:
    """Check if critical Python modules can be imported."""
    print("\n🐍 Python Import Checks:")

    modules_to_check = [
        ("pytest", "pytest testing framework"),
        ("ruff", "ruff linter"),
        ("safety", "safety security scanner"),
        ("bandit", "bandit security scanner"),
    ]

    for module, description in modules_to_check:
        try:
            __import__(module)
            print(f"✅ {description}: {module}")
        except ImportError:
            print(f"❌ {description}: {module} (not installed)")


def check_package_json() -> None:
    """Check package.json configuration."""
    print("\n📦 Package.json Checks:")

    if not check_file_exists("package.json", "package.json file"):
        return

    try:
        with open("package.json", "r") as f:
            package_data = json.load(f)

        # Check test scripts
        scripts = package_data.get("scripts", {})
        if "test" in scripts:
            print(f"✅ Test script defined: {scripts['test']}")
        else:
            print("❌ No test script defined in package.json")

        # Check if test files exist
        test_patterns = ["src/**/*.test.js", "ui/**/*.test.js"]
        for pattern in test_patterns:
            # Simple check for test files
            if "src" in pattern and Path("src").exists():
                test_files = list(Path("src").glob("*.test.js"))
                if test_files:
                    print(f"✅ Found test files in src/: {len(test_files)} files")
                else:
                    print("❌ No test files found in src/")
            elif "ui" in pattern and Path("ui").exists():
                test_files = list(Path("ui").rglob("*.test.js"))
                if test_files:
                    print(f"✅ Found test files in ui/: {len(test_files)} files")
                else:
                    print("❌ No test files found in ui/")

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in package.json: {e}")
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")


def check_workflow_files() -> None:
    """Check GitHub Actions workflow files."""
    print("\n🔧 Workflow File Checks:")

    workflow_dir = Path(".github/workflows")
    if not check_directory_exists(str(workflow_dir), "Workflows directory"):
        return

    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    print(f"✅ Found {len(workflow_files)} workflow files")

    for workflow_file in workflow_files:
        print(f"  - {workflow_file.name}")


def check_test_files() -> None:
    """Check for test files and directories."""
    print("\n🧪 Test File Checks:")

    test_directories = ["tests", "test"]
    for test_dir in test_directories:
        if check_directory_exists(test_dir, f"Test directory"):
            test_files = list(Path(test_dir).rglob("test_*.py")) + list(Path(test_dir).rglob("*_test.py"))
            print(f"  Found {len(test_files)} Python test files")

            # Check for specific test files mentioned in workflow
            specific_tests = [
                "tests/test_basic.py",
                "tests/test_models.py",
                "tests/ai_models/adapters/test_mcp_adapter.py",
                "tests/ai_models/test_mcp_import.py",
                "tests/test_mcp_top_level_import.py",
                "tests/test_crewai_agents.py"
            ]

            for test_file in specific_tests:
                check_file_exists(test_file, f"Specific test file")


def check_scripts() -> None:
    """Check for required scripts."""
    print("\n📜 Script Checks:")

    required_scripts = [
        "scripts/check_logger_initialization.py",
        "install_mcp_sdk.py",
        "run_tests.py",
        "run_mcp_tests.py",
    ]

    for script in required_scripts:
        check_file_exists(script, f"Required script")


def check_configuration_files() -> None:
    """Check for configuration files."""
    print("\n⚙️  Configuration File Checks:")

    config_files = [
        ("pyproject.toml", "Python project configuration"),
        ("ruff.toml", "Ruff configuration"),
        ("bandit.yaml", "Bandit configuration"),
        ("requirements.txt", "Python requirements"),
        ("requirements-dev.txt", "Development requirements"),
    ]

    for file_path, description in config_files:
        check_file_exists(file_path, description)


def check_environment() -> None:
    """Check environment variables and settings."""
    print("\n🌍 Environment Checks:")

    # Check if we're in a CI environment
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITHUB_WORKFLOW"]
    for var in ci_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: not set")

    # Check Python version
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")


def main() -> None:
    """Run all checks."""
    print("🔍 Workflow Issue Debug Report")
    print("=" * 50)

    check_environment()
    check_configuration_files()
    check_scripts()
    check_test_files()
    check_workflow_files()
    check_package_json()
    check_python_imports()

    print("\n" + "=" * 50)
    print("🏁 Debug report complete!")
    print("\nIf you see ❌ marks above, those might be causing workflow failures.")
    print("Check the GitHub Actions logs for more specific error messages.")


if __name__ == "__main__":
    main()
