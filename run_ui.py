"""
Run the pAIssive Income Framework UI.

This script is the main entry point for running the web interface.
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the UI module
from ui.app import app

if __name__ == '__main__':
    # Log startup information
    logger.info("Starting pAIssive Income UI")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
