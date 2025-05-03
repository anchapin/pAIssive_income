"""
Script to run the webhook tests.

This script focuses on running webhook-specific tests with various options.
"""


import argparse
import subprocess
import sys
from pathlib import Path


def main():
    """Parse command line arguments and run webhook tests."""
    parser = argparse.ArgumentParser(description="Run webhook tests for pAIssive_income")
    
    parser.add_argument("--unit", action="store_true", default=False,
                      help="Run only unit tests for webhook functionality")
    parser.add_argument("--integration", action="store_true", default=False,
                      help="Run only integration tests for webhook functionality") 
    parser.add_argument("--all", action="store_true", default=False,
                      help="Run all webhook tests (unit and integration)")
    parser.add_argument("-c", "--coverage", action="store_true", default=False,
                      help="Generate coverage report")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                      help="Verbose output")
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.unit:
        print("Running webhook unit tests...")
        cmd = [sys.executable, "run_tests.py", "--webhook", "-m", "unit"]
    elif args.integration:
        print("Running webhook integration tests...")
        cmd = [sys.executable, "run_tests.py", "--webhook", "-m", "integration"]
    elif args.all:
        print("Running all webhook tests...")
        cmd = [sys.executable, "run_tests.py", "--webhook"]
    else:
        # Default: run the main webhook test
        print("Running standalone webhook test...")
        cmd = [sys.executable, "-m", "pytest", "test_webhook_service.py", "-v"]
    
    # Add optional flags
    if args.coverage:
        cmd.append("--coverage")
    if args.verbose:
        cmd.append("--verbose")
    
    # Execute the command
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()