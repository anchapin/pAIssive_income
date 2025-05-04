#!/usr/bin/env python
"""
"""
Script to run tests directly without using Act.
Script to run tests directly without using Act.
This script helps verify that tests will pass before pushing to the repository.
This script helps verify that tests will pass before pushing to the repository.
"""
"""


import subprocess
import subprocess
import sys
import sys
from pathlib import Path
from pathlib import Path




def run_tests():
    def run_tests():
    """Run the test suite."""
    print("🚀 Running tests...")
    try:
    subprocess.run(
    ["python", "-m", "pytest", "tests/", "-v", "--import-mode=importlib"],
    check=True,
    )
    print("✅ Tests completed successfully!")
    return True
except subprocess.CalledProcessError as e:
    print(f"❌ Tests failed with exit code {e.returncode}")
    return False


    def run_linting():
    """Run linting checks."""
    print("🚀 Running linting checks...")
    try:
    subprocess.run(
    ["python", "run_linting.py"],
    check=True,
    )
    print("✅ Linting completed successfully!")
    return True
except subprocess.CalledProcessError as e:
    print(f"❌ Linting failed with exit code {e.returncode}")
    return False


    def main():
    """Main function to run tests and linting."""
    tests_success = run_tests()
    linting_success = run_linting()

    if tests_success and linting_success:
    print("\n✅ All checks passed!")
    return 0
    else:
    print("\n❌ Some checks failed.")
    return 1


    if __name__ == "__main__":
    sys.exit(main())