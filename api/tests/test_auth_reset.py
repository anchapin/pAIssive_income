"""Test module for authentication reset functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from api.app import create_app
from api.routes.auth import PasswordResetToken, SessionLocal

if TYPE_CHECKING:
    from flask.testing import FlaskClient

# HTTP status codes
HTTP_OK = 200
HTTP_BAD_REQUEST = 400


@pytest.fixture
def client() -> FlaskClient:
    """
    Create a test client for the Flask application.

    Returns:
        FlaskClient: Test client for making HTTP requests.

    """
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_forgot_password_success(client: FlaskClient) -> None:
    """
    Test successful password reset request for known user.

    Args:
        client: Flask test client fixture.

    """
    # Request a reset for a known user
    resp = client.post(
        "/api/auth/forgot-password", json={"email": "e2euser@example.com"}
    )
    assert resp.status_code == HTTP_OK  # noqa: S101
    data = resp.get_json()
    assert "reset link will be sent" in data["message"].lower()  # noqa: S101

    # Check that a token was generated in the database
    session = SessionLocal()
    try:
        token = (
            session.query(PasswordResetToken)
            .filter_by(email="e2euser@example.com")
            .first()
        )
        assert token is not None  # noqa: S101
    finally:
        session.close()


def test_forgot_password_unknown_email(client: FlaskClient) -> None:
    """
    Test password reset request for unknown email.

    Args:
        client: Flask test client fixture.

    """
    resp = client.post(
        "/api/auth/forgot-password", json={"email": "notarealuser@fake.com"}
    )
    assert resp.status_code == HTTP_OK  # noqa: S101
    data = resp.get_json()
    assert "reset link will be sent" in data["message"].lower()  # noqa: S101


def test_reset_password_success(client: FlaskClient) -> None:
    """
    Test successful password reset with valid token.

    Args:
        client: Flask test client fixture.

    """
    # Simulate requesting a reset to get a token
    client.post("/api/auth/forgot-password", json={"email": "e2euser@example.com"})

    # Get the token from the database
    session = SessionLocal()
    try:
        token_record = (
            session.query(PasswordResetToken)
            .filter_by(email="e2euser@example.com")
            .first()
        )
        assert token_record is not None  # noqa: S101
        token = token_record.token
    finally:
        session.close()

    resp = client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": "MyNewSecurePassword123!"},
    )
    assert resp.status_code == HTTP_OK  # noqa: S101
    data = resp.get_json()
    assert "password has been reset" in data["message"].lower()  # noqa: S101

    # Verify token was deleted from database
    session = SessionLocal()
    try:
        token_record = session.query(PasswordResetToken).filter_by(token=token).first()
        assert token_record is None  # noqa: S101
    finally:
        session.close()


def test_reset_password_invalid_token(client: FlaskClient) -> None:
    """
    Test password reset with invalid token.

    Args:
        client: Flask test client fixture.

    """
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": "not-a-real-token", "new_password": "irrelevant"},
    )
    assert resp.status_code == HTTP_BAD_REQUEST  # noqa: S101
    data = resp.get_json()
    assert "invalid" in data["message"].lower()  # noqa: S101


def test_reset_password_missing_fields(client: FlaskClient) -> None:
    """
    Test password reset with missing required fields.

    Args:
        client: Flask test client fixture.

    """
    resp = client.post("/api/auth/reset-password", json={})
    assert resp.status_code == HTTP_BAD_REQUEST  # noqa: S101
    data = resp.get_json()
    assert "missing" in data["message"].lower()  # noqa: S101
