"""
"""
System resource monitoring for pAIssive_income application.
System resource monitoring for pAIssive_income application.


This module provides functionality for monitoring system resources such as CPU, memory,
This module provides functionality for monitoring system resources such as CPU, memory,
disk usage, and network activity. It integrates with the metrics system to record
disk usage, and network activity. It integrates with the metrics system to record
and track resource usage over time.
and track resource usage over time.
"""
"""


import platform
import platform
import threading
import threading
import time
import time
from enum import Enum
from enum import Enum
from typing import Any, Dict, Optional, Union
from typing import Any, Dict, Optional, Union


from common_utils.logging import get_logger
from common_utils.logging import get_logger
from common_utils.monitoring.metrics import (MetricType, create_metric,
from common_utils.monitoring.metrics import (MetricType, create_metric,
record_value)
record_value)


logger
logger
import psutil
import psutil


# Import our logging and metrics modules
# Import our logging and metrics modules
= get_logger(__name__)
= get_logger(__name__)




class ResourceType(str, Enum):
    class ResourceType(str, Enum):
    """Types of system resources that can be monitored."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    GPU = "gpu"


    class SystemMonitor:
    """
    """
    Monitors system resources and records metrics.
    Monitors system resources and records metrics.


    This class provides functionality to monitor various system resources
    This class provides functionality to monitor various system resources
    and record their metrics. It can run in a background thread to
    and record their metrics. It can run in a background thread to
    continuously monitor resources.
    continuously monitor resources.
    """
    """


    _instance = None
    _instance = None
    _lock = threading.Lock()
    _lock = threading.Lock()


    def __new__(cls):
    def __new__(cls):
    with cls._lock:
    with cls._lock:
    if cls._instance is None:
    if cls._instance is None:
    cls._instance = super(SystemMonitor, cls).__new__(cls)
    cls._instance = super(SystemMonitor, cls).__new__(cls)
    cls._instance._initialized = False
    cls._instance._initialized = False
    cls._instance._monitoring_thread = None
    cls._instance._monitoring_thread = None
    cls._instance._stop_event = threading.Event()
    cls._instance._stop_event = threading.Event()
    cls._instance._monitor_interval = (
    cls._instance._monitor_interval = (
    60  # Default: Monitor every 60 seconds
    60  # Default: Monitor every 60 seconds
    )
    )
    return cls._instance
    return cls._instance


    def __init__(self):
    def __init__(self):
    if self._initialized:
    if self._initialized:
    return # Initialize metrics
    return # Initialize metrics
    self._cpu_usage = create_metric(
    self._cpu_usage = create_metric(
    "system_cpu_usage_percent", MetricType.GAUGE, "CPU usage in percent"
    "system_cpu_usage_percent", MetricType.GAUGE, "CPU usage in percent"
    )
    )


    self._memory_usage = create_metric(
    self._memory_usage = create_metric(
    "system_memory_usage_bytes", MetricType.GAUGE, "Memory usage in bytes"
    "system_memory_usage_bytes", MetricType.GAUGE, "Memory usage in bytes"
    )
    )


    self._memory_percent = create_metric(
    self._memory_percent = create_metric(
    "system_memory_usage_percent", MetricType.GAUGE, "Memory usage in percent"
    "system_memory_usage_percent", MetricType.GAUGE, "Memory usage in percent"
    )
    )


    self._disk_usage = create_metric(
    self._disk_usage = create_metric(
    "system_disk_usage_bytes", MetricType.GAUGE, "Disk usage in bytes"
    "system_disk_usage_bytes", MetricType.GAUGE, "Disk usage in bytes"
    )
    )


    self._disk_percent = create_metric(
    self._disk_percent = create_metric(
    "system_disk_usage_percent", MetricType.GAUGE, "Disk usage in percent"
    "system_disk_usage_percent", MetricType.GAUGE, "Disk usage in percent"
    )
    )


    self._process_count = create_metric(
    self._process_count = create_metric(
    "system_process_count", MetricType.GAUGE, "Number of processes running"
    "system_process_count", MetricType.GAUGE, "Number of processes running"
    )
    )


    self._initialized = True
    self._initialized = True


    def get_cpu_metrics(self) -> Dict[str, float]:
    def get_cpu_metrics(self) -> Dict[str, float]:
    """
    """
    Get current CPU usage metrics.
    Get current CPU usage metrics.


    Returns:
    Returns:
    Dictionary of CPU metrics
    Dictionary of CPU metrics
    """
    """
    try:
    try:




    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    cpu_freq = psutil.cpu_freq()


    metrics = {
    metrics = {
    "usage_percent": cpu_percent,
    "usage_percent": cpu_percent,
    "core_count": cpu_count,
    "core_count": cpu_count,
    }
    }


    if cpu_freq:
    if cpu_freq:
    metrics["frequency_mhz"] = cpu_freq.current
    metrics["frequency_mhz"] = cpu_freq.current


    # Record the metric
    # Record the metric
    record_value("system_cpu_usage_percent", cpu_percent)
    record_value("system_cpu_usage_percent", cpu_percent)


    return metrics
    return metrics
except ImportError:
except ImportError:
    logger.warning("psutil not installed, cannot monitor CPU usage")
    logger.warning("psutil not installed, cannot monitor CPU usage")
    return {"error": "psutil not installed"}
    return {"error": "psutil not installed"}
except Exception as e:
except Exception as e:
    logger.error(f"Error getting CPU metrics: {e}")
    logger.error(f"Error getting CPU metrics: {e}")
    return {"error": str(e)}
    return {"error": str(e)}


    def get_memory_metrics(self) -> Dict[str, float]:
    def get_memory_metrics(self) -> Dict[str, float]:
    """
    """
    Get current memory usage metrics.
    Get current memory usage metrics.


    Returns:
    Returns:
    Dictionary of memory metrics
    Dictionary of memory metrics
    """
    """
    try:
    try:




    memory = psutil.virtual_memory()
    memory = psutil.virtual_memory()


    metrics = {
    metrics = {
    "total_bytes": memory.total,
    "total_bytes": memory.total,
    "available_bytes": memory.available,
    "available_bytes": memory.available,
    "used_bytes": memory.used,
    "used_bytes": memory.used,
    "usage_percent": memory.percent,
    "usage_percent": memory.percent,
    }
    }


    # Record the metrics
    # Record the metrics
    record_value("system_memory_usage_bytes", memory.used)
    record_value("system_memory_usage_bytes", memory.used)
    record_value("system_memory_usage_percent", memory.percent)
    record_value("system_memory_usage_percent", memory.percent)


    return metrics
    return metrics
except ImportError:
except ImportError:
    logger.warning("psutil not installed, cannot monitor memory usage")
    logger.warning("psutil not installed, cannot monitor memory usage")
    return {"error": "psutil not installed"}
    return {"error": "psutil not installed"}
except Exception as e:
except Exception as e:
    logger.error(f"Error getting memory metrics: {e}")
    logger.error(f"Error getting memory metrics: {e}")
    return {"error": str(e)}
    return {"error": str(e)}


    def get_disk_metrics(self, path: str = "/") -> Dict[str, float]:
    def get_disk_metrics(self, path: str = "/") -> Dict[str, float]:
    """
    """
    Get current disk usage metrics.
    Get current disk usage metrics.


    Args:
    Args:
    path: Path to the disk partition to check
    path: Path to the disk partition to check


    Returns:
    Returns:
    Dictionary of disk metrics
    Dictionary of disk metrics
    """
    """
    try:
    try:




    disk = psutil.disk_usage(path)
    disk = psutil.disk_usage(path)


    metrics = {
    metrics = {
    "total_bytes": disk.total,
    "total_bytes": disk.total,
    "used_bytes": disk.used,
    "used_bytes": disk.used,
    "free_bytes": disk.free,
    "free_bytes": disk.free,
    "usage_percent": disk.percent,
    "usage_percent": disk.percent,
    }
    }


    # Record the metrics
    # Record the metrics
    record_value("system_disk_usage_bytes", disk.used, {"path": path})
    record_value("system_disk_usage_bytes", disk.used, {"path": path})
    record_value("system_disk_usage_percent", disk.percent, {"path": path})
    record_value("system_disk_usage_percent", disk.percent, {"path": path})


    return metrics
    return metrics
except ImportError:
except ImportError:
    logger.warning("psutil not installed, cannot monitor disk usage")
    logger.warning("psutil not installed, cannot monitor disk usage")
    return {"error": "psutil not installed"}
    return {"error": "psutil not installed"}
except Exception as e:
except Exception as e:
    logger.error(f"Error getting disk metrics: {e}")
    logger.error(f"Error getting disk metrics: {e}")
    return {"error": str(e)}
    return {"error": str(e)}


    def get_network_metrics(self) -> Dict[str, Dict[str, float]]:
    def get_network_metrics(self) -> Dict[str, Dict[str, float]]:
    """
    """
    Get current network usage metrics.
    Get current network usage metrics.


    Returns:
    Returns:
    Dictionary of network metrics by interface
    Dictionary of network metrics by interface
    """
    """
    try:
    try:




    network = psutil.net_io_counters(pernic=True)
    network = psutil.net_io_counters(pernic=True)


    metrics = {}
    metrics = {}
    for interface, counters in network.items():
    for interface, counters in network.items():
    metrics[interface] = {
    metrics[interface] = {
    "bytes_sent": counters.bytes_sent,
    "bytes_sent": counters.bytes_sent,
    "bytes_recv": counters.bytes_recv,
    "bytes_recv": counters.bytes_recv,
    "packets_sent": counters.packets_sent,
    "packets_sent": counters.packets_sent,
    "packets_recv": counters.packets_recv,
    "packets_recv": counters.packets_recv,
    "errin": counters.errin,
    "errin": counters.errin,
    "errout": counters.errout,
    "errout": counters.errout,
    "dropin": counters.dropin,
    "dropin": counters.dropin,
    "dropout": counters.dropout,
    "dropout": counters.dropout,
    }
    }


    # Record metrics for main interfaces only, not loopback or virtual
    # Record metrics for main interfaces only, not loopback or virtual
    if interface not in ("lo", "bridge", "veth", "docker"):
    if interface not in ("lo", "bridge", "veth", "docker"):
    record_value(
    record_value(
    "system_network_bytes_sent",
    "system_network_bytes_sent",
    counters.bytes_sent,
    counters.bytes_sent,
    {"interface": interface},
    {"interface": interface},
    )
    )
    record_value(
    record_value(
    "system_network_bytes_recv",
    "system_network_bytes_recv",
    counters.bytes_recv,
    counters.bytes_recv,
    {"interface": interface},
    {"interface": interface},
    )
    )


    return metrics
    return metrics
except ImportError:
except ImportError:
    logger.warning("psutil not installed, cannot monitor network usage")
    logger.warning("psutil not installed, cannot monitor network usage")
    return {"error": "psutil not installed"}
    return {"error": "psutil not installed"}
except Exception as e:
except Exception as e:
    logger.error(f"Error getting network metrics: {e}")
    logger.error(f"Error getting network metrics: {e}")
    return {"error": str(e)}
    return {"error": str(e)}


    def get_process_metrics(self) -> Dict[str, Any]:
    def get_process_metrics(self) -> Dict[str, Any]:
    """
    """
    Get metrics about running processes.
    Get metrics about running processes.


    Returns:
    Returns:
    Dictionary of process metrics
    Dictionary of process metrics
    """
    """
    try:
    try:




    current_process = psutil.Process()
    current_process = psutil.Process()


    # Get information about the current process
    # Get information about the current process
    process_info = {
    process_info = {
    "pid": current_process.pid,
    "pid": current_process.pid,
    "memory_percent": current_process.memory_percent(),
    "memory_percent": current_process.memory_percent(),
    "cpu_percent": current_process.cpu_percent(),
    "cpu_percent": current_process.cpu_percent(),
    "num_threads": current_process.num_threads(),
    "num_threads": current_process.num_threads(),
    "create_time": current_process.create_time(),
    "create_time": current_process.create_time(),
    }
    }


    # Count total processes
    # Count total processes
    process_count = len(psutil.pids())
    process_count = len(psutil.pids())
    record_value("system_process_count", process_count)
    record_value("system_process_count", process_count)


    # Record process-specific metrics
    # Record process-specific metrics
    record_value("process_memory_percent", process_info["memory_percent"])
    record_value("process_memory_percent", process_info["memory_percent"])
    record_value("process_cpu_percent", process_info["cpu_percent"])
    record_value("process_cpu_percent", process_info["cpu_percent"])


    return {"current_process": process_info, "total_processes": process_count}
    return {"current_process": process_info, "total_processes": process_count}
except ImportError:
except ImportError:
    logger.warning("psutil not installed, cannot monitor processes")
    logger.warning("psutil not installed, cannot monitor processes")
    return {"error": "psutil not installed"}
    return {"error": "psutil not installed"}
except Exception as e:
except Exception as e:
    logger.error(f"Error getting process metrics: {e}")
    logger.error(f"Error getting process metrics: {e}")
    return {"error": str(e)}
    return {"error": str(e)}


    def get_all_metrics(self) -> Dict[str, Any]:
    def get_all_metrics(self) -> Dict[str, Any]:
    """
    """
    Get all system metrics in a single call.
    Get all system metrics in a single call.


    Returns:
    Returns:
    Dictionary containing all system metrics
    Dictionary containing all system metrics
    """
    """
    return {
    return {
    "cpu": self.get_cpu_metrics(),
    "cpu": self.get_cpu_metrics(),
    "memory": self.get_memory_metrics(),
    "memory": self.get_memory_metrics(),
    "disk": self.get_disk_metrics(),
    "disk": self.get_disk_metrics(),
    "network": self.get_network_metrics(),
    "network": self.get_network_metrics(),
    "process": self.get_process_metrics(),
    "process": self.get_process_metrics(),
    "system_info": {
    "system_info": {
    "platform": platform.platform(),
    "platform": platform.platform(),
    "python_version": platform.python_version(),
    "python_version": platform.python_version(),
    "node": platform.node(),
    "node": platform.node(),
    },
    },
    }
    }


    def start_monitoring(self, interval: int = 60) -> None:
    def start_monitoring(self, interval: int = 60) -> None:
    """
    """
    Start monitoring system resources in a background thread.
    Start monitoring system resources in a background thread.


    Args:
    Args:
    interval: Time between monitoring checks in seconds
    interval: Time between monitoring checks in seconds
    """
    """
    if self._monitoring_thread and self._monitoring_thread.is_alive():
    if self._monitoring_thread and self._monitoring_thread.is_alive():
    logger.warning("Monitoring thread is already running")
    logger.warning("Monitoring thread is already running")
    return self._stop_event.clear()
    return self._stop_event.clear()
    self._monitor_interval = interval
    self._monitor_interval = interval


    self._monitoring_thread = threading.Thread(
    self._monitoring_thread = threading.Thread(
    target=self._monitor_loop, daemon=True, name="SystemMonitorThread"
    target=self._monitor_loop, daemon=True, name="SystemMonitorThread"
    )
    )
    self._monitoring_thread.start()
    self._monitoring_thread.start()
    logger.info(f"Started system monitoring thread with interval {interval}s")
    logger.info(f"Started system monitoring thread with interval {interval}s")


    def stop_monitoring(self) -> None:
    def stop_monitoring(self) -> None:
    """Stop the background monitoring thread."""
    if not self._monitoring_thread or not self._monitoring_thread.is_alive():
    logger.warning("Monitoring thread is not running")
    return logger.info("Stopping system monitoring thread")
    self._stop_event.set()
    self._monitoring_thread.join(timeout=5.0)

    if self._monitoring_thread.is_alive():
    logger.warning("Monitoring thread did not stop gracefully")

    def _monitor_loop(self) -> None:
    """Internal loop for continuous monitoring."""
    logger.info("System monitoring loop started")
    try:
    while not self._stop_event.is_set():
    try:
    self.get_all_metrics()
except Exception as e:
    logger.error(f"Error in monitoring loop: {e}")

    # Wait for the next interval or until stopped
    self._stop_event.wait(self._monitor_interval)
finally:
    logger.info("System monitoring loop ended")


    # Create a global system monitor instance
    _monitor = SystemMonitor()


    # Public API functions


    def get_system_metrics(
    resource_type: Optional[Union[str, ResourceType]] = None,
    ) -> Dict[str, Any]:
    """
    """
    Get system metrics for the specified resource type.
    Get system metrics for the specified resource type.


    Args:
    Args:
    resource_type: Type of resource to get metrics for, or None for all
    resource_type: Type of resource to get metrics for, or None for all


    Returns:
    Returns:
    Dictionary containing the requested metrics
    Dictionary containing the requested metrics
    """
    """
    if resource_type is None:
    if resource_type is None:
    return _monitor.get_all_metrics()
    return _monitor.get_all_metrics()


    if isinstance(resource_type, str):
    if isinstance(resource_type, str):
    resource_type = ResourceType(resource_type)
    resource_type = ResourceType(resource_type)


    if resource_type == ResourceType.CPU:
    if resource_type == ResourceType.CPU:
    return _monitor.get_cpu_metrics()
    return _monitor.get_cpu_metrics()
    elif resource_type == ResourceType.MEMORY:
    elif resource_type == ResourceType.MEMORY:
    return _monitor.get_memory_metrics()
    return _monitor.get_memory_metrics()
    elif resource_type == ResourceType.DISK:
    elif resource_type == ResourceType.DISK:
    return _monitor.get_disk_metrics()
    return _monitor.get_disk_metrics()
    elif resource_type == ResourceType.NETWORK:
    elif resource_type == ResourceType.NETWORK:
    return _monitor.get_network_metrics()
    return _monitor.get_network_metrics()
    elif resource_type == ResourceType.PROCESS:
    elif resource_type == ResourceType.PROCESS:
    return _monitor.get_process_metrics()
    return _monitor.get_process_metrics()
    else:
    else:
    logger.error(f"Unknown resource type: {resource_type}")
    logger.error(f"Unknown resource type: {resource_type}")
    return {"error": f"Unknown resource type: {resource_type}"}
    return {"error": f"Unknown resource type: {resource_type}"}




    def monitor_resources(interval: int = 60, start_monitoring: bool = True) -> None:
    def monitor_resources(interval: int = 60, start_monitoring: bool = True) -> None:
    """
    """
    Configure system resource monitoring.
    Configure system resource monitoring.


    Args:
    Args:
    interval: Time between monitoring checks in seconds
    interval: Time between monitoring checks in seconds
    start_monitoring: Whether to start monitoring immediately
    start_monitoring: Whether to start monitoring immediately
    """
    """
    if start_monitoring:
    if start_monitoring:
    _monitor.start_monitoring(interval)
    _monitor.start_monitoring(interval)
    else:
    else:
    _monitor.stop_monitoring()
    _monitor.stop_monitoring()