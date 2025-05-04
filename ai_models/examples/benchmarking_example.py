"""
Example usage of the benchmarking tools.

This script demonstrates how to use the benchmarking tools to measure
the performance of AI models.
"""

try:
    import torch
except ImportError:
    pass


    import argparse
    import logging
    import os
    import sys
    from typing import List

    import matplotlib.pyplot
    import torch
    import transformers

    # Add the parent directory to the path to import the ai_models module
    sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    from ai_models.benchmarking import (BenchmarkType, compare_models,
    plot_benchmark_results, plot_comparison,
    plot_latency_distribution,
    plot_memory_usage, run_benchmark)

    # Set up logging
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Try to import optional dependencies
    try:


    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. Some examples will not work.")
    TORCH_AVAILABLE = False

    try:


    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Some examples will not work.")
    TRANSFORMERS_AVAILABLE = False

    try:
    as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    logger.warning("Matplotlib not available. Plotting will not work.")
    MATPLOTLIB_AVAILABLE = False


    def test_latency_benchmark(
    model_path: str, output_dir: str, num_runs: int = 20, max_tokens: int = 100
    ) -> None:
    """
    Test latency benchmarking.

    Args:
    model_path: Path to the model
    output_dir: Directory to save the results
    num_runs: Number of runs
    max_tokens: Maximum number of tokens to generate
    """
    print("\n" + "=" * 80)
    print("Testing Latency Benchmark")
    print("=" * 80)

    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    print("PyTorch and Transformers are required for latency benchmarks")
    return # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
    # Run benchmark
    print(f"Running latency benchmark for {model_path}")
    result = run_benchmark(
    model_path=model_path,
    benchmark_type=BenchmarkType.LATENCY,
    model_type="text-generation",
    output_dir=output_dir,
    num_runs=num_runs,
    max_tokens=max_tokens,
    device="cuda" if torch.cuda.is_available() else "cpu",
    )

    # Print results
    latency_stats = result.get_latency_stats()
    print("\nLatency Statistics:")
    print(f"Min: {latency_stats.get('min', 0):.2f} ms")
    print(f"Max: {latency_stats.get('max', 0):.2f} ms")
    print(f"Mean: {latency_stats.get('mean', 0):.2f} ms")
    print(f"Median: {latency_stats.get('median', 0):.2f} ms")
    print(f"P90: {latency_stats.get('p90', 0):.2f} ms")
    print(f"P95: {latency_stats.get('p95', 0):.2f} ms")
    print(f"P99: {latency_stats.get('p99', 0):.2f} ms")

    # Plot results
    if MATPLOTLIB_AVAILABLE:
    # Plot benchmark results
    plot_path = os.path.join(
    output_dir, f"{os.path.basename(model_path)}_latency.png"
    )
    plot_benchmark_results(result, output_path=plot_path, show=False)
    print(f"Saved plot to {plot_path}")

    # Plot latency distribution
    dist_plot_path = os.path.join(
    output_dir, f"{os.path.basename(model_path)}_latency_dist.png"
    )
    plot_latency_distribution(result, output_path=dist_plot_path, show=False)
    print(f"Saved latency distribution plot to {dist_plot_path}")

except Exception as e:
    print(f"Error during latency benchmark: {e}")


    def test_throughput_benchmark(
    model_path: str,
    output_dir: str,
    batch_size: int = 4,
    num_samples: int = 20,
    max_tokens: int = 100,
    ) -> None:
    """
    Test throughput benchmarking.

    Args:
    model_path: Path to the model
    output_dir: Directory to save the results
    batch_size: Batch size
    num_samples: Number of samples
    max_tokens: Maximum number of tokens to generate
    """
    print("\n" + "=" * 80)
    print("Testing Throughput Benchmark")
    print("=" * 80)

    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    print("PyTorch and Transformers are required for throughput benchmarks")
    return # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
    # Run benchmark
    print(f"Running throughput benchmark for {model_path}")
    result = run_benchmark(
    model_path=model_path,
    benchmark_type=BenchmarkType.THROUGHPUT,
    model_type="text-generation",
    output_dir=output_dir,
    batch_size=batch_size,
    num_samples=num_samples,
    max_tokens=max_tokens,
    device="cuda" if torch.cuda.is_available() else "cpu",
    )

    # Print results
    print("\nThroughput:")
    print(f"{result.throughput:.2f} tokens/second")

    # Plot results
    if MATPLOTLIB_AVAILABLE:
    plot_path = os.path.join(
    output_dir, f"{os.path.basename(model_path)}_throughput.png"
    )
    plot_benchmark_results(result, output_path=plot_path, show=False)
    print(f"Saved plot to {plot_path}")

