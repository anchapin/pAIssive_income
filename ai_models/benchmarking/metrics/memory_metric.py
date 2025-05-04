"""
"""
Memory metric for benchmarking AI models.
Memory metric for benchmarking AI models.


This module provides a metric for measuring the memory usage of AI models.
This module provides a metric for measuring the memory usage of AI models.
"""
"""


import gc
import gc
import os
import os
from typing import Any, Callable, Dict, Optional
from typing import Any, Callable, Dict, Optional


from .base_metric import BaseMetric
from .base_metric import BaseMetric


# Try to import optional dependencies
# Try to import optional dependencies
try:
    try:
    import psutil
    import psutil


    PSUTIL_AVAILABLE = True
    PSUTIL_AVAILABLE = True
except ImportError:
except ImportError:
    PSUTIL_AVAILABLE = False
    PSUTIL_AVAILABLE = False


    try:
    try:
    import torch
    import torch


    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False




    class MemoryMetric(BaseMetric):
    class MemoryMetric(BaseMetric):
    """
    """
    Metric for measuring memory usage.
    Metric for measuring memory usage.
    """
    """


    def __init__(self, unit: str = "MB", device: str = "cpu", **kwargs):
    def __init__(self, unit: str = "MB", device: str = "cpu", **kwargs):
    """
    """
    Initialize the memory metric.
    Initialize the memory metric.


    Args:
    Args:
    unit: Unit of measurement (MB or GB)
    unit: Unit of measurement (MB or GB)
    device: Device to measure memory for (cpu or cuda)
    device: Device to measure memory for (cpu or cuda)
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    super().__init__(name="memory", unit=unit, **kwargs)
    super().__init__(name="memory", unit=unit, **kwargs)
    self.device = device
    self.device = device
    self.peak_memory = 0.0
    self.peak_memory = 0.0


    # Check if we can measure memory for the specified device
    # Check if we can measure memory for the specified device
    if self.device == "cuda" and not (
    if self.device == "cuda" and not (
    TORCH_AVAILABLE and torch.cuda.is_available()
    TORCH_AVAILABLE and torch.cuda.is_available()
    ):
    ):
    raise ValueError(
    raise ValueError(
    "CUDA memory measurement requires PyTorch with CUDA support"
    "CUDA memory measurement requires PyTorch with CUDA support"
    )
    )
    elif self.device == "cpu" and not PSUTIL_AVAILABLE:
    elif self.device == "cpu" and not PSUTIL_AVAILABLE:
    raise ValueError("CPU memory measurement requires psutil")
    raise ValueError("CPU memory measurement requires psutil")


    def measure(self, func: Optional[Callable] = None, *args, **kwargs) -> float:
    def measure(self, func: Optional[Callable] = None, *args, **kwargs) -> float:
    """
    """
    Measure the memory usage of a function call.
    Measure the memory usage of a function call.


    Args:
    Args:
    func: Optional function to measure
    func: Optional function to measure
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    Memory usage in the specified unit
    Memory usage in the specified unit
    """
    """
    # Clear memory before measurement
    # Clear memory before measurement
    gc.collect()
    gc.collect()
    if self.device == "cuda" and TORCH_AVAILABLE:
    if self.device == "cuda" and TORCH_AVAILABLE:
    torch.cuda.empty_cache()
    torch.cuda.empty_cache()


    # Measure baseline memory
    # Measure baseline memory
    baseline_memory = self._get_memory_usage()
    baseline_memory = self._get_memory_usage()


    # Run function if provided
    # Run function if provided
    if func is not None:
    if func is not None:
    func(*args, **kwargs)
    func(*args, **kwargs)


    # Force garbage collection
    # Force garbage collection
    gc.collect()
    gc.collect()
    if self.device == "cuda" and TORCH_AVAILABLE:
    if self.device == "cuda" and TORCH_AVAILABLE:
    torch.cuda.empty_cache()
    torch.cuda.empty_cache()


    # Measure memory after function call
    # Measure memory after function call
    current_memory = self._get_memory_usage()
    current_memory = self._get_memory_usage()


    # Calculate memory usage
    # Calculate memory usage
    memory_usage = current_memory - baseline_memory
    memory_usage = current_memory - baseline_memory


    # Convert to the specified unit
    # Convert to the specified unit
    if self.unit == "GB":
    if self.unit == "GB":
    memory_usage /= 1024
    memory_usage /= 1024


    # Update peak memory
    # Update peak memory
    self.peak_memory = max(self.peak_memory, memory_usage)
    self.peak_memory = max(self.peak_memory, memory_usage)


    # Add value
    # Add value
    self.add_value(memory_usage)
    self.add_value(memory_usage)


    return memory_usage
    return memory_usage


    def _get_memory_usage(self) -> float:
    def _get_memory_usage(self) -> float:
    """
    """
    Get current memory usage.
    Get current memory usage.


    Returns:
    Returns:
    Memory usage in MB
    Memory usage in MB
    """
    """
    if self.device == "cuda" and TORCH_AVAILABLE:
    if self.device == "cuda" and TORCH_AVAILABLE:
    return torch.cuda.memory_allocated() / (1024 * 1024)
    return torch.cuda.memory_allocated() / (1024 * 1024)
    elif self.device == "cpu" and PSUTIL_AVAILABLE:
    elif self.device == "cpu" and PSUTIL_AVAILABLE:
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    else:
    else:
    return 0.0
    return 0.0


    def get_peak_memory(self) -> float:
    def get_peak_memory(self) -> float:
    """
    """
    Get the peak memory usage.
    Get the peak memory usage.


    Returns:
    Returns:
    Peak memory usage in the specified unit
    Peak memory usage in the specified unit
    """
    """
    return self.peak_memory
    return self.peak_memory


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
    self.peak_memory = 0.0
    self.peak_memory = 0.0


    # Clear memory
    # Clear memory
    gc.collect()
    gc.collect()
    if self.device == "cuda" and TORCH_AVAILABLE:
    if self.device == "cuda" and TORCH_AVAILABLE:
    torch.cuda.empty_cache()
    torch.cuda.empty_cache()


    def get_stats(self) -> Dict[str, float]:
    def get_stats(self) -> Dict[str, float]:
    """
    """
    Get statistics about the memory usage values.
    Get statistics about the memory usage values.


    Returns:
    Returns:
    Dictionary with statistics
    Dictionary with statistics
    """
    """
    stats = super().get_stats()
    stats = super().get_stats()


    # Add peak memory
    # Add peak memory
    stats["peak"] = self.peak_memory
    stats["peak"] = self.peak_memory


    return stats
    return stats


    def measure_model_size(self, model: Any) -> float:
    def measure_model_size(self, model: Any) -> float:
    """
    """
    Measure the size of a model in memory.
    Measure the size of a model in memory.


    Args:
    Args:
    model: Model to measure
    model: Model to measure


    Returns:
    Returns:
    Model size in the specified unit
    Model size in the specified unit
    """
    """
    # Clear memory before measurement
    # Clear memory before measurement
    gc.collect()
    gc.collect()
    if self.device == "cuda" and TORCH_AVAILABLE:
    if self.device == "cuda" and TORCH_AVAILABLE:
    torch.cuda.empty_cache()
    torch.cuda.empty_cache()


    # Measure baseline memory
    # Measure baseline memory
    baseline_memory = self._get_memory_usage()
    baseline_memory = self._get_memory_usage()


    # Force model to the specified device if it's a PyTorch model
    # Force model to the specified device if it's a PyTorch model
    if TORCH_AVAILABLE and hasattr(model, "to") and callable(model.to):
    if TORCH_AVAILABLE and hasattr(model, "to") and callable(model.to):
    model.to(self.device)
    model.to(self.device)


    # Measure memory after loading model
    # Measure memory after loading model
    current_memory = self._get_memory_usage()
    current_memory = self._get_memory_usage()


    # Calculate memory usage
    # Calculate memory usage
    memory_usage = current_memory - baseline_memory
    memory_usage = current_memory - baseline_memory


    # Convert to the specified unit
    # Convert to the specified unit
    if self.unit == "GB":
    if self.unit == "GB":
    memory_usage /= 1024
    memory_usage /= 1024


    # Update peak memory
    # Update peak memory
    self.peak_memory = max(self.peak_memory, memory_usage)
    self.peak_memory = max(self.peak_memory, memory_usage)


    # Add value
    # Add value
    self.add_value(memory_usage)
    self.add_value(memory_usage)


    return memory_usage
    return memory_usage

