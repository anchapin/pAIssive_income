"""
Integration tests for API gateway with circuit breaker.

This module contains integration tests for the API gateway service
with circuit breaker pattern for resilience.
"""

import json
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests

from services.gateway import APIGateway, AuthManager, GatewayConfig, RateLimiter, 
    RouteManager
from services.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    FailureDetector,
    FallbackHandler,
)


class TestAPIGatewayCircuitBreaker:
    """Integration tests for API gateway with circuit breaker."""

    def setup_method(self):
        """Set up test fixtures."""
        # Gateway configuration
        self.gateway_config = GatewayConfig(
            host="localhost",
            port=8000,
            jwt_secret="test_secret",
            rate_limit_window=60,  # seconds
            rate_limit_max_requests=100,
            auth_cache_ttl=300,  # seconds
        )

        # Circuit breaker configuration
        self.circuit_config = CircuitBreakerConfig(
            failure_threshold=3,
            reset_timeout=10,  # seconds
            half_open_requests=2,
            failure_window=60,  # seconds
            min_throughput=5,
        )

        # Initialize components
        self.gateway = APIGateway(self.gateway_config)
        self.route_manager = RouteManager(self.gateway_config)
        self.circuit_breaker = CircuitBreaker(self.circuit_config)
        self.fallback_handler = FallbackHandler()

        # Register test routes
        self.routes = [
            {
                "path": " / api / users",
                "service": "user - service",
                "methods": ["GET", "POST"],
                "version": "1.0",
                "timeout": 5000,
            },
            {
                "path": " / api / orders",
                "service": "order - service",
                "methods": ["GET", "POST", "PUT"],
                "version": "1.0",
                "timeout": 10000,
            },
            {
                "path": " / api / products",
                "service": "product - service",
                "methods": ["GET"],
                "version": "1.0",
                "timeout": 5000,
            },
        ]

        for route in self.routes:
            self.route_manager.register_route(**route)

        # Register fallback handlers
        self.fallback_handler.register_fallback(
            "user - service",
            lambda error: {"status": "fallback", "service": "user - service", 
                "error": str(error)},
        )
        self.fallback_handler.register_fallback(
            "order - service",
            lambda error: {"status": "fallback", "service": "order - service", 
                "error": str(error)},
        )
        self.fallback_handler.register_fallback(
            "product - service",
            lambda error: {"status": "fallback", "service": "product - service", 
                "error": str(error)},
        )

        # Start gateway in test mode
        self.gateway.start(test_mode=True)

    def teardown_method(self):
        """Clean up after tests."""
        self.gateway.stop()

    def test_circuit_breaker_integration(self):
        """Test integration of API gateway with circuit breaker."""
        # Mock service responses
        service_responses = {
            "user - service": {"status": 200, "data": {"users": [{"id": 1, 
                "name": "Test User"}]}},
            "order - service": {"status": 200, "data": {"orders": [{"id": 1, 
                "user_id": 1}]}},
            "product - service": {
                "status": 200,
                "data": {"products": [{"id": 1, "name": "Test Product"}]},
            },
        }

        # Mock service failures
        service_failures = {"user - service": False, "order - service": False, 
            "product - service": False}

        # Mock forward request method
        def mock_forward_request(request_data):
            """Mock forwarding requests to backend services."""
            service = request_data.get("service")

            # Check if service should fail
            if service_failures.get(service, False):
                raise ConnectionError(f"Service unavailable: {service}")

            # Return mock response
            return service_responses.get(
                service, {"status": 404, "data": {"error": "Service not found"}}
            )

        # Patch the forward request method
        with patch(
            "services.gateway.APIGateway._forward_request", 
                side_effect=mock_forward_request
        ):
            # Test successful requests
            response = requests.get("http://localhost:8000 / api / users", timeout=30)
            assert response.status_code == 200
            assert "users" in response.json()

            response = requests.get("http://localhost:8000 / api / orders", timeout=30)
            assert response.status_code == 200
            assert "orders" in response.json()

            # Make user - service fail
            service_failures["user - service"] = True

            # Integrate circuit breaker with gateway
            def circuit_wrapped_forward(request_data):
                """Wrap forward request with circuit breaker."""
                service = request_data.get("service")

                try:
                    # Execute request through circuit breaker
                    return self.circuit_breaker.execute_with_fallback(
                        service, lambda: mock_forward_request(request_data), 
                            self.fallback_handler
                    )
                except Exception as e:
                    # If circuit breaker fails, return error response
                    return {"status": 503, "data": {"error": str(e)}}

            # Replace the forward method with circuit - wrapped version
            with patch(
                "services.gateway.APIGateway._forward_request", 
                    side_effect=circuit_wrapped_forward
            ):
                # First few requests should fail but not trip the circuit
                for _ in range(2):
                    response = requests.get("http://localhost:8000 / api / users", 
                        timeout=30)
                    assert response.status_code in (503, 500)

                # Next request should trip the circuit
                response = requests.get("http://localhost:8000 / api / users", 
                    timeout=30)
                assert response.status_code in (503, 500)

                # Verify circuit is open for user - service
                assert self.circuit_breaker.get_state("user - \
                    service") == CircuitState.OPEN

                # Subsequent requests should use fallback
                response = requests.get("http://localhost:8000 / api / users", 
                    timeout=30)
                assert response.status_code == 200
                assert response.json()["status"] == "fallback"
                assert response.json()["service"] == "user - service"

                # Other services should still work
                response = requests.get("http://localhost:8000 / api / orders", 
                    timeout=30)
                assert response.status_code == 200
                assert "orders" in response.json()

                # Fix the user - service
                service_failures["user - service"] = False

                # Wait for circuit to go to half - open state
                time.sleep(self.circuit_config.reset_timeout)

                # Circuit should be half - open now
                assert self.circuit_breaker.get_state("user - \
                    service") == CircuitState.HALF_OPEN

                # Next request should succeed and close the circuit
                response = requests.get("http://localhost:8000 / api / users", 
                    timeout=30)
                assert response.status_code == 200
                assert "users" in response.json()

                # One more successful request to fully close the circuit
                response = requests.get("http://localhost:8000 / api / users", 
                    timeout=30)
                assert response.status_code == 200

                # Circuit should be closed now
                assert self.circuit_breaker.get_state("user - \
                    service") == CircuitState.CLOSED

    def test_multiple_service_failures(self):
        """Test handling multiple service failures simultaneously."""
        # Mock service responses
        service_responses = {
            "user - service": {"status": 200, "data": {"users": [{"id": 1, 
                "name": "Test User"}]}},
            "order - service": {"status": 200, "data": {"orders": [{"id": 1, 
                "user_id": 1}]}},
            "product - service": {
                "status": 200,
                "data": {"products": [{"id": 1, "name": "Test Product"}]},
            },
        }

        # All services start as healthy
        service_failures = {"user - service": False, "order - service": False, 
            "product - service": False}

        # Mock forward request method
        def mock_forward_request(request_data):
            """Mock forwarding requests to backend services."""
            service = request_data.get("service")

            # Check if service should fail
            if service_failures.get(service, False):
                raise ConnectionError(f"Service unavailable: {service}")

            # Return mock response
            return service_responses.get(
                service, {"status": 404, "data": {"error": "Service not found"}}
            )

        # Integrate circuit breaker with gateway
        def circuit_wrapped_forward(request_data):
            """Wrap forward request with circuit breaker."""
            service = request_data.get("service")

            try:
                # Execute request through circuit breaker
                return self.circuit_breaker.execute_with_fallback(
                    service, lambda: mock_forward_request(request_data), 
                        self.fallback_handler
                )
            except Exception as e:
                # If circuit breaker fails, return error response
                return {"status": 503, "data": {"error": str(e)}}

        # Patch the forward request method
        with patch(
            "services.gateway.APIGateway._forward_request", 
                side_effect=circuit_wrapped_forward
        ):
            # Make multiple services fail
            service_failures["user - service"] = True
            service_failures["order - service"] = True

            # Trip the circuit for both services
            for _ in range(self.circuit_config.failure_threshold):
                requests.get("http://localhost:8000 / api / users", timeout=30)
                requests.get("http://localhost:8000 / api / orders", timeout=30)

            # Verify circuits are open
            assert self.circuit_breaker.get_state("user - service") == CircuitState.OPEN
            assert self.circuit_breaker.get_state("order - \
                service") == CircuitState.OPEN

            # Verify fallbacks are used
            response = requests.get("http://localhost:8000 / api / users", timeout=30)
            assert response.status_code == 200
            assert response.json()["status"] == "fallback"
            assert response.json()["service"] == "user - service"

            response = requests.get("http://localhost:8000 / api / orders", timeout=30)
            assert response.status_code == 200
            assert response.json()["status"] == "fallback"
            assert response.json()["service"] == "order - service"

            # Product service should still work
            response = requests.get("http://localhost:8000 / api / products", 
                timeout=30)
            assert response.status_code == 200
            assert "products" in response.json()

            # Fix one service
            service_failures["user - service"] = False

            # Wait for circuit to go to half - open state
            time.sleep(self.circuit_config.reset_timeout)

            # User service circuit should recover
            response = requests.get("http://localhost:8000 / api / users", timeout=30)
            assert response.status_code == 200
            assert "users" in response.json()

            # Order service should still use fallback
            response = requests.get("http://localhost:8000 / api / orders", timeout=30)
            assert response.status_code == 200
            assert response.json()["status"] == "fallback"

            # Fix the other service
            service_failures["order - service"] = False

            # Wait for circuit to go to half - open state
            time.sleep(self.circuit_config.reset_timeout)

            # Order service circuit should recover
            response = requests.get("http://localhost:8000 / api / orders", timeout=30)
            assert response.status_code == 200
            assert "orders" in response.json()

            # All services should be working now
            assert self.circuit_breaker.get_state("user - \
                service") == CircuitState.CLOSED
            assert self.circuit_breaker.get_state("order - \
                service") == CircuitState.CLOSED

    def test_partial_failures(self):
        """Test handling partial failures in services."""

        # Mock service with partial failures
        def mock_product_service(request_data):
            """Mock product service with occasional failures."""
            # Fail every third request
            if getattr(mock_product_service, "counter", 0) % 3 == 0:
                mock_product_service.counter = getattr(mock_product_service, "counter", 
                    0) + 1
                raise ConnectionError("Service temporarily unavailable")

            mock_product_service.counter = getattr(mock_product_service, "counter", 
                0) + 1
            return {"status": 200, "data": {"products": [{"id": 1, 
                "name": "Test Product"}]}}

        # Mock forward request method
        def mock_forward_request(request_data):
            """Mock forwarding requests to backend services."""
            service = request_data.get("service")

            if service == "product - service":
                return mock_product_service(request_data)

            # Other services work normally
            return {"status": 200, "data": {"message": f"{service} response"}}

        # Integrate circuit breaker with gateway
        def circuit_wrapped_forward(request_data):
            """Wrap forward request with circuit breaker."""
            service = request_data.get("service")

            try:
                # Execute request through circuit breaker
                return self.circuit_breaker.execute_with_fallback(
                    service, lambda: mock_forward_request(request_data), 
                        self.fallback_handler
                )
            except Exception as e:
                # If circuit breaker fails, return error response
                return {"status": 503, "data": {"error": str(e)}}

        # Patch the forward request method
        with patch(
            "services.gateway.APIGateway._forward_request", 
                side_effect=circuit_wrapped_forward
        ):
            # Configure circuit breaker for higher threshold
            self.circuit_breaker = CircuitBreaker(
                CircuitBreakerConfig(
                    failure_threshold=5,  # Higher threshold for partial failures
                    reset_timeout=10,
                    half_open_requests=2,
                    failure_window=60,
                    min_throughput=5,
                )
            )

            # Make several requests to product service
            responses = []
            for _ in range(10):
                response = requests.get("http://localhost:8000 / api / products", 
                    timeout=30)
                responses.append(response.status_code)

            # Some requests should fail, but circuit should stay closed
            assert 503 in responses or 500 in responses
            assert 200 in responses
            assert self.circuit_breaker.get_state("product - \
                service") != CircuitState.OPEN

            # Get circuit breaker metrics
            metrics = self.circuit_breaker.get_metrics("product - service")

            # Verify error rate is tracked
            assert metrics["error_rate"] > 0
            assert metrics["error_rate"] < 1.0  # Not all requests failed

            # Verify success and failure counts
            assert metrics["success_count"] > 0
            assert metrics["failure_count"] > 0

            # Make the service fail consistently
            def always_fail(request_data):
                raise ConnectionError("Service unavailable")

            # Replace the product service mock
            mock_product_service = always_fail

            # Make enough requests to trip the circuit
            for _ in range(5):
                requests.get("http://localhost:8000 / api / products", timeout=30)

            # Circuit should be open now
            assert self.circuit_breaker.get_state("product - \
                service") == CircuitState.OPEN

            # Requests should use fallback
            response = requests.get("http://localhost:8000 / api / products", 
                timeout=30)
            assert response.status_code == 200
            assert response.json()["status"] == "fallback"
            assert response.json()["service"] == "product - service"


if __name__ == "__main__":
    pytest.main([" - v", "test_api_gateway_circuit_breaker.py"])
