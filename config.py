"""config.py - Configuration for Flask app and SQLAlchemy."""

import os


class Config:
    # Use a class variable instead of a property for SQLAlchemy compatibility
    # The class variable is initialized with the default value
    SQLALCHEMY_DATABASE_URI = "postgresql://myuser:mypassword@db:5433/mydb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        # Override the class variable with the environment variable if it exists
        env_uri = os.environ.get("DATABASE_URL")
        if env_uri:
            self.SQLALCHEMY_DATABASE_URI = env_uri
