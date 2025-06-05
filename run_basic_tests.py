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

        # Test app context
        with app.app_context():
            from app_flask import db


        return True

    except Exception:
        traceback.print_exc()
        return False


def test_models_import() -> bool:
    """Test that the models can be imported successfully."""
    try:
        from app_flask.models import Agent, Team, User

        return True

    except Exception:
        traceback.print_exc()
        return False


def run_pytest_tests() -> bool:
    """Run the actual pytest tests."""
    try:
        # Run basic tests
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

        if result_basic.stderr:
            pass

        # Run model tests
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

        if result_models.stderr:
            pass

        # Check results
        basic_passed = result_basic.returncode == 0
        models_passed = result_models.returncode == 0


        return basic_passed and models_passed

    except Exception:
        traceback.print_exc()
        return False


def main() -> bool:
    """Main test runner function."""
    # Environment information

    # Check if we're in the right directory
    if not Path("app_flask").exists():
        return False

    if not Path("tests").exists():
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

    return bool(all(tests_passed))


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
