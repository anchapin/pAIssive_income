"""
Main application file for the pAIssive Income UI.

This file is the entry point for running the web interface.
"""

import logging
import os
from datetime import datetime

from flask import Flask

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

    # Use environment variables to configure the server
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    host = "127.0.0.1" if debug_mode else "0.0.0.0"
    port = int(os.environ.get("FLASK_PORT", "5000"))
    
    # Run the application with appropriate settings based on environment
    app.run(debug=debug_mode, host=host, port=port)
