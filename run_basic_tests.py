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
    print("=== Testing Flask App Import ===")  # noqa: T201
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
        print("✅ Flask app created successfully")  # noqa: T201
        print(f"   App name: {app.name}")  # noqa: T201
        print(f"   Testing mode: {app.config.get('TESTING', False)}")  # noqa: T201
        print(f"   Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")  # noqa: T201

        # Test app context
        with app.app_context():
            from app_flask import db

            print(f"   Database object: {db}")  # noqa: T201
            print("✅ App context works correctly")  # noqa: T201

        return True

    except Exception as e:
        print(f"❌ Flask app import/creation failed: {e}")  # noqa: T201
        print("=== Traceback ===")  # noqa: T201
        traceback.print_exc()
        return False


def test_models_import() -> bool:
    """Test that the models can be imported successfully."""
    print("\n=== Testing Models Import ===")  # noqa: T201
    try:
        from app_flask.models import Agent, Team, User

        print("✅ Models imported successfully")  # noqa: T201
        print(f"   User model: {User}")  # noqa: T201
        print(f"   Team model: {Team}")  # noqa: T201
        print(f"   Agent model: {Agent}")  # noqa: T201
        return True

    except Exception as e:
        print(f"❌ Models import failed: {e}")  # noqa: T201
        print("=== Traceback ===")  # noqa: T201
        traceback.print_exc()
        return False


def run_pytest_tests() -> bool:
    """Run the actual pytest tests."""
    print("\n=== Running Pytest Tests ===")  # noqa: T201
    try:
        # Run basic tests
        print("Running basic tests...")  # noqa: T201
        result_basic = subprocess.run(  # noqa: S603
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

        print("Basic tests output:")  # noqa: T201
        print(result_basic.stdout)  # noqa: T201
        if result_basic.stderr:
            print("Basic tests errors:")  # noqa: T201
            print(result_basic.stderr)  # noqa: T201

        # Run model tests
        print("\nRunning model tests...")  # noqa: T201
        result_models = subprocess.run(  # noqa: S603
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

        print("Model tests output:")  # noqa: T201
        print(result_models.stdout)  # noqa: T201
        if result_models.stderr:
            print("Model tests errors:")  # noqa: T201
            print(result_models.stderr)  # noqa: T201

        # Check results
        basic_passed = result_basic.returncode == 0
        models_passed = result_models.returncode == 0

        print("\n=== Test Results ===")  # noqa: T201
        print(f"Basic tests: {'✅ PASSED' if basic_passed else '❌ FAILED'}")  # noqa: T201
        print(f"Model tests: {'✅ PASSED' if models_passed else '❌ FAILED'}")  # noqa: T201

        return basic_passed and models_passed

    except Exception as e:
        print(f"❌ Pytest execution failed: {e}")  # noqa: T201
        print("=== Traceback ===")  # noqa: T201
        traceback.print_exc()
        return False


def main() -> bool:
    """Main test runner function."""
    print("Flask Application Basic Test Runner")  # noqa: T201
    print("=" * 50)  # noqa: T201

    # Environment information
    print(f"Python version: {sys.version}")  # noqa: T201
    print(f"Working directory: {os.getcwd()}")  # noqa: T201
    print(f"Python path: {sys.path[:3]}...")  # noqa: T201

    # Check if we're in the right directory
    if not Path("app_flask").exists():
        print("❌ Error: app_flask directory not found. Are you in the project root?")  # noqa: T201
        return False

    if not Path("tests").exists():
        print("❌ Error: tests directory not found. Are you in the project root?")  # noqa: T201
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
    print(f"\n{'=' * 50}")  # noqa: T201
    print("Test Summary:")  # noqa: T201
    print(f"Tests run: {len(tests_passed)}")  # noqa: T201
    print(f"Tests passed: {sum(tests_passed)}")  # noqa: T201
    print(f"Tests failed: {len(tests_passed) - sum(tests_passed)}")  # noqa: T201

    if all(tests_passed):
        print("🎉 All tests passed!")  # noqa: T201
        return True
    print("💥 Some tests failed!")  # noqa: T201
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
