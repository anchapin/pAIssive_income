"""app - Module for api.app."""

from flask import Flask

# Import and register the password reset/auth blueprint
from api.routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    # Register the password reset/auth endpoints
    app.register_blueprint(auth_bp)
    return app

# For local dev/testing: `python -m api.app` will launch the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
