"""
Latency metric for benchmarking AI models.

This module provides a metric for measuring the latency of AI models.
"""

import time
from typing import Callable, Dict

from .base_metric import BaseMetric


class LatencyMetric(BaseMetric):
    """
    Metric for measuring latency.
    """

    def __init__(self, **kwargs):
        """
        Initialize the latency metric.

        Args:
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="latency", unit="ms", **kwargs)

    def measure(self, func: Callable, *args, **kwargs) -> float:
        """
        Measure the latency of a function call.

        Args:
            func: Function to measure
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Latency in milliseconds
        """
        # Measure latency
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()

        # Calculate latency in milliseconds
        latency = (end_time - start_time) * 1000

        # Add value
        self.add_value(latency)

        return latency

    def get_percentile(self, percentile: float) -> float:
        """
        Get a percentile of the latency values.

        Args:
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not self.values:
            return 0

        # Sort values
        sorted_values = sorted(self.values)

        # Calculate index
        size = len(sorted_values)
        k = (size - 1) * percentile / 100
        f = int(k)
        c = int(k) + 1 if k > f else f

        if f >= size:
            return sorted_values[-1]

        if c >= size:
            return sorted_values[-1]

        # Interpolate
        d0 = sorted_values[f] * (c - k)
        d1 = sorted_values[c] * (k - f)
        return d0 + d1

    def get_stats(self) -> Dict[str, float]:
        """
        Get statistics about the latency values.

        Returns:
            Dictionary with statistics
        """
        stats = super().get_stats()

        # Add percentiles
        if self.values:
            stats["p50"] = self.get_percentile(50)
            stats["p90"] = self.get_percentile(90)
            stats["p95"] = self.get_percentile(95)
            stats["p99"] = self.get_percentile(99)

        return stats
