"""
conftest - Module for tests.conftest.

Ensures that pytest does not collect or execute any files or directories ignored by .gitignore.
Provides fixtures for database setup using Docker Compose.
"""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try to import Flask-related modules, but provide mocks if they're not available
try:
    from sqlalchemy import text

    from app_flask import create_app, db

    FLASK_AVAILABLE = True
except ImportError:
    # Create mocks for Flask-related imports
    FLASK_AVAILABLE = False
    text = MagicMock()
    create_app = MagicMock()
    db = MagicMock()
    db.create_all = MagicMock()
    db.drop_all = MagicMock()
    db.session = MagicMock()
    db.create_scoped_session = MagicMock(return_value=MagicMock())


# Mock crewai module for testing
class MockCrewAI:
    """Mock for the crewai module."""

    class Agent:
        """Mock Agent class."""

        def __init__(self, role=None, goal=None, backstory=None, **kwargs):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            self.kwargs = kwargs

        def execute_task(self, task):
            """Mock execute_task method."""
            return f"Executed task: {task.description}"

    class Task:
        """Mock Task class."""

        def __init__(self, description=None, agent=None, **kwargs):
            self.description = description
            self.agent = agent
            self.kwargs = kwargs

    class Crew:
        """Mock Crew class."""

        def __init__(self, agents=None, tasks=None, **kwargs):
            self.agents = agents or []
            self.tasks = tasks or []
            self.kwargs = kwargs

        def kickoff(self, inputs=None, *args, **kwargs):
            """Mock kickoff method."""
            if inputs:
                return f"Mock crew output with inputs: {inputs}"
            return "Mock crew output"

        # Alias for backward compatibility
        run = kickoff


# Add mock modules to sys.modules
sys.modules["crewai"] = MagicMock()
sys.modules["crewai"].Agent = MockCrewAI.Agent
sys.modules["crewai"].Task = MockCrewAI.Task
sys.modules["crewai"].Crew = MockCrewAI.Crew

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


def pytest_collect_file(parent, file_path):
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
    # Skip if Flask is not available
    if not FLASK_AVAILABLE:
        pytest.skip("Flask is not available - skipping test")

    # Ensure we always use SQLite for tests, regardless of environment variables
    import os
    old_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

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
            pytest.skip("Could not connect to database - skipping test")

        yield app

        # Clean up after tests
        db.session.remove()
        db.drop_all()

        # Restore original DATABASE_URL environment variable
        if old_database_url is not None:
            os.environ["DATABASE_URL"] = old_database_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]


@pytest.fixture
def test_db(app):
    """Create a fresh database for each test."""
    # Skip if Flask is not available
    if not FLASK_AVAILABLE:
        pytest.skip("Flask is not available - skipping test")

    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(test_db):
    """Create a new database session for a test."""
    # Skip if Flask is not available
    if not FLASK_AVAILABLE:
        pytest.skip("Flask is not available - skipping test")

    connection = test_db.engine.connect()
    transaction = connection.begin()

    options = {"bind": connection, "binds": {}}
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
    # Skip if Flask is not available
    if not FLASK_AVAILABLE:
        pytest.skip("Flask is not available - skipping test")

    return app.test_client()
