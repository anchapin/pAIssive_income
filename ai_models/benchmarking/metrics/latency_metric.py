"""
"""
Latency metric for benchmarking AI models.
Latency metric for benchmarking AI models.


This module provides a metric for measuring the latency of AI models.
This module provides a metric for measuring the latency of AI models.
"""
"""


import time
import time
from typing import Any, Callable, Dict, List, Optional
from typing import Any, Callable, Dict, List, Optional


from .base_metric import BaseMetric
from .base_metric import BaseMetric




class LatencyMetric(BaseMetric):
    class LatencyMetric(BaseMetric):
    """
    """
    Metric for measuring latency.
    Metric for measuring latency.
    """
    """


    def __init__(self, unit: str = "ms", **kwargs):
    def __init__(self, unit: str = "ms", **kwargs):
    """
    """
    Initialize the latency metric.
    Initialize the latency metric.


    Args:
    Args:
    unit: Unit of measurement (ms or s)
    unit: Unit of measurement (ms or s)
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    super().__init__(name="latency", unit=unit, **kwargs)
    super().__init__(name="latency", unit=unit, **kwargs)
    self.warmup_runs = kwargs.get("warmup_runs", 3)
    self.warmup_runs = kwargs.get("warmup_runs", 3)
    self.total_time = 0.0
    self.total_time = 0.0
    self.total_calls = 0
    self.total_calls = 0


    def measure(self, func: Callable, *args, **kwargs) -> float:
    def measure(self, func: Callable, *args, **kwargs) -> float:
    """
    """
    Measure the latency of a function call.
    Measure the latency of a function call.


    Args:
    Args:
    func: Function to measure
    func: Function to measure
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    Latency in the specified unit
    Latency in the specified unit
    """
    """
    # Perform warmup runs
    # Perform warmup runs
    for _ in range(self.warmup_runs):
    for _ in range(self.warmup_runs):
    func(*args, **kwargs)
    func(*args, **kwargs)


    # Measure latency
    # Measure latency
    start_time = time.time()
    start_time = time.time()
    func(*args, **kwargs)
    func(*args, **kwargs)
    end_time = time.time()
    end_time = time.time()


    # Calculate latency
    # Calculate latency
    latency = (end_time - start_time) * (1000 if self.unit == "ms" else 1)
    latency = (end_time - start_time) * (1000 if self.unit == "ms" else 1)


    # Update counters
    # Update counters
    self.total_time += latency
    self.total_time += latency
    self.total_calls += 1
    self.total_calls += 1


    # Add value
    # Add value
    self.add_value(latency)
    self.add_value(latency)


    return latency
    return latency


    def measure_batch(
    def measure_batch(
    self, func: Callable, inputs: List[Any], *args, **kwargs
    self, func: Callable, inputs: List[Any], *args, **kwargs
    ) -> List[float]:
    ) -> List[float]:
    """
    """
    Measure the latency of a function on a batch of inputs.
    Measure the latency of a function on a batch of inputs.


    Args:
    Args:
    func: Function to measure
    func: Function to measure
    inputs: List of inputs
    inputs: List of inputs
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    List of latencies in the specified unit
    List of latencies in the specified unit
    """
    """
    latencies = []
    latencies = []


    for input_data in inputs:
    for input_data in inputs:
    latency = self.measure(func, input_data, *args, **kwargs)
    latency = self.measure(func, input_data, *args, **kwargs)
    latencies.append(latency)
    latencies.append(latency)


    return latencies
    return latencies


    def get_average_latency(self) -> float:
    def get_average_latency(self) -> float:
    """
    """
    Get the average latency across all measurements.
    Get the average latency across all measurements.


    Returns:
    Returns:
    Average latency in the specified unit
    Average latency in the specified unit
    """
    """
    return self.total_time / self.total_calls if self.total_calls > 0 else 0
    return self.total_time / self.total_calls if self.total_calls > 0 else 0


    def reset(self) -> None:
    def reset(self) -> None:
    """
    """
    Reset the metric.
    Reset the metric.
    """
    """
    super().reset()
    super().reset()
    self.total_time = 0.0
    self.total_time = 0.0
    self.total_calls = 0
    self.total_calls = 0


    def get_stats(self) -> Dict[str, float]:
    def get_stats(self) -> Dict[str, float]:
    """
    """
    Get statistics about the latency values.
    Get statistics about the latency values.


    Returns:
    Returns:
    Dictionary with statistics
    Dictionary with statistics
    """
    """
    stats = super().get_stats()
    stats = super().get_stats()


    # Add average latency
    # Add average latency
    stats["average"] = self.get_average_latency()
    stats["average"] = self.get_average_latency()


    return stats
    return stats


    def get_percentile(self, percentile: float) -> Optional[float]:
    def get_percentile(self, percentile: float) -> Optional[float]:
    """
    """
    Get a specific percentile of the latency values.
    Get a specific percentile of the latency values.


    Args:
    Args:
    percentile: Percentile to get (0-100)
    percentile: Percentile to get (0-100)


    Returns:
    Returns:
    Latency value at the specified percentile, or None if no values
    Latency value at the specified percentile, or None if no values
    """
    """
    if not self.values:
    if not self.values:
    return None
    return None


    sorted_values = sorted(self.values)
    sorted_values = sorted(self.values)
    index = int(len(sorted_values) * percentile / 100)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[index]
    return sorted_values[index]

