"""
Main application file for the pAIssive Income UI.

This file is the entry point for running the web interface.
"""

import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the UI module
from ui import app

if __name__ == "__main__":
    # Log startup information
    logger.info("Starting pAIssive Income UI")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")

    # Run the application
    app.run(debug=True, host="0.0.0.0", port=5000)
