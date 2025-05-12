"""__init__.py - Flask app initialization with SQLAlchemy."""

from typing import Any

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Import Flask with type ignore
from flask import Flask  # type: ignore

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app() -> Any:
    """Create and configure the Flask application.

    Returns:
        Any: The configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they're registered with SQLAlchemy
    # Import inside function to avoid circular imports
    from . import models

    # Register routes here when implementing views

    return app
