"""
Throughput metric for benchmarking AI models.

This module provides a metric for measuring the throughput of AI models.
"""

import time
from typing import Callable

from .base_metric import BaseMetric


class ThroughputMetric(BaseMetric):
    """
    Metric for measuring throughput.
    """

    def __init__(self, **kwargs):
        """
        Initialize the throughput metric.

        Args:
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="throughput", unit="tokens / s", **kwargs)

    def measure(self, func: Callable, token_counter: Callable, *args, **kwargs) -> float:
        """
        Measure the throughput of a function call.

        Args:
            func: Function to measure
            token_counter: Function to count tokens in the result
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Throughput in tokens per second
        """
        # Measure throughput
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Count tokens
        num_tokens = token_counter(result)

        # Calculate time in seconds
        elapsed_time = end_time - start_time

        # Calculate throughput
        throughput = num_tokens / elapsed_time if elapsed_time > 0 else 0

        # Add value
        self.add_value(throughput)

        return throughput

    def measure_batch(
        self, func: Callable, token_counter: Callable, batch_size: int, *args, **kwargs
    ) -> float:
        """
        Measure the throughput of a batch function call.

        Args:
            func: Function to measure
            token_counter: Function to count tokens in the results
            batch_size: Size of the batch
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Throughput in tokens per second
        """
        # Measure throughput
        start_time = time.time()
        results = func(*args, **kwargs)
        end_time = time.time()

        # Count tokens
        total_tokens = sum(token_counter(result) for result in results)

        # Calculate time in seconds
        elapsed_time = end_time - start_time

        # Calculate throughput
        throughput = total_tokens / elapsed_time if elapsed_time > 0 else 0

        # Add value
        self.add_value(throughput)

        return throughput
