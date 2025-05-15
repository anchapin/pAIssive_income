"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

from __future__ import annotations

# Standard library imports
from typing import Any, TypeVar, Union, cast

# Third-party imports
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.local import LocalProxy

# Local imports
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Define FlaskApp as an alias for the actual Flask class with proper typing
FlaskApp = Flask
# Type alias for Flask config
FlaskConfig = Any


def create_app(
    test_config: dict[str, Any] | None = None,
) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        test_config: Optional configuration dictionary for testing

    Returns:
        Flask: The configured Flask application

    """
    app = FlaskApp(__name__)
    # Load configuration
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

    # Add health check endpoint
    @app.route("/health")
    def health_check() -> dict[str, str]:
        """
        Health check endpoint for monitoring.

        Returns:
            dict[str, str]: Health status information

        """
        return {"status": "healthy", "service": "paissive-income-ui"}

    return app
