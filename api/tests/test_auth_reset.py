import pytest

from api.app import create_app
from api.routes.auth import RESET_TOKENS


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_forgot_password_success(client):
    # Request a reset for a known user
    resp = client.post("/api/auth/forgot-password", json={"email": "e2euser@example.com"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reset link will be sent" in data["message"].lower()
    # A token should be generated
    assert any(v["email"] == "e2euser@example.com" for v in RESET_TOKENS.values())

def test_forgot_password_unknown_email(client):
    resp = client.post("/api/auth/forgot-password", json={"email": "notarealuser@fake.com"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reset link will be sent" in data["message"].lower()

def test_reset_password_success(client):
    # Simulate requesting a reset to get a token
    client.post("/api/auth/forgot-password", json={"email": "e2euser@example.com"})
    token = next(k for k, v in RESET_TOKENS.items() if v["email"] == "e2euser@example.com")
    resp = client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "MyNewSecurePassword123!"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "password has been reset" in data["message"].lower()
    assert token not in RESET_TOKENS

def test_reset_password_invalid_token(client):
    resp = client.post("/api/auth/reset-password", json={
        "token": "not-a-real-token",
        "new_password": "irrelevant"
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert "invalid" in data["message"].lower()

def test_reset_password_missing_fields(client):
    resp = client.post("/api/auth/reset-password", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "missing" in data["message"].lower()