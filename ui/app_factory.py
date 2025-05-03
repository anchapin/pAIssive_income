"""
Factory module for creating Flask application instances.

This module provides functions to create and configure Flask applications.
"""

import logging
from typing import Dict, Any, Optional

from flask import Flask
from flask_cors import CORS


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Create and configure a Flask application instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Apply default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True
    )

    # Apply passed configuration
    if config:
        app.config.from_mapping(config)

    # Enable CORS
    CORS(app)

    # Configure logging
    _configure_logging(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register blueprints
    _register_blueprints(app)

    return app


def _configure_logging(app: Flask) -> None:
    """
    Configure logging for the Flask application.

    Args:
        app: Flask application instance
    """
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    app.logger.setLevel(log_level)

    # Create console handler if it doesn't exist
    if not app.logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)

    app.logger.info('Logging configured for Flask application')


def _register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the Flask application.

    Args:
        app: Flask application instance
    """
    # Import error handlers here to avoid circular imports
    from .errors import handle_bad_request, handle_not_found, handle_server_error

    app.register_error_handler(400, handle_bad_request)
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(500, handle_server_error)

    app.logger.info('Error handlers registered')


def _register_blueprints(app: Flask) -> None:
    """
    Register blueprints with the Flask application.

    Args:
        app: Flask application instance
    """
    # Import blueprints here to avoid circular imports
    from .routes import main_bp, api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    app.logger.info('Blueprints registered')
