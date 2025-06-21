"""
conftest - Module for tests.conftest.

Simplified conftest for better CI compatibility.
"""

import logging
import tempfile
from pathlib import Path

import pytest

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def app():
    """Create a Flask application for testing."""
    try:
        from app_flask import create_app, db
        from sqlalchemy import text
        import shutil

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
            except Exception:
                logger.exception("Database setup failed")
                pytest.fail("Could not set up database")

            yield app

            # Clean up after tests
            try:
                db.session.remove()
                db.drop_all()
            except Exception:
                logger.warning("Error during database cleanup")
            finally:
                # Clean up temporary directory
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    logger.warning("Error cleaning up temp directory")
    except ImportError:
        # If app_flask is not available, create a minimal Flask app
        from flask import Flask
        app = Flask(__name__)
        app.config.update({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
        })
        yield app


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
    try:
        from app_flask import db

        with app.app_context():
            # Start a transaction
            connection = db.engine.connect()
            transaction = connection.begin()

            # Configure session to use the transaction
            session = db.create_scoped_session(options={"bind": connection, "binds": {}})

            # Make session available to the app
            db.session = session

            yield session

            # Rollback transaction and close connection
            transaction.rollback()
            connection.close()
            session.remove()
    except ImportError:
        # If db is not available, yield None
        yield None
