"""
Base metric for benchmarking AI models.

This module provides the base class for metrics used in benchmarking.
"""


import abc
from typing import Any, Dict


class BaseMetric

        import statistics

(abc.ABC):
    """
    Base class for benchmark metrics.
    """

    def __init__(self, name: str, unit: str, **kwargs):
        """
        Initialize the metric.

        Args:
            name: Name of the metric
            unit: Unit of measurement
            **kwargs: Additional parameters for the metric
        """
        self.name = name
        self.unit = unit
        self.kwargs = kwargs
        self.values = []

    @abc.abstractmethod
    def measure(self, *args, **kwargs) -> float:
        """
        Measure the metric.

        Args:
            *args: Positional arguments for measurement
            **kwargs: Keyword arguments for measurement

        Returns:
            Measured value
        """
        pass

    def add_value(self, value: float) -> None:
        """
        Add a measured value.

        Args:
            value: Measured value
        """
        self.values.append(value)

    def reset(self) -> None:
        """
        Reset the metric.
        """
        self.values = []

    def get_stats(self) -> Dict[str, float]:
        """
        Get statistics about the measured values.

        Returns:
            Dictionary with statistics
        """
        if not self.values:
            return {}


        return {
            "min": min(self.values),
            "max": max(self.values),
            "mean": statistics.mean(self.values),
            "median": statistics.median(self.values),
            "std_dev": statistics.stdev(self.values) if len(self.values) > 1 else 0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metric to a dictionary.

        Returns:
            Dictionary representation of the metric
        """
        return {
            "name": self.name,
            "unit": self.unit,
            "values": self.values,
            "stats": self.get_stats(),
        }