"""test_user_api - Tests for User API endpoints, edge cases, and error handling."""

import pytest

from fastapi.testclient import TestClient

try:
    from api.main import app  # Adjust import if main FastAPI app is elsewhere
except ImportError:
    app = None

client = TestClient(app) if app else None


@pytest.mark.skipif(app is None, reason="Main FastAPI app not found for testing")
class TestUserAPI:
    def test_create_user_success(self):
        # Test data - not real credentials
        response = client.post(
            "/users/",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPassword123!",  # Test credential only
            },
        )
        assert response.status_code == 201
        assert response.json()["username"] == "newuser"

    def test_create_user_missing_fields(self):
        response = client.post("/users/", json={"username": "incomplete"})
        assert response.status_code == 422

    def test_get_user_success(self):
        # Setup: Create user
        # Test data - not real credentials
        post_resp = client.post(
            "/users/",
            json={
                "username": "getme",
                "email": "getme@example.com",
                "password": "StrongPassword123!",  # Test credential only
            },
        )
        user_id = post_resp.json().get("id")
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "getme"

    def test_get_user_not_found(self):
        response = client.get("/users/999999")
        assert response.status_code == 404

    def test_update_user_success(self):
        # Setup: Create user
        # Test data - not real credentials
        post_resp = client.post(
            "/users/",
            json={
                "username": "updateu",
                "email": "updateu@example.com",
                "password": "StrongPassword123!",  # Test credential only
            },
        )
        user_id = post_resp.json().get("id")
        response = client.put(
            f"/users/{user_id}", json={"email": "updated@example.com"}
        )
        assert response.status_code in (200, 202)
        assert response.json()["email"] == "updated@example.com"

    def test_update_user_not_found(self):
        response = client.put("/users/999999", json={"email": "notfound@example.com"})
        assert response.status_code == 404

    def test_delete_user_success(self):
        # Setup: Create user
        # Test data - not real credentials
        post_resp = client.post(
            "/users/",
            json={
                "username": "delu",
                "email": "delu@example.com",
                "password": "StrongPassword123!",  # Test credential only
            },
        )
        user_id = post_resp.json().get("id")
        response = client.delete(f"/users/{user_id}")
        assert response.status_code in (200, 204)

    def test_delete_user_not_found(self):
        response = client.delete("/users/999999")
        assert response.status_code == 404

    def test_authentication_required(self):
        # Try accessing a protected endpoint with no token
        response = client.get("/users/me")
        assert response.status_code in (401, 403)

    def test_invalid_token(self):
        # Test data - not a real token
        headers = {"Authorization": "Bearer invalidtoken"}  # Test token only
        response = client.get("/users/me", headers=headers)
        assert response.status_code in (401, 403)

    def test_access_forbidden_for_non_admin(self):
        # Simulate a non-admin token if RBAC is implemented
        # Test data - not a real token
        headers = {"Authorization": "Bearer nonadmintoken"}  # Test token only
        response = client.delete("/users/1", headers=headers)
        assert response.status_code in (401, 403, 405)

    def test_email_uniqueness(self):
        # Test data - not real credentials
        client.post(
            "/users/",
            json={
                "username": "unique1",
                "email": "unique@example.com",
                "password": "StrongPassword123!",  # Test credential only
            },
        )
        # Test data - not real credentials
        response = client.post(
            "/users/",
            json={
                "username": "unique2",
                "email": "unique@example.com",
                "password": "StrongPassword123!",  # Test credential only
            },
        )
        assert response.status_code in (400, 409, 422)

    def test_password_strength_validation(self):
        # Test data - intentionally weak password for testing validation
        response = client.post(
            "/users/",
            json={
                "username": "weakpw",
                "email": "weakpw@example.com",
                "password": "123",  # Intentionally weak test password
            },
        )
        assert response.status_code in (400, 422)
