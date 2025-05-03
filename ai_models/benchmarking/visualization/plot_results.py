"""
Plotting functions for benchmark results.

This module provides functions for plotting benchmark results.
"""

import os
from typing import List, Optional

from ..benchmark_config import BenchmarkType
from ..benchmark_result import BenchmarkResult

# Try to import optional dependencies
try:
    pass

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def plot_benchmark_results(
    result: BenchmarkResult,
    output_path: Optional[str] = None,
    show: bool = True,
    **kwargs,
) -> Optional[plt.Figure]:
    """
    Plot benchmark results.

    Args:
        result: Benchmark result
        output_path: Path to save the plot
        show: Whether to show the plot
        **kwargs: Additional parameters for plotting

    Returns:
        Matplotlib figure or None if matplotlib is not available
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for plotting")

    # Create figure
    fig = plt.figure(figsize=(10, 6))

    # Plot based on benchmark type
    if result.benchmark_type == BenchmarkType.LATENCY:
        _plot_latency_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.THROUGHPUT:
        _plot_throughput_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.MEMORY:
        _plot_memory_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.ACCURACY:
        _plot_accuracy_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.PERPLEXITY:
        _plot_perplexity_results(fig, result, **kwargs)
    elif result.benchmark_type == BenchmarkType.ROUGE:
        _plot_rouge_results(fig, result, **kwargs)
    else:
        plt.text(
            0.5,
            0.5,
            f"No plot available for {result.benchmark_type.value}",
            ha="center",
            va="center",
            fontsize=14,
        )

    # Add title
    plt.suptitle(
        f"{result.benchmark_type.value.capitalize()} Benchmark: {os.path.basename(result.model_path)}",
        fontsize=16,
    )

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save plot if requested
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Show plot if requested
    if show:
        plt.show()

    return fig


def plot_comparison(
    results: List[BenchmarkResult],
    metric: str,
    output_path: Optional[str] = None,
    show: bool = True,
    **kwargs,
) -> Optional[plt.Figure]:
    """
    Plot a comparison of benchmark results.

    Args:
        results: List of benchmark results
        metric: Metric to compare
        output_path: Path to save the plot
        show: Whether to show the plot
        **kwargs: Additional parameters for plotting

    Returns:
        Matplotlib figure or None if matplotlib is not available
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for plotting")

    if not results:
        raise ValueError("No results to plot")

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get model names
    model_names = [os.path.basename(result.model_path) for result in results]

    # Get metric values
    metric_values = []
    for result in results:
        if metric == "latency" and result.latency_ms:
            metric_values.append(sum(result.latency_ms) / len(result.latency_ms))
        elif metric == "throughput" and result.throughput:
            metric_values.append(result.throughput)
        elif metric == "memory" and result.memory_usage_mb:
            metric_values.append(result.memory_usage_mb.get("total_mb", 0))
        elif metric == "accuracy" and result.accuracy:
            metric_values.append(result.accuracy)
        elif metric == "perplexity" and result.perplexity:
            metric_values.append(result.perplexity)
        elif metric == "rouge" and result.rouge_scores:
            metric_values.append(result.rouge_scores.get("rougeL", 0))
        else:
            metric_values.append(0)

    # Plot bar chart
    bars = ax.bar(model_names, metric_values, **kwargs)

    # Add values on top of bars
    for bar, value in zip(bars, metric_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
        )

    # Add labels and title
    ax.set_xlabel("Model")
    ax.set_ylabel(metric.capitalize())
    ax.set_title(f"{metric.capitalize()} Comparison")

    # Rotate x - axis labels if there are many models
    if len(model_names) > 3:
        plt.xticks(rotation=45, ha="right")

    # Adjust layout
    plt.tight_layout()

    # Save plot if requested
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Show plot if requested
    if show:
        plt.show()

    return fig


def plot_latency_distribution(
    result: BenchmarkResult,
    output_path: Optional[str] = None,
    show: bool = True,
    **kwargs,
) -> Optional[plt.Figure]:
    """
    Plot the distribution of latency values.

    Args:
        result: Benchmark result
        output_path: Path to save the plot
        show: Whether to show the plot
        **kwargs: Additional parameters for plotting

    Returns:
        Matplotlib figure or None if matplotlib is not available
    """
    if not MATPLOTLIB_AVAILABLE or not NUMPY_AVAILABLE:
        raise ImportError("matplotlib and numpy are required for plotting")

    if result.benchmark_type != BenchmarkType.LATENCY or not result.latency_ms:
        raise ValueError("Result must be a latency benchmark with latency values")

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot histogram
    ax.hist(result.latency_ms, bins=20, alpha=0.7, **kwargs)

    # Add percentile lines
    latency_stats = result.get_latency_stats()
    percentiles = [
        ("Median", latency_stats.get("median", 0)),
        ("P90", latency_stats.get("p90", 0)),
        ("P95", latency_stats.get("p95", 0)),
        ("P99", latency_stats.get("p99", 0)),
    ]

    colors = ["r", "g", "b", "m"]
    for (label, value), color in zip(percentiles, colors):
        ax.axvline(value, color=color, linestyle="--", linewidth=1)
        ax.text(
            value,
            ax.get_ylim()[1] * 0.9,
            f"{label}: {value:.2f} ms",
            color=color,
            ha="center",
            va="top",
            rotation=90,
        )

    # Add labels and title
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Latency Distribution: {os.path.basename(result.model_path)}")

    # Adjust layout
    plt.tight_layout()

    # Save plot if requested
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Show plot if requested
    if show:
        plt.show()

    return fig


