"""conftest - Module for tests.conftest.

Ensures that pytest does not collect or execute any files or directories ignored by .gitignore.
Provides fixtures for database setup using Docker Compose.
"""

import logging
import os
import subprocess

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
        subprocess.check_output(
            ["git", "ls-files", "--error-unmatch", os.path.relpath(path)],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def pytest_collect_file(parent, path):
    """Hook called by pytest for every file considered for collection.

    Skips files that are not tracked by git (i.e., are git-ignored).
    """
    # Only apply check to files (not directories)
    if path.isfile():
        abspath = str(path)
        if not is_git_tracked(abspath):
            # Skip collection of ignored/untracked files
            return None
    # Let pytest handle normal collection
    # Returning None means normal behavior if not ignored


@pytest.fixture(scope="session")
def app():
    """Create a Flask application for testing."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-key",
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


@pytest.fixture(scope="function")
def test_db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def session(test_db):
    """Create a new database session for a test."""
    connection = test_db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = test_db.create_scoped_session(options=options)

    # Replace the session with our test session
    old_session = test_db.session
    test_db.session = session

    yield session

    # Restore original session
    test_db.session = old_session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()
