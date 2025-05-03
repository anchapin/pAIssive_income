"""
Run the pAIssive Income Framework UI.

This script is the main entry point for running the web interface.
"""

import logging
import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the UI module and SocketIO
from ui.app import app  # noqa: E402
from ui.socketio_app import socketio  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Log startup information
    logger.info("Starting pAIssive Income UI")
    logger.info(f"Current working directory: {os.getcwd()}")

    # Run the application with SocketIO
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
