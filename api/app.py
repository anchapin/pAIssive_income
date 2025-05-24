"""app - Module for api.app."""

import os

# Import and register the password reset/auth blueprint
from api.routes.auth import auth_bp
from flask import Flask


def create_app():
    app = Flask(__name__)
    # Register the password reset/auth endpoints
    app.register_blueprint(auth_bp)
    return app


# For local dev/testing: `python -m api.app` will launch the app
if __name__ == "__main__":
    app = create_app()
    # Only enable debug mode in development environment, never in production
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug_mode)
