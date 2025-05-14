#!/usr/bin/env python3
"""run_ui.py - Entry point for the Flask web application."""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Dict

from app_flask import create_app

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# Set up file handler
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "flask.log"),
    maxBytes=10485760,  # 10MB
    backupCount=10,
)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
)
file_handler.setLevel(logging.INFO)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Create Flask application
app = create_app()


@app.route("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring.

    Returns:
        Dict[str, str]: Health status information
    """
    return {"status": "healthy", "service": "paissive-income-ui"}


if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))

    # Log startup information
    app.logger.info(f"Starting Flask application on {host}:{port}")
    app.logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")

    # Run the application
    app.run(host=host, port=port)
