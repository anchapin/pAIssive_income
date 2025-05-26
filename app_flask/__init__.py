"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

from __future__ import annotations

# Standard library imports
import os
from typing import Any

# Third-party imports
from flask import Flask

# Import database extensions
from .database import db, migrate

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
    
    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        try:
            from config import Config
            app.config.from_object(Config)
        except ImportError:
            # Fallback configuration if config.py is not available
            app.config.update({
                'SQLALCHEMY_DATABASE_URI': os.environ.get(
                    'DATABASE_URL', 'sqlite:///:memory:'
                ),
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
            })
    else:
        # Load the test config if passed in
        app.config.update(test_config)
        
    # Ensure SQLALCHEMY_DATABASE_URI is always set
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Ensure SQLALCHEMY_TRACK_MODIFICATIONS is set
    if 'SQLALCHEMY_TRACK_MODIFICATIONS' not in app.config:
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database and migration
    try:
        db.init_app(app)
        migrate.init_app(app, db)
    except Exception as e:
        # Log the error but don't fail completely
        print(f"Warning: Database initialization failed: {e}")

    # Import models so they're registered with SQLAlchemy
    # This must be done after db.init_app() to avoid circular imports
    with app.app_context():
        try:
            from . import models  # noqa: F401 - Import needed for SQLAlchemy registration
        except Exception as e:
            print(f"Warning: Model import failed: {e}")

    # Register blueprints
    try:
        from api.routes.user_router import user_bp
        app.register_blueprint(user_bp)
    except ImportError:
        # Blueprint not available, skip registration
        pass
    except Exception as e:
        print(f"Warning: User blueprint registration failed: {e}")

    # Register MCP servers blueprint
    try:
        from .mcp_servers import mcp_servers_api
        app.register_blueprint(mcp_servers_api)
    except ImportError:
        # MCP servers blueprint not available, skip registration
        pass
    except Exception as e:
        print(f"Warning: MCP servers blueprint registration failed: {e}")

    return app
