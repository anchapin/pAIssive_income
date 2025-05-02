"""
Health check system for pAIssive_income application.

This module provides functionality for monitoring the health of various system components,
integrating with monitoring systems, and providing a status endpoint for health checks.
"""

import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple
import threading
from common_utils.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Possible health status values for components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckRegistry:
    """
    Registry for health check functions.

    This class manages the registration and execution of health checks
    for various components of the system.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(HealthCheckRegistry, cls).__new__(cls)
                cls._instance._health_checks: Dict[
                    str, Callable[[], Tuple[HealthStatus, Dict[str, Any]]]
                ] = {}
                cls._instance._results_cache: Dict[str, Dict[str, Any]] = {}
                cls._instance._cache_timestamp: Dict[str, float] = {}
                cls._instance._cache_duration = (
                    60  # Cache health check results for 60 seconds by default
                )
        return cls._instance

    def register_check(
        self, name: str, check_func: Callable[[], Tuple[HealthStatus, Dict[str, Any]]]
    ) -> None:
        """
        Register a health check function.

        Args:
            name: Unique name for the health check
            check_func: Function that performs the health check and returns status and details
        """
        if name in self._health_checks:
            logger.warning(f"Health check '{name}' already registered, overwriting")

        self._health_checks[name] = check_func
        logger.debug(f"Registered health check: {name}")

    def run_check(self, name: str) -> Tuple[HealthStatus, Dict[str, Any]]:
        """
        Run a specific health check.

        Args:
            name: Name of the health check to run

        Returns:
            Tuple of (status, details)
        """
        if name not in self._health_checks:
            logger.error(f"Health check '{name}' not registered")
            return HealthStatus.UNKNOWN, {
                "error": f"Health check '{name}' not registered"
            }

        # Check if we have a recent cached result
        current_time = time.time()
        if (
            name in self._cache_timestamp
            and current_time - self._cache_timestamp[name] < self._cache_duration
        ):
            return (
                self._results_cache[name]["status"],
                self._results_cache[name]["details"],
            )

        # Run the health check
        try:
            status, details = self._health_checks[name]()

            # Cache the result
            self._results_cache[name] = {
                "status": status,
                "details": details,
                "timestamp": current_time,
            }
            self._cache_timestamp[name] = current_time

            return status, details
        except Exception as e:
            logger.error(f"Error running health check '{name}': {str(e)}")
            return HealthStatus.UNHEALTHY, {"error": str(e)}

    def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """
        Run all registered health checks.

        Returns:
            Dictionary mapping check names to their results
        """
        results = {}
        for name in self._health_checks:
            status, details = self.run_check(name)
            results[name] = {
                "status": status,
                "details": details,
                "timestamp": time.time(),
            }
        return results

    def set_cache_duration(self, seconds: int) -> None:
        """
        Set the duration for which health check results are cached.

        Args:
            seconds: Duration in seconds
        """
        self._cache_duration = max(1, seconds)  # Minimum 1 second


# Create a global health check registry
_registry = HealthCheckRegistry()


# Public API functions


def register_health_check(
    name: str, check_func: Callable[[], Tuple[HealthStatus, Dict[str, Any]]]
) -> None:
    """
    Register a health check function.

    Args:
        name: Unique name for the health check
        check_func: Function that performs the health check and returns status and details
    """
    _registry.register_check(name, check_func)


def get_health_status(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the health status of the system or a specific component.

    Args:
        name: Name of the specific health check to run, or None to run all checks

    Returns:
        Dictionary containing health status information
    """
    if name:
        status, details = _registry.run_check(name)
        return {name: {"status": status, "details": details, "timestamp": time.time()}}
    else:
        results = _registry.run_all_checks()

        # Determine overall system health based on component health
        overall_status = HealthStatus.HEALTHY
        for check_result in results.values():
            if check_result["status"] == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif (
                check_result["status"] == HealthStatus.DEGRADED
                and overall_status != HealthStatus.UNHEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "components": results,
        }


# Common health check functions


def database_health_check(
    db_connection,
) -> Callable[[], Tuple[HealthStatus, Dict[str, Any]]]:
    """
    Create a health check function for database connectivity.

    Args:
        db_connection: Database connection object

    Returns:
        Function that checks database health
    """

    def check() -> Tuple[HealthStatus, Dict[str, Any]]:
        try:
            # Simple query to check database connectivity
            start_time = time.time()
            db_connection.execute("SELECT 1")
            response_time = time.time() - start_time

            return HealthStatus.HEALTHY, {
                "response_time_ms": round(response_time * 1000, 2),
                "connected": True,
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {"error": str(e), "connected": False}

    return check


def api_health_check(
    api_url: str, timeout: float = 5.0
) -> Callable[[], Tuple[HealthStatus, Dict[str, Any]]]:
    """
    Create a health check function for an external API.

    Args:
        api_url: URL of the API endpoint to check
        timeout: Timeout in seconds

    Returns:
        Function that checks API health
    """

    def check() -> Tuple[HealthStatus, Dict[str, Any]]:
        try:
            import requests

            start_time = time.time()
            response = requests.get(api_url, timeout=timeout)
            response_time = time.time() - start_time

            if response.status_code < 300:
                return HealthStatus.HEALTHY, {
                    "response_time_ms": round(response_time * 1000, 2),
                    "status_code": response.status_code,
                }
            else:
                return HealthStatus.DEGRADED, {
                    "response_time_ms": round(response_time * 1000, 2),
                    "status_code": response.status_code,
                    "error": f"API returned status code {response.status_code}",
                }
        except requests.Timeout:
            return HealthStatus.DEGRADED, {
                "error": f"API request timed out after {timeout} seconds",
                "status_code": None,
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {"error": str(e), "status_code": None}

    return check
