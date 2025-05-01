"""
Health check functionality for the pAIssive_income project.

This module provides functions for checking the health of the application.
"""

import logging
import os
import platform
import socket
import subprocess
import sys
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Configure logger
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """
    Enum for health check status.
    """

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


def health_check() -> Dict[str, Any]:
    """
    Perform a health check of the application.

    Returns:
        Dictionary with health check results
    """
    # Start time for measuring execution time
    start_time = time.time()

    # Collect health check data
    system_info = _get_system_info()
    python_info = _get_python_info()
    memory_info = _get_memory_info()
    disk_info = _get_disk_info()
    network_info = _get_network_info()

    # Determine overall status
    status = HealthStatus.OK

    # Check memory usage
    if memory_info["percent_used"] > 90:
        status = HealthStatus.ERROR
    elif memory_info["percent_used"] > 80:
        status = HealthStatus.WARNING

    # Check disk usage
    for disk in disk_info:
        if disk["percent_used"] > 90:
            status = HealthStatus.ERROR
            break
        elif disk["percent_used"] > 80 and status != HealthStatus.ERROR:
            status = HealthStatus.WARNING

    # Calculate execution time
    execution_time = time.time() - start_time

    # Return health check results
    return {
        "status": status.value,
        "timestamp": time.time(),
        "execution_time": execution_time,
        "system": system_info,
        "python": python_info,
        "memory": memory_info,
        "disk": disk_info,
        "network": network_info,
    }


def _get_system_info() -> Dict[str, Any]:
    """
    Get system information.

    Returns:
        Dictionary with system information
    """
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "uptime": _get_uptime(),
    }


def _get_python_info() -> Dict[str, Any]:
    """
    Get Python information.

    Returns:
        Dictionary with Python information
    """
    return {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
        "build": platform.python_build(),
        "executable": sys.executable,
        "threads": threading.active_count(),
    }


def _get_memory_info() -> Dict[str, Any]:
    """
    Get memory information.

    Returns:
        Dictionary with memory information
    """
    try:
        import psutil

        # Get virtual memory
        virtual_memory = psutil.virtual_memory()

        return {
            "total": virtual_memory.total,
            "available": virtual_memory.available,
            "used": virtual_memory.used,
            "percent_used": virtual_memory.percent,
        }
    except ImportError:
        logger.warning("psutil not installed. Cannot get memory information.")
        return {"total": 0, "available": 0, "used": 0, "percent_used": 0}


def _get_disk_info() -> List[Dict[str, Any]]:
    """
    Get disk information.

    Returns:
        List of dictionaries with disk information
    """
    try:
        import psutil

        # Get disk partitions
        partitions = psutil.disk_partitions()

        disk_info = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent_used": usage.percent,
                    }
                )
            except (PermissionError, OSError):
                # Skip partitions that cannot be accessed
                pass

        return disk_info
    except ImportError:
        logger.warning("psutil not installed. Cannot get disk information.")
        return []


def _get_network_info() -> Dict[str, Any]:
    """
    Get network information.

    Returns:
        Dictionary with network information
    """
    try:
        import psutil

        # Get network connections
        connections = psutil.net_connections()

        # Count connections by status
        connection_counts = {}
        for conn in connections:
            status = conn.status
            connection_counts[status] = connection_counts.get(status, 0) + 1

        # Get network interfaces
        interfaces = []
        for name, stats in psutil.net_if_stats().items():
            interfaces.append(
                {"name": name, "up": stats.isup, "speed": stats.speed, "mtu": stats.mtu}
            )

        return {"connections": connection_counts, "interfaces": interfaces}
    except ImportError:
        logger.warning("psutil not installed. Cannot get network information.")
        return {"connections": {}, "interfaces": []}


def _get_uptime() -> Optional[float]:
    """
    Get system uptime in seconds.

    Returns:
        Uptime in seconds, or None if not available
    """
    try:
        import psutil

        return time.time() - psutil.boot_time()
    except ImportError:
        logger.warning("psutil not installed. Cannot get uptime.")
        return None
