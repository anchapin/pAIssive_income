"""
Integration tests for API gateway functionality.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
import pytest
import requests

from services.errors import AuthenticationError, RateLimitExceededError, RoutingError
from services.gateway import (
    APIGateway,
    AuthManager,
    GatewayConfig,
    RateLimiter,
    RouteManager,
)


class TestAPIGateway:
    """Integration tests for API gateway functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = GatewayConfig(
            host="localhost",
            port=8000,
            jwt_secret="test_secret",
            rate_limit_window=60,  # seconds
            rate_limit_max_requests=100,
            auth_cache_ttl=300,  # seconds
        )
        self.gateway = APIGateway(self.config)
        self.route_manager = RouteManager(self.config)
        self.auth_manager = AuthManager(self.config)
        self.rate_limiter = RateLimiter(self.config)

        # Start gateway in test mode
        self.gateway.start(test_mode=True)

    def teardown_method(self):
        """Clean up after tests."""
        self.gateway.stop()

    def test_request_routing(self):
        """Test request routing functionality."""
        # Register test routes
        routes = [
            {
                "path": "/api/v1/users",
                "service": "user-service",
                "methods": ["GET", "POST"],
                "version": "1.0",
                "timeout": 5000,
            },
            {
                "path": "/api/v1/orders",
                "service": "order-service",
                "methods": ["GET", "POST", "PUT"],
                "version": "1.0",
                "timeout": 10000,
            },
        ]

        for route in routes:
            self.route_manager.register_route(**route)

        # Test route resolution
        resolved = self.route_manager.resolve_route(path="/api/v1/users", method="GET")
        assert resolved["service"] == "user-service"
        assert "GET" in resolved["methods"]

        # Test version-based routing
        self.route_manager.register_route(
            path="/api/v2/users",
            service="user-service-v2",
            methods=["GET"],
            version="2.0",
        )

        v2_route = self.route_manager.resolve_route(path="/api/v2/users", method="GET")
        assert v2_route["service"] == "user-service-v2"
        assert v2_route["version"] == "2.0"

        # Test method not allowed
        with pytest.raises(RoutingError) as exc:
            self.route_manager.resolve_route(path="/api/v1/users", method="DELETE")
        assert "Method not allowed" in str(exc.value)

        # Test route not found
        with pytest.raises(RoutingError) as exc:
            self.route_manager.resolve_route(path="/api/v1/invalid", method="GET")
        assert "Route not found" in str(exc.value)

    def test_authentication(self):
        """Test authentication and authorization."""
        # Create test JWT token
        payload = {
            "user_id": "123",
            "roles": ["user"],
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, self.config.jwt_secret, algorithm="HS256")

        # Test successful authentication
        auth_result = self.auth_manager.authenticate(token)
        assert auth_result["authenticated"] is True
        assert auth_result["user_id"] == "123"
        assert "user" in auth_result["roles"]

        # Test expired token
        expired_payload = {
            "user_id": "123",
            "roles": ["user"],
            "exp": datetime.utcnow() - timedelta(hours=1),
        }
        expired_token = jwt.encode(
            expired_payload, self.config.jwt_secret, algorithm="HS256"
        )

        with pytest.raises(AuthenticationError) as exc:
            self.auth_manager.authenticate(expired_token)
        assert "Token has expired" in str(exc.value)

        # Test invalid token
        with pytest.raises(AuthenticationError):
            self.auth_manager.authenticate("invalid.token.here")

        # Test role-based authorization
        admin_payload = {
            "user_id": "456",
            "roles": ["admin"],
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        admin_token = jwt.encode(
            admin_payload, self.config.jwt_secret, algorithm="HS256"
        )

        # Admin can access admin routes
        assert self.auth_manager.authorize(admin_token, required_role="admin")

        # Regular user cannot access admin routes
        assert not self.auth_manager.authorize(token, required_role="admin")

        # Test token caching
        with patch("services.gateway.AuthManager._verify_token") as mock_verify:
            # First call should verify
            self.auth_manager.authenticate(token)
            assert mock_verify.called

            # Second call should use cache
            mock_verify.reset_mock()
            self.auth_manager.authenticate(token)
            assert not mock_verify.called

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        client_id = "test_client"
        path = "/api/test"

        # Test successful requests within limit
        for _ in range(5):
            assert self.rate_limiter.check_rate_limit(client_id, path)

        # Test rate limit info
        limit_info = self.rate_limiter.get_limit_info(client_id, path)
        assert limit_info["remaining"] == self.config.rate_limit_max_requests - 5
        assert limit_info["reset_time"] is not None

        # Test rate limit exceeded
        self.rate_limiter.update_config(max_requests=5, window=60)

        # Next request should fail
        with pytest.raises(RateLimitExceededError) as exc:
            self.rate_limiter.check_rate_limit(client_id, path)
        assert "Rate limit exceeded" in str(exc.value)

        # Test rate limit reset
        self.rate_limiter.reset_limits(client_id)
        assert self.rate_limiter.check_rate_limit(client_id, path)

        # Test different paths have separate limits
        other_path = "/api/other"
        assert self.rate_limiter.check_rate_limit(client_id, other_path)

    def test_request_lifecycle(self):
        """Test complete request lifecycle through gateway."""
        # Setup test route
        self.route_manager.register_route(
            path="/api/test", service="test-service", methods=["GET"], version="1.0"
        )

        # Create auth token
        token = jwt.encode(
            {
                "user_id": "123",
                "roles": ["user"],
                "exp": datetime.utcnow() + timedelta(hours=1),
            },
            self.config.jwt_secret,
            algorithm="HS256",
        )

        # Mock backend service
        with patch("services.gateway.APIGateway._forward_request") as mock_forward:
            mock_forward.return_value = {"status": 200, "data": {"message": "success"}}

            # Make request through gateway
            response = requests.get(
                "http://localhost:8000/api/test",
                headers={"Authorization": f"Bearer {token}"},
            )

            # Verify response
            assert response.status_code == 200
            assert response.json()["message"] == "success"

            # Verify request was properly processed
            mock_forward.assert_called_once()
            call_args = mock_forward.call_args[0][0]
            assert call_args["path"] == "/api/test"
            assert call_args["method"] == "GET"
            assert call_args["user_id"] == "123"

    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test invalid route configuration
        with pytest.raises(RoutingError):
            self.route_manager.register_route(
                path="/invalid/path/",  # Missing leading /api
                service="test-service",
                methods=["GET"],
            )

        # Test service timeout
        self.route_manager.register_route(
            path="/api/slow",
            service="slow-service",
            methods=["GET"],
            timeout=100,  # Very short timeout
        )

        with patch("services.gateway.APIGateway._forward_request") as mock_forward:
            mock_forward.side_effect = TimeoutError("Service timeout")

            response = requests.get("http://localhost:8000/api/slow")
            assert response.status_code == 504  # Gateway Timeout

        # Test service unavailable
        with patch("services.gateway.APIGateway._forward_request") as mock_forward:
            mock_forward.side_effect = ConnectionError("Service unavailable")

            response = requests.get("http://localhost:8000/api/test")
            assert response.status_code == 503  # Service Unavailable

    def test_request_transformation(self):
        """Test request/response transformation."""
        # Register route with transforms
        self.route_manager.register_route(
            path="/api/transform",
            service="transform-service",
            methods=["POST"],
            request_transform="camelToSnake",
            response_transform="snakeToCamel",
        )

        # Test request with camelCase
        request_data = {"userId": 123, "firstName": "John", "lastName": "Doe"}

        with patch("services.gateway.APIGateway._forward_request") as mock_forward:
            mock_forward.return_value = {
                "status": 200,
                "data": {"user_id": 123, "full_name": "John Doe"},
            }

            response = requests.post(
                "http://localhost:8000/api/transform", json=request_data
            )

            # Verify request transformation
            call_args = mock_forward.call_args[0][0]
            assert "user_id" in call_args["body"]
            assert "first_name" in call_args["body"]
            assert "last_name" in call_args["body"]

            # Verify response transformation
            response_data = response.json()
            assert "userId" in response_data
            assert "fullName" in response_data


if __name__ == "__main__":
    pytest.main(["-v", "test_api_gateway.py"])
