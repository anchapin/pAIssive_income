"""run_ui - Module for run_ui."""

# Standard library imports
import logging
import os
import sys
from typing import Any, Dict, Tuple

# Third-party imports
from flask import create_app, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Create Flask application
try:
    logger.info("Creating Flask application...")
    app = create_app()
    logger.info("Flask application created successfully")
except Exception:
    logger.exception("Error creating Flask application")
    raise


# Add health check endpoint
@app.route("/health")
def health_check() -> Tuple[Dict[str, Any], int]:
    """Return health status.

    Returns:
        Tuple[Dict[str, Any], int]: JSON response with health status and HTTP status code
    """
    health_status: Dict[str, Any] = {"status": "healthy", "components": {}}

    # Check application status
    health_status["components"]["app"] = "running"

    # Check database connection
    try:
        from app_flask import db

        db.session.execute("SELECT 1")
        db.session.commit()
        logger.info("Health check: Database connection successful")
        health_status["components"]["database"] = "connected"
    except Exception as e:
        logger.warning(f"Health check: Database connection issue: {e!s}")
        health_status["components"]["database"] = "error"
        # Don't fail the entire health check just because of database issues
        # This allows the container to start and potentially recover

    # For initial startup, we'll consider the app healthy even if the database isn't ready yet
    # This prevents Docker from restarting the container repeatedly during initialization
    logger.info(f"Health check result: {health_status}")
    return jsonify(health_status), 200


if __name__ == "__main__":
    # Wait for database to be ready
    logger.info("Starting Flask application...")
    port = int(os.environ.get("PORT", "5000"))

    try:
        app.run(host="0.0.0.0", port=port)
    except Exception:
        logger.exception("Error starting Flask application")
        sys.exit(1)
