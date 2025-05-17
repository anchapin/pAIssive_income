"""config.py - Configuration for Flask app and SQLAlchemy."""

import os


class Config:
    # Use a property to ensure the environment variable is checked each time
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return os.environ.get(
            "DATABASE_URL", "postgresql://myuser:mypassword@db:5433/mydb"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