def plot_memory_usage(
    result: BenchmarkResult,
    output_path: Optional[str] = None,
    show: bool = True,
    **kwargs,
) -> Optional[plt.Figure]:
    """
    Plot memory usage breakdown.

    Args:
        result: Benchmark result
        output_path: Path to save the plot
        show: Whether to show the plot
        **kwargs: Additional parameters for plotting

    Returns:
        Matplotlib figure or None if matplotlib is not available
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for plotting")

    if result.benchmark_type != BenchmarkType.MEMORY or not result.memory_usage_mb:
        raise ValueError("Result must be a memory benchmark with memory usage values")

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get memory usage breakdown
    memory_usage = result.memory_usage_mb
    categories = []
    values = []

    if "tokenizer_mb" in memory_usage:
        categories.append("Tokenizer")
        values.append(memory_usage["tokenizer_mb"])

    if "model_mb" in memory_usage:
        categories.append("Model")
        values.append(memory_usage["model_mb"])

    if "inference_mb" in memory_usage:
        categories.append("Inference")
        values.append(memory_usage["inference_mb"])

    # Plot bar chart
    bars = ax.bar(categories, values, **kwargs)

    # Add values on top of bars
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f} MB",
            ha="center",
            va="bottom",
        )

    # Add labels and title
    ax.set_xlabel("Component")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_title(f"Memory Usage Breakdown: {os.path.basename(result.model_path)}")

    # Adjust layout
    plt.tight_layout()

    # Save plot if requested
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Show plot if requested
    if show:
        plt.show()

    return fig


def _plot_latency_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    Plot latency benchmark results.

    Args:
        fig: Matplotlib figure
        result: Benchmark result
        **kwargs: Additional parameters for plotting
    """
    if not result.latency_ms:
        plt.text(0.5, 0.5, "No latency data available", ha="center", va="center", fontsize=14)
        return

    # Create subplots
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    # Plot latency over time
    ax1.plot(result.latency_ms, marker="o", linestyle=" - ", markersize=3, **kwargs)
    ax1.set_xlabel("Run")
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title("Latency over Time")
    ax1.grid(True, linestyle="--", alpha=0.7)

    # Plot latency statistics
    latency_stats = result.get_latency_stats()
    stats_labels = ["Min", "Max", "Mean", "Median", "P90", "P95", "P99"]
    stats_values = [
        latency_stats.get("min", 0),
        latency_stats.get("max", 0),
        latency_stats.get("mean", 0),
        latency_stats.get("median", 0),
        latency_stats.get("p90", 0),
        latency_stats.get("p95", 0),
        latency_stats.get("p99", 0),
    ]

    ax2.bar(stats_labels, stats_values, **kwargs)
    ax2.set_xlabel("Statistic")
    ax2.set_ylabel("Latency (ms)")
    ax2.set_title("Latency Statistics")

    # Add values on top of bars
    for i, value in enumerate(stats_values):
        ax2.text(i, value, f"{value:.2f}", ha="center", va="bottom")

    # Plot latency histogram
    ax3.hist(result.latency_ms, bins=20, alpha=0.7, **kwargs)
    ax3.set_xlabel("Latency (ms)")
    ax3.set_ylabel("Frequency")
    ax3.set_title("Latency Distribution")

    # Add percentile lines
    colors = ["r", "g", "b", "m"]
    percentiles = [
        ("Median", latency_stats.get("median", 0)),
        ("P90", latency_stats.get("p90", 0)),
        ("P95", latency_stats.get("p95", 0)),
        ("P99", latency_stats.get("p99", 0)),
    ]

    for (label, value), color in zip(percentiles, colors):
        ax3.axvline(value, color=color, linestyle="--", linewidth=1)
        ax3.text(
            value,
            ax3.get_ylim()[1] * 0.9,
            f"{label}: {value:.2f} ms",
            color=color,
            ha="center",
            va="top",
            rotation=90,
        )


