"""__init__.py - Flask app initialization with SQLAlchemy."""

from typing import Any, cast

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Import the actual Flask library with an alias to avoid naming conflicts
import flask as flask_lib
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Define FlaskApp as an alias for the actual Flask class
# Use type ignore to bypass mypy checks
FlaskApp = flask_lib.Flask  # type: ignore

# Define proxies for flask objects to avoid cyclic imports
# These are needed for compatibility with flask_migrate
current_app = flask_lib.current_app  # type: ignore
g = flask_lib.g  # type: ignore


def create_app() -> Any:
    """Create and configure the Flask application.

    Returns:
        Any: The configured Flask application
    """
    app = FlaskApp(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they're registered with SQLAlchemy
    # Import inside function to avoid circular imports
    from . import models

    # Register routes here when implementing views

    return app
