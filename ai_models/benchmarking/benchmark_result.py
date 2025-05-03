"""
Benchmark results for AI models.

This module provides classes for storing and analyzing benchmark results.
"""


import json
import os
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .benchmark_config import BenchmarkConfig, BenchmarkType




@dataclass
class BenchmarkResult:
    """
    Results of a benchmark run.
    """

    # Basic information
    model_path: str
    model_type: str
    benchmark_type: BenchmarkType
    timestamp: float = field(default_factory=time.time)

    # Configuration
    config: Optional[BenchmarkConfig] = None

    # Metrics
    latency_ms: Optional[List[float]] = None
    throughput: Optional[float] = None
    memory_usage_mb: Optional[Dict[str, float]] = None
    accuracy: Optional[float] = None
    perplexity: Optional[float] = None
    rouge_scores: Optional[Dict[str, float]] = None

    # Custom metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    # Raw data
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result to a dictionary.

        Returns:
            Dictionary representation of the result
        """
        result = {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "benchmark_type": self.benchmark_type.value,
            "timestamp": self.timestamp,
            "config": self.config.to_dict() if self.config else None,
        }

        # Add metrics based on benchmark type
        if self.benchmark_type == BenchmarkType.LATENCY and self.latency_ms:
            result["latency_ms"] = self.latency_ms
            result["latency_stats"] = self.get_latency_stats()

        if self.benchmark_type == BenchmarkType.THROUGHPUT and self.throughput:
            result["throughput"] = self.throughput

        if self.benchmark_type == BenchmarkType.MEMORY and self.memory_usage_mb:
            result["memory_usage_mb"] = self.memory_usage_mb

        if self.benchmark_type == BenchmarkType.ACCURACY and self.accuracy:
            result["accuracy"] = self.accuracy

        if self.benchmark_type == BenchmarkType.PERPLEXITY and self.perplexity:
            result["perplexity"] = self.perplexity

        if self.benchmark_type == BenchmarkType.ROUGE and self.rouge_scores:
            result["rouge_scores"] = self.rouge_scores

        # Add custom metrics
        if self.custom_metrics:
            result["custom_metrics"] = self.custom_metrics

                return result

    @classmethod
    def from_dict(cls, result_dict: Dict[str, Any]) -> "BenchmarkResult":
        """
        Create a result from a dictionary.

        Args:
            result_dict: Dictionary with result data

        Returns:
            Benchmark result
        """
        # Extract benchmark type
        benchmark_type_str = result_dict.pop("benchmark_type", "latency")
        try:
            benchmark_type = BenchmarkType(benchmark_type_str)
        except ValueError:
            benchmark_type = BenchmarkType.LATENCY

        # Extract config
        config_dict = result_dict.pop("config", None)
        config = BenchmarkConfig.from_dict(config_dict) if config_dict else None

        # Create result
        result = cls(
            model_path=result_dict.pop("model_path"),
            model_type=result_dict.pop("model_type"),
            benchmark_type=benchmark_type,
            timestamp=result_dict.pop("timestamp", time.time()),
            config=config,
        )

        # Add metrics based on benchmark type
        if benchmark_type == BenchmarkType.LATENCY:
            result.latency_ms = result_dict.pop("latency_ms", None)

        if benchmark_type == BenchmarkType.THROUGHPUT:
            result.throughput = result_dict.pop("throughput", None)

        if benchmark_type == BenchmarkType.MEMORY:
            result.memory_usage_mb = result_dict.pop("memory_usage_mb", None)

        if benchmark_type == BenchmarkType.ACCURACY:
            result.accuracy = result_dict.pop("accuracy", None)

        if benchmark_type == BenchmarkType.PERPLEXITY:
            result.perplexity = result_dict.pop("perplexity", None)

        if benchmark_type == BenchmarkType.ROUGE:
            result.rouge_scores = result_dict.pop("rouge_scores", None)

        # Add custom metrics
        result.custom_metrics = result_dict.pop("custom_metrics", {})

        # Add remaining data as raw data
        result.raw_data = result_dict

                return result

    def save(self, output_path: str) -> str:
        """
        Save the result to a file.

        Args:
            output_path: Path to save the result

        Returns:
            Path to the saved file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save result
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

                return output_path

    @classmethod
    def load(cls, input_path: str) -> "BenchmarkResult":
        """
        Load a result from a file.

        Args:
            input_path: Path to the result file

        Returns:
            Benchmark result
        """
        with open(input_path, "r", encoding="utf-8") as f:
            result_dict = json.load(f)

                return cls.from_dict(result_dict)

    def get_latency_stats(self) -> Dict[str, float]:
        """
        Get statistics about latency measurements.

        Returns:
            Dictionary with latency statistics
        """
        if not self.latency_ms:
                    return {}

                return {
            "min": min(self.latency_ms),
            "max": max(self.latency_ms),
            "mean": statistics.mean(self.latency_ms),
            "median": statistics.median(self.latency_ms),
            "p90": self._percentile(self.latency_ms, 90),
            "p95": self._percentile(self.latency_ms, 95),
            "p99": self._percentile(self.latency_ms, 99),
            "std_dev": (
                statistics.stdev(self.latency_ms) if len(self.latency_ms) > 1 else 0
            ),
        }

    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        Calculate a percentile of a list of values.

        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        size = len(data)
        sorted_data = sorted(data)

        if not size:
                    return 0

        if size == 1:
                    return sorted_data[0]

        # Calculate the index
        k = (size - 1) * percentile / 100
        f = int(k)
        c = int(k) + 1 if k > f else f

        if f >= size:
                    return sorted_data[-1]

        if c >= size:
                    return sorted_data[-1]

        # Interpolate
        d0 = sorted_data[f] * (c - k)
        d1 = sorted_data[c] * (k - f)
                return d0 + d1