"""
"""
Run the pAIssive Income Framework UI.
Run the pAIssive Income Framework UI.


This script is the main entry point for running the web interface.
This script is the main entry point for running the web interface.
"""
"""


import logging
import logging
import os
import os
import sys
import sys


from ui.app import app
from ui.app import app
from ui.socketio_app import socketio
from ui.socketio_app import socketio


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


# Add the current directory to the path
# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    if __name__ == "__main__":
    # Log startup information
    # Log startup information
    logger.info("Starting pAIssive Income UI")
    logger.info("Starting pAIssive Income UI")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Current working directory: {os.getcwd()}")


    # Run the application with SocketIO
    # Run the application with SocketIO
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

