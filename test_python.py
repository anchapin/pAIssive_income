#!/usr/bin/env python3
"""Test if Python is working correctly."""

import os
import sys
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    """Print Python environment information."""
    logger.info("Python executable: %s", sys.executable)
    logger.info("Python version: %s", sys.version)
    logger.info("Current working directory: %s", os.getcwd())
    logger.info(
        "Is virtual environment: %s",
        hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    logger.info("sys.prefix: %s", sys.prefix)
    if hasattr(sys, "base_prefix"):
        logger.info("sys.base_prefix: %s", sys.base_prefix)


if __name__ == "__main__":
    main()
