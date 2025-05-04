"""
"""
Factory for creating and initializing the Flask application.
Factory for creating and initializing the Flask application.


This module provides functions for creating and initializing the Flask application
This module provides functions for creating and initializing the Flask application
used by the pAIssive Income UI.
used by the pAIssive Income UI.
"""
"""


import json
import json
import logging
import logging
import os
import os
import uuid
import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta


from flask import Flask
from flask import Flask


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def create_app():
    def create_app():
    """
    """
    Create and configure the Flask application.
    Create and configure the Flask application.


    Returns:
    Returns:
    Flask application
    Flask application
    """
    """
    # Create Flask application
    # Create Flask application
    app = Flask(
    app = Flask(
    __name__,
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )
    )


    # Configure the app
    # Configure the app
    app.config["SECRET_KEY"] = os.environ.get(
    app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev_key_" + str(uuid.uuid4())
    "SECRET_KEY", "dev_key_" + str(uuid.uuid4())
    )
    )
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)


    return app
    return app




    def init_app(app, initialize_services_func=None):
    def init_app(app, initialize_services_func=None):
    """
    """
    Initialize the Flask application.
    Initialize the Flask application.


    Args:
    Args:
    app: Flask application
    app: Flask application
    initialize_services_func: Function to initialize services
    initialize_services_func: Function to initialize services


    Returns:
    Returns:
    Initialized Flask application
    Initialized Flask application
    """
    """
    logger.info("Initializing pAIssive Income UI")
    logger.info("Initializing pAIssive Income UI")


    # Create necessary directories if they don't exist
    # Create necessary directories if they don't exist
    os.makedirs(
    os.makedirs(
    app.config.get("UPLOAD_FOLDER", os.path.join(app.static_folder, "uploads")),
    app.config.get("UPLOAD_FOLDER", os.path.join(app.static_folder, "uploads")),
    exist_ok=True,
    exist_ok=True,
    )
    )


    # Load configuration
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = None
    config = None
    if os.path.exists(config_path):
    if os.path.exists(config_path):
    try:
    try:
    with open(config_path, "r") as f:
    with open(config_path, "r") as f:
    config = json.load(f)
    config = json.load(f)
    for key, value in config.items():
    for key, value in config.items():
    app.config[key] = value
    app.config[key] = value
    logger.info(f"Loaded configuration from {config_path}")
    logger.info(f"Loaded configuration from {config_path}")
except Exception as e:
except Exception as e:
    logger.error(f"Error loading configuration from {config_path}: {e}")
    logger.error(f"Error loading configuration from {config_path}: {e}")


    # Initialize services with dependency injection if function is provided
    # Initialize services with dependency injection if function is provided
    if initialize_services_func:
    if initialize_services_func:
    initialize_services_func(config)
    initialize_services_func(config)
    logger.info("Services initialized with dependency injection")
    logger.info("Services initialized with dependency injection")


    logger.info("pAIssive Income UI initialized")
    logger.info("pAIssive Income UI initialized")


    return app
    return app