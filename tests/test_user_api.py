"""Test the user API endpoints with the ORM/database."""

import pytest
from flask import Flask
from flask import json
from flask import current_app

from flask.models import db
from flask.__init__ import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_and_authenticate_user(client):
    # Create a user
    response = client.post(
        "/api/users/",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

    # Authenticate the user
    response = client.post(
        "/api/users/authenticate",
        json={"username_or_email": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "testuser@example.com"
