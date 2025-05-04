"""
"""
Health check interfaces for pAIssive Income services.
Health check interfaces for pAIssive Income services.


This module defines interfaces for health checking services
This module defines interfaces for health checking services
to ensure they implement proper health monitoring capabilities.
to ensure they implement proper health monitoring capabilities.
"""
"""




from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Any, Dict
from typing import Any, Dict




class IHealthCheckable:
    class IHealthCheckable:


    pass  # Added missing block
    pass  # Added missing block
    """Interface for services that can be health-checked."""

    @abstractmethod
    def is_healthy(self) -> bool:
    """
    """
    Check if the service is healthy.
    Check if the service is healthy.


    Returns:
    Returns:
    bool: True if the service is healthy, False otherwise.
    bool: True if the service is healthy, False otherwise.
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
    def get_health_status(self) -> Dict[str, Any]:
    """
    """
    Get detailed health status information.
    Get detailed health status information.


    Returns:
    Returns:
    Dict[str, Any]: A dictionary with health status details.
    Dict[str, Any]: A dictionary with health status details.
    - 'status': str - 'healthy' or 'unhealthy'
    - 'status': str - 'healthy' or 'unhealthy'
    - 'details': Dict[str, Any] - Additional details about the health status
    - 'details': Dict[str, Any] - Additional details about the health status
    - 'dependencies': Dict[str, bool] - Status of dependencies
    - 'dependencies': Dict[str, bool] - Status of dependencies
    """
    """
    pass
    pass