
import logging

from service_initialization import initialize_services

from . import routes
from .app_factory import create_app, init_app
from .celery_app import create_celery_app
from .socketio_app import init_socketio, socketio

init_app

# noqa: E402, F811
# noqa: E402, F811
# noqa: E402, F811, F401
# noqa: E402, F811, F401

"""
"""
UI module for the pAIssive Income project.
UI module for the pAIssive Income project.


This module provides a web interface for interacting with the pAIssive Income framework,
This module provides a web interface for interacting with the pAIssive Income framework,
allowing users to analyze niches, develop solutions, create monetization strategies,
allowing users to analyze niches, develop solutions, create monetization strategies,
and plan marketing campaigns.
and plan marketing campaigns.
"""
"""
# noqa: E402
# noqa: E402


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


# Create and initialize the Flask application
# Create and initialize the Flask application
# noqa: E402, F811
# noqa: E402, F811


app = create_app()
app = create_app()


# Initialize Celery
# Initialize Celery
# noqa: E402, F811
# noqa: E402, F811


celery = create_celery_app(app)
celery = create_celery_app(app)


# Initialize SocketIO
# Initialize SocketIO
# noqa: E402, F811, F401
# noqa: E402, F811, F401


init_socketio(app)
init_socketio(app)


# Import routes after app is created to avoid circular imports
# Import routes after app is created to avoid circular imports
# noqa: E402, F811, F401
# noqa: E402, F811, F401




# Initialize the application with services
# Initialize the application with services
def init_app_with_services():
    def init_app_with_services():
    """Initialize the application with services."""
    (app, initialize_services)
    logger.info("pAIssive Income UI initialized with services")


    # This function can be called after all modules are imported to initialize services
    # It's not called automatically to avoid circular imports