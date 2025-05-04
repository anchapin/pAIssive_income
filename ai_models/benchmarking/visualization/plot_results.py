"""
"""
Plotting functions for benchmark results.
Plotting functions for benchmark results.


This module provides functions for plotting benchmark results.
This module provides functions for plotting benchmark results.
"""
"""


import os
import os
import time
import time
from typing import List, Optional
from typing import List, Optional


import matplotlib.pyplot
import matplotlib.pyplot
import matplotlib.ticker
import matplotlib.ticker
import numpy
import numpy


from ..benchmark_config import BenchmarkType
from ..benchmark_config import BenchmarkType
from ..benchmark_result import BenchmarkResult
from ..benchmark_result import BenchmarkResult


# Try to import optional dependencies
# Try to import optional dependencies
try:
    try:
    as np
    as np


    NUMPY_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
except ImportError:
    NUMPY_AVAILABLE = False
    NUMPY_AVAILABLE = False


    try:
    try:
    as plt
    as plt
    as ticker
    as ticker


    MATPLOTLIB_AVAILABLE = True
    MATPLOTLIB_AVAILABLE = True
except ImportError:
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    MATPLOTLIB_AVAILABLE = False




    def plot_benchmark_results(
    def plot_benchmark_results(
    result: BenchmarkResult,
    result: BenchmarkResult,
    output_path: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = True,
    show: bool = True,
    **kwargs,
    **kwargs,
    ) -> Optional[plt.Figure]:
    ) -> Optional[plt.Figure]:
    """
    """
    Plot benchmark results.
    Plot benchmark results.


    Args:
    Args:
    result: Benchmark result
    result: Benchmark result
    output_path: Path to save the plot
    output_path: Path to save the plot
    show: Whether to show the plot
    show: Whether to show the plot
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting


    Returns:
    Returns:
    Matplotlib figure or None if matplotlib is not available
    Matplotlib figure or None if matplotlib is not available
    """
    """
    if not MATPLOTLIB_AVAILABLE:
    if not MATPLOTLIB_AVAILABLE:
    raise ImportError("matplotlib is required for plotting")
    raise ImportError("matplotlib is required for plotting")


    # Create figure
    # Create figure
    fig = plt.figure(figsize=(10, 6))
    fig = plt.figure(figsize=(10, 6))


    # Plot based on benchmark type
    # Plot based on benchmark type
    if result.benchmark_type == BenchmarkType.LATENCY:
    if result.benchmark_type == BenchmarkType.LATENCY:
    _plot_latency_results(fig, result, **kwargs)
    _plot_latency_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.THROUGHPUT:
    elif result.benchmark_type == BenchmarkType.THROUGHPUT:
    _plot_throughput_results(fig, result, **kwargs)
    _plot_throughput_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.MEMORY:
    elif result.benchmark_type == BenchmarkType.MEMORY:
    _plot_memory_results(fig, result, **kwargs)
    _plot_memory_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.ACCURACY:
    elif result.benchmark_type == BenchmarkType.ACCURACY:
    _plot_accuracy_results(fig, result, **kwargs)
    _plot_accuracy_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.PERPLEXITY:
    elif result.benchmark_type == BenchmarkType.PERPLEXITY:
    _plot_perplexity_results(fig, result, **kwargs)
    _plot_perplexity_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.ROUGE:
    elif result.benchmark_type == BenchmarkType.ROUGE:
    _plot_rouge_results(fig, result, **kwargs)
    _plot_rouge_results(fig, result, **kwargs)
    else:
    else:
    plt.text(
    plt.text(
    0.5,
    0.5,
    0.5,
    0.5,
    f"No plot available for {result.benchmark_type.value}",
    f"No plot available for {result.benchmark_type.value}",
    ha="center",
    ha="center",
    va="center",
    va="center",
    fontsize=14,
    fontsize=14,
    )
    )


    # Add title
    # Add title
    plt.suptitle(
    plt.suptitle(
    f"{result.benchmark_type.value.capitalize()} Benchmark: {os.path.basename(result.model_path)}",
    f"{result.benchmark_type.value.capitalize()} Benchmark: {os.path.basename(result.model_path)}",
    fontsize=16,
    fontsize=16,
    )
    )


    # Adjust layout
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.tight_layout(rect=[0, 0, 1, 0.95])


    # Save plot if requested
    # Save plot if requested
    if output_path:
    if output_path:
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


    # Show plot if requested
    # Show plot if requested
    if show:
    if show:
    plt.show()
    plt.show()


    return fig
    return fig




    def plot_comparison(
    def plot_comparison(
    results: List[BenchmarkResult],
    results: List[BenchmarkResult],
    metric: str,
    metric: str,
    output_path: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = True,
    show: bool = True,
    **kwargs,
    **kwargs,
    ) -> Optional[plt.Figure]:
    ) -> Optional[plt.Figure]:
    """
    """
    Plot a comparison of benchmark results.
    Plot a comparison of benchmark results.


    Args:
    Args:
    results: List of benchmark results
    results: List of benchmark results
    metric: Metric to compare
    metric: Metric to compare
    output_path: Path to save the plot
    output_path: Path to save the plot
    show: Whether to show the plot
    show: Whether to show the plot
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting


    Returns:
    Returns:
    Matplotlib figure or None if matplotlib is not available
    Matplotlib figure or None if matplotlib is not available
    """
    """
    if not MATPLOTLIB_AVAILABLE:
    if not MATPLOTLIB_AVAILABLE:
    raise ImportError("matplotlib is required for plotting")
    raise ImportError("matplotlib is required for plotting")


    if not results:
    if not results:
    raise ValueError("No results to plot")
    raise ValueError("No results to plot")


    # Create figure
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    fig, ax = plt.subplots(figsize=(10, 6))


    # Get model names
    # Get model names
    model_names = [os.path.basename(result.model_path) for result in results]
    model_names = [os.path.basename(result.model_path) for result in results]


    # Get metric values
    # Get metric values
    metric_values = []
    metric_values = []
    for result in results:
    for result in results:
    if metric == "latency" and result.latency_ms:
    if metric == "latency" and result.latency_ms:
    metric_values.append(sum(result.latency_ms) / len(result.latency_ms))
    metric_values.append(sum(result.latency_ms) / len(result.latency_ms))
    elif metric == "throughput" and result.throughput:
    elif metric == "throughput" and result.throughput:
    metric_values.append(result.throughput)
    metric_values.append(result.throughput)
    elif metric == "memory" and result.memory_usage_mb:
    elif metric == "memory" and result.memory_usage_mb:
    metric_values.append(result.memory_usage_mb.get("total_mb", 0))
    metric_values.append(result.memory_usage_mb.get("total_mb", 0))
    elif metric == "accuracy" and result.accuracy:
    elif metric == "accuracy" and result.accuracy:
    metric_values.append(result.accuracy)
    metric_values.append(result.accuracy)
    elif metric == "perplexity" and result.perplexity:
    elif metric == "perplexity" and result.perplexity:
    metric_values.append(result.perplexity)
    metric_values.append(result.perplexity)
    elif metric == "rouge" and result.rouge_scores:
    elif metric == "rouge" and result.rouge_scores:
    metric_values.append(result.rouge_scores.get("rougeL", 0))
    metric_values.append(result.rouge_scores.get("rougeL", 0))
    else:
    else:
    metric_values.append(0)
    metric_values.append(0)


    # Plot bar chart
    # Plot bar chart
    bars = ax.bar(model_names, metric_values, **kwargs)
    bars = ax.bar(model_names, metric_values, **kwargs)


    # Add values on top of bars
    # Add values on top of bars
    for bar, value in zip(bars, metric_values):
    for bar, value in zip(bars, metric_values):
    ax.text(
    ax.text(
    bar.get_x() + bar.get_width() / 2,
    bar.get_x() + bar.get_width() / 2,
    bar.get_height(),
    bar.get_height(),
    f"{value:.2f}",
    f"{value:.2f}",
    ha="center",
    ha="center",
    va="bottom",
    va="bottom",
    )
    )


    # Add labels and title
    # Add labels and title
    ax.set_xlabel("Model")
    ax.set_xlabel("Model")
    ax.set_ylabel(metric.capitalize())
    ax.set_ylabel(metric.capitalize())
    ax.set_title(f"{metric.capitalize()} Comparison")
    ax.set_title(f"{metric.capitalize()} Comparison")


    # Rotate x-axis labels if there are many models
    # Rotate x-axis labels if there are many models
    if len(model_names) > 3:
    if len(model_names) > 3:
    plt.xticks(rotation=45, ha="right")
    plt.xticks(rotation=45, ha="right")


    # Adjust layout
    # Adjust layout
    plt.tight_layout()
    plt.tight_layout()


    # Save plot if requested
    # Save plot if requested
    if output_path:
    if output_path:
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


    # Show plot if requested
    # Show plot if requested
    if show:
    if show:
    plt.show()
    plt.show()


    return fig
    return fig




    def plot_latency_distribution(
    def plot_latency_distribution(
    result: BenchmarkResult,
    result: BenchmarkResult,
    output_path: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = True,
    show: bool = True,
    **kwargs,
    **kwargs,
    ) -> Optional[plt.Figure]:
    ) -> Optional[plt.Figure]:
    """
    """
    Plot the distribution of latency values.
    Plot the distribution of latency values.


    Args:
    Args:
    result: Benchmark result
    result: Benchmark result
    output_path: Path to save the plot
    output_path: Path to save the plot
    show: Whether to show the plot
    show: Whether to show the plot
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting


    Returns:
    Returns:
    Matplotlib figure or None if matplotlib is not available
    Matplotlib figure or None if matplotlib is not available
    """
    """
    if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
    if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
    raise ImportError("matplotlib and numpy are required for plotting")
    raise ImportError("matplotlib and numpy are required for plotting")


    if result.benchmark_type != BenchmarkType.LATENCY or not result.latency_ms:
    if result.benchmark_type != BenchmarkType.LATENCY or not result.latency_ms:
    raise ValueError("Result must be a latency benchmark with latency values")
    raise ValueError("Result must be a latency benchmark with latency values")


    # Create figure
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    fig, ax = plt.subplots(figsize=(10, 6))


    # Plot histogram
    # Plot histogram
    ax.hist(result.latency_ms, bins=20, alpha=0.7, **kwargs)
    ax.hist(result.latency_ms, bins=20, alpha=0.7, **kwargs)


    # Add percentile lines
    # Add percentile lines
    latency_stats = result.get_latency_stats()
    latency_stats = result.get_latency_stats()
    percentiles = [
    percentiles = [
    ("Median", latency_stats.get("median", 0)),
    ("Median", latency_stats.get("median", 0)),
    ("P90", latency_stats.get("p90", 0)),
    ("P90", latency_stats.get("p90", 0)),
    ("P95", latency_stats.get("p95", 0)),
    ("P95", latency_stats.get("p95", 0)),
    ("P99", latency_stats.get("p99", 0)),
    ("P99", latency_stats.get("p99", 0)),
    ]
    ]


    colors = ["r", "g", "b", "m"]
    colors = ["r", "g", "b", "m"]
    for (label, value), color in zip(percentiles, colors):
    for (label, value), color in zip(percentiles, colors):
    ax.axvline(value, color=color, linestyle="--", linewidth=1)
    ax.axvline(value, color=color, linestyle="--", linewidth=1)
    ax.text(
    ax.text(
    value,
    value,
    ax.get_ylim()[1] * 0.9,
    ax.get_ylim()[1] * 0.9,
    f"{label}: {value:.2f} ms",
    f"{label}: {value:.2f} ms",
    color=color,
    color=color,
    ha="center",
    ha="center",
    va="top",
    va="top",
    rotation=90,
    rotation=90,
    )
    )


    # Add labels and title
    # Add labels and title
    ax.set_xlabel("Latency (ms)")
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("Frequency")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Latency Distribution: {os.path.basename(result.model_path)}")
    ax.set_title(f"Latency Distribution: {os.path.basename(result.model_path)}")


    # Adjust layout
    # Adjust layout
    plt.tight_layout()
    plt.tight_layout()


    # Save plot if requested
    # Save plot if requested
    if output_path:
    if output_path:
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


    # Show plot if requested
    # Show plot if requested
    if show:
    if show:
    plt.show()
    plt.show()


    return fig
    return fig




    def plot_memory_usage(
    def plot_memory_usage(
    result: BenchmarkResult,
    result: BenchmarkResult,
    output_path: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = True,
    show: bool = True,
    **kwargs,
    **kwargs,
    ) -> Optional[plt.Figure]:
    ) -> Optional[plt.Figure]:
    """
    """
    Plot memory usage breakdown.
    Plot memory usage breakdown.


    Args:
    Args:
    result: Benchmark result
    result: Benchmark result
    output_path: Path to save the plot
    output_path: Path to save the plot
    show: Whether to show the plot
    show: Whether to show the plot
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting


    Returns:
    Returns:
    Matplotlib figure or None if matplotlib is not available
    Matplotlib figure or None if matplotlib is not available
    """
    """
    if not MATPLOTLIB_AVAILABLE:
    if not MATPLOTLIB_AVAILABLE:
    raise ImportError("matplotlib is required for plotting")
    raise ImportError("matplotlib is required for plotting")


    if result.benchmark_type != BenchmarkType.MEMORY or not result.memory_usage_mb:
    if result.benchmark_type != BenchmarkType.MEMORY or not result.memory_usage_mb:
    raise ValueError("Result must be a memory benchmark with memory usage values")
    raise ValueError("Result must be a memory benchmark with memory usage values")


    # Create figure
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    fig, ax = plt.subplots(figsize=(10, 6))


    # Get memory usage breakdown
    # Get memory usage breakdown
    memory_usage = result.memory_usage_mb
    memory_usage = result.memory_usage_mb
    categories = []
    categories = []
    values = []
    values = []


    if "tokenizer_mb" in memory_usage:
    if "tokenizer_mb" in memory_usage:
    categories.append("Tokenizer")
    categories.append("Tokenizer")
    values.append(memory_usage["tokenizer_mb"])
    values.append(memory_usage["tokenizer_mb"])


    if "model_mb" in memory_usage:
    if "model_mb" in memory_usage:
    categories.append("Model")
    categories.append("Model")
    values.append(memory_usage["model_mb"])
    values.append(memory_usage["model_mb"])


    if "inference_mb" in memory_usage:
    if "inference_mb" in memory_usage:
    categories.append("Inference")
    categories.append("Inference")
    values.append(memory_usage["inference_mb"])
    values.append(memory_usage["inference_mb"])


    # Plot bar chart
    # Plot bar chart
    bars = ax.bar(categories, values, **kwargs)
    bars = ax.bar(categories, values, **kwargs)


    # Add values on top of bars
    # Add values on top of bars
    for bar, value in zip(bars, values):
    for bar, value in zip(bars, values):
    ax.text(
    ax.text(
    bar.get_x() + bar.get_width() / 2,
    bar.get_x() + bar.get_width() / 2,
    bar.get_height(),
    bar.get_height(),
    f"{value:.2f} MB",
    f"{value:.2f} MB",
    ha="center",
    ha="center",
    va="bottom",
    va="bottom",
    )
    )


    # Add labels and title
    # Add labels and title
    ax.set_xlabel("Component")
    ax.set_xlabel("Component")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_title(f"Memory Usage Breakdown: {os.path.basename(result.model_path)}")
    ax.set_title(f"Memory Usage Breakdown: {os.path.basename(result.model_path)}")


    # Adjust layout
    # Adjust layout
    plt.tight_layout()
    plt.tight_layout()


    # Save plot if requested
    # Save plot if requested
    if output_path:
    if output_path:
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


    # Show plot if requested
    # Show plot if requested
    if show:
    if show:
    plt.show()
    plt.show()


    return fig
    return fig




    def _plot_latency_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    def _plot_latency_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    """
    Plot latency benchmark results.
    Plot latency benchmark results.


    Args:
    Args:
    fig: Matplotlib figure
    fig: Matplotlib figure
    result: Benchmark result
    result: Benchmark result
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting
    """
    """
    if not result.latency_ms:
    if not result.latency_ms:
    plt.text(
    plt.text(
    0.5, 0.5, "No latency data available", ha="center", va="center", fontsize=14
    0.5, 0.5, "No latency data available", ha="center", va="center", fontsize=14
    )
    )
    return # Create subplots
    return # Create subplots
    gs = fig.add_gridspec(2, 2)
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    ax3 = fig.add_subplot(gs[1, :])


    # Plot latency over time
    # Plot latency over time
    ax1.plot(result.latency_ms, marker="o", linestyle="-", markersize=3, **kwargs)
    ax1.plot(result.latency_ms, marker="o", linestyle="-", markersize=3, **kwargs)
    ax1.set_xlabel("Run")
    ax1.set_xlabel("Run")
    ax1.set_ylabel("Latency (ms)")
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title("Latency over Time")
    ax1.set_title("Latency over Time")
    ax1.grid(True, linestyle="--", alpha=0.7)
    ax1.grid(True, linestyle="--", alpha=0.7)


    # Plot latency statistics
    # Plot latency statistics
    latency_stats = result.get_latency_stats()
    latency_stats = result.get_latency_stats()
    stats_labels = ["Min", "Max", "Mean", "Median", "P90", "P95", "P99"]
    stats_labels = ["Min", "Max", "Mean", "Median", "P90", "P95", "P99"]
    stats_values = [
    stats_values = [
    latency_stats.get("min", 0),
    latency_stats.get("min", 0),
    latency_stats.get("max", 0),
    latency_stats.get("max", 0),
    latency_stats.get("mean", 0),
    latency_stats.get("mean", 0),
    latency_stats.get("median", 0),
    latency_stats.get("median", 0),
    latency_stats.get("p90", 0),
    latency_stats.get("p90", 0),
    latency_stats.get("p95", 0),
    latency_stats.get("p95", 0),
    latency_stats.get("p99", 0),
    latency_stats.get("p99", 0),
    ]
    ]


    ax2.bar(stats_labels, stats_values, **kwargs)
    ax2.bar(stats_labels, stats_values, **kwargs)
    ax2.set_xlabel("Statistic")
    ax2.set_xlabel("Statistic")
    ax2.set_ylabel("Latency (ms)")
    ax2.set_ylabel("Latency (ms)")
    ax2.set_title("Latency Statistics")
    ax2.set_title("Latency Statistics")


    # Add values on top of bars
    # Add values on top of bars
    for i, value in enumerate(stats_values):
    for i, value in enumerate(stats_values):
    ax2.text(i, value, f"{value:.2f}", ha="center", va="bottom")
    ax2.text(i, value, f"{value:.2f}", ha="center", va="bottom")


    # Plot latency histogram
    # Plot latency histogram
    ax3.hist(result.latency_ms, bins=20, alpha=0.7, **kwargs)
    ax3.hist(result.latency_ms, bins=20, alpha=0.7, **kwargs)
    ax3.set_xlabel("Latency (ms)")
    ax3.set_xlabel("Latency (ms)")
    ax3.set_ylabel("Frequency")
    ax3.set_ylabel("Frequency")
    ax3.set_title("Latency Distribution")
    ax3.set_title("Latency Distribution")


    # Add percentile lines
    # Add percentile lines
    colors = ["r", "g", "b", "m"]
    colors = ["r", "g", "b", "m"]
    percentiles = [
    percentiles = [
    ("Median", latency_stats.get("median", 0)),
    ("Median", latency_stats.get("median", 0)),
    ("P90", latency_stats.get("p90", 0)),
    ("P90", latency_stats.get("p90", 0)),
    ("P95", latency_stats.get("p95", 0)),
    ("P95", latency_stats.get("p95", 0)),
    ("P99", latency_stats.get("p99", 0)),
    ("P99", latency_stats.get("p99", 0)),
    ]
    ]


    for (label, value), color in zip(percentiles, colors):
    for (label, value), color in zip(percentiles, colors):
    ax3.axvline(value, color=color, linestyle="--", linewidth=1)
    ax3.axvline(value, color=color, linestyle="--", linewidth=1)
    ax3.text(
    ax3.text(
    value,
    value,
    ax3.get_ylim()[1] * 0.9,
    ax3.get_ylim()[1] * 0.9,
    f"{label}: {value:.2f} ms",
    f"{label}: {value:.2f} ms",
    color=color,
    color=color,
    ha="center",
    ha="center",
    va="top",
    va="top",
    rotation=90,
    rotation=90,
    )
    )




    def _plot_throughput_results(
    def _plot_throughput_results(
    fig: plt.Figure, result: BenchmarkResult, **kwargs
    fig: plt.Figure, result: BenchmarkResult, **kwargs
    ) -> None:
    ) -> None:
    """
    """
    Plot throughput benchmark results.
    Plot throughput benchmark results.


    Args:
    Args:
    fig: Matplotlib figure
    fig: Matplotlib figure
    result: Benchmark result
    result: Benchmark result
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting
    """
    """
    if result.throughput is None:
    if result.throughput is None:
    plt.text(
    plt.text(
    0.5,
    0.5,
    0.5,
    0.5,
    "No throughput data available",
    "No throughput data available",
    ha="center",
    ha="center",
    va="center",
    va="center",
    fontsize=14,
    fontsize=14,
    )
    )
    return # Create subplot
    return # Create subplot
    ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_subplot(1, 1, 1)


    # Plot throughput
    # Plot throughput
    ax.bar(["Throughput"], [result.throughput], **kwargs)
    ax.bar(["Throughput"], [result.throughput], **kwargs)
    ax.set_ylabel("Tokens per Second")
    ax.set_ylabel("Tokens per Second")
    ax.set_title("Throughput")
    ax.set_title("Throughput")


    # Add value on top of bar
    # Add value on top of bar
    ax.text(
    ax.text(
    0,
    0,
    result.throughput,
    result.throughput,
    f"{result.throughput:.2f} tokens/s",
    f"{result.throughput:.2f} tokens/s",
    ha="center",
    ha="center",
    va="bottom",
    va="bottom",
    )
    )


    # Add batch size information
    # Add batch size information
    if result.config and hasattr(result.config, "batch_size"):
    if result.config and hasattr(result.config, "batch_size"):
    ax.text(
    ax.text(
    0,
    0,
    result.throughput * 0.5,
    result.throughput * 0.5,
    f"Batch Size: {result.config.batch_size}",
    f"Batch Size: {result.config.batch_size}",
    ha="center",
    ha="center",
    va="center",
    va="center",
    )
    )




    def _plot_memory_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    def _plot_memory_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    """
    Plot memory benchmark results.
    Plot memory benchmark results.


    Args:
    Args:
    fig: Matplotlib figure
    fig: Matplotlib figure
    result: Benchmark result
    result: Benchmark result
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting
    """
    """
    if not result.memory_usage_mb:
    if not result.memory_usage_mb:
    plt.text(
    plt.text(
    0.5, 0.5, "No memory data available", ha="center", va="center", fontsize=14
    0.5, 0.5, "No memory data available", ha="center", va="center", fontsize=14
    )
    )
    return # Create subplot
    return # Create subplot
    ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_subplot(1, 1, 1)


    # Get memory usage breakdown
    # Get memory usage breakdown
    memory_usage = result.memory_usage_mb
    memory_usage = result.memory_usage_mb
    categories = []
    categories = []
    values = []
    values = []


    if "tokenizer_mb" in memory_usage:
    if "tokenizer_mb" in memory_usage:
    categories.append("Tokenizer")
    categories.append("Tokenizer")
    values.append(memory_usage["tokenizer_mb"])
    values.append(memory_usage["tokenizer_mb"])


    if "model_mb" in memory_usage:
    if "model_mb" in memory_usage:
    categories.append("Model")
    categories.append("Model")
    values.append(memory_usage["model_mb"])
    values.append(memory_usage["model_mb"])


    if "inference_mb" in memory_usage:
    if "inference_mb" in memory_usage:
    categories.append("Inference")
    categories.append("Inference")
    values.append(memory_usage["inference_mb"])
    values.append(memory_usage["inference_mb"])


    # Plot bar chart
    # Plot bar chart
    bars = ax.bar(categories, values, **kwargs)
    bars = ax.bar(categories, values, **kwargs)


    # Add values on top of bars
    # Add values on top of bars
    for bar, value in zip(bars, values):
    for bar, value in zip(bars, values):
    ax.text(
    ax.text(
    bar.get_x() + bar.get_width() / 2,
    bar.get_x() + bar.get_width() / 2,
    bar.get_height(),
    bar.get_height(),
    f"{value:.2f} MB",
    f"{value:.2f} MB",
    ha="center",
    ha="center",
    va="bottom",
    va="bottom",
    )
    )


    # Add total memory usage
    # Add total memory usage
    if "total_mb" in memory_usage:
    if "total_mb" in memory_usage:
    ax.text(
    ax.text(
    0.5,
    0.5,
    max(values) * 1.1,
    max(values) * 1.1,
    f"Total: {memory_usage['total_mb']:.2f} MB",
    f"Total: {memory_usage['total_mb']:.2f} MB",
    ha="center",
    ha="center",
    va="bottom",
    va="bottom",
    fontsize=12,
    fontsize=12,
    fontweight="bold",
    fontweight="bold",
    )
    )


    # Add labels and title
    # Add labels and title
    ax.set_xlabel("Component")
    ax.set_xlabel("Component")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_title("Memory Usage Breakdown")
    ax.set_title("Memory Usage Breakdown")




    def _plot_accuracy_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    def _plot_accuracy_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    """
    Plot accuracy benchmark results.
    Plot accuracy benchmark results.


    Args:
    Args:
    fig: Matplotlib figure
    fig: Matplotlib figure
    result: Benchmark result
    result: Benchmark result
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting
    """
    """
    if result.accuracy is None:
    if result.accuracy is None:
    plt.text(
    plt.text(
    0.5,
    0.5,
    0.5,
    0.5,
    "No accuracy data available",
    "No accuracy data available",
    ha="center",
    ha="center",
    va="center",
    va="center",
    fontsize=14,
    fontsize=14,
    )
    )
    return # Create subplot
    return # Create subplot
    ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_subplot(1, 1, 1)


    # Plot accuracy
    # Plot accuracy
    ax.bar(["Accuracy"], [result.accuracy], **kwargs)
    ax.bar(["Accuracy"], [result.accuracy], **kwargs)
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy")
    ax.set_title("Accuracy")


    # Add value on top of bar
    # Add value on top of bar
    ax.text(0, result.accuracy, f"{result.accuracy:.2f}%", ha="center", va="bottom")
    ax.text(0, result.accuracy, f"{result.accuracy:.2f}%", ha="center", va="bottom")


    # Set y-axis limits
    # Set y-axis limits
    ax.set_ylim(0, 100)
    ax.set_ylim(0, 100)




    def _plot_perplexity_results(
    def _plot_perplexity_results(
    fig: plt.Figure, result: BenchmarkResult, **kwargs
    fig: plt.Figure, result: BenchmarkResult, **kwargs
    ) -> None:
    ) -> None:
    """
    """
    Plot perplexity benchmark results.
    Plot perplexity benchmark results.


    Args:
    Args:
    fig: Matplotlib figure
    fig: Matplotlib figure
    result: Benchmark result
    result: Benchmark result
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting
    """
    """
    if result.perplexity is None:
    if result.perplexity is None:
    plt.text(
    plt.text(
    0.5,
    0.5,
    0.5,
    0.5,
    "No perplexity data available",
    "No perplexity data available",
    ha="center",
    ha="center",
    va="center",
    va="center",
    fontsize=14,
    fontsize=14,
    )
    )
    return # Create subplot
    return # Create subplot
    ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_subplot(1, 1, 1)


    # Plot perplexity
    # Plot perplexity
    ax.bar(["Perplexity"], [result.perplexity], **kwargs)
    ax.bar(["Perplexity"], [result.perplexity], **kwargs)
    ax.set_ylabel("Perplexity")
    ax.set_ylabel("Perplexity")
    ax.set_title("Perplexity")
    ax.set_title("Perplexity")


    # Add value on top of bar
    # Add value on top of bar
    ax.text(0, result.perplexity, f"{result.perplexity:.2f}", ha="center", va="bottom")
    ax.text(0, result.perplexity, f"{result.perplexity:.2f}", ha="center", va="bottom")


    # Add note about perplexity
    # Add note about perplexity
    ax.text(
    ax.text(
    0,
    0,
    result.perplexity * 0.5,
    result.perplexity * 0.5,
    "Lower is better",
    "Lower is better",
    ha="center",
    ha="center",
    va="center",
    va="center",
    fontsize=10,
    fontsize=10,
    style="italic",
    style="italic",
    )
    )




    def _plot_rouge_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    def _plot_rouge_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    """
    Plot ROUGE benchmark results.
    Plot ROUGE benchmark results.


    Args:
    Args:
    fig: Matplotlib figure
    fig: Matplotlib figure
    result: Benchmark result
    result: Benchmark result
    **kwargs: Additional parameters for plotting
    **kwargs: Additional parameters for plotting
    """
    """
    if not result.rouge_scores:
    if not result.rouge_scores:
    plt.text(
    plt.text(
    0.5, 0.5, "No ROUGE data available", ha="center", va="center", fontsize=14
    0.5, 0.5, "No ROUGE data available", ha="center", va="center", fontsize=14
    )
    )
    return # Create subplot
    return # Create subplot
    ax = fig.add_subplot(1, 1, 1)
    ax = fig.add_subplot(1, 1, 1)


    # Get ROUGE scores
    # Get ROUGE scores
    rouge_scores = result.rouge_scores
    rouge_scores = result.rouge_scores
    categories = list(rouge_scores.keys())
    categories = list(rouge_scores.keys())
    values = list(rouge_scores.values())
    values = list(rouge_scores.values())


    # Plot bar chart
    # Plot bar chart
    bars = ax.bar(categories, values, **kwargs)
    bars = ax.bar(categories, values, **kwargs)


    # Add values on top of bars
    # Add values on top of bars
    for bar, value in zip(bars, values):
    for bar, value in zip(bars, values):
    ax.text(
    ax.text(
    bar.get_x() + bar.get_width() / 2,
    bar.get_x() + bar.get_width() / 2,
    bar.get_height(),
    bar.get_height(),
    f"{value:.4f}",
    f"{value:.4f}",
    ha="center",
    ha="center",
    va="bottom",
    va="bottom",
    )
    )


    # Add labels and title
    # Add labels and title
    ax.set_xlabel("ROUGE Type")
    ax.set_xlabel("ROUGE Type")
    ax.set_ylabel("F1 Score")
    ax.set_ylabel("F1 Score")
    ax.set_title("ROUGE Scores")
    ax.set_title("ROUGE Scores")


    # Set y-axis limits
    # Set y-axis limits
    ax.set_ylim(0, 1)
    ax.set_ylim(0, 1)