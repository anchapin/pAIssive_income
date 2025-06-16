#!/usr/bin/env python3
"""Debug script to identify potential workflow issues."""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and report the result."""
    exists = Path(file_path).exists()
    status = "✅" if exists else "❌"
    logger.info("%s %s: %s", status, description, file_path)
    return exists


def check_directory_exists(dir_path: str, description: str) -> bool:
    """Check if a directory exists and report the result."""
    exists = Path(dir_path).exists() and Path(dir_path).is_dir()
    status = "✅" if exists else "❌"
    logger.info("%s %s: %s", status, description, dir_path)
    return exists


def check_modules(modules: list[str], description: str) -> None:
    """Check if modules can be imported and log the result."""
    failed = []
    for module in modules:
        # PERF203: try-except within a loop is acceptable here for import checks
        try:
            __import__(module)
            logger.info("\u2705 %s: %s", description, module)
        except ImportError:  # noqa: PERF203
            failed.append(module)  # PERF203: acceptable here for import checks
    for module in failed:
        logger.info("\u274c %s: %s (not installed)", description, module)


def check_package_json() -> None:
    """Check package.json configuration."""
    logger.info("\n📦 Package.json Checks:")

    if not check_file_exists("package.json", "package.json file"):
        return

    try:
        with Path("package.json").open() as f:
            package_data = json.load(f)

        # Check test scripts
        scripts = package_data.get("scripts", {})
        if "test" in scripts:
            logger.info("\u2705 Test script defined: %s", scripts["test"])
        else:
            logger.info("\u274c No test script defined in package.json")

        # Check if test files exist
        test_patterns = ["src/**/*.test.js", "ui/**/*.test.js"]
        for pattern in test_patterns:
            # Simple check for test files
            if "src" in pattern and Path("src").exists():
                test_files = list(Path("src").glob("*.test.js"))
                if test_files:
                    logger.info(
                        "\u2705 Found test files in src/: %d files", len(test_files)
                    )
                else:
                    logger.info("\u274c No test files found in src/")
            elif "ui" in pattern and Path("ui").exists():
                test_files = list(Path("ui").rglob("*.test.js"))
                if test_files:
                    logger.info(
                        "\u2705 Found test files in ui/: %d files", len(test_files)
                    )
                else:
                    logger.info("\u274c No test files found in ui/")

    except json.JSONDecodeError as e:
        logger.info("\u274c Invalid JSON in package.json: %s", e)
    except OSError as e:
        logger.info("\u274c Error reading package.json: %s", e)


def check_workflow_files() -> None:
    """Check GitHub Actions workflow files."""
    logger.info("\n🔧 Workflow File Checks:")

    workflow_dir = Path(".github/workflows")
    if not check_directory_exists(str(workflow_dir), "Workflows directory"):
        return

    workflow_files = list(workflow_dir.glob("*.yml")) + list(
        workflow_dir.glob("*.yaml")
    )
    logger.info("\u2705 Found %d workflow files", len(workflow_files))

    for workflow_file in workflow_files:
        logger.info("  - %s", workflow_file.name)


def check_test_files() -> None:
    """Check for test files and directories."""
    logger.info("\n🧪 Test File Checks:")

    test_directories = ["tests", "test"]
    for test_dir in test_directories:
        if check_directory_exists(test_dir, "Test directory"):
            test_files = list(Path(test_dir).rglob("test_*.py")) + list(
                Path(test_dir).rglob("*_test.py")
            )
            logger.info("  Found %d Python test files", len(test_files))

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
    logger.info("\n📜 Script Checks:")

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
    logger.info("\n⚙️  Configuration File Checks:")

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
    logger.info("\n🌍 Environment Checks:")

    # Check if we're in a CI environment
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITHUB_WORKFLOW"]
    for var in ci_vars:
        value = os.environ.get(var)
        if value:
            logger.info("\u2705 %s: %s", var, value)
        else:
            logger.info("\u274c %s: not set", var)

    # Check Python version
    logger.info("\u2705 Python version: %s", sys.version)
    logger.info("\u2705 Python executable: %s", sys.executable)


def main() -> None:
    """Run all checks."""
    logger.info("🔍 Workflow Issue Debug Report")
    logger.info("%s", "=" * 50)

    check_environment()
    check_configuration_files()
    check_scripts()
    check_test_files()
    check_workflow_files()
    check_package_json()
    check_modules(["pytest", "ruff", "safety", "bandit"], "Python modules")

    logger.info("%s", "\n" + "=" * 50)
    logger.info("🏁 Debug report complete!")
    logger.info(
        "\nIf you see ❌ marks above, those might be causing workflow failures."
    )
    logger.info("Check the GitHub Actions logs for more specific error messages.")


if __name__ == "__main__":
    main()
