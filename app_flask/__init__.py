"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Local imports
from .mcp_servers import mcp_servers_api
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Define FlaskApp as an alias for the actual Flask class
FlaskApp = Flask


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Any:
    """Create and configure the Flask application.

    Args:
        test_config: Optional configuration dictionary for testing

    Returns:
        Any: The configured Flask application
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
    from . import models

    # Create all tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    try:
        from api.routes.flask_user_router import user_bp
        app.register_blueprint(user_bp)
    except ImportError:
        # Skip blueprint registration if not available
        pass

    return app
