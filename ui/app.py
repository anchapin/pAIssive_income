import logging
import os

from ui import app

# noqa: E402, F811
# noqa: E402, F811

"""
"""
Main application file for the pAIssive Income UI.
Main application file for the pAIssive Income UI.


This file is the entry point for running the web interface.
This file is the entry point for running the web interface.
"""
"""
# noqa: E402, F811
# noqa: E402, F811
# noqa: E402, F811
# noqa: E402, F811


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


# Import the UI module
# Import the UI module
# noqa: E402, F811
# noqa: E402, F811


if __name__ == "__main__":
    if __name__ == "__main__":
    # Log startup information
    # Log startup information
    logger.info("Starting pAIssive Income UI")
    logger.info("Starting pAIssive Income UI")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Static folder: {app.static_folder}")


    # Run the application
    # Run the application
    app.run(debug=True, host="0.0.0.0", port=5000)
    app.run(debug=True, host="0.0.0.0", port=5000)

