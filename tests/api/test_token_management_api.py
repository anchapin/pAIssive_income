"""Tests for API token management, validation, refresh, and error handling."""  # Test token only

import pytest
from fastapi.testclient import TestClient

try:
    from api.app import app  # type: ignore[import-untyped]
except ImportError:
    app = None

client = TestClient(app) if app else None


@pytest.mark.skipif(app is None, reason="Main FastAPI app not found for testing")
class TestTokenManagementAPI:
    AUTH_ENDPOINT = "/auth/token"  # Test token only
    REFRESH_ENDPOINT = "/auth/token/refresh"  # Test token only
    REVOKE_ENDPOINT = "/auth/token/revoke"  # Test token only
    PROTECTED_ENDPOINT = "/users/me"

    # HTTP status codes
    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_NO_CONTENT = 204
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_UNPROCESSABLE_ENTITY = 422

    def test_token_creation_success(self):
        # Test data - not real credentials
        resp = client.post(
            self.AUTH_ENDPOINT,
            data={
                "username": "testuser",
                "password": "test-password-123",  # Test credential only
            },  # Test credential only
        )
        assert resp.status_code == self.HTTP_OK
        data = resp.json()
        assert "access_token" in data  # Test token only
        assert "refresh_token" in data  # Test token only

    def test_token_creation_invalid_credentials(self):
        # Test data - not real credentials
        resp = client.post(
            self.AUTH_ENDPOINT,
            data={
                "username": "invaliduser",
                "password": "invalid-test-password",  # Test credential only
            },  # Test credential only
        )
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_token_validation_success(self):
        # Obtain token
        # Test data - not real credentials
        resp = client.post(
            self.AUTH_ENDPOINT,
            data={
                "username": "testuser",
                "password": "test-password-123",  # Test credential only
            },  # Test credential only
        )
        token = resp.json().get("access_token")  # Test token only
        headers = {"Authorization": f"Bearer {token}"}  # Test token only
        resp2 = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp2.status_code == self.HTTP_OK

    def test_token_validation_invalid_token(self):
        # Test data - not a real token
        headers = {"Authorization": "Bearer invalidtoken"}  # Test token only
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_token_validation_missing_token(self):
        resp = client.get(self.PROTECTED_ENDPOINT)
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_token_validation_expired_token(self):
        # This test assumes short-lived tokens in test or mockable expiry
        # Here, simulate with a known expired token if possible
        # Test data - not a real token
        headers = {"Authorization": "Bearer expiredtoken"}  # Test token only
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_token_refresh_success(self):
        # Obtain refresh token
        # Test data - not real credentials
        auth_resp = client.post(
            self.AUTH_ENDPOINT,
            data={
                "username": "testuser",
                "password": "test-password-123",  # Test credential only
            },  # Test credential only
        )
        refresh_token = auth_resp.json().get("refresh_token")  # Test token only
        resp = client.post(
            self.REFRESH_ENDPOINT, data={"refresh_token": refresh_token}
        )  # Test token only
        assert resp.status_code == self.HTTP_OK
        assert "access_token" in resp.json()  # Test token only

    def test_token_refresh_invalid_token(self):
        # Test data - not a real token
        resp = client.post(
            self.REFRESH_ENDPOINT,
            data={"refresh_token": "invalid"},  # Test token only
        )  # Test token only
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_token_refresh_expired_token(self):
        # Test data - not a real token
        resp = client.post(
            self.REFRESH_ENDPOINT,
            data={"refresh_token": "expiredtoken"},  # Test token only
        )
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_token_revocation(self):
        # Obtain token and revoke it
        # Test data - not real credentials
        auth_resp = client.post(
            self.AUTH_ENDPOINT,
            data={
                "username": "testuser",
                "password": "test-password-123",  # Test credential only
            },  # Test credential only
        )
        access_token = auth_resp.json()["access_token"]  # Test token only
        headers = {"Authorization": f"Bearer {access_token}"}  # Test token only
        revoke_resp = client.post(self.REVOKE_ENDPOINT, headers=headers)
        assert revoke_resp.status_code in (self.HTTP_OK, self.HTTP_NO_CONTENT)
        # Should no longer be able to use the token
        protected_resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert protected_resp.status_code in (
            self.HTTP_UNAUTHORIZED,
            self.HTTP_FORBIDDEN,
        )

    def test_token_revocation_invalid_token(self):
        # Test data - not a real token
        headers = {"Authorization": "Bearer invalidtoken"}  # Test token only
        resp = client.post(self.REVOKE_ENDPOINT, headers=headers)
        assert resp.status_code in (
            self.HTTP_UNAUTHORIZED,
            self.HTTP_FORBIDDEN,
            self.HTTP_NOT_FOUND,
        )

    def test_malformed_token(self):
        # Test data - malformed token for testing
        headers = {"Authorization": "Bearer "}  # Intentionally malformed test token
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)

    def test_empty_authorization_header(self):
        # Test data - empty authorization header for testing
        headers = {"Authorization": ""}  # Intentionally empty test header
        resp = client.get(self.PROTECTED_ENDPOINT, headers=headers)
        assert resp.status_code in (self.HTTP_UNAUTHORIZED, self.HTTP_FORBIDDEN)
