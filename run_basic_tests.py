#!/usr/bin/env python3
"""
Basic test runner for Flask application.

This script runs basic tests to verify the Flask application works correctly.
It's designed to be used in CI/CD environments and provides detailed debugging information.
"""

import os
import subprocess
import sys
import traceback
from pathlib import Path


def test_flask_app_import() -> bool:
    """Test that the Flask app can be imported and created successfully."""
    print("=== Testing Flask App Import ===")
    try:
        from app_flask import create_app

        # Create app with test configuration
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "test-secret-key-for-testing-only",
        }

        app = create_app(test_config)
        print("✅ Flask app created successfully")
        print(f"   App name: {app.name}")
        print(f"   Testing mode: {app.config.get('TESTING', False)}")
        print(f"   Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")

        # Test app context
        with app.app_context():
            from app_flask import db

            print(f"   Database object: {db}")
            print("✅ App context works correctly")

        return True

    except Exception as e:
        print(f"❌ Flask app import/creation failed: {e}")
        print("=== Traceback ===")
        traceback.print_exc()
        return False


def test_models_import() -> bool:
    """Test that the models can be imported successfully."""
    print("\n=== Testing Models Import ===")
    try:
        from app_flask.models import Agent, Team, User

        print("✅ Models imported successfully")
        print(f"   User model: {User}")
        print(f"   Team model: {Team}")
        print(f"   Agent model: {Agent}")
        return True

    except Exception as e:
        print(f"❌ Models import failed: {e}")
        print("=== Traceback ===")
        traceback.print_exc()
        return False


def run_pytest_tests() -> bool:
    """Run the actual pytest tests."""
    print("\n=== Running Pytest Tests ===")
    try:
        # Run basic tests
        print("Running basic tests...")
        result_basic = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_basic.py",
                "-v",
                "--tb=short",
                "--no-cov",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        print("Basic tests output:")
        print(result_basic.stdout)
        if result_basic.stderr:
            print("Basic tests errors:")
            print(result_basic.stderr)

        # Run model tests
        print("\nRunning model tests...")
        result_models = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_models.py",
                "-v",
                "--tb=short",
                "--no-cov",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        print("Model tests output:")
        print(result_models.stdout)
        if result_models.stderr:
            print("Model tests errors:")
            print(result_models.stderr)

        # Check results
        basic_passed = result_basic.returncode == 0
        models_passed = result_models.returncode == 0

        print("\n=== Test Results ===")
        print(f"Basic tests: {'✅ PASSED' if basic_passed else '❌ FAILED'}")
        print(f"Model tests: {'✅ PASSED' if models_passed else '❌ FAILED'}")

        return basic_passed and models_passed

    except Exception as e:
        print(f"❌ Pytest execution failed: {e}")
        print("=== Traceback ===")
        traceback.print_exc()
        return False


def main() -> bool:
    """Main test runner function."""
    print("Flask Application Basic Test Runner")
    print("=" * 50)

    # Environment information
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")

    # Check if we're in the right directory
    if not Path("app_flask").exists():
        print("❌ Error: app_flask directory not found. Are you in the project root?")
        return False

    if not Path("tests").exists():
        print("❌ Error: tests directory not found. Are you in the project root?")
        return False

    # Run tests
    tests_passed = []

    # Test 1: Flask app import
    tests_passed.append(test_flask_app_import())

    # Test 2: Models import
    tests_passed.append(test_models_import())

    # Test 3: Run pytest tests
    tests_passed.append(run_pytest_tests())

    # Summary
    print(f"\n{'=' * 50}")
    print("Test Summary:")
    print(f"Tests run: {len(tests_passed)}")
    print(f"Tests passed: {sum(tests_passed)}")
    print(f"Tests failed: {len(tests_passed) - sum(tests_passed)}")

    if all(tests_passed):
        print("🎉 All tests passed!")
        return True
    print("💥 Some tests failed!")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
