"""
"""
Throughput metric for benchmarking AI models.
Throughput metric for benchmarking AI models.


This module provides a metric for measuring the throughput of AI models.
This module provides a metric for measuring the throughput of AI models.
"""
"""




import time
import time
from typing import Callable
from typing import Callable


from .base_metric import BaseMetric
from .base_metric import BaseMetric




class ThroughputMetric:
    class ThroughputMetric:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    Metric for measuring throughput.
    Metric for measuring throughput.
    """
    """


    def __init__(self, **kwargs):
    def __init__(self, **kwargs):
    """
    """
    Initialize the throughput metric.
    Initialize the throughput metric.


    Args:
    Args:
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    super().__init__(name="throughput", unit="tokens/s", **kwargs)
    super().__init__(name="throughput", unit="tokens/s", **kwargs)


    def measure(
    def measure(
    self, func: Callable, token_counter: Callable, *args, **kwargs
    self, func: Callable, token_counter: Callable, *args, **kwargs
    ) -> float:
    ) -> float:
    """
    """
    Measure the throughput of a function call.
    Measure the throughput of a function call.


    Args:
    Args:
    func: Function to measure
    func: Function to measure
    token_counter: Function to count tokens in the result
    token_counter: Function to count tokens in the result
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    Throughput in tokens per second
    Throughput in tokens per second
    """
    """
    # Measure throughput
    # Measure throughput
    start_time = time.time()
    start_time = time.time()
    result = func(*args, **kwargs)
    result = func(*args, **kwargs)
    end_time = time.time()
    end_time = time.time()


    # Count tokens
    # Count tokens
    num_tokens = token_counter(result)
    num_tokens = token_counter(result)


    # Calculate time in seconds
    # Calculate time in seconds
    elapsed_time = end_time - start_time
    elapsed_time = end_time - start_time


    # Calculate throughput
    # Calculate throughput
    throughput = num_tokens / elapsed_time if elapsed_time > 0 else 0
    throughput = num_tokens / elapsed_time if elapsed_time > 0 else 0


    # Add value
    # Add value
    self.add_value(throughput)
    self.add_value(throughput)


    return throughput
    return throughput


    def measure_batch(
    def measure_batch(
    self, func: Callable, token_counter: Callable, batch_size: int, *args, **kwargs
    self, func: Callable, token_counter: Callable, batch_size: int, *args, **kwargs
    ) -> float:
    ) -> float:
    """
    """
    Measure the throughput of a batch function call.
    Measure the throughput of a batch function call.


    Args:
    Args:
    func: Function to measure
    func: Function to measure
    token_counter: Function to count tokens in the results
    token_counter: Function to count tokens in the results
    batch_size: Size of the batch
    batch_size: Size of the batch
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    Throughput in tokens per second
    Throughput in tokens per second
    """
    """
    # Measure throughput
    # Measure throughput
    start_time = time.time()
    start_time = time.time()
    results = func(*args, **kwargs)
    results = func(*args, **kwargs)
    end_time = time.time()
    end_time = time.time()


    # Count tokens
    # Count tokens
    total_tokens = sum(token_counter(result) for result in results)
    total_tokens = sum(token_counter(result) for result in results)


    # Calculate time in seconds
    # Calculate time in seconds
    elapsed_time = end_time - start_time
    elapsed_time = end_time - start_time


    # Calculate throughput
    # Calculate throughput
    throughput = total_tokens / elapsed_time if elapsed_time > 0 else 0
    throughput = total_tokens / elapsed_time if elapsed_time > 0 else 0


    # Add value
    # Add value
    self.add_value(throughput)
    self.add_value(throughput)


    return throughput
    return throughput