"""
Main application entry point.

This module provides the main entry point for the pAIssive_income application.
It sets up logging configuration and serves as the primary application launcher.
"""

import logging
import sys
from pathlib import Path

# Configure logger for this module
logger = logging.getLogger(__name__)


def configure_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "application.log")
        ]
    )
    
    logger.info("Logging configured successfully")


def _run_main() -> None:
    """
    Internal function to run the main application logic.
    
    This function is called when the module is executed as a script.
    """
    configure_logging()
    logger.info("Main application started.")
    
    # Add main application logic here
    logger.info("Application initialization complete")


def main() -> None:
    """
    Main entry point for the application.
    
    This function serves as the primary entry point and can be called
    from other modules or scripts.
    """
    try:
        _run_main()
    except Exception as e:
        logger.exception("An error occurred in main application: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    configure_logging()
    logger.info("Main application started.")
    main()
