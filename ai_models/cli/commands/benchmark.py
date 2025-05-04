"""
"""
Benchmark command for the command-line interface.
Benchmark command for the command-line interface.


This module provides a command for benchmarking models.
This module provides a command for benchmarking models.
"""
"""




import argparse
import argparse
import json
import json
import logging
import logging
import os
import os


from ..base import BaseCommand
from ..base import BaseCommand


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class BenchmarkCommand(BaseCommand):
    class BenchmarkCommand(BaseCommand):
    """
    """
    Command for benchmarking models.
    Command for benchmarking models.
    """
    """


    description = "Benchmark a model"
    description = "Benchmark a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.


    Args:
    Args:
    parser: Argument parser
    parser: Argument parser
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    "--model-path", type=str, required=True, help="Path to the model"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--model-type",
    "--model-type",
    type=str,
    type=str,
    default="text-generation",
    default="text-generation",
    choices=[
    choices=[
    "text-generation",
    "text-generation",
    "text-classification",
    "text-classification",
    "embedding",
    "embedding",
    "image",
    "image",
    "audio",
    "audio",
    ],
    ],
    help="Type of the model",
    help="Type of the model",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--benchmark-type",
    "--benchmark-type",
    type=str,
    type=str,
    default="latency",
    default="latency",
    choices=[
    choices=[
    "latency",
    "latency",
    "throughput",
    "throughput",
    "memory",
    "memory",
    "accuracy",
    "accuracy",
    "perplexity",
    "perplexity",
    "rouge",
    "rouge",
    ],
    ],
    help="Type of benchmark to run",
    help="Type of benchmark to run",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir",
    "--output-dir",
    type=str,
    type=str,
    default="benchmark_results",
    default="benchmark_results",
    help="Directory to save benchmark results",
    help="Directory to save benchmark results",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--num-runs",
    "--num-runs",
    type=int,
    type=int,
    default=20,
    default=20,
    help="Number of runs for latency benchmark",
    help="Number of runs for latency benchmark",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--batch-size",
    "--batch-size",
    type=int,
    type=int,
    default=4,
    default=4,
    help="Batch size for throughput benchmark",
    help="Batch size for throughput benchmark",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--num-samples",
    "--num-samples",
    type=int,
    type=int,
    default=10,
    default=10,
    help="Number of samples for benchmarks",
    help="Number of samples for benchmarks",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--max-tokens",
    "--max-tokens",
    type=int,
    type=int,
    default=100,
    default=100,
    help="Maximum number of tokens to generate",
    help="Maximum number of tokens to generate",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--device",
    "--device",
    type=str,
    type=str,
    default="cuda",
    default="cuda",
    choices=["cpu", "cuda"],
    choices=["cpu", "cuda"],
    help="Device to use for benchmarking",
    help="Device to use for benchmarking",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--input-file", type=str, help="Path to input file for benchmarking"
    "--input-file", type=str, help="Path to input file for benchmarking"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--compare-models",
    "--compare-models",
    type=str,
    type=str,
    help="Comma-separated list of model paths to compare",
    help="Comma-separated list of model paths to compare",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--plot", action="store_true", help="Generate plots of benchmark results"
    "--plot", action="store_true", help="Generate plots of benchmark results"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--plot-format",
    "--plot-format",
    type=str,
    type=str,
    default="png",
    default="png",
    choices=["png", "pd", "svg"],
    choices=["png", "pd", "svg"],
    help="Format for benchmark plots",
    help="Format for benchmark plots",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--config-file", type=str, help="Path to configuration file"
    "--config-file", type=str, help="Path to configuration file"
    )
    )


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_path"]):
    if not self._validate_args(["model_path"]):
    return 1
    return 1


    try:
    try:
    # Import required modules
    # Import required modules
    from ...benchmarking import (BenchmarkType, compare_models,
    from ...benchmarking import (BenchmarkType, compare_models,
    plot_benchmark_results,
    plot_benchmark_results,
    plot_comparison,
    plot_comparison,
    plot_latency_distribution,
    plot_latency_distribution,
    plot_memory_usage, run_benchmark)
    plot_memory_usage, run_benchmark)


    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(self.args.output_dir, exist_ok=True)
    os.makedirs(self.args.output_dir, exist_ok=True)


    # Load configuration from file if provided
    # Load configuration from file if provided
    config_dict = {}
    config_dict = {}
    if self.args.config_file and os.path.exists(self.args.config_file):
    if self.args.config_file and os.path.exists(self.args.config_file):
    with open(self.args.config_file, "r", encoding="utf-8") as f:
    with open(self.args.config_file, "r", encoding="utf-8") as f:
    config_dict = json.load(f)
    config_dict = json.load(f)


    # Convert benchmark type string to enum
    # Convert benchmark type string to enum
    benchmark_type_map = {
    benchmark_type_map = {
    "latency": BenchmarkType.LATENCY,
    "latency": BenchmarkType.LATENCY,
    "throughput": BenchmarkType.THROUGHPUT,
    "throughput": BenchmarkType.THROUGHPUT,
    "memory": BenchmarkType.MEMORY,
    "memory": BenchmarkType.MEMORY,
    "accuracy": BenchmarkType.ACCURACY,
    "accuracy": BenchmarkType.ACCURACY,
    "perplexity": BenchmarkType.PERPLEXITY,
    "perplexity": BenchmarkType.PERPLEXITY,
    "rouge": BenchmarkType.ROUGE,
    "rouge": BenchmarkType.ROUGE,
    }
    }
    benchmark_type = benchmark_type_map.get(
    benchmark_type = benchmark_type_map.get(
    self.args.benchmark_type, BenchmarkType.LATENCY
    self.args.benchmark_type, BenchmarkType.LATENCY
    )
    )


    # Check if we need to compare models
    # Check if we need to compare models
    if self.args.compare_models:
    if self.args.compare_models:
    # Get list of models to compare
    # Get list of models to compare
    model_paths = [self.args.model_path]
    model_paths = [self.args.model_path]
    model_paths.extend(
    model_paths.extend(
    [path.strip() for path in self.args.compare_models.split(",")]
    [path.strip() for path in self.args.compare_models.split(",")]
    )
    )


    # Run comparison
    # Run comparison
    logger.info(f"Comparing {len(model_paths)} models")
    logger.info(f"Comparing {len(model_paths)} models")


    # Create benchmark parameters
    # Create benchmark parameters
    params = {
    params = {
    "model_paths": model_paths,
    "model_paths": model_paths,
    "benchmark_type": benchmark_type,
    "benchmark_type": benchmark_type,
    "model_type": self.args.model_type,
    "model_type": self.args.model_type,
    "output_dir": self.args.output_dir,
    "output_dir": self.args.output_dir,
    "device": self.args.device,
    "device": self.args.device,
    }
    }


    # Add benchmark-specific parameters
    # Add benchmark-specific parameters
    if benchmark_type == BenchmarkType.LATENCY:
    if benchmark_type == BenchmarkType.LATENCY:
    params.update(
    params.update(
    {
    {
    "num_runs": self.args.num_runs,
    "num_runs": self.args.num_runs,
    "max_tokens": self.args.max_tokens,
    "max_tokens": self.args.max_tokens,
    }
    }
    )
    )
    elif benchmark_type == BenchmarkType.THROUGHPUT:
    elif benchmark_type == BenchmarkType.THROUGHPUT:
    params.update(
    params.update(
    {
    {
    "batch_size": self.args.batch_size,
    "batch_size": self.args.batch_size,
    "max_tokens": self.args.max_tokens,
    "max_tokens": self.args.max_tokens,
    }
    }
    )
    )
    elif benchmark_type in [
    elif benchmark_type in [
    BenchmarkType.ACCURACY,
    BenchmarkType.ACCURACY,
    BenchmarkType.PERPLEXITY,
    BenchmarkType.PERPLEXITY,
    BenchmarkType.ROUGE,
    BenchmarkType.ROUGE,
    ]:
    ]:
    params.update(
    params.update(
    {
    {
    "input_file": self.args.input_file,
    "input_file": self.args.input_file,
    "num_samples": self.args.num_samples,
    "num_samples": self.args.num_samples,
    }
    }
    )
    )


    # Update with configuration from file
    # Update with configuration from file
    params.update(config_dict)
    params.update(config_dict)


    # Run comparison
    # Run comparison
    results = compare_models(**params)
    results = compare_models(**params)


    # Print comparison results
    # Print comparison results
    print(f"\nComparison Results ({len(results)} models):")
    print(f"\nComparison Results ({len(results)} models):")
    for i, result in enumerate(results):
    for i, result in enumerate(results):
    model_name = os.path.basename(result.model_path)
    model_name = os.path.basename(result.model_path)


    if benchmark_type == BenchmarkType.LATENCY and result.latency_ms:
    if benchmark_type == BenchmarkType.LATENCY and result.latency_ms:
    latency_stats = result.get_latency_stats()
    latency_stats = result.get_latency_stats()
    print(
    print(
    f"{i+1}. {model_name}: {latency_stats.get('mean', 0):.2f} ms (mean)"
    f"{i+1}. {model_name}: {latency_stats.get('mean', 0):.2f} ms (mean)"
    )
    )


    elif (
    elif (
    benchmark_type == BenchmarkType.THROUGHPUT and result.throughput
    benchmark_type == BenchmarkType.THROUGHPUT and result.throughput
    ):
    ):
    print(
    print(
    f"{i+1}. {model_name}: {result.throughput:.2f} tokens/second"
    f"{i+1}. {model_name}: {result.throughput:.2f} tokens/second"
    )
    )


    elif (
    elif (
    benchmark_type == BenchmarkType.MEMORY
    benchmark_type == BenchmarkType.MEMORY
    and result.memory_usage_mb
    and result.memory_usage_mb
    ):
    ):
    print(
    print(
    f"{i+1}. {model_name}: {result.memory_usage_mb.get('total_mb', 0):.2f} MB"
    f"{i+1}. {model_name}: {result.memory_usage_mb.get('total_mb', 0):.2f} MB"
    )
    )


    elif benchmark_type == BenchmarkType.ACCURACY and result.accuracy:
    elif benchmark_type == BenchmarkType.ACCURACY and result.accuracy:
    print(f"{i+1}. {model_name}: {result.accuracy:.4f} accuracy")
    print(f"{i+1}. {model_name}: {result.accuracy:.4f} accuracy")


    elif (
    elif (
    benchmark_type == BenchmarkType.PERPLEXITY and result.perplexity
    benchmark_type == BenchmarkType.PERPLEXITY and result.perplexity
    ):
    ):
    print(
    print(
    f"{i+1}. {model_name}: {result.perplexity:.4f} perplexity"
    f"{i+1}. {model_name}: {result.perplexity:.4f} perplexity"
    )
    )


    elif benchmark_type == BenchmarkType.ROUGE and result.rouge_scores:
    elif benchmark_type == BenchmarkType.ROUGE and result.rouge_scores:
    rouge_l = result.rouge_scores.get("rougeL", 0)
    rouge_l = result.rouge_scores.get("rougeL", 0)
    print(f"{i+1}. {model_name}: {rouge_l:.4f} ROUGE-L")
    print(f"{i+1}. {model_name}: {rouge_l:.4f} ROUGE-L")


    # Generate comparison plot if requested
    # Generate comparison plot if requested
    if self.args.plot:
    if self.args.plot:
    plot_path = os.path.join(
    plot_path = os.path.join(
    self.args.output_dir,
    self.args.output_dir,
    f"model_comparison_{self.args.benchmark_type}.{self.args.plot_format}",
    f"model_comparison_{self.args.benchmark_type}.{self.args.plot_format}",
    )
    )
    plot_comparison(
    plot_comparison(
    results,
    results,
    metric=self.args.benchmark_type,
    metric=self.args.benchmark_type,
    output_path=plot_path,
    output_path=plot_path,
    show=False,
    show=False,
    )
    )
    logger.info(f"Comparison plot saved to {plot_path}")
    logger.info(f"Comparison plot saved to {plot_path}")
    else:
    else:
    # Run single model benchmark
    # Run single model benchmark
    logger.info(f"Benchmarking model {self.args.model_path}")
    logger.info(f"Benchmarking model {self.args.model_path}")


    # Create benchmark parameters
    # Create benchmark parameters
    params = {
    params = {
    "model_path": self.args.model_path,
    "model_path": self.args.model_path,
    "benchmark_type": benchmark_type,
    "benchmark_type": benchmark_type,
    "model_type": self.args.model_type,
    "model_type": self.args.model_type,
    "output_dir": self.args.output_dir,
    "output_dir": self.args.output_dir,
    "device": self.args.device,
    "device": self.args.device,
    }
    }


    # Add benchmark-specific parameters
    # Add benchmark-specific parameters
    if benchmark_type == BenchmarkType.LATENCY:
    if benchmark_type == BenchmarkType.LATENCY:
    params.update(
    params.update(
    {
    {
    "num_runs": self.args.num_runs,
    "num_runs": self.args.num_runs,
    "max_tokens": self.args.max_tokens,
    "max_tokens": self.args.max_tokens,
    }
    }
    )
    )
    elif benchmark_type == BenchmarkType.THROUGHPUT:
    elif benchmark_type == BenchmarkType.THROUGHPUT:
    params.update(
    params.update(
    {
    {
    "batch_size": self.args.batch_size,
    "batch_size": self.args.batch_size,
    "max_tokens": self.args.max_tokens,
    "max_tokens": self.args.max_tokens,
    }
    }
    )
    )
    elif benchmark_type in [
    elif benchmark_type in [
    BenchmarkType.ACCURACY,
    BenchmarkType.ACCURACY,
    BenchmarkType.PERPLEXITY,
    BenchmarkType.PERPLEXITY,
    BenchmarkType.ROUGE,
    BenchmarkType.ROUGE,
    ]:
    ]:
    params.update(
    params.update(
    {
    {
    "input_file": self.args.input_file,
    "input_file": self.args.input_file,
    "num_samples": self.args.num_samples,
    "num_samples": self.args.num_samples,
    }
    }
    )
    )


    # Update with configuration from file
    # Update with configuration from file
    params.update(config_dict)
    params.update(config_dict)


    # Run benchmark
    # Run benchmark
    result = run_benchmark(**params)
    result = run_benchmark(**params)


    # Print benchmark results
    # Print benchmark results
    if benchmark_type == BenchmarkType.LATENCY and result.latency_ms:
    if benchmark_type == BenchmarkType.LATENCY and result.latency_ms:
    latency_stats = result.get_latency_stats()
    latency_stats = result.get_latency_stats()
    print("\nLatency Statistics:")
    print("\nLatency Statistics:")
    print(f"Min: {latency_stats.get('min', 0):.2f} ms")
    print(f"Min: {latency_stats.get('min', 0):.2f} ms")
    print(f"Max: {latency_stats.get('max', 0):.2f} ms")
    print(f"Max: {latency_stats.get('max', 0):.2f} ms")
    print(f"Mean: {latency_stats.get('mean', 0):.2f} ms")
    print(f"Mean: {latency_stats.get('mean', 0):.2f} ms")
    print(f"Median: {latency_stats.get('median', 0):.2f} ms")
    print(f"Median: {latency_stats.get('median', 0):.2f} ms")
    print(f"P90: {latency_stats.get('p90', 0):.2f} ms")
    print(f"P90: {latency_stats.get('p90', 0):.2f} ms")
    print(f"P95: {latency_stats.get('p95', 0):.2f} ms")
    print(f"P95: {latency_stats.get('p95', 0):.2f} ms")
    print(f"P99: {latency_stats.get('p99', 0):.2f} ms")
    print(f"P99: {latency_stats.get('p99', 0):.2f} ms")


    elif benchmark_type == BenchmarkType.THROUGHPUT and result.throughput:
    elif benchmark_type == BenchmarkType.THROUGHPUT and result.throughput:
    print("\nThroughput:")
    print("\nThroughput:")
    print(f"{result.throughput:.2f} tokens/second")
    print(f"{result.throughput:.2f} tokens/second")


    elif benchmark_type == BenchmarkType.MEMORY and result.memory_usage_mb:
    elif benchmark_type == BenchmarkType.MEMORY and result.memory_usage_mb:
    print("\nMemory Usage:")
    print("\nMemory Usage:")
    print(
    print(
    f"Tokenizer: {result.memory_usage_mb.get('tokenizer_mb', 0):.2f} MB"
    f"Tokenizer: {result.memory_usage_mb.get('tokenizer_mb', 0):.2f} MB"
    )
    )
    print(f"Model: {result.memory_usage_mb.get('model_mb', 0):.2f} MB")
    print(f"Model: {result.memory_usage_mb.get('model_mb', 0):.2f} MB")
    print(
    print(
    f"Inference: {result.memory_usage_mb.get('inference_mb', 0):.2f} MB"
    f"Inference: {result.memory_usage_mb.get('inference_mb', 0):.2f} MB"
    )
    )
    print(f"Total: {result.memory_usage_mb.get('total_mb', 0):.2f} MB")
    print(f"Total: {result.memory_usage_mb.get('total_mb', 0):.2f} MB")


    elif benchmark_type == BenchmarkType.ACCURACY and result.accuracy:
    elif benchmark_type == BenchmarkType.ACCURACY and result.accuracy:
    print("\nAccuracy:")
    print("\nAccuracy:")
    print(f"{result.accuracy:.4f}")
    print(f"{result.accuracy:.4f}")


    elif benchmark_type == BenchmarkType.PERPLEXITY and result.perplexity:
    elif benchmark_type == BenchmarkType.PERPLEXITY and result.perplexity:
    print("\nPerplexity:")
    print("\nPerplexity:")
    print(f"{result.perplexity:.4f}")
    print(f"{result.perplexity:.4f}")


    elif benchmark_type == BenchmarkType.ROUGE and result.rouge_scores:
    elif benchmark_type == BenchmarkType.ROUGE and result.rouge_scores:
    print("\nROUGE Scores:")
    print("\nROUGE Scores:")
    for rouge_type, score in result.rouge_scores.items():
    for rouge_type, score in result.rouge_scores.items():
    print(f"{rouge_type}: {score:.4f}")
    print(f"{rouge_type}: {score:.4f}")


    # Generate plots if requested
    # Generate plots if requested
    if self.args.plot:
    if self.args.plot:
    # Generate benchmark plot
    # Generate benchmark plot
    plot_path = os.path.join(
    plot_path = os.path.join(
    self.args.output_dir,
    self.args.output_dir,
    f"{os.path.basename(self.args.model_path)}_{self.args.benchmark_type}.{self.args.plot_format}",
    f"{os.path.basename(self.args.model_path)}_{self.args.benchmark_type}.{self.args.plot_format}",
    )
    )
    plot_benchmark_results(result, output_path=plot_path, show=False)
    plot_benchmark_results(result, output_path=plot_path, show=False)
    logger.info(f"Benchmark plot saved to {plot_path}")
    logger.info(f"Benchmark plot saved to {plot_path}")


    # Generate additional plots based on benchmark type
    # Generate additional plots based on benchmark type
    if benchmark_type == BenchmarkType.LATENCY:
    if benchmark_type == BenchmarkType.LATENCY:
    dist_plot_path = os.path.join(
    dist_plot_path = os.path.join(
    self.args.output_dir,
    self.args.output_dir,
    f"{os.path.basename(self.args.model_path)}_latency_dist.{self.args.plot_format}",
    f"{os.path.basename(self.args.model_path)}_latency_dist.{self.args.plot_format}",
    )
    )
    plot_latency_distribution(
    plot_latency_distribution(
    result, output_path=dist_plot_path, show=False
    result, output_path=dist_plot_path, show=False
    )
    )
    logger.info(
    logger.info(
    f"Latency distribution plot saved to {dist_plot_path}"
    f"Latency distribution plot saved to {dist_plot_path}"
    )
    )


    elif benchmark_type == BenchmarkType.MEMORY:
    elif benchmark_type == BenchmarkType.MEMORY:
    memory_plot_path = os.path.join(
    memory_plot_path = os.path.join(
    self.args.output_dir,
    self.args.output_dir,
    f"{os.path.basename(self.args.model_path)}_memory_breakdown.{self.args.plot_format}",
    f"{os.path.basename(self.args.model_path)}_memory_breakdown.{self.args.plot_format}",
    )
    )
    plot_memory_usage(
    plot_memory_usage(
    result, output_path=memory_plot_path, show=False
    result, output_path=memory_plot_path, show=False
    )
    )
    logger.info(
    logger.info(
    f"Memory breakdown plot saved to {memory_plot_path}"
    f"Memory breakdown plot saved to {memory_plot_path}"
    )
    )


    return 0
    return 0


except Exception as e:
except Exception as e:
    logger.error(f"Error benchmarking model: {e}", exc_info=True)
    logger.error(f"Error benchmarking model: {e}", exc_info=True)
    return 1
    return 1