"""
UI module for the pAIssive Income project.

This module provides a web interface for interacting with the pAIssive Income framework,
allowing users to analyze niches, develop solutions, create monetization strategies,
and plan marketing campaigns.
"""

import json
import logging
import os
import uuid
from datetime import timedelta

from flask import Flask
from service_initialization import initialize_services

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

# Configure the app
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_" + str(uuid.uuid4()))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# Import these modules after app is created to avoid circular imports
from .celery_app import create_celery_app
from .socketio_app import init_socketio

# Initialize Celery
celery = create_celery_app(app)

# Initialize SocketIO
init_socketio(app)

# Import routes after app is created to avoid circular imports


# Initialize the application
def init_app():
    """Initialize the application."""
    logger.info("Initializing pAIssive Income UI")

    # Create necessary directories if they don't exist
    os.makedirs(
        app.config.get("UPLOAD_FOLDER", os.path.join(app.static_folder, "uploads")),
        exist_ok=True,
    )

    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = None
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                for key, value in config.items():
                    app.config[key] = value
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")

    # Initialize services with dependency injection
    initialize_services()
    logger.info("Services initialized with dependency injection")

    logger.info("pAIssive Income UI initialized")


# Initialize the application when this module is imported
init_app()
