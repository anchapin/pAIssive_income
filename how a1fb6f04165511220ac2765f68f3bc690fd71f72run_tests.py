"""
run_tests.py - Script to run tests for the pAIssive Income project.:

This script provides a convenient way to run tests with various options,:
including running specific test files, test directories, or test methods.
"""

import argparse
import subprocess
import sys


def run_tests(
    test_path=None,
    verbose=False,
    coverage=False,
    junit_xml=False,
    xvs=False,
    specific_test=None,
)
    """Run tests with pytest."""
    # Build the command
    cmd = ["pytest"]

    # Add test path if specified:
    if test_path:
        cmd.append(test_path)

    # Add specific test if specified:
    if specific_test:
        cmd.append(f"-k {specific_test}")

    # Add verbose flag if specified:
    if verbose:
        cmd.append("-v")

    # Add coverage flag if specified:
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])

    # Add JUnit XML flag if specified:
    if junit_xml:
        cmd.append("--junitxml=test-results.xml")

    # Add xvs flag if specified:
    if xvs:
        cmd.append("-xvs")

    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main()
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Run tests for the pAIssive Income project":
    )

    parser.add_argument(
        "test_path", nargs="?", default=None, help="Path to test file or directory"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "--junit-xml", action="store_true", help="Generate JUnit XML report"
    )
    parser.add_argument(
        "--xvs",
        action="store_true",
        help="Exit on first failure, verbose output, show locals",
    )
    parser.add_argument(
        "-k",
        "--specific-test",
        help="Only run tests matching the given substring expression",
    )

    args = parser.parse_args()

    return run_tests(
        test_path=args.test_path,
        verbose=args.verbose,
        coverage=args.coverage,
        junit_xml=args.junit_xml,
        xvs=args.xvs,
        specific_test=args.specific_test,
    )


if __name__ == "__main__":
    sys.exit(main())
