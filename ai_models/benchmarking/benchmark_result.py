"""
"""
Benchmark result for AI models.
Benchmark result for AI models.


This module provides classes for storing and analyzing benchmark results.
This module provides classes for storing and analyzing benchmark results.
"""
"""


import json
import json
import time
import time
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .benchmark_config import BenchmarkType
from .benchmark_config import BenchmarkType




@dataclass
@dataclass
class BenchmarkResult:
    class BenchmarkResult:
    """
    """
    Result of a benchmark run.
    Result of a benchmark run.
    """
    """


    # Basic information
    # Basic information
    model_id: str
    model_id: str
    model_type: str
    model_type: str
    benchmark_type: BenchmarkType
    benchmark_type: BenchmarkType
    timestamp: float = field(default_factory=time.time)
    timestamp: float = field(default_factory=time.time)


    # Performance metrics
    # Performance metrics
    latency_ms: Optional[float] = None
    latency_ms: Optional[float] = None
    throughput: Optional[float] = None
    throughput: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    memory_usage_mb: Optional[float] = None


    # Accuracy metrics
    # Accuracy metrics
    accuracy: Optional[float] = None
    accuracy: Optional[float] = None
    perplexity: Optional[float] = None
    perplexity: Optional[float] = None
    rouge_scores: Optional[Dict[str, float]] = None
    rouge_scores: Optional[Dict[str, float]] = None


    # Detailed results
    # Detailed results
    run_times: List[float] = field(default_factory=list)
    run_times: List[float] = field(default_factory=list)
    input_tokens: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


    # Hardware information
    # Hardware information
    device: str = "unknown"
    device: str = "unknown"
    num_threads: int = 1
    num_threads: int = 1
    batch_size: int = 1
    batch_size: int = 1


    # Additional metrics
    # Additional metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the result to a dictionary.
    Convert the result to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the result
    Dictionary representation of the result
    """
    """
    result = {
    result = {
    "model_id": self.model_id,
    "model_id": self.model_id,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "benchmark_type": self.benchmark_type.value,
    "benchmark_type": self.benchmark_type.value,
    "timestamp": self.timestamp,
    "timestamp": self.timestamp,
    "device": self.device,
    "device": self.device,
    "num_threads": self.num_threads,
    "num_threads": self.num_threads,
    "batch_size": self.batch_size,
    "batch_size": self.batch_size,
    }
    }


    # Add performance metrics if available
    # Add performance metrics if available
    if self.latency_ms is not None:
    if self.latency_ms is not None:
    result["latency_ms"] = self.latency_ms
    result["latency_ms"] = self.latency_ms
    if self.throughput is not None:
    if self.throughput is not None:
    result["throughput"] = self.throughput
    result["throughput"] = self.throughput
    if self.memory_usage_mb is not None:
    if self.memory_usage_mb is not None:
    result["memory_usage_mb"] = self.memory_usage_mb
    result["memory_usage_mb"] = self.memory_usage_mb


    # Add accuracy metrics if available
    # Add accuracy metrics if available
    if self.accuracy is not None:
    if self.accuracy is not None:
    result["accuracy"] = self.accuracy
    result["accuracy"] = self.accuracy
    if self.perplexity is not None:
    if self.perplexity is not None:
    result["perplexity"] = self.perplexity
    result["perplexity"] = self.perplexity


    # Add token counts if available
    # Add token counts if available
    if self.input_tokens is not None:
    if self.input_tokens is not None:
    result["input_tokens"] = self.input_tokens
    result["input_tokens"] = self.input_tokens
    if self.output_tokens is not None:
    if self.output_tokens is not None:
    result["output_tokens"] = self.output_tokens
    result["output_tokens"] = self.output_tokens
    if self.total_tokens is not None:
    if self.total_tokens is not None:
    result["total_tokens"] = self.total_tokens
    result["total_tokens"] = self.total_tokens


    # Add run times if available
    # Add run times if available
    if self.run_times:
    if self.run_times:
    result["run_times"] = self.run_times
    result["run_times"] = self.run_times


    # Add ROUGE scores if available
    # Add ROUGE scores if available
    if self.benchmark_type == BenchmarkType.ROUGE and self.rouge_scores:
    if self.benchmark_type == BenchmarkType.ROUGE and self.rouge_scores:
    result["rouge_scores"] = self.rouge_scores
    result["rouge_scores"] = self.rouge_scores


    # Add custom metrics
    # Add custom metrics
    if self.custom_metrics:
    if self.custom_metrics:
    result["custom_metrics"] = self.custom_metrics
    result["custom_metrics"] = self.custom_metrics


    return result
    return result


    @classmethod
    @classmethod
    def from_dict(cls, result_dict: Dict[str, Any]) -> "BenchmarkResult":
    def from_dict(cls, result_dict: Dict[str, Any]) -> "BenchmarkResult":
    """
    """
    Create a result from a dictionary.
    Create a result from a dictionary.


    Args:
    Args:
    result_dict: Dictionary with result data
    result_dict: Dictionary with result data


    Returns:
    Returns:
    Benchmark result
    Benchmark result
    """
    """
    # Extract benchmark type
    # Extract benchmark type
    benchmark_type_str = result_dict.pop("benchmark_type", "latency")
    benchmark_type_str = result_dict.pop("benchmark_type", "latency")
    try:
    try:
    benchmark_type = BenchmarkType(benchmark_type_str)
    benchmark_type = BenchmarkType(benchmark_type_str)
