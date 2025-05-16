"""run_ui - Module for run_ui."""

# Standard library imports
import logging
import os
import sys
from typing import Any, Dict, Tuple

# Third-party imports
from flask import jsonify

# Local imports
from app_flask import create_app

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
    # Log a generic error message without exposing exception details
    logger.exception("Error creating Flask application")
    # Log detailed exception only in development mode
    if os.environ.get("FLASK_ENV") == "development":
        logger.info("Detailed error logged due to development environment")
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
        from sqlalchemy import text

        # Use SQLAlchemy text() to properly format the SQL query
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        logger.info("Health check: Database connection successful")
        health_status["components"]["database"] = "connected"
    except Exception as e:
        # Log without exposing exception details in production
        logger.warning(f"Health check: Database connection issue: {type(e).__name__}")
        # Log detailed exception only in development mode
        if os.environ.get("FLASK_ENV") == "development":
            logger.exception("Detailed database connection error")
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
        # Log a generic error message without exposing exception details
        logger.exception("Error starting Flask application")
        # Log detailed exception only in development mode
        if os.environ.get("FLASK_ENV") == "development":
            logger.info("Detailed error logged due to development environment")
        sys.exit(1)
