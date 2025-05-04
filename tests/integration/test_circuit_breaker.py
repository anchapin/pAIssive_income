"""
Integration tests for circuit breaker functionality.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from services.errors import CircuitBreakerError, ServiceUnavailableError
from services.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    FailureDetector,
    FallbackHandler,
)

class TestCircuitBreaker:
    """Integration tests for circuit breaker functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CircuitBreakerConfig(
            failure_threshold=5,
            reset_timeout=30,  # seconds
            half_open_requests=3,
            failure_window=60,  # seconds
            min_throughput=10,
        )
        self.circuit_breaker = CircuitBreaker(self.config)
        self.failure_detector = FailureDetector(self.config)
        self.fallback_handler = FallbackHandler()

    def test_failure_detection(self):
        """Test failure detection mechanisms."""
        service_name = "test - service"

        # Test successful calls
        for _ in range(10):
            self.failure_detector.record_success(service_name)

        stats = self.failure_detector.get_statistics(service_name)
        assert stats["success_count"] == 10
        assert stats["failure_count"] == 0
        assert stats["error_rate"] == 0.0

        # Test failure threshold
        for _ in range(self.config.failure_threshold):
            self.failure_detector.record_failure(service_name, 
                error=ValueError("Test error"))

        stats = self.failure_detector.get_statistics(service_name)
        assert stats["failure_count"] == self.config.failure_threshold
        assert stats["error_rate"] > 0.0

        # Test failure window rolling
        time.sleep(1)  # Ensure we're in a new time bucket
        self.failure_detector.record_success(service_name)
        stats = self.failure_detector.get_statistics(service_name)
        assert stats["success_count"] == 1  # Only count from new window

    def test_circuit_state_transitions(self):
        """Test circuit breaker state transitions."""
        service_name = "state - test - service"

        # Initial state should be CLOSED
        assert self.circuit_breaker.get_state(service_name) == CircuitState.CLOSED

        # Trigger failures to open circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.record_failure(
                service_name, error=ConnectionError("Service unavailable")
            )

        # Circuit should be OPEN
        assert self.circuit_breaker.get_state(service_name) == CircuitState.OPEN

        # Wait for reset timeout
        time.sleep(self.config.reset_timeout)

        # Circuit should transition to HALF_OPEN
        assert self.circuit_breaker.get_state(service_name) == CircuitState.HALF_OPEN

        # Test successful recovery
        for _ in range(self.config.half_open_requests):
            self.circuit_breaker.record_success(service_name)

        # Circuit should be CLOSED again
        assert self.circuit_breaker.get_state(service_name) == CircuitState.CLOSED

    def test_request_handling(self):
        """Test request handling through circuit breaker."""
        service_name = "request - test - service"

        def service_call():
            return {"status": "success"}

        def failing_service():
            raise ConnectionError("Service unavailable")

        # Test successful request
        result = self.circuit_breaker.execute(service_name, service_call)
        assert result["status"] == "success"

        # Test failing requests
        for _ in range(self.config.failure_threshold):
            with pytest.raises(CircuitBreakerError):
                self.circuit_breaker.execute(service_name, failing_service)

        # Circuit should be open
        assert self.circuit_breaker.get_state(service_name) == CircuitState.OPEN

        # Test request with open circuit
        with pytest.raises(CircuitBreakerError) as exc:
            self.circuit_breaker.execute(service_name, service_call)
        assert "Circuit breaker is open" in str(exc.value)

    def test_fallback_handling(self):
        """Test fallback behavior when circuit is open."""
        service_name = "fallback - test - service"

        # Register fallback handler
        def fallback_response(error):
            return {"status": "fallback", "error": str(error)}

        self.fallback_handler.register_fallback(service_name, fallback_response)

        # Open the circuit
        for _ in range(self.config.failure_threshold):
            self.circuit_breaker.record_failure(
                service_name, error=ServiceUnavailableError("Service down")
            )

        # Test fallback execution
        def failing_function():
            raise ServiceUnavailableError("Service down")

        result = self.circuit_breaker.execute_with_fallback(
            service_name, failing_function, self.fallback_handler
        )

        assert result["status"] == "fallback"
        assert "Service down" in result["error"]

    def test_custom_failure_detection(self):
        """Test custom failure detection rules."""
        service_name = "custom - failure - service"

        # Define custom failure detector
        def is_failure(response):
            if isinstance(response, dict):
                return response.get("status_code", 200) >= 500
            return False

        self.failure_detector.register_failure_check(service_name, is_failure)

        # Test response that counts as failure
        response = {"status_code": 503, "message": "Service unavailable"}
        self.failure_detector.analyze_response(service_name, response)

        stats = self.failure_detector.get_statistics(service_name)
        assert stats["failure_count"] == 1

        # Test response that counts as success
        response = {"status_code": 200, "message": "Success"}
        self.failure_detector.analyze_response(service_name, response)

        stats = self.failure_detector.get_statistics(service_name)
        assert stats["success_count"] == 1

    def test_concurrent_requests(self):
        """Test circuit breaker behavior with concurrent requests."""
        service_name = "concurrent - test - service"

        # Simulate concurrent failures
        with patch("threading.Thread") as mock_thread:
            threads = []
            for _ in range(10):  # Simulate 10 concurrent failures
                thread = MagicMock()
                thread.start = lambda: self.circuit_breaker.record_failure(
                    service_name, error=ConnectionError("Concurrent failure")
                )
                threads.append(thread)
            mock_thread.side_effect = threads

            # Trigger concurrent failures
            for thread in threads:
                thread.start()

        # Circuit should be open after concurrent failures
        assert self.circuit_breaker.get_state(service_name) == CircuitState.OPEN

        # Verify failure count
        stats = self.failure_detector.get_statistics(service_name)
        assert stats["failure_count"] >= self.config.failure_threshold

    def test_circuit_breaker_metrics(self):
        """Test circuit breaker metrics collection."""
        service_name = "metrics - test - service"

        # Record mix of successes and failures
        for _ in range(5):
            self.circuit_breaker.record_success(service_name)

        for _ in range(3):
            self.circuit_breaker.record_failure(service_name, 
                error=ValueError("Test error"))

        # Get metrics
        metrics = self.circuit_breaker.get_metrics(service_name)

        # Verify metrics
        assert metrics["total_requests"] == 8
        assert metrics["success_count"] == 5
        assert metrics["failure_count"] == 3
        assert metrics["error_rate"] == 3 / 8
        assert "last_failure_time" in metrics
        assert "state_transition_times" in metrics

    def test_error_categorization(self):
        """Test error categorization and handling."""
        service_name = "error - test - service"

        # Register error categories
        self.failure_detector.register_error_category("timeout", [TimeoutError, 
            ConnectionError])
        self.failure_detector.register_error_category("validation", [ValueError, 
            TypeError])

        # Record different types of errors
        self.failure_detector.record_failure(service_name, 
            error=TimeoutError("Request timeout"))
        self.failure_detector.record_failure(service_name, 
            error=ValueError("Invalid input"))

        # Get error statistics
        error_stats = self.failure_detector.get_error_statistics(service_name)

        assert error_stats["timeout"]["count"] == 1
        assert error_stats["validation"]["count"] == 1

        # Verify error thresholds
        assert (
            self.failure_detector.check_error_threshold(service_name, "timeout", 
                threshold=2)
            is False
        )  # Below threshold

        assert (
            self.failure_detector.check_error_threshold(service_name, "timeout", 
                threshold=1)
            is True
        )  # At threshold

if __name__ == "__main__":
    pytest.main([" - v", "test_circuit_breaker.py"])
