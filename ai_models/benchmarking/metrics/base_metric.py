"""
"""
Base metric for benchmarking AI models.
Base metric for benchmarking AI models.


This module provides the base class for metrics used in benchmarking.
This module provides the base class for metrics used in benchmarking.
"""
"""


import abc
import abc
import statistics
import statistics
from typing import Any, Dict
from typing import Any, Dict




class BaseMetric(abc.ABC):
    class BaseMetric(abc.ABC):
    """
    """
    Base class for benchmark metrics.
    Base class for benchmark metrics.
    """
    """


    def __init__(self, name: str, unit: str, **kwargs):
    def __init__(self, name: str, unit: str, **kwargs):
    """
    """
    Initialize the metric.
    Initialize the metric.


    Args:
    Args:
    name: Name of the metric
    name: Name of the metric
    unit: Unit of measurement
    unit: Unit of measurement
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    self.name = name
    self.name = name
    self.unit = unit
    self.unit = unit
    self.kwargs = kwargs
    self.kwargs = kwargs
    self.values = []
    self.values = []


    @abc.abstractmethod
    @abc.abstractmethod
    def measure(self, *args, **kwargs) -> float:
    def measure(self, *args, **kwargs) -> float:
    """
    """
    Measure the metric.
    Measure the metric.


    Args:
    Args:
    *args: Positional arguments for measurement
    *args: Positional arguments for measurement
    **kwargs: Keyword arguments for measurement
    **kwargs: Keyword arguments for measurement


    Returns:
    Returns:
    Measured value
    Measured value
    """
    """
    pass
    pass


    def add_value(self, value: float) -> None:
    def add_value(self, value: float) -> None:
    """
    """
    Add a measured value.
    Add a measured value.


    Args:
    Args:
    value: Measured value
    value: Measured value
    """
    """
    self.values.append(value)
    self.values.append(value)


    def reset(self) -> None:
    def reset(self) -> None:
    """
    """
    Reset the metric.
    Reset the metric.
    """
    """
    self.values = []
    self.values = []


    def get_stats(self) -> Dict[str, float]:
    def get_stats(self) -> Dict[str, float]:
    """
    """
    Get statistics about the measured values.
    Get statistics about the measured values.


    Returns:
    Returns:
    Dictionary with statistics
    Dictionary with statistics
    """
    """
    if not self.values:
    if not self.values:
    return {}
    return {}


    return {
    return {
    "min": min(self.values),
    "min": min(self.values),
    "max": max(self.values),
    "max": max(self.values),
    "mean": statistics.mean(self.values),
    "mean": statistics.mean(self.values),
    "median": statistics.median(self.values),
    "median": statistics.median(self.values),
    "std_dev": statistics.stdev(self.values) if len(self.values) > 1 else 0,
    "std_dev": statistics.stdev(self.values) if len(self.values) > 1 else 0,
    }
    }


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the metric to a dictionary.
    Convert the metric to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the metric
    Dictionary representation of the metric
    """
    """
    return {
    return {
    "name": self.name,
    "name": self.name,
    "unit": self.unit,
    "unit": self.unit,
    "values": self.values,
    "values": self.values,
    "stats": self.get_stats(),
    "stats": self.get_stats(),
    }
    }

