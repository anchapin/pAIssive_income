#!/usr/bin/env python

import logging

# Configure logging
logger = logging.getLogger(__name__)

"""
Centralized Logging Service Runner

This script starts the centralized logging service, which collects logs from
distributed applications and stores them in a central location.

Usage:
    python tools/run_centralized_logging_service.py [--host HOST] [--port PORT] [--log-dir LOG_DIR]

Arguments:
    --host HOST       Host to bind the service to (default: 0.0.0.0)
    --port PORT       Port to bind the service to (default: 5000)
    --log-dir LOG_DIR Directory to store log files (default: logs)
"""

import argparse
import os
import signal
import sys
import time

from logging_config import configure_logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the centralized logging service
from common_utils.logging.centralized_logging import CentralizedLoggingService
from common_utils.logging.secure_logging import get_secure_logger

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Set up logging
logger = get_secure_logger("centralized_logging_service_runner")


def parse_args():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments

    """
    parser = argparse.ArgumentParser(description="Centralized Logging Service Runner")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the service to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind the service to (default: 5000)",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory to store log files (default: logs)",
    )
    return parser.parse_args()


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()

    # Create the log directory if it doesn't exist
    os.makedirs(args.log_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(args.log_dir, "centralized_logging_service.log")),
        ],
    )

    # Create the centralized logging service
    service = CentralizedLoggingService(
        host=args.host,
        port=args.port,
        log_dir=args.log_dir,
    )

    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received signal %s, shutting down...", sig)
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the service
    try:
        logger.info("Starting centralized logging service on %s:%s", args.host, args.port)
        service.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error("Error running centralized logging service: %s", e)
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    configure_logging()
    main()