except ValueError:
except ValueError:
    benchmark_type = BenchmarkType.LATENCY
    benchmark_type = BenchmarkType.LATENCY


    # Extract custom metrics
    # Extract custom metrics
    custom_metrics = result_dict.pop("custom_metrics", {})
    custom_metrics = result_dict.pop("custom_metrics", {})


    # Extract ROUGE scores
    # Extract ROUGE scores
    rouge_scores = result_dict.pop("rouge_scores", None)
    rouge_scores = result_dict.pop("rouge_scores", None)


    # Create result
    # Create result
    result = cls(
    result = cls(
    model_id=result_dict.pop("model_id"),
    model_id=result_dict.pop("model_id"),
    model_type=result_dict.pop("model_type"),
    model_type=result_dict.pop("model_type"),
    benchmark_type=benchmark_type,
    benchmark_type=benchmark_type,
    **result_dict
    **result_dict
    )
    )


    result.custom_metrics = custom_metrics
    result.custom_metrics = custom_metrics
    result.rouge_scores = rouge_scores
    result.rouge_scores = rouge_scores
    return result
    return result


    def save_to_file(self, file_path: str) -> None:
    def save_to_file(self, file_path: str) -> None:
    """
    """
    Save the result to a JSON file.
    Save the result to a JSON file.


    Args:
    Args:
    file_path: Path to the output file
    file_path: Path to the output file
    """
    """
    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    json.dump(self.to_dict(), f, indent=2)
    json.dump(self.to_dict(), f, indent=2)


    @classmethod
    @classmethod
    def load_from_file(cls, file_path: str) -> "BenchmarkResult":
    def load_from_file(cls, file_path: str) -> "BenchmarkResult":
    """
    """
    Load a result from a JSON file.
    Load a result from a JSON file.


    Args:
    Args:
    file_path: Path to the input file
    file_path: Path to the input file


    Returns:
    Returns:
    Benchmark result
    Benchmark result
    """
    """
    with open(file_path, "r") as f:
    with open(file_path, "r") as f:
    result_dict = json.load(f)
    result_dict = json.load(f)
    return cls.from_dict(result_dict)
    return cls.from_dict(result_dict)


    def get_summary(self) -> Dict[str, Any]:
    def get_summary(self) -> Dict[str, Any]:
    """
    """
    Get a summary of the benchmark result.
    Get a summary of the benchmark result.


    Returns:
    Returns:
    Dictionary with summary information
    Dictionary with summary information
    """
    """
    summary = {
    summary = {
    "model_id": self.model_id,
    "model_id": self.model_id,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "benchmark_type": self.benchmark_type.value,
    "benchmark_type": self.benchmark_type.value,
    }
    }


    if self.benchmark_type == BenchmarkType.LATENCY:
    if self.benchmark_type == BenchmarkType.LATENCY:
    summary["latency_ms"] = self.latency_ms
    summary["latency_ms"] = self.latency_ms
    if self.run_times:
    if self.run_times:
    summary["min_latency_ms"] = min(self.run_times)
    summary["min_latency_ms"] = min(self.run_times)
    summary["max_latency_ms"] = max(self.run_times)
    summary["max_latency_ms"] = max(self.run_times)
    summary["std_dev"] = self._calculate_std_dev()
    summary["std_dev"] = self._calculate_std_dev()


    elif self.benchmark_type == BenchmarkType.THROUGHPUT:
    elif self.benchmark_type == BenchmarkType.THROUGHPUT:
    summary["throughput"] = self.throughput
    summary["throughput"] = self.throughput
    summary["batch_size"] = self.batch_size
    summary["batch_size"] = self.batch_size


    elif self.benchmark_type == BenchmarkType.MEMORY:
    elif self.benchmark_type == BenchmarkType.MEMORY:
    summary["memory_usage_mb"] = self.memory_usage_mb
    summary["memory_usage_mb"] = self.memory_usage_mb


    elif self.benchmark_type == BenchmarkType.ACCURACY:
    elif self.benchmark_type == BenchmarkType.ACCURACY:
    summary["accuracy"] = self.accuracy
    summary["accuracy"] = self.accuracy


    elif self.benchmark_type == BenchmarkType.PERPLEXITY:
    elif self.benchmark_type == BenchmarkType.PERPLEXITY:
    summary["perplexity"] = self.perplexity
    summary["perplexity"] = self.perplexity


    elif self.benchmark_type == BenchmarkType.ROUGE:
    elif self.benchmark_type == BenchmarkType.ROUGE:
    summary["rouge_scores"] = self.rouge_scores
    summary["rouge_scores"] = self.rouge_scores


    return summary
    return summary


    def _calculate_std_dev(self) -> float:
    def _calculate_std_dev(self) -> float:
    """
    """
    Calculate the standard deviation of run times.
    Calculate the standard deviation of run times.


    Returns:
    Returns:
    Standard deviation
    Standard deviation
    """
    """
    if not self.run_times or len(self.run_times) < 2:
    if not self.run_times or len(self.run_times) < 2:
    return 0.0
    return 0.0


    mean = sum(self.run_times) / len(self.run_times)
    mean = sum(self.run_times) / len(self.run_times)
    variance = sum((t - mean) ** 2 for t in self.run_times) / len(self.run_times)
    variance = sum((t - mean) ** 2 for t in self.run_times) / len(self.run_times)
    return variance**0.5
    return variance**0.5




    @dataclass
    @dataclass
    class BenchmarkResultSet:
    class BenchmarkResultSet:
    """
    """
    A set of benchmark results for comparison.
    A set of benchmark results for comparison.
    """
    """


    results: List[BenchmarkResult] = field(default_factory=list)
    results: List[BenchmarkResult] = field(default_factory=list)
    name: str = "Benchmark Result Set"
    name: str = "Benchmark Result Set"
    description: str = ""
    description: str = ""


    def add_result(self, result: BenchmarkResult) -> None:
    def add_result(self, result: BenchmarkResult) -> None:
    """
    """
    Add a result to the set.
    Add a result to the set.


    Args:
    Args:
    result: Benchmark result to add
    result: Benchmark result to add
    """
    """
    self.results.append(result)
    self.results.append(result)


    def get_results_by_model(self, model_id: str) -> List[BenchmarkResult]:
    def get_results_by_model(self, model_id: str) -> List[BenchmarkResult]:
    """
    """
    Get all results for a specific model.
    Get all results for a specific model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    List of benchmark results for the model
    List of benchmark results for the model
    """
    """
    return [result for result in self.results if result.model_id == model_id]
    return [result for result in self.results if result.model_id == model_id]


    def get_results_by_type(
    def get_results_by_type(
    self, benchmark_type: BenchmarkType
    self, benchmark_type: BenchmarkType
    ) -> List[BenchmarkResult]:
    ) -> List[BenchmarkResult]:
    """
    """
    Get all results for a specific benchmark type.
    Get all results for a specific benchmark type.


    Args:
    Args:
    benchmark_type: Type of benchmark
    benchmark_type: Type of benchmark


    Returns:
    Returns:
    List of benchmark results for the benchmark type
    List of benchmark results for the benchmark type
    """
    """
    return [
    return [
    result for result in self.results if result.benchmark_type == benchmark_type
    result for result in self.results if result.benchmark_type == benchmark_type
    ]
    ]


    def get_comparison(self, metric: str = "latency_ms") -> Dict[str, Any]:
    def get_comparison(self, metric: str = "latency_ms") -> Dict[str, Any]:
    """
    """
    Get a comparison of results based on a specific metric.
    Get a comparison of results based on a specific metric.


    Args:
    Args:
    metric: Metric to compare (e.g., "latency_ms", "throughput", "accuracy")
    metric: Metric to compare (e.g., "latency_ms", "throughput", "accuracy")


    Returns:
    Returns:
    Dictionary with comparison data
    Dictionary with comparison data
    """
    """
    comparison = {}
    comparison = {}
    for result in self.results:
    for result in self.results:
    if hasattr(result, metric) and getattr(result, metric) is not None:
    if hasattr(result, metric) and getattr(result, metric) is not None:
    comparison[result.model_id] = getattr(result, metric)
    comparison[result.model_id] = getattr(result, metric)
    return comparison
    return comparison


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the result set to a dictionary.
    Convert the result set to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the result set
    Dictionary representation of the result set
    """
    """
    return {
    return {
    "name": self.name,
    "name": self.name,
    "description": self.description,
    "description": self.description,
    "results": [result.to_dict() for result in self.results],
    "results": [result.to_dict() for result in self.results],
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkResultSet":
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkResultSet":
    """
    """
    Create a result set from a dictionary.
    Create a result set from a dictionary.


    Args:
    Args:
    data: Dictionary with result set data
    data: Dictionary with result set data


    Returns:
    Returns:
    Benchmark result set
    Benchmark result set
    """
    """
    result_set = cls(
    result_set = cls(
    name=data.get("name", "Benchmark Result Set"),
    name=data.get("name", "Benchmark Result Set"),
    description=data.get("description", ""),
    description=data.get("description", ""),
    )
    )
    for result_dict in data.get("results", []):
    for result_dict in data.get("results", []):
    result_set.add_result(BenchmarkResult.from_dict(result_dict))
    result_set.add_result(BenchmarkResult.from_dict(result_dict))
    return result_set
    return result_set


    def save_to_file(self, file_path: str) -> None:
    def save_to_file(self, file_path: str) -> None:
    """
    """
    Save the result set to a JSON file.
    Save the result set to a JSON file.


    Args:
    Args:
    file_path: Path to the output file
    file_path: Path to the output file
    """
    """
    with open(file_path, "w") as f:
    with open(file_path, "w") as f:
    json.dump(self.to_dict(), f, indent=2)
    json.dump(self.to_dict(), f, indent=2)


    @classmethod
    @classmethod
    def load_from_file(cls, file_path: str) -> "BenchmarkResultSet":
    def load_from_file(cls, file_path: str) -> "BenchmarkResultSet":
    """
    """
    Load a result set from a JSON file.
    Load a result set from a JSON file.


    Args:
    Args:
    file_path: Path to the input file
    file_path: Path to the input file


    Returns:
    Returns:
    Benchmark result set
    Benchmark result set
    """
    """
    with open(file_path, "r") as f:
    with open(file_path, "r") as f:
    data = json.load(f)
    data = json.load(f)
    return cls.from_dict(data)
    return cls.from_dict(data)

