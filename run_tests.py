"""
run_tests.py - Script to run tests for the pAIssive Income project.

This script provides a convenient way to run tests with various options
such as running specific test categories, generating coverage reports,
and running tests in parallel.
"""

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def run_tests(
    test_path=None,
    markers=None,
    pattern=None,
    verbose=False,
    coverage=False,
    html_report=False,
    parallel=False,
    failed_only=False,
    specific_file=None,
):
    """Run tests with the specified options."""
    # Build the pytest command
    cmd = ["pytest"]

    # Add test path if specified
    if specific_file:
        cmd.append(specific_file)
    elif test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests")

    # Add markers if specified
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])

    # Add pattern if specified
    if pattern:
        cmd.extend(["-k", pattern])

    # Add verbose flag if specified
    if verbose:
        cmd.append("-v")

    # Add coverage flags if specified
    if coverage:
        cmd.extend(["--cov=."])

        # Add coverage report formats
        cmd.extend(["--cov-report=term-missing"])

        if html_report:
            cmd.extend(["--cov-report=html:coverage_html"])

        cmd.extend(
            [
                f"--cov-report=xml:coverage-{sys.version_info.major}.{sys.version_info.minor}.xml"
            ]
        )

    # Add parallel flag if specified
    if parallel:
        cmd.extend(["-n", "auto"])

    # Add failed only flag if specified
    if failed_only:
        cmd.append("--lf")

    # Add import mode
    cmd.extend(["--import-mode=importlib"])

    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())

    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)

    # Open HTML coverage report if generated
    if coverage and html_report and result.returncode == 0:
        coverage_html = Path("coverage_html/index.html")
        if coverage_html.exists():
            print(f"Opening coverage report: {coverage_html}")
            webbrowser.open(f"file://{coverage_html.absolute()}")

    return result.returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run tests for the pAIssive Income project"
    )

    # Test selection options
    parser.add_argument("--path", help="Path to test directory or file")
    parser.add_argument("--file", help="Specific file to test")
    parser.add_argument("--pattern", help="Pattern to match test names")
    parser.add_argument(
        "--failed-only", action="store_true", help="Run only previously failed tests"
    )

    # Test category options
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    parser.add_argument("--webhook", action="store_true", help="Run webhook tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--payment", action="store_true", help="Run payment tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--model", action="store_true", help="Run model tests")
    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests"
    )
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")

    # Test execution options
    parser.add_argument(
        "--verbose", action="store_true", help="Run tests with verbose output"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")

    args = parser.parse_args()

    # Collect markers based on category options
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.webhook:
        markers.append("webhook")
    if args.api:
        markers.append("api")
    if args.payment:
        markers.append("payment")
    if args.security:
        markers.append("security")
    if args.model:
        markers.append("model")
    if args.performance:
        markers.append("performance")
    if args.smoke:
        markers.append("smoke")

    # Run tests with the specified options
    return run_tests(
        test_path=args.path,
        markers=markers if markers else None,
        pattern=args.pattern,
        verbose=args.verbose,
        coverage=args.coverage,
        html_report=args.html,
        parallel=args.parallel,
        failed_only=args.failed_only,
        specific_file=args.file,
    )


if __name__ == "__main__":
    sys.exit(main())
