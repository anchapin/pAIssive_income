"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

from __future__ import annotations

import contextlib
import logging

# Standard library imports
import os
from typing import Any

# Third-party imports
from flask import Flask

# Import database extensions
from .database import db, migrate

# Define FlaskApp as an alias for the actual Flask class
FlaskApp = Flask

# Module-level logger for this file
logger = logging.getLogger(__name__)


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        test_config: Optional configuration dictionary for testing

    Returns:
        Flask: The configured Flask application

    """
    app = FlaskApp(__name__)

    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        try:
            from config import Config

            app.config.from_object(Config)
        except ImportError:
            # Fallback configuration if config.py is not available
            app.config.update(
                {
                    "SQLALCHEMY_DATABASE_URI": os.environ.get(
                        "DATABASE_URL", "sqlite:///:memory:"
                    ),
                    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                    "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-secret-key"),
                }
            )
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure SQLALCHEMY_DATABASE_URI is always set
    if "SQLALCHEMY_DATABASE_URI" not in app.config:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # Ensure SQLALCHEMY_TRACK_MODIFICATIONS is set
    if "SQLALCHEMY_TRACK_MODIFICATIONS" not in app.config:
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database and migration
    try:
        db.init_app(app)
        migrate.init_app(app, db)
    except (RuntimeError, OSError, ValueError) as e:  # Avoid blind except
        logger.warning("Error initializing database or migration: %s", e)

    # Import models so they're registered with SQLAlchemy
    # This must be done after db.init_app() to avoid circular imports
    with app.app_context(), contextlib.suppress(Exception):
        from . import models

    # Register blueprints
    try:
        from api.routes.user_router import user_bp

        app.register_blueprint(user_bp)
    except ImportError:
        logger.info("User blueprint not available, skipping registration.")
    except (RuntimeError, OSError, ValueError) as e:
        logger.warning("Error registering user blueprint: %s", e)

    # Register MCP servers blueprint
    try:
        from .mcp_servers import mcp_servers_api

        app.register_blueprint(mcp_servers_api)
    except ImportError:
        logger.info("MCP servers blueprint not available, skipping registration.")
    except (RuntimeError, OSError, ValueError) as e:
        logger.warning("Error registering MCP servers blueprint: %s", e)

    return app
