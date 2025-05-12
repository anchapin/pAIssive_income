"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

# Standard library imports
from typing import Any

# Third-party imports
from flask import Flask, current_app, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Local imports
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Define FlaskApp as an alias for the actual Flask class
FlaskApp = Flask


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
    from . import models

    # Register blueprints
    from api.routes.user_router import user_bp

    app.register_blueprint(user_bp)

    return app
