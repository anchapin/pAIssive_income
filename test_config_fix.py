#!/usr/bin/env python3
"""Test script to verify configuration loads correctly with environment variables."""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Set environment variables for testing
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "true"

try:
    from config import Config

    logger.info("✅ Config loaded successfully!")
    logger.info("FLASK_ENV: %s", os.environ.get("FLASK_ENV"))
    logger.info("DATABASE_URL: %s", Config.SQLALCHEMY_DATABASE_URI)
    logger.info("DEBUG: %s", Config.DEBUG)
    sys.exit(0)
except (ImportError, ValueError, AttributeError) as e:
    logger.exception("❌ Config failed to load: %s", e)
    sys.exit(1)
