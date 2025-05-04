"""
"""
Benchmark configuration for AI models.
Benchmark configuration for AI models.


This module provides configuration classes for benchmarking AI models.
This module provides configuration classes for benchmarking AI models.
"""
"""


import enum
import enum
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union




class BenchmarkType(enum.Enum):
    class BenchmarkType(enum.Enum):
    """
    """
    Enumeration of benchmark types.
    Enumeration of benchmark types.
    """
    """


    LATENCY = "latency"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    THROUGHPUT = "throughput"
    MEMORY = "memory"
    MEMORY = "memory"
    ACCURACY = "accuracy"
    ACCURACY = "accuracy"
    PERPLEXITY = "perplexity"
    PERPLEXITY = "perplexity"
    ROUGE = "rouge"
    ROUGE = "rouge"
    CUSTOM = "custom"
    CUSTOM = "custom"




    @dataclass
    @dataclass
    class BenchmarkConfig:
    class BenchmarkConfig:
    """
    """
    Configuration for benchmarking AI models.
    Configuration for benchmarking AI models.
    """
    """


    # Basic configuration
    # Basic configuration
    model_path: str
    model_path: str
    model_type: str = "text-generation"
    model_type: str = "text-generation"
    benchmark_type: BenchmarkType = BenchmarkType.LATENCY
    benchmark_type: BenchmarkType = BenchmarkType.LATENCY


    # Input data
    # Input data
    input_data: Optional[Union[str, List[str]]] = None
    input_data: Optional[Union[str, List[str]]] = None
    input_file: Optional[str] = None
    input_file: Optional[str] = None
    num_samples: int = 100
    num_samples: int = 100
    max_tokens: int = 100
    max_tokens: int = 100


    # Hardware configuration
    # Hardware configuration
    device: str = "cuda"
    device: str = "cuda"
    num_threads: int = 4
    num_threads: int = 4
    batch_size: int = 1
    batch_size: int = 1


    # Benchmark parameters
    # Benchmark parameters
    warmup_runs: int = 5
    warmup_runs: int = 5
    num_runs: int = 20
    num_runs: int = 20
    timeout: int = 60  # seconds
    timeout: int = 60  # seconds


    # Output configuration
    # Output configuration
    output_dir: Optional[str] = None
    output_dir: Optional[str] = None
    save_results: bool = True
    save_results: bool = True


    # Additional parameters
    # Additional parameters
    additional_params: Dict[str, Any] = field(default_factory=dict)
    additional_params: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the configuration to a dictionary.
    Convert the configuration to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the configuration
    Dictionary representation of the configuration
    """
    """
    return {
    return {
    "model_path": self.model_path,
    "model_path": self.model_path,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "benchmark_type": self.benchmark_type.value,
    "benchmark_type": self.benchmark_type.value,
    "input_data": self.input_data,
    "input_data": self.input_data,
    "input_file": self.input_file,
    "input_file": self.input_file,
    "num_samples": self.num_samples,
    "num_samples": self.num_samples,
    "max_tokens": self.max_tokens,
    "max_tokens": self.max_tokens,
    "device": self.device,
    "device": self.device,
    "num_threads": self.num_threads,
    "num_threads": self.num_threads,
    "batch_size": self.batch_size,
    "batch_size": self.batch_size,
    "warmup_runs": self.warmup_runs,
    "warmup_runs": self.warmup_runs,
    "num_runs": self.num_runs,
    "num_runs": self.num_runs,
    "timeout": self.timeout,
    "timeout": self.timeout,
    "output_dir": self.output_dir,
    "output_dir": self.output_dir,
    "save_results": self.save_results,
    "save_results": self.save_results,
    **self.additional_params,
    **self.additional_params,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "BenchmarkConfig":
    def from_dict(cls, config_dict: Dict[str, Any]) -> "BenchmarkConfig":
    """
    """
    Create a configuration from a dictionary.
    Create a configuration from a dictionary.


    Args:
    Args:
    config_dict: Dictionary with configuration parameters
    config_dict: Dictionary with configuration parameters


    Returns:
    Returns:
    Benchmark configuration
    Benchmark configuration
    """
    """
    # Extract benchmark type
    # Extract benchmark type
    benchmark_type_str = config_dict.pop("benchmark_type", "latency")
    benchmark_type_str = config_dict.pop("benchmark_type", "latency")
    try:
    try:
    benchmark_type = BenchmarkType(benchmark_type_str)
    benchmark_type = BenchmarkType(benchmark_type_str)
except ValueError:
except ValueError:
    benchmark_type = BenchmarkType.LATENCY
    benchmark_type = BenchmarkType.LATENCY


    # Extract additional parameters
    # Extract additional parameters
    additional_params = {}
    additional_params = {}
    for key, value in list(config_dict.items()):
    for key, value in list(config_dict.items()):
    if key not in cls.__annotations__:
    if key not in cls.__annotations__:
    additional_params[key] = config_dict.pop(key)
    additional_params[key] = config_dict.pop(key)


    # Create configuration
    # Create configuration
    config = cls(benchmark_type=benchmark_type, **config_dict)
    config = cls(benchmark_type=benchmark_type, **config_dict)


    config.additional_params = additional_params
    config.additional_params = additional_params
    return config
    return config

