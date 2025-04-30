"""
Monitoring module for pAIssive_income application.

This module provides functionality for monitoring system performance, resource usage,
and application metrics. It integrates with the logging system and exports metrics
to visualization platforms.
"""

from common_utils.monitoring.metrics import (
    create_metric,
    increment_counter,
    record_value,
    record_latency,
    get_metrics,
    export_metrics,
)

from common_utils.monitoring.health import (
    HealthStatus,
    get_health_status,
    register_health_check,
)

from common_utils.monitoring.system import (
    get_system_metrics,
    monitor_resources,
    ResourceType,
)

__all__ = [
    # Metrics
    "create_metric",
    "increment_counter",
    "record_value",
    "record_latency",
    "get_metrics",
    "export_metrics",
    # Health checks
    "HealthStatus",
    "get_health_status",
    "register_health_check",
    # System monitoring
    "get_system_metrics",
    "monitor_resources",
    "ResourceType",
]
