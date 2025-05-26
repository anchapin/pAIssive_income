"""Test module for authentication reset functionality."""

import pytest
from flask.testing import FlaskClient

from api.app import create_app
from api.routes.auth import RESET_TOKENS

HTTP_OK = 200
HTTP_BAD_REQUEST = 400


@pytest.fixture
def client() -> FlaskClient:
    """
    Create a test client for the Flask app.

    Returns:
        FlaskClient: A Flask test client

    """
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_forgot_password_success(client: FlaskClient) -> None:
    """
    Test that the forgot password endpoint works for a known user.

    Args:
        client: The test client

    """
    # Request a reset for a known user
    resp = client.post(
        "/api/auth/forgot-password", json={"email": "e2euser@example.com"}
    )
    data = resp.get_json()
    assert resp.status_code == HTTP_OK, (
        f"Expected status code {HTTP_OK}, got {resp.status_code}"
    )
    assert "reset link will be sent" in data["message"].lower(), (
        "Reset link message not found in response"
    )
    # A token should be generated
    assert any(v["email"] == "e2euser@example.com" for v in RESET_TOKENS.values()), (
        "Token not generated for the user"
    )


def test_forgot_password_unknown_email(client: FlaskClient) -> None:
    """
    Test that the forgot password endpoint works for unknown users.

    Args:
        client: The test client

    """
    resp = client.post(
        "/api/auth/forgot-password", json={"email": "notarealuser@fake.com"}
    )
    data = resp.get_json()
    assert resp.status_code == HTTP_OK, (
        f"Expected status code {HTTP_OK}, got {resp.status_code}"
    )
    assert "reset link will be sent" in data["message"].lower(), (
        "Reset link message not found in response"
    )


def test_reset_password_success(client: FlaskClient) -> None:
    """
    Test that the password reset endpoint works successfully.

    Args:
        client: The test client

    """
    # Simulate requesting a reset to get a token
    client.post("/api/auth/forgot-password", json={"email": "e2euser@example.com"})
    token = next(
        k for k, v in RESET_TOKENS.items() if v["email"] == "e2euser@example.com"
    )
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": "MyNewSecurePassword123!"},
    )
    data = resp.get_json()
    assert resp.status_code == HTTP_OK, (
        f"Expected status code {HTTP_OK}, got {resp.status_code}"
    )
    assert "password has been reset" in data["message"].lower(), (
        "Password reset message not found in response"
    )
    assert token not in RESET_TOKENS, (
        "Token not removed after successful password reset"
    )


def test_reset_password_invalid_token(client: FlaskClient) -> None:
    """
    Test that reset password fails with an invalid token.

    Args:
        client: The test client to use for the test

    """
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": "not-a-real-token", "new_password": "irrelevant"},
    )
    assert resp.status_code == HTTP_BAD_REQUEST, (
        f"Expected status code {HTTP_BAD_REQUEST}, got {resp.status_code}"
    )
    data = resp.get_json()
    assert "invalid" in data["message"].lower()


def test_reset_password_missing_fields(client: FlaskClient) -> None:
    """
    Test that reset password fails with missing required fields.

    Args:
        client: The test client

    """
    resp = client.post("/api/auth/reset-password", json={})
    data = resp.get_json()
    assert resp.status_code == HTTP_BAD_REQUEST, (
        f"Expected status code {HTTP_BAD_REQUEST}, got {resp.status_code}"
    )
    assert "missing" in data["message"].lower(), (
        "Missing fields message not found in response"
    )
