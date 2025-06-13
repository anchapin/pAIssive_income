"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

from __future__ import annotations

import os
from pathlib import Path

# Standard library imports
from typing import Any

# Third-party imports
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Local imports
from config import Config

from .mcp_servers import mcp_servers_api
from .middleware.logging_middleware import setup_request_logging

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

    # Load config
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.update(test_config)

    # Enable security middleware
    from .middleware.security import setup_security_middleware

    setup_security_middleware(app)

    # Setup logging middleware
    setup_request_logging(app)

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(mcp_servers_api)

    # Import models so they're registered with SQLAlchemy
    from . import models  # Ensure instance folder exists

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Disable Flask debug mode in production
    if (
        not app.debug
        and not app.testing
        and os.environ.get("FLASK_ENV") == "production"
    ):
        app.config["DEBUG"] = False
        app.config["TESTING"] = False
        app.config["PROPAGATE_EXCEPTIONS"] = False

    return app
