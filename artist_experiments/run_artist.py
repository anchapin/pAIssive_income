"""
ARTIST experiment runner.

This script provides a simple Flask application for running ARTIST experiments.
"""

import logging
import os
from pathlib import Path

from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(Path("artist_experiments/logs/app.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check() -> dict:
    """
    Perform a health check.

    Returns:
        dict: Health status information.

    """
    return jsonify({"status": "healthy", "service": "artist-experiments"})


@app.route("/", methods=["GET"])
def home() -> dict:
    """
    Home endpoint.

    Returns:
        dict: Welcome message.

    """
    return jsonify(
        {
            "message": "Welcome to ARTIST Experiments",
            "description": "This service provides endpoints for running ARTIST experiments.",
        }
    )


@app.route("/experiments", methods=["GET"])
def list_experiments() -> dict:
    """
    List available experiments.

    Returns:
        dict: List of available experiments.

    """
    return jsonify(
        {
            "experiments": [
                {
                    "id": "math-problem-solving",
                    "name": "Mathematical Problem Solving",
                    "description": "Experiment for solving mathematical problems using ARTIST.",
                },
                {
                    "id": "multi-api-orchestration",
                    "name": "Multi-API Orchestration",
                    "description": "Experiment for orchestrating multiple APIs using ARTIST.",
                },
            ]
        }
    )


if __name__ == "__main__":
    port_str = os.environ.get("PORT", "5000")
    try:
        port = int(port_str)
    except ValueError:
        logger.warning(
            "Invalid PORT environment variable: %s, defaulting to 5000", port_str
        )
        port = 5000
    # Only enable debug and 0.0.0.0 binding if explicitly set for development
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    # SECURITY WARNING: Binding to 0.0.0.0 is only enabled if FLASK_DEBUG=1 (development only).
    host = "0.0.0.0" if debug_mode else "127.0.0.1"  # noqa: S104
    app.run(host=host, port=port, debug=debug_mode)
