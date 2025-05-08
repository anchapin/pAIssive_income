"""test_token_management_api - Tests for API token management, validation, refresh, and error handling."""

import pytest
from fastapi.testclient import TestClient
import time

try:
    from api.main import app  # Adjust if FastAPI app is elsewhere
except ImportError:
    app = None

client = TestClient(app) if app else None

@pytest.mark.skipif(app is None, reason="Main FastAPI app not found for testing")
class TestTokenManagementAPI:
    AUTH_ENDPOINT = "/auth/token"
    REFRESH_ENDPOINT = "/auth/token/refresh"
    REVOKE_ENDPOINT = "/auth/token/revoke"
    PROTECTED_ENDPOINT = "/users/me"

    def test_token_creation_success(self):
        resp = client.post(self.AUTH_ENDPOINT, data={
            "username": "testuser",
            "password": "StrongPassword123!"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_token_creation_invalid_credentials(self):
        resp = client.post(self.AUTH_ENDPOINT, data={
            "username": "invaliduser",
            "password": "WrongPassword"
        })
        assert resp.status_code in (401, 403)

    def test_token_validation_success(self):
        # Obtain token
        resp = client.post(self.AUTH_ENDPOINT, data={
            "username": "testuser",
            "password": "StrongPassword123!"
        })
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        resp2 = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp2.status_code == 200

    def test_token_validation_invalid_token(self):
        headers = {"Authorization": "Bearer invalidtoken"}
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (401, 403)

    def test_token_validation_missing_token(self):
        resp = client.get(self.PROTECTED_ENDPOINT)
        assert resp.status_code in (401, 403)

    def test_token_validation_expired_token(self):
        # This test assumes short-lived tokens in test or mockable expiry
        # Here, simulate with a known expired token if possible
        headers = {"Authorization": "Bearer expiredtoken"}
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (401, 403)

    def test_token_refresh_success(self):
        # Obtain refresh token
        auth_resp = client.post(self.AUTH_ENDPOINT, data={
            "username": "testuser",
            "password": "StrongPassword123!"
        })
        refresh_token = auth_resp.json().get("refresh_token")
        resp = client.post(self.REFRESH_ENDPOINT, data={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_token_refresh_invalid_token(self):
        resp = client.post(self.REFRESH_ENDPOINT, data={"refresh_token": "invalid"})
        assert resp.status_code in (401, 403)

    def test_token_refresh_expired_token(self):
        resp = client.post(self.REFRESH_ENDPOINT, data={"refresh_token": "expiredtoken"})
        assert resp.status_code in (401, 403)

    def test_token_revocation(self):
        # Obtain token and revoke it
        auth_resp = client.post(self.AUTH_ENDPOINT, data={
            "username": "testuser",
            "password": "StrongPassword123!"
        })
        access_token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        revoke_resp = client.post(self.REVOKE_ENDPOINT, headers=headers)
        assert revoke_resp.status_code in (200, 204)
        # Should no longer be able to use the token
        protected_resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert protected_resp.status_code in (401, 403)

    def test_token_revocation_invalid_token(self):
        headers = {"Authorization": "Bearer invalidtoken"}
        resp = client.post(self.REVOKE_ENDPOINT, headers=headers)
        assert resp.status_code in (401, 403, 404)

    def test_malformed_token(self):
        headers = {"Authorization": "Bearer "}
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (401, 403)

    def test_empty_authorization_header(self):
        headers = {"Authorization": ""}
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (401, 403)
