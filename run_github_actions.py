#!/usr/bin/env python3
"""
Script to run GitHub Actions workflows locally.
This script simulates the GitHub Actions CI/CD pipeline locally.
"""

import argparse
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional


# Define colors for better output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(message: str) -> None:
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}\n")


def print_step(message: str) -> None:
    """Print a formatted step message."""
    print(f"{Colors.BLUE}→ {message}{Colors.ENDC}")


def print_success(message: str) -> None:
    """Print a formatted success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_warning(message: str) -> None:
    """Print a formatted warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_error(message: str) -> None:
    """Print a formatted error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def run_command(command: List[str], env: Optional[Dict[str, str]] = None) -> int:
    """Run a command and return its exit code."""
    try:
        # Check if we're in a virtual environment
        venv_python = os.path.join("venv", "bin", "python")
        if os.path.exists(venv_python):
            # If the command is a Python module, run it with the venv Python
            if command[0] in [
                "flake8",
                "black",
                "isort",
                "mypy",
                "pytest",
                "bandit",
                "safety",
                "semgrep",
                "pylint",
            ]:
                command = [venv_python, "-m"] + command

        result = subprocess.run(command, env={**os.environ, **(env or {})}, check=False)
        return result.returncode
    except Exception as e:
        print_error(f"Failed to run command: {' '.join(command)}")
        print_error(str(e))
        return 1


def run_lint_checks() -> bool:
    """Run linting checks similar to the GitHub Actions workflow."""
    print_header("Running Lint Checks")

    # Check if required tools are installed
    tools = ["flake8", "black", "isort", "mypy"]
    missing_tools = []

    for tool in tools:
        print_step(f"Checking if {tool} is installed...")
        if run_command(["which", tool]) != 0:
            missing_tools.append(tool)

    if missing_tools:
        print_warning(f"Missing tools: {', '.join(missing_tools)}")
        print_step("Installing missing tools...")
        run_command([sys.executable, "-m", "pip", "install"] + missing_tools)

    # Run flake8
    print_step("Running flake8...")
    flake8_result = run_command(["flake8", ".", "--count", "--statistics"])

    # Run black
    print_step("Running black...")
    black_result = run_command(["black", ".", "--check"])

    # Run isort
    print_step("Running isort...")
    isort_result = run_command(["isort", ".", "--check-only"])

    # Run mypy
    print_step("Running mypy...")
    mypy_result = run_command(["mypy", "."])

    # Check results
    all_passed = all(
        result == 0 for result in [flake8_result, black_result, isort_result, mypy_result]
    )

    if all_passed:
        print_success("All lint checks passed!")
    else:
        print_error("Some lint checks failed.")
        if flake8_result != 0:
            print_error("flake8 check failed.")
        if black_result != 0:
            print_error("black check failed.")
        if isort_result != 0:
            print_error("isort check failed.")
        if mypy_result != 0:
            print_error("mypy check failed.")

    return all_passed


def run_tests() -> bool:
    """Run tests similar to the GitHub Actions workflow."""
    print_header("Running Tests")

    # Check if pytest and pytest-cov are installed
    tools = ["pytest"]
    missing_tools = []

    for tool in tools:
        print_step(f"Checking if {tool} is installed...")
        if run_command(["which", tool]) != 0:
            missing_tools.append(tool)

    if missing_tools:
        print_warning(f"Missing tools: {', '.join(missing_tools)}")
        print_step("Installing missing tools...")
        run_command([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])

    # Run tests with coverage
    print_step("Running tests with pytest and coverage...")
    test_result = run_command(["pytest", "tests/", "--cov=./", "--cov-report=xml"])

    if test_result == 0:
        print_success("All tests passed!")
    else:
        print_error("Some tests failed.")

    return test_result == 0


def run_security_scan() -> bool:
    """Run security scans similar to the GitHub Actions workflow."""
    print_header("Running Security Scans")

    # Check if required tools are installed
    tools = ["bandit", "safety", "semgrep", "pylint"]
    missing_tools = []

    for tool in tools:
        print_step(f"Checking if {tool} is installed...")
        if run_command(["which", tool]) != 0:
            missing_tools.append(tool)

    if missing_tools:
        print_warning(f"Missing tools: {', '.join(missing_tools)}")
        print_step("Installing missing tools...")
        run_command([sys.executable, "-m", "pip", "install"] + missing_tools)

    # Run bandit
    print_step("Running bandit...")
    try:
        bandit_result = run_command(["bandit", "-r", ".", "-c", "pyproject.toml", "-ll"])
    except:
        print_warning(
            "Failed to run bandit with pyproject.toml config, falling back to default config..."
        )
        bandit_result = run_command(["bandit", "-r", ".", "-ll"])

    # Run safety
    print_step("Running safety...")
    safety_result = run_command(["safety", "check", "-i", "51457", "-i", "51668"])

    # Run semgrep
    print_step("Running semgrep...")
    semgrep_result = run_command(["semgrep", "scan", "--config=auto", "--severity=ERROR"])

    # Run pylint security checks
    print_step("Running pylint security checks...")
    pylint_result = run_command(["pylint", "--disable=all", "--enable=security", "."])

    # Check results - note that pylint often returns non-zero even for warnings
    all_passed = all(result == 0 for result in [bandit_result, safety_result, semgrep_result])

    if all_passed and pylint_result <= 1:  # Allow pylint to have warnings
        print_success("All security scans passed!")
    else:
        print_error("Some security scans failed.")
        if bandit_result != 0:
            print_error("bandit scan failed.")
        if safety_result != 0:
            print_error("safety scan failed.")
        if semgrep_result != 0:
            print_error("semgrep scan failed.")
        if pylint_result > 1:
            print_error("pylint security checks failed.")

    return all_passed and pylint_result <= 1


def main() -> int:
    """Main function to run the GitHub Actions workflows locally."""
    parser = argparse.ArgumentParser(description="Run GitHub Actions workflows locally")
    parser.add_argument("--lint", action="store_true", help="Run lint checks")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--security", action="store_true", help="Run security scans")
    parser.add_argument("--all", action="store_true", help="Run all checks")

    args = parser.parse_args()

    # If no arguments are provided, run all checks
    if not any([args.lint, args.test, args.security, args.all]):
        args.all = True

    results = []

    if args.lint or args.all:
        lint_passed = run_lint_checks()
        results.append(("Lint Checks", lint_passed))

    if args.test or args.all:
        tests_passed = run_tests()
        results.append(("Tests", tests_passed))

    if args.security or args.all:
        security_passed = run_security_scan()
        results.append(("Security Scans", security_passed))

    # Print summary
    print_header("Summary")
    all_passed = True

    for name, passed in results:
        if passed:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
            all_passed = False

    if all_passed:
        print_success("\nAll checks passed successfully!")
        return 0
    else:
        print_error("\nSome checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
