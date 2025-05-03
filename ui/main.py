"""
Main entry point for the pAIssive Income UI.

This module initializes the UI application and services in the correct order.
"""


import logging
    from ui import app, init_app_with_services

    
from ui.routes import init_services

init_services

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_application():
    """Initialize the application and services in the correct order."""
    logger.info("Initializing pAIssive Income application")

# Import the UI module
# Initialize services
    init_app_with_services()

# Initialize routes services
()

logger.info("pAIssive Income application initialized")

            return app


# Create the application
app = initialize_application()

if __name__ == "__main__":
    # Run the application
    app.run(debug=True)