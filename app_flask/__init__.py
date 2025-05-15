"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Local imports
from config import Config

from .mcp_servers import mcp_servers_api

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Define FlaskApp as an alias for the actual Flask class
FlaskApp = Flask


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        test_config: Optional configuration dictionary for testing

    Returns:
        Flask: The configured Flask application

    """
    app = FlaskApp(__name__)
    app.config.from_object(Config)

    # Override config with test config if provided
    if test_config:
        app.config.update(test_config)

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they're registered with SQLAlchemy
    # Register blueprints
    from api.routes.user_router import user_bp

    from . import models

    app.register_blueprint(user_bp)

    return app
