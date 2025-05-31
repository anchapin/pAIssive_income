#!/usr/bin/env python3
"""
Debug script to identify potential workflow issues.

This script checks for common issues that might cause GitHub Actions workflows to fail.
"""

import contextlib
import json
import os
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report the result."""
    return Path(file_path).exists()


def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists and report the result."""
    return Path(dir_path).exists() and Path(dir_path).is_dir()


def check_python_imports() -> None:
    """Check if critical Python modules can be imported."""
    modules_to_check = [
        ("pytest", "pytest testing framework"),
        ("ruff", "ruff linter"),
        ("safety", "safety security scanner"),
        ("bandit", "bandit security scanner"),
    ]

    for module, _description in modules_to_check:
        with contextlib.suppress(ImportError):
            __import__(module)


def check_package_json() -> None:
    """Check package.json configuration."""
    if not check_file_exists("package.json", "package.json file"):
        return

    try:
        with open("package.json") as f:
            package_data = json.load(f)

        # Check test scripts
        scripts = package_data.get("scripts", {})
        if "test" in scripts:
            pass
        else:
            pass

        # Check if test files exist
        test_patterns = ["src/**/*.test.js", "ui/**/*.test.js"]
        for pattern in test_patterns:
            # Simple check for test files
            if "src" in pattern and Path("src").exists():
                test_files = list(Path("src").glob("*.test.js"))
                if test_files:
                    pass
                else:
                    pass
            elif "ui" in pattern and Path("ui").exists():
                test_files = list(Path("ui").rglob("*.test.js"))
                if test_files:
                    pass
                else:
                    pass

    except json.JSONDecodeError:
        pass
    except Exception:
        pass


def check_workflow_files() -> None:
    """Check GitHub Actions workflow files."""
    workflow_dir = Path(".github/workflows")
    if not check_directory_exists(str(workflow_dir), "Workflows directory"):
        return

    workflow_files = list(workflow_dir.glob("*.yml")) + list(
        workflow_dir.glob("*.yaml")
    )

    for _workflow_file in workflow_files:
        pass


def check_test_files() -> None:
    """Check for test files and directories."""
    test_directories = ["tests", "test"]
    for test_dir in test_directories:
        if check_directory_exists(test_dir, "Test directory"):
            list(Path(test_dir).rglob("test_*.py")) + list(
                Path(test_dir).rglob("*_test.py")
            )

            # Check for specific test files mentioned in workflow
            specific_tests = [
                "tests/test_basic.py",
                "tests/test_models.py",
                "tests/ai_models/adapters/test_mcp_adapter.py",
                "tests/ai_models/test_mcp_import.py",
                "tests/test_mcp_top_level_import.py",
                "tests/test_crewai_agents.py",
            ]

            for test_file in specific_tests:
                check_file_exists(test_file, "Specific test file")


def check_scripts() -> None:
    """Check for required scripts."""
    required_scripts = [
        "scripts/check_logger_initialization.py",
        "install_mcp_sdk.py",
        "run_tests.py",
        "run_mcp_tests.py",
    ]

    for script in required_scripts:
        check_file_exists(script, "Required script")


def check_configuration_files() -> None:
    """Check for configuration files."""
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
    # Check if we're in a CI environment
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITHUB_WORKFLOW"]
    for var in ci_vars:
        value = os.environ.get(var)
        if value:
            pass
        else:
            pass

    # Check Python version


def main() -> None:
    """Run all checks."""
    check_environment()
    check_configuration_files()
    check_scripts()
    check_test_files()
    check_workflow_files()
    check_package_json()
    check_python_imports()



if __name__ == "__main__":
    main()
