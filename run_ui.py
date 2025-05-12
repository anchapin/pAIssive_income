"""run_ui - Module for run_ui."""

# Standard library imports
import os

# Local imports
# Third-party imports
from flask import create_app, jsonify

app = create_app()


# Add health check endpoint
@app.route("/health")
def health_check() -> tuple:
    """Return health status."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
