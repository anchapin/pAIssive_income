"""
"""
Enhanced test runner for pAIssive_income.
Enhanced test runner for pAIssive_income.


This script provides advanced test running capabilities with:
    This script provides advanced test running capabilities with:
    - Test categorization (unit, integration, etc.)
    - Test categorization (unit, integration, etc.)
    - Test coverage reporting
    - Test coverage reporting
    - HTML test reports
    - HTML test reports
    - Parallelization options
    - Parallelization options
    """
    """


    import argparse
    import argparse
    import os
    import os
    import sys
    import sys
    import time
    import time
    import webbrowser
    import webbrowser
    from datetime import datetime
    from datetime import datetime


    try:
    try:
    import pytest
    import pytest
except ImportError:
except ImportError:
    print("pytest is required to run tests. Install it with 'pip install pytest'")
    print("pytest is required to run tests. Install it with 'pip install pytest'")
    sys.exit(1)
    sys.exit(1)


    try:
    try:
    import pytest_cov
    import pytest_cov
except ImportError:
except ImportError:
    print("Warning: pytest-cov not found. Coverage reporting will not be available.")
    print("Warning: pytest-cov not found. Coverage reporting will not be available.")
    print("Install it with 'pip install pytest-cov'")
    print("Install it with 'pip install pytest-cov'")
    HAS_COVERAGE = False
    HAS_COVERAGE = False
    else:
    else:
    HAS_COVERAGE = True
    HAS_COVERAGE = True




    def run_tests(
    def run_tests(
    test_type=None,
    test_type=None,
    pattern=None,
    pattern=None,
    verbose=False,
    verbose=False,
    coverage=False,
    coverage=False,
    html_report=False,
    html_report=False,
    parallel=False,
    parallel=False,
    failed_only=False,
    failed_only=False,
    ) -> int:
    ) -> int:
    """
    """
    Run tests with specified options.
    Run tests with specified options.


    Args:
    Args:
    test_type: Type of tests to run (unit, integration, etc.)
    test_type: Type of tests to run (unit, integration, etc.)
    pattern: Pattern to match test files
    pattern: Pattern to match test files
    verbose: Whether to run with verbose output
    verbose: Whether to run with verbose output
    coverage: Whether to generate coverage report
    coverage: Whether to generate coverage report
    html_report: Whether to generate HTML report
    html_report: Whether to generate HTML report
    parallel: Whether to run tests in parallel
    parallel: Whether to run tests in parallel
    failed_only: Whether to run only failed tests
    failed_only: Whether to run only failed tests


    Returns:
    Returns:
    Exit code (0 for success, non-zero for failures)
    Exit code (0 for success, non-zero for failures)
    """
    """
    start_time = time.time()
    start_time = time.time()
    print(f"🚀 Starting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🚀 Starting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


    args = ["-v"] if verbose else []
    args = ["-v"] if verbose else []


    # Add marker filtering
    # Add marker filtering
    if test_type == "unit":
    if test_type == "unit":
    args.extend(["-m", "unit"])
    args.extend(["-m", "unit"])
    print("🧪 Running unit tests")
    print("🧪 Running unit tests")
    elif test_type == "integration":
    elif test_type == "integration":
    args.extend(["-m", "integration"])
    args.extend(["-m", "integration"])
    print("🔄 Running integration tests")
    print("🔄 Running integration tests")
    elif test_type == "webhook":
    elif test_type == "webhook":
    args.extend(["-m", "webhook"])
    args.extend(["-m", "webhook"])
    print("🔔 Running webhook tests")
    print("🔔 Running webhook tests")
    elif test_type == "api":
    elif test_type == "api":
    args.extend(["-m", "api"])
    args.extend(["-m", "api"])
    print("🌐 Running API tests")
    print("🌐 Running API tests")
    elif test_type == "slow":
    elif test_type == "slow":
    args.extend(["-m", "slow"])
    args.extend(["-m", "slow"])
    print("⏱️ Running slow tests")
    print("⏱️ Running slow tests")
    elif test_type == "smoke":
    elif test_type == "smoke":
    args.extend(["-m", "smoke"])
    args.extend(["-m", "smoke"])
    print("🔥 Running smoke tests")
    print("🔥 Running smoke tests")
    else:
    else:
    print("🔍 Running all tests")
    print("🔍 Running all tests")


    # Run tests in parallel
    # Run tests in parallel
    if parallel:
    if parallel:
    try:
    try:
    import xdist
    import xdist


    args.append("-xvs")
    args.append("-xvs")
    print("⚡ Running tests in parallel")
    print("⚡ Running tests in parallel")
except ImportError:
except ImportError:
    print("Warning: pytest-xdist not found. Tests will run sequentially.")
    print("Warning: pytest-xdist not found. Tests will run sequentially.")
    print("Install it with 'pip install pytest-xdist'")
    print("Install it with 'pip install pytest-xdist'")


    # Add pattern matching
    # Add pattern matching
    if pattern:
    if pattern:
    args.append(pattern)
    args.append(pattern)
    print(f"🔍 Filtering tests with pattern: {pattern}")
    print(f"🔍 Filtering tests with pattern: {pattern}")


    # Run only failed tests
    # Run only failed tests
    if failed_only:
    if failed_only:
    args.append("--last-failed")
    args.append("--last-failed")
    print("❌ Running only previously failed tests")
    print("❌ Running only previously failed tests")


    # Coverage reporting
    # Coverage reporting
    if coverage and HAS_COVERAGE:
    if coverage and HAS_COVERAGE:
    cover_args = [
    cover_args = [
    "--cov=api",
    "--cov=api",
    "--cov=services",
    "--cov=services",
    "--cov-report=term",
    "--cov-report=term",
    "--cov-report=html:coverage_html",
    "--cov-report=html:coverage_html",
    f"--cov-report=xml:coverage-{sys.version.split('.')[0]}.{sys.version.split('.')[1]}.xml",
    f"--cov-report=xml:coverage-{sys.version.split('.')[0]}.{sys.version.split('.')[1]}.xml",
    ]
    ]
    args.extend(cover_args)
    args.extend(cover_args)
    print("📊 Generating coverage report")
    print("📊 Generating coverage report")


    # HTML report
    # HTML report
    if html_report:
    if html_report:
    try:
    try:
    import pytest_html
    import pytest_html


    report_path = (
    report_path = (
    f"reports/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    f"reports/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    args.extend(["--html", report_path, "--self-contained-html"])
    args.extend(["--html", report_path, "--self-contained-html"])
    print(f"📄 Generating HTML report at {report_path}")
    print(f"📄 Generating HTML report at {report_path}")
except ImportError:
except ImportError:
    print("Warning: pytest-html not found. HTML report will not be generated.")
    print("Warning: pytest-html not found. HTML report will not be generated.")
    print("Install it with 'pip install pytest-html'")
    print("Install it with 'pip install pytest-html'")


    # Run the tests
    # Run the tests
    exit_code = pytest.main(args)
    exit_code = pytest.main(args)


    # Display results
    # Display results
    duration = time.time() - start_time
    duration = time.time() - start_time
    if exit_code == 0:
    if exit_code == 0:
    print(f"✅ All tests passed in {duration:.2f} seconds!")
    print(f"✅ All tests passed in {duration:.2f} seconds!")
    else:
    else:
    print(f"❌ Tests failed in {duration:.2f} seconds.")
    print(f"❌ Tests failed in {duration:.2f} seconds.")


    # Open HTML report in browser if generated
    # Open HTML report in browser if generated
    if html_report and exit_code == 0 and "report_path" in locals():
    if html_report and exit_code == 0 and "report_path" in locals():
    try:
    try:
    webbrowser.open(f"file://{os.path.abspath(report_path)}")
    webbrowser.open(f"file://{os.path.abspath(report_path)}")
except Exception as e:
except Exception as e:
    print(f"Could not open report in browser: {e}")
    print(f"Could not open report in browser: {e}")


    # Open coverage report in browser if generated
    # Open coverage report in browser if generated
    if coverage and HAS_COVERAGE and exit_code == 0:
    if coverage and HAS_COVERAGE and exit_code == 0:
    try:
    try:
    coverage_path = os.path.abspath("coverage_html/index.html")
    coverage_path = os.path.abspath("coverage_html/index.html")
    if os.path.exists(coverage_path):
    if os.path.exists(coverage_path):
    webbrowser.open(f"file://{coverage_path}")
    webbrowser.open(f"file://{coverage_path}")
except Exception as e:
except Exception as e:
    print(f"Could not open coverage report in browser: {e}")
    print(f"Could not open coverage report in browser: {e}")


    return exit_code
    return exit_code




    def main():
    def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for pAIssive_income")

    test_type_group = parser.add_argument_group("Test Type")
    test_type = test_type_group.add_mutually_exclusive_group()
    test_type.add_argument(
    "--unit",
    action="store_const",
    const="unit",
    dest="test_type",
    help="Run unit tests only",
    )
    test_type.add_argument(
    "--integration",
    action="store_const",
    const="integration",
    dest="test_type",
    help="Run integration tests only",
    )
    test_type.add_argument(
    "--webhook",
    action="store_const",
    const="webhook",
    dest="test_type",
    help="Run webhook tests only",
    )
    test_type.add_argument(
    "--api",
    action="store_const",
    const="api",
    dest="test_type",
    help="Run API tests only",
    )
    test_type.add_argument(
    "--smoke",
    action="store_const",
    const="smoke",
    dest="test_type",
    help="Run smoke tests only",
    )
    test_type.add_argument(
    "--slow",
    action="store_const",
    const="slow",
    dest="test_type",
    help="Run slow tests only",
    )

    parser.add_argument(
    "-k",
    "--pattern",
    type=str,
    help="Only run tests matching the given substring expression",
    )
    parser.add_argument(
    "-v", "--verbose", action="store_true", help="Run with verbose output"
    )
    parser.add_argument(
    "-c", "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
    "--html", action="store_true", dest="html_report", help="Generate HTML report"
    )
    parser.add_argument(
    "-p", "--parallel", action="store_true", help="Run tests in parallel"
    )
    parser.add_argument(
    "-f",
    "--failed-only",
    action="store_true",
    help="Run only failed tests from last run",
    )

    args = parser.parse_args()

    sys.exit(
    run_tests(
    test_type=args.test_type,
    pattern=args.pattern,
    verbose=args.verbose,
    coverage=args.coverage,
    html_report=args.html_report,
    parallel=args.parallel,
    failed_only=args.failed_only,
    )
    )


    if __name__ == "__main__":
    main()
