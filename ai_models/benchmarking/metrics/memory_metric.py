"""
Memory metric for benchmarking AI models.

This module provides a metric for measuring the memory usage of AI models.
"""

import os
import gc
from typing import Dict, Any, Optional, List, Union, Tuple, Callable

from .base_metric import BaseMetric

# Try to import optional dependencies
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class MemoryMetric(BaseMetric):
    """
    Metric for measuring memory usage.
    """

    def __init__(self, **kwargs):
        """
        Initialize the memory metric.

        Args:
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="memory", unit="MB", **kwargs)

        if not PSUTIL_AVAILABLE:
            raise ImportError("psutil is required for memory metrics")

        self.process = psutil.Process(os.getpid())
        self.device = kwargs.get("device", "cpu")

    def measure(self, func: Optional[Callable] = None, *args, **kwargs) -> float:
        """
        Measure the memory usage.

        Args:
            func: Optional function to measure
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Memory usage in megabytes
        """
        # Clear cache
        if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()

        # Get initial memory usage
        initial_memory = self._get_memory_usage()

        # Run function if provided
        if func is not None:
            result = func(*args, **kwargs)

        # Get final memory usage
        final_memory = self._get_memory_usage()

        # Calculate memory usage
        memory_usage = final_memory - initial_memory

        # Add value
        self.add_value(memory_usage)

        return memory_usage

    def _get_memory_usage(self) -> float:
        """
        Get current memory usage.

        Returns:
            Memory usage in megabytes
        """
        # Get process memory usage
        memory_info = self.process.memory_info()

        # Convert to megabytes
        memory_mb = memory_info.rss / (1024 * 1024)

        # Get GPU memory usage if available
        if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / (1024 * 1024)
            memory_mb += gpu_memory

        return memory_mb

    def measure_peak(self, func: Callable, *args, **kwargs) -> float:
        """
        Measure the peak memory usage during a function call.

        Args:
            func: Function to measure
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Peak memory usage in megabytes
        """
        # Clear cache
        if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()

        # Get initial memory usage
        initial_memory = self._get_memory_usage()

        # Set up peak memory tracking
        if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

        # Run function
        result = func(*args, **kwargs)

        # Get peak memory usage
        if TORCH_AVAILABLE and self.device == "cuda" and torch.cuda.is_available():
            peak_memory = torch.cuda.max_memory_allocated() / (1024 * 1024)
        else:
            peak_memory = self._get_memory_usage()

        # Calculate peak memory usage
        peak_memory_usage = peak_memory - initial_memory

        # Add value
        self.add_value(peak_memory_usage)

        return peak_memory_usage