except Exception as e:
    print(f"Error during throughput benchmark: {e}")


    def test_memory_benchmark(model_path: str, output_dir: str) -> None:
    """
    Test memory benchmarking.

    Args:
    model_path: Path to the model
    output_dir: Directory to save the results
    """
    print("\n" + "=" * 80)
    print("Testing Memory Benchmark")
    print("=" * 80)

    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    print("PyTorch and Transformers are required for memory benchmarks")
    return # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
    # Run benchmark
    print(f"Running memory benchmark for {model_path}")
    result = run_benchmark(
    model_path=model_path,
    benchmark_type=BenchmarkType.MEMORY,
    model_type="text-generation",
    output_dir=output_dir,
    device="cuda" if torch.cuda.is_available() else "cpu",
    )

    # Print results
    memory_usage = result.memory_usage_mb
    print("\nMemory Usage:")
    print(f"Tokenizer: {memory_usage.get('tokenizer_mb', 0):.2f} MB")
    print(f"Model: {memory_usage.get('model_mb', 0):.2f} MB")
    print(f"Inference: {memory_usage.get('inference_mb', 0):.2f} MB")
    print(f"Total: {memory_usage.get('total_mb', 0):.2f} MB")

    # Plot results
    if MATPLOTLIB_AVAILABLE:
    plot_path = os.path.join(
    output_dir, f"{os.path.basename(model_path)}_memory.png"
    )
    plot_benchmark_results(result, output_path=plot_path, show=False)
    print(f"Saved plot to {plot_path}")

    memory_plot_path = os.path.join(
    output_dir, f"{os.path.basename(model_path)}_memory_breakdown.png"
    )
    plot_memory_usage(result, output_path=memory_plot_path, show=False)
    print(f"Saved memory breakdown plot to {memory_plot_path}")

except Exception as e:
    print(f"Error during memory benchmark: {e}")


    def test_model_comparison(
    model_paths: List[str],
    output_dir: str,
    benchmark_type: str = "latency",
    num_runs: int = 10,
    max_tokens: int = 50,
    ) -> None:
    """
    Test model comparison.

    Args:
    model_paths: List of paths to the models
    output_dir: Directory to save the results
    benchmark_type: Type of benchmark to run
    num_runs: Number of runs
    max_tokens: Maximum number of tokens to generate
    """
    print("\n" + "=" * 80)
    print(f"Testing Model Comparison ({benchmark_type.capitalize()})")
    print("=" * 80)

    if not TORCH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
    print("PyTorch and Transformers are required for model comparison")
    return # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    try:
    # Run comparison
    print(f"Comparing {len(model_paths)} models")
    results = compare_models(
    model_paths=model_paths,
    benchmark_type=benchmark_type,
    model_type="text-generation",
    output_dir=output_dir,
    num_runs=num_runs,
    max_tokens=max_tokens,
    device="cuda" if torch.cuda.is_available() else "cpu",
    )

    # Print results
    print(f"\nComparison Results ({len(results)} models):")
    for i, result in enumerate(results):
    model_name = os.path.basename(result.model_path)

    if benchmark_type == "latency" and result.latency_ms:
    latency_stats = result.get_latency_stats()
    print(
    f"{i+1}. {model_name}: {latency_stats.get('mean', 0):.2f} ms (mean)"
    )

    elif benchmark_type == "throughput" and result.throughput:
    print(f"{i+1}. {model_name}: {result.throughput:.2f} tokens/second")

    elif benchmark_type == "memory" and result.memory_usage_mb:
    print(
    f"{i+1}. {model_name}: {result.memory_usage_mb.get('total_mb', 0):.2f} MB"
    )

    # Plot comparison
    if MATPLOTLIB_AVAILABLE and results:
    plot_path = os.path.join(
    output_dir, f"model_comparison_{benchmark_type}.png"
    )
    plot_comparison(
    results, metric=benchmark_type, output_path=plot_path, show=False
    )
    print(f"Saved comparison plot to {plot_path}")

except Exception as e:
    print(f"Error during model comparison: {e}")


    def main():
    """
    Main function to demonstrate the benchmarking tools.
    """
    parser = argparse.ArgumentParser(description="Test benchmarking tools")
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    )
    parser.add_argument(
    "--output-dir",
    type=str,
    default="benchmark_results",
    help="Directory to save benchmark results",
    )
    parser.add_argument(
    "--benchmark",
    type=str,
    choices=["latency", "throughput", "memory", "comparison", "all"],
    default="all",
    help="Benchmark to run",
    )
    parser.add_argument(
    "--num-runs", type=int, default=20, help="Number of runs for latency benchmark"
    )
    parser.add_argument(
    "--batch-size", type=int, default=4, help="Batch size for throughput benchmark"
    )
    parser.add_argument(
    "--max-tokens",
    type=int,
    default=100,
    help="Maximum number of tokens to generate",
    )
    parser.add_argument(
    "--compare-models",
    type=str,
    nargs="+",
    help="Additional models to compare with the main model",
    )

    args = parser.parse_args()

    # Create list of models for comparison
    model_paths = [args.model_path]
    if args.compare_models:
    model_paths.extend(args.compare_models)

    if args.benchmark == "latency" or args.benchmark == "all":
    test_latency_benchmark(
    model_path=args.model_path,
    output_dir=args.output_dir,
    num_runs=args.num_runs,
    max_tokens=args.max_tokens,
    )

    if args.benchmark == "throughput" or args.benchmark == "all":
    test_throughput_benchmark(
    model_path=args.model_path,
    output_dir=args.output_dir,
    batch_size=args.batch_size,
    max_tokens=args.max_tokens,
    )

    if args.benchmark == "memory" or args.benchmark == "all":
    test_memory_benchmark(model_path=args.model_path, output_dir=args.output_dir)

    if (args.benchmark == "comparison" or args.benchmark == "all") and len(
    model_paths
    ) > 1:
    test_model_comparison(
    model_paths=model_paths,
    output_dir=args.output_dir,
    benchmark_type="latency",
    num_runs=args.num_runs,
    max_tokens=args.max_tokens,
    )


    if __name__ == "__main__":
    main()