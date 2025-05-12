"""__init__.py - Flask app initialization with SQLAlchemy."""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config
from flask import Flask

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they're registered with SQLAlchemy
    from . import models

    # Register routes when needed
    # For example: from .views import main_blueprint
    # Then: app.register_blueprint(main_blueprint)

    return app
