"""
ARTIST experiment runner.

This script provides a simple Flask application for running ARTIST experiments.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

from flask import Flask, Response, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(Path("artist_experiments/logs/app.log")),
        logging.StreamHandler(),
    ],
)
logger: Final = logging.getLogger(__name__)

# Create Flask app
app: Final = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check() -> Response:
    """
    Perform a health check.

    Returns:
        Response: Health status information as JSON response

    """
    return jsonify({"status": "healthy", "service": "artist-experiments"})


@app.route("/", methods=["GET"])
def home() -> Response:
    """
    Home endpoint.

    Returns:
        Response: Welcome message as JSON response

    """
    return jsonify(
        {
            "message": "Welcome to ARTIST Experiments",
            "description": "This service provides endpoints for running ARTIST experiments.",
        }
    )


@app.route("/experiments", methods=["GET"])
def list_experiments() -> Response:
    """
    List available experiments.

    Returns:
        Response: List of available experiments as JSON response

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
    port: int = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "127.0.0.1")  # Default to localhost
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host=host, port=port, debug=debug)
