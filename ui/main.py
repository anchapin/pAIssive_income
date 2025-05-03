"""
Main entry point for the UI service.

This module provides the main entry point for starting the UI service
as a standalone application.
"""

import logging
from typing import Any, Dict, Optional

from .app_factory import create_app


def start_ui(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Start the UI service.

    Args:
        config: Optional configuration dictionary
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Create and configure the Flask app
    app = create_app(config)
    
    # Log startup
    logger.info("Starting UI service")
    
    # Start the app
    app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    start_ui()
