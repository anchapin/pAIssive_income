"""
Benchmark configuration for AI models.

This module provides configuration classes for benchmarking AI models.
"""


import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


class BenchmarkType

(enum.Enum):
    """
    Enumeration of benchmark types.
    """

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY = "memory"
    ACCURACY = "accuracy"
    PERPLEXITY = "perplexity"
    ROUGE = "rouge"
    CUSTOM = "custom"


@dataclass
class BenchmarkConfig:
    """
    Configuration for benchmarking AI models.
    """

    # Basic configuration
    model_path: str
    model_type: str = "text-generation"
    benchmark_type: BenchmarkType = BenchmarkType.LATENCY

    # Input data
    input_data: Optional[Union[str, List[str]]] = None
    input_file: Optional[str] = None
    num_samples: int = 100
    max_tokens: int = 100

    # Hardware configuration
    device: str = "cuda"
    num_threads: int = 4
    batch_size: int = 1

    # Benchmark parameters
    warmup_runs: int = 5
    num_runs: int = 20
    timeout: int = 60  # seconds

    # Output configuration
    output_dir: Optional[str] = None
    save_results: bool = True

    # Additional parameters
    additional_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "benchmark_type": self.benchmark_type.value,
            "input_data": self.input_data,
            "input_file": self.input_file,
            "num_samples": self.num_samples,
            "max_tokens": self.max_tokens,
            "device": self.device,
            "num_threads": self.num_threads,
            "batch_size": self.batch_size,
            "warmup_runs": self.warmup_runs,
            "num_runs": self.num_runs,
            "timeout": self.timeout,
            "output_dir": self.output_dir,
            "save_results": self.save_results,
            **self.additional_params,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "BenchmarkConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            Benchmark configuration
        """
        # Extract benchmark type
        benchmark_type_str = config_dict.pop("benchmark_type", "latency")
        try:
            benchmark_type = BenchmarkType(benchmark_type_str)
        except ValueError:
            benchmark_type = BenchmarkType.LATENCY

        # Extract additional parameters
        additional_params = {}
        for key, value in list(config_dict.items()):
            if key not in cls.__annotations__:
                additional_params[key] = config_dict.pop(key)

        # Create configuration
        config = cls(benchmark_type=benchmark_type, **config_dict)

        config.additional_params = additional_params
        return config