"""
Enhanced test runner for pAIssive_income.

This script provides advanced test running capabilities with:
- Test categorization (unit, integration, etc.)
- Test coverage reporting
- HTML test reports
- Parallelization options
"""

import argparse
import os
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path

try:
    import pytest
except ImportError:
    print("pytest is required to run tests. Install it with 'pip install pytest'")
    sys.exit(1)

try:
    import pytest_cov
except ImportError:
    print("Warning: pytest-cov not found. Coverage reporting will not be available.")
    print("Install it with 'pip install pytest-cov'")
    HAS_COVERAGE = False
else:
    HAS_COVERAGE = True


def run_tests(test_type=None, pattern=None, verbose=False, coverage=False, 
              html_report=False, parallel=False, failed_only=False) -> int:
    """
    Run tests with specified options.
    
    Args:
        test_type: Type of tests to run (unit, integration, etc.)
        pattern: Pattern to match test files
        verbose: Whether to run with verbose output
        coverage: Whether to generate coverage report
        html_report: Whether to generate HTML report
        parallel: Whether to run tests in parallel
        failed_only: Whether to run only failed tests
        
    Returns:
        Exit code (0 for success, non-zero for failures)
    """
    start_time = time.time()
    print(f"🚀 Starting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    args = ["-v"] if verbose else []
    
    # Add marker filtering
    if test_type == "unit":
        args.extend(["-m", "unit"])
        print("🧪 Running unit tests")
    elif test_type == "integration":
        args.extend(["-m", "integration"])
        print("🔄 Running integration tests")
    elif test_type == "webhook":
        args.extend(["-m", "webhook"])
        print("🔔 Running webhook tests")
    elif test_type == "api":
        args.extend(["-m", "api"])
        print("🌐 Running API tests")
    elif test_type == "slow":
        args.extend(["-m", "slow"])
        print("⏱️ Running slow tests")
    elif test_type == "smoke":
        args.extend(["-m", "smoke"])
        print("🔥 Running smoke tests")
    else:
        print("🔍 Running all tests")
    
    # Run tests in parallel
    if parallel:
        try:
            import xdist
            args.append("-xvs")
            print("⚡ Running tests in parallel")
        except ImportError:
            print("Warning: pytest-xdist not found. Tests will run sequentially.")
            print("Install it with 'pip install pytest-xdist'")
    
    # Add pattern matching
    if pattern:
        args.append(pattern)
        print(f"🔍 Filtering tests with pattern: {pattern}")
    
    # Run only failed tests
    if failed_only:
        args.append("--last-failed")
        print("❌ Running only previously failed tests")
    
    # Coverage reporting
    if coverage and HAS_COVERAGE:
        cover_args = [
            "--cov=api",
            "--cov=services",
            "--cov-report=term",
            "--cov-report=html:coverage_html",
            f"--cov-report=xml:coverage-{sys.version.split('.')[0]}.{sys.version.split('.')[1]}.xml",
        ]
        args.extend(cover_args)
        print("📊 Generating coverage report")
    
    # HTML report
    if html_report:
        try:
            import pytest_html
            report_path = f"reports/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            args.extend(["--html", report_path, "--self-contained-html"])
            print(f"📄 Generating HTML report at {report_path}")
        except ImportError:
            print("Warning: pytest-html not found. HTML report will not be generated.")
            print("Install it with 'pip install pytest-html'")
    
    # Run the tests
    exit_code = pytest.main(args)
    
    # Display results
    duration = time.time() - start_time
    if exit_code == 0:
        print(f"✅ All tests passed in {duration:.2f} seconds!")
    else:
        print(f"❌ Tests failed in {duration:.2f} seconds.")
    
    # Open HTML report in browser if generated
    if html_report and exit_code == 0 and "report_path" in locals():
        try:
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
        except Exception as e:
            print(f"Could not open report in browser: {e}")
    
    # Open coverage report in browser if generated
    if coverage and HAS_COVERAGE and exit_code == 0:
        try:
            coverage_path = os.path.abspath("coverage_html/index.html")
            if os.path.exists(coverage_path):
                webbrowser.open(f"file://{coverage_path}")
        except Exception as e:
            print(f"Could not open coverage report in browser: {e}")
    
    return exit_code


def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for pAIssive_income")
    
    test_type_group = parser.add_argument_group("Test Type")
    test_type = test_type_group.add_mutually_exclusive_group()
    test_type.add_argument("--unit", action="store_const", const="unit", dest="test_type",
                         help="Run unit tests only")
    test_type.add_argument("--integration", action="store_const", const="integration", dest="test_type",
                         help="Run integration tests only")
    test_type.add_argument("--webhook", action="store_const", const="webhook", dest="test_type",
                         help="Run webhook tests only")
    test_type.add_argument("--api", action="store_const", const="api", dest="test_type",
                         help="Run API tests only")
    test_type.add_argument("--smoke", action="store_const", const="smoke", dest="test_type",
                         help="Run smoke tests only")
    test_type.add_argument("--slow", action="store_const", const="slow", dest="test_type",
                         help="Run slow tests only")
    
    parser.add_argument("-k", "--pattern", type=str,
                      help="Only run tests matching the given substring expression")
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Run with verbose output")
    parser.add_argument("-c", "--coverage", action="store_true",
                      help="Generate coverage report")
    parser.add_argument("--html", action="store_true", dest="html_report",
                      help="Generate HTML report")
    parser.add_argument("-p", "--parallel", action="store_true",
                      help="Run tests in parallel")
    parser.add_argument("-f", "--failed-only", action="store_true",
                      help="Run only failed tests from last run")
    
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