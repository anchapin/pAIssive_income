"""config.py - Configuration for Flask app and SQLAlchemy."""

import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://myuser:mypassword@db:5433/mydb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
