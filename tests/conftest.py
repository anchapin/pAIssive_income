"""
conftest - Module for tests.conftest.

Ensures that pytest does not collect or execute any files or directories ignored by .gitignore.
Provides fixtures for database setup using Docker Compose.
"""

import logging
import os
import shutil
import subprocess

# Set environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-development-only")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("TOOL_API_KEY", "dummy-test-api-key-local-dev-only")

import pytest
from sqlalchemy import text

from app_flask import create_app, db

# Set up logger
logger = logging.getLogger(__name__)


def is_git_tracked(path) -> bool:
    """Return True if the file is tracked by git (not ignored), False otherwise."""
    try:
        # Use git ls-files to check if the file is tracked (not ignored)
        # --error-unmatch causes non-tracked files to raise an error
        git_exe = shutil.which("git") or "git"
        subprocess.check_output(
            [git_exe, "ls-files", "--error-unmatch", os.path.relpath(path)],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def pytest_collect_file(parent, file_path):  # noqa: ARG001 - parent is required by pytest
    """
    Skip files that are not tracked by git (i.e., are git-ignored).

    Args:
        parent: The parent collector node.
        file_path: The path to the file being considered for collection.

    """
    # Only apply check to files (not directories)
    if file_path.is_file():
        abspath = str(file_path)
        if not is_git_tracked(abspath):
            # Skip collection of ignored/untracked files
            return
    # Let pytest handle normal collection
    # Returning None means normal behavior if not ignored


@pytest.fixture(scope="session")
def app():
    """Create a Flask application for testing."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    app = create_app(test_config)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Verify database connection
        try:
            db.session.execute(text("SELECT 1"))
            logger.info("Database connection verified!")
        except Exception:
            logger.exception("Database connection failed")
            pytest.fail("Could not connect to database")

        yield app

        # Clean up after tests
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()
