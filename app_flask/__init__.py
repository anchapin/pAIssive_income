"""__init__.py - Custom Flask app initialization with SQLAlchemy."""

# Standard library imports

# Third-party imports

# Local imports

from flask import Flask
from .mcp_servers import mcp_servers_api

def create_app():
    app = Flask(__name__)
    app.register_blueprint(mcp_servers_api)
    # Register other blueprints or config here
    return app
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
    # Register blueprints
    from api.routes.user_router import user_bp

    from . import models

    app.register_blueprint(user_bp)

    return app
