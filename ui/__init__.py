"""
UI module for the pAIssive Income project.

This module provides a web interface for interacting with the pAIssive Income framework,
allowing users to analyze niches, develop solutions, create monetization strategies,
and plan marketing campaigns.
"""

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create and initialize the Flask application
from .app_factory import create_app

app = create_app()

# Initialize Celery
from .celery_app import create_celery_app

celery = create_celery_app(app)

# Initialize SocketIO
from .socketio_app import init_socketio, socketio

init_socketio(app)

# Import routes after app is created to avoid circular imports
from . import routes


# Initialize the application with services
def init_app_with_services():
    """Initialize the application with services."""
    from service_initialization import initialize_services

    from .app_factory import init_app

    init_app(app, initialize_services)
    logger.info("pAIssive Income UI initialized with services")


# This function can be called after all modules are imported to initialize services
# It's not called automatically to avoid circular imports
