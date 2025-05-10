"""__init__.py - Flask app initialization with SQLAlchemy."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they're registered with SQLAlchemy
    from . import models

    # Register routes/blueprints here as needed
    # e.g. from .views import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    return app
