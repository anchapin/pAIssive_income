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
    try:
        # Check database connection
        from app_flask import db

        db.session.execute("SELECT 1")
        db.session.commit()
        logger.info("Health check: Database connection successful")
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logger.exception("Health check: Database connection failed")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == "__main__":
    # Wait for database to be ready
    max_retries = 10
    retry_interval = 5

    logger.info("Starting Flask application...")
    port = int(os.environ.get("PORT", "5000"))

    try:
        app.run(host="0.0.0.0", port=port)
    except Exception:
        logger.exception("Error starting Flask application")
        sys.exit(1)
