"""
conftest - Module for tests.conftest.

Ensures that pytest does not collect or execute any files or directories ignored by .gitignore.
Provides fixtures for database setup using Docker Compose.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

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
        subprocess.check_output(  # noqa: S603 - Using git with proper arguments
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
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
    }

    app = create_app(test_config)

    with app.app_context():
        try:
            # Create all tables
            db.create_all()

            # Verify database connection
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            logger.info("Database connection verified!")
        except Exception as e:
            logger.exception("Database setup failed: %s", e)
            pytest.fail(f"Could not set up database: {e}")

        yield app

        # Clean up after tests
        try:
            db.session.remove()
            db.drop_all()
        except Exception as e:
            logger.warning("Error during database cleanup: %s", e)
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning("Error cleaning up temp directory: %s", e)


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    with app.app_context():
        # Start a transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Configure session to use the transaction
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )

        # Make session available to the app
        db.session = session

        yield session

        # Rollback transaction and close connection
        transaction.rollback()
        connection.close()
        session.remove()
