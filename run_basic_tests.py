#!/usr/bin/env python3
"""
Basic test runner for Flask application.

This script runs basic tests to verify the Flask application works correctly.
It's designed to be used in CI/CD environments and provides detailed debugging information.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# type: ignore[import, assignment]


def test_flask_app_import() -> bool:
    """Test that the Flask app can be imported and created successfully."""
    logger = logging.getLogger("test_flask_app_import")
    try:
        from app_flask import create_app

        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "test-secret-key-for-testing-only",
        }
        app = create_app(test_config)
        logger.info("Flask app created successfully")
        logger.info("   App name: %s", app.name)
        logger.info("   Testing mode: %s", app.config.get("TESTING", False))
        logger.info(
            "   Database URI: %s", app.config.get("SQLALCHEMY_DATABASE_URI", "Not set")
        )
        with app.app_context():
            from app_flask import db

            logger.info("   Database object: %s", db)
            logger.info("App context works correctly")
    except ImportError:
        logger.exception("Flask app import/creation failed")
    else:
        return True
    return False


def test_models_import() -> bool:
    """Test that the models can be imported successfully."""
    logger = logging.getLogger("test_models_import")
    try:
        from app_flask.models import Agent, Team, User

        logger.info("Models imported successfully")
        logger.info("   User model: %s", User)
        logger.info("   Team model: %s", Team)
        logger.info("   Agent model: %s", Agent)
    except ImportError:
        logger.exception("Models import failed")
    else:
        return True
    return False


# Shared set of allowed/supported kwargs for subprocess.run
_ALLOWED_SUBPROCESS_KWARGS = {
    "stdin",
    "stdout",
    "stderr",
    "capture_output",
    "shell",
    "cwd",
    "timeout",
    "env",
    "text",
    "encoding",
    "errors",
    "bufsize",
    "close_fds",
    "pass_fds",
    "input",
    "universal_newlines",
    "start_new_session",
    "restore_signals",
    "creationflags",
    "check",
}


def _filter_subprocess_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Filter and normalize kwargs for subprocess.run, converting Path to str where needed."""
    allowed_keys = _ALLOWED_SUBPROCESS_KWARGS
    filtered: dict[str, Any] = {}
    for k, v in kwargs.items():
        if k not in allowed_keys or v is None:
            continue
        if (
            (k in {"cwd", "encoding", "errors"} and isinstance(v, (str, bytes)))
            or (k == "timeout" and isinstance(v, (int, float)))
            or (k in {"bufsize", "creationflags"} and isinstance(v, int))
            or (
                k
                in {
                    "close_fds",
                    "shell",
                    "text",
                    "universal_newlines",
                    "start_new_session",
                    "restore_signals",
                    "check",
                }
                and isinstance(v, bool)
            )
        ):
            filtered[k] = v
        elif k in {"stdin", "stdout", "stderr", "input"}:
            filtered[k] = v  # Accept file handles or strings
        elif (k == "env" and isinstance(v, dict)) or (
            k == "pass_fds" and isinstance(v, (list, tuple, set))
        ):
            filtered[k] = v
    if "cwd" in filtered and isinstance(filtered["cwd"], Path):
        filtered["cwd"] = str(filtered["cwd"])
    return filtered


def _safe_subprocess_run(
    cmd: list[str], **kwargs: object
) -> subprocess.CompletedProcess[object]:
    """Run subprocess.run with filtered/normalized kwargs. Only for trusted commands, shell is always False."""
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    filtered_kwargs = _filter_subprocess_kwargs(kwargs)  # type: ignore[arg-type]
    if "check" not in filtered_kwargs:
        filtered_kwargs["check"] = False
    # Security note: Only trusted commands should be passed here. No user input.
    return subprocess.run(  # noqa: S603
        cmd,
        **filtered_kwargs,
        check=filtered_kwargs.get("check", False),  # type: ignore[call-arg]
    )


def run_subprocess(
    cmd: list[str], **kwargs: object
) -> subprocess.CompletedProcess[object]:
    """Run subprocess only for trusted commands, with strict argument filtering and type safety. shell is always False."""
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    allowed_binaries = {sys.executable, "pytest"}
    if not cmd or (cmd[0] not in allowed_binaries and not cmd[0].endswith("pytest")):
        msg = f"Untrusted or unsupported command: {cmd}"
        raise ValueError(msg)  # TRY003, EM102
    filtered_kwargs = _filter_subprocess_kwargs(kwargs)  # type: ignore[arg-type]
    if "check" not in filtered_kwargs:
        filtered_kwargs["check"] = False
    # Security note: Only trusted commands should be passed here. No user input.
    return subprocess.run(  # noqa: S603
        cmd,
        **filtered_kwargs,
        check=filtered_kwargs.get("check", False),  # type: ignore[call-arg]
    )


def run_pytest_tests() -> bool:
    """Run the actual pytest tests and return True if all pass."""
    logger = logging.getLogger("run_pytest_tests")
    try:
        logger.info("Running basic tests...")
        result_basic = run_subprocess(
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
        logger.info("Basic tests output:\n%s", result_basic.stdout)
        if result_basic.stderr:
            logger.warning("Basic tests errors:\n%s", result_basic.stderr)
        logger.info("Running model tests...")
        result_models = run_subprocess(
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
        logger.info("Model tests output:\n%s", result_models.stdout)
        if result_models.stderr:
            logger.warning("Model tests errors:\n%s", result_models.stderr)
        basic_passed = result_basic.returncode == 0
        models_passed = result_models.returncode == 0
        logger.info(
            "Test Results: Basic tests: %s, Model tests: %s",
            basic_passed,
            models_passed,
        )
    except Exception:
        logger.exception("Pytest execution failed")
    else:
        return basic_passed and models_passed
    return False


def main() -> bool:
    """Run the main test runner."""
    logger = logging.getLogger("main")
    logger.info("Flask Application Basic Test Runner")
    logger.info("%s", "=" * 50)
    logger.info("Python version: %s", sys.version)
    logger.info("Working directory: %s", Path.cwd())
    logger.info("Python path: %s...", sys.path[:3])
    if not Path("app_flask").exists():
        logger.error(
            "Error: app_flask directory not found. Are you in the project root?"
        )
        return False
    if not Path("tests").exists():
        logger.error("Error: tests directory not found. Are you in the project root?")
        return False
    tests_passed = []
    tests_passed.append(test_flask_app_import())
    tests_passed.append(test_models_import())
    tests_passed.append(run_pytest_tests())
    logger.info("%s", "=" * 50)
    logger.info("Test Summary:")
    logger.info("Tests run: %d", len(tests_passed))
    logger.info("Tests passed: %d", sum(tests_passed))
    logger.info("Tests failed: %d", len(tests_passed) - sum(tests_passed))
    if all(tests_passed):
        logger.info("All tests passed!")
        return True
    logger.error("Some tests failed!")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
