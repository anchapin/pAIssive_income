"""
Factory for creating and initializing the Flask application.

This module provides functions for creating and initializing the Flask application
used by the pAIssive Income UI.
"""

from datetime import datetime


import json
import logging
import os
import uuid
from datetime import timedelta

from flask import Flask



# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure the Flask application.

Returns:
        Flask application
    """
    # Create Flask application
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

# Configure the app
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev_key_" + str(uuid.uuid4())
    )
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

            return app


def init_app(app, initialize_services_func=None):
    """
    Initialize the Flask application.

Args:
        app: Flask application
        initialize_services_func: Function to initialize services

Returns:
        Initialized Flask application
    """
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

# Initialize services with dependency injection if function is provided
    if initialize_services_func:
        initialize_services_func(config)
        logger.info("Services initialized with dependency injection")

logger.info("pAIssive Income UI initialized")

            return app