"""Entrypoint for running the Flask UI server."""

import os
from ui.app import create_app

# For production deployment, prefer Gunicorn:
#   gunicorn ui.app:create_app --bind 0.0.0.0:8000

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)