def _plot_throughput_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    Plot throughput benchmark results.

    Args:
        fig: Matplotlib figure
        result: Benchmark result
        **kwargs: Additional parameters for plotting
    """
    if result.throughput is None:
        plt.text(
            0.5,
            0.5,
            "No throughput data available",
            ha="center",
            va="center",
            fontsize=14,
        )
        return

    # Create subplot
    ax = fig.add_subplot(1, 1, 1)

    # Plot throughput
    ax.bar(["Throughput"], [result.throughput], **kwargs)
    ax.set_ylabel("Tokens per Second")
    ax.set_title("Throughput")

    # Add value on top of bar
    ax.text(
        0,
        result.throughput,
        f"{result.throughput:.2f} tokens / s",
        ha="center",
        va="bottom",
    )

    # Add batch size information
    if result.config and hasattr(result.config, "batch_size"):
        ax.text(
            0,
            result.throughput * 0.5,
            f"Batch Size: {result.config.batch_size}",
            ha="center",
            va="center",
        )


def _plot_memory_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    Plot memory benchmark results.

    Args:
        fig: Matplotlib figure
        result: Benchmark result
        **kwargs: Additional parameters for plotting
    """
    if not result.memory_usage_mb:
        plt.text(0.5, 0.5, "No memory data available", ha="center", va="center", fontsize=14)
        return

    # Create subplot
    ax = fig.add_subplot(1, 1, 1)

    # Get memory usage breakdown
    memory_usage = result.memory_usage_mb
    categories = []
    values = []

    if "tokenizer_mb" in memory_usage:
        categories.append("Tokenizer")
        values.append(memory_usage["tokenizer_mb"])

    if "model_mb" in memory_usage:
        categories.append("Model")
        values.append(memory_usage["model_mb"])

    if "inference_mb" in memory_usage:
        categories.append("Inference")
        values.append(memory_usage["inference_mb"])

    # Plot bar chart
    bars = ax.bar(categories, values, **kwargs)

    # Add values on top of bars
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f} MB",
            ha="center",
            va="bottom",
        )

    # Add total memory usage
    if "total_mb" in memory_usage:
        ax.text(
            0.5,
            max(values) * 1.1,
            f"Total: {memory_usage['total_mb']:.2f} MB",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    # Add labels and title
    ax.set_xlabel("Component")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_title("Memory Usage Breakdown")


def _plot_accuracy_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    Plot accuracy benchmark results.

    Args:
        fig: Matplotlib figure
        result: Benchmark result
        **kwargs: Additional parameters for plotting
    """
    if result.accuracy is None:
        plt.text(
            0.5,
            0.5,
            "No accuracy data available",
            ha="center",
            va="center",
            fontsize=14,
        )
        return

    # Create subplot
    ax = fig.add_subplot(1, 1, 1)

    # Plot accuracy
    ax.bar(["Accuracy"], [result.accuracy], **kwargs)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy")

    # Add value on top of bar
    ax.text(0, result.accuracy, f"{result.accuracy:.2f}%", ha="center", va="bottom")

    # Set y - axis limits
    ax.set_ylim(0, 100)


def _plot_perplexity_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    Plot perplexity benchmark results.

    Args:
        fig: Matplotlib figure
        result: Benchmark result
        **kwargs: Additional parameters for plotting
    """
    if result.perplexity is None:
        plt.text(
            0.5,
            0.5,
            "No perplexity data available",
            ha="center",
            va="center",
            fontsize=14,
        )
        return

    # Create subplot
    ax = fig.add_subplot(1, 1, 1)

    # Plot perplexity
    ax.bar(["Perplexity"], [result.perplexity], **kwargs)
    ax.set_ylabel("Perplexity")
    ax.set_title("Perplexity")

    # Add value on top of bar
    ax.text(0, result.perplexity, f"{result.perplexity:.2f}", ha="center", va="bottom")

    # Add note about perplexity
    ax.text(
        0,
        result.perplexity * 0.5,
        "Lower is better",
        ha="center",
        va="center",
        fontsize=10,
        style="italic",
    )


def _plot_rouge_results(fig: plt.Figure, result: BenchmarkResult, **kwargs) -> None:
    """
    Plot ROUGE benchmark results.

    Args:
        fig: Matplotlib figure
        result: Benchmark result
        **kwargs: Additional parameters for plotting
    """
    if not result.rouge_scores:
        plt.text(0.5, 0.5, "No ROUGE data available", ha="center", va="center", fontsize=14)
        return

    # Create subplot
    ax = fig.add_subplot(1, 1, 1)

    # Get ROUGE scores
    rouge_scores = result.rouge_scores
    categories = list(rouge_scores.keys())
    values = list(rouge_scores.values())

    # Plot bar chart
    bars = ax.bar(categories, values, **kwargs)

    # Add values on top of bars
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.4f}",
            ha="center",
            va="bottom",
        )

    # Add labels and title
    ax.set_xlabel("ROUGE Type")
    ax.set_ylabel("F1 Score")
    ax.set_title("ROUGE Scores")

    # Set y - axis limits
    ax.set_ylim(0, 1)
