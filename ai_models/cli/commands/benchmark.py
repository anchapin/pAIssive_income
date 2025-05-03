"""
Benchmark command for the command - line interface.

This module provides a command for benchmarking models.
"""

import argparse
import json
import logging
import os

from ..base import BaseCommand

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BenchmarkCommand(BaseCommand):
    """
    Command for benchmarking models.
    """

    description = "Benchmark a model"

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Add command - specific arguments to the parser.

        Args:
            parser: Argument parser
        """
        parser.add_argument("--model - path", type=str, required=True, 
            help="Path to the model")
        parser.add_argument(
            "--model - type",
            type=str,
            default="text - generation",
            choices=[
                "text - generation",
                "text - classification",
                "embedding",
                "image",
                "audio",
            ],
            help="Type of the model",
        )
        parser.add_argument(
            "--benchmark - type",
            type=str,
            default="latency",
            choices=[
                "latency",
                "throughput",
                "memory",
                "accuracy",
                "perplexity",
                "rouge",
            ],
            help="Type of benchmark to run",
        )
        parser.add_argument(
            "--output - dir",
            type=str,
            default="benchmark_results",
            help="Directory to save benchmark results",
        )
        parser.add_argument(
            "--num - runs",
            type=int,
            default=20,
            help="Number of runs for latency benchmark",
        )
        parser.add_argument(
            "--batch - size",
            type=int,
            default=4,
            help="Batch size for throughput benchmark",
        )
        parser.add_argument(
            "--num - samples",
            type=int,
            default=10,
            help="Number of samples for benchmarks",
        )
        parser.add_argument(
            "--max - tokens",
            type=int,
            default=100,
            help="Maximum number of tokens to generate",
        )
        parser.add_argument(
            "--device",
            type=str,
            default="cuda",
            choices=["cpu", "cuda"],
            help="Device to use for benchmarking",
        )
        parser.add_argument("--input - file", type=str, 
            help="Path to input file for benchmarking")
        parser.add_argument(
            "--compare - models",
            type=str,
            help="Comma - separated list of model paths to compare",
        )
        parser.add_argument(
            "--plot", action="store_true", help="Generate plots of benchmark results"
        )
        parser.add_argument(
            "--plot - format",
            type=str,
            default="png",
            choices=["png", "pdf", "svg"],
            help="Format for benchmark plots",
        )
        parser.add_argument("--config - file", type=str, 
            help="Path to configuration file")

    def run(self) -> int:
        """
        Run the command.

        Returns:
            Exit code
        """
        # Validate arguments
        if not self._validate_args(["model_path"]):
            return 1

        try:
            # Import required modules
            from ...benchmarking import (
                BenchmarkType,
                compare_models,
                plot_benchmark_results,
                plot_comparison,
                plot_latency_distribution,
                plot_memory_usage,
                run_benchmark,
            )

            # Create output directory if it doesn't exist
            os.makedirs(self.args.output_dir, exist_ok=True)

            # Load configuration from file if provided
            config_dict = {}
            if self.args.config_file and os.path.exists(self.args.config_file):
                with open(self.args.config_file, "r", encoding="utf - 8") as f:
                    config_dict = json.load(f)

            # Convert benchmark type string to enum
            benchmark_type_map = {
                "latency": BenchmarkType.LATENCY,
                "throughput": BenchmarkType.THROUGHPUT,
                "memory": BenchmarkType.MEMORY,
                "accuracy": BenchmarkType.ACCURACY,
                "perplexity": BenchmarkType.PERPLEXITY,
                "rouge": BenchmarkType.ROUGE,
            }
            benchmark_type = benchmark_type_map.get(self.args.benchmark_type, 
                BenchmarkType.LATENCY)

            # Check if we need to compare models
            if self.args.compare_models:
                # Get list of models to compare
                model_paths = [self.args.model_path]
                model_paths.extend([path.strip() for path in self.args.compare_models.split(",
                    ")])

                # Run comparison
                logger.info(f"Comparing {len(model_paths)} models")

                # Create benchmark parameters
                params = {
                    "model_paths": model_paths,
                    "benchmark_type": benchmark_type,
                    "model_type": self.args.model_type,
                    "output_dir": self.args.output_dir,
                    "device": self.args.device,
                }

                # Add benchmark - specific parameters
                if benchmark_type == BenchmarkType.LATENCY:
                    params.update(
                        {
                            "num_runs": self.args.num_runs,
                            "max_tokens": self.args.max_tokens,
                        }
                    )
                elif benchmark_type == BenchmarkType.THROUGHPUT:
                    params.update(
                        {
                            "batch_size": self.args.batch_size,
                            "max_tokens": self.args.max_tokens,
                        }
                    )
                elif benchmark_type in [
                    BenchmarkType.ACCURACY,
                    BenchmarkType.PERPLEXITY,
                    BenchmarkType.ROUGE,
                ]:
                    params.update(
                        {
                            "input_file": self.args.input_file,
                            "num_samples": self.args.num_samples,
                        }
                    )

                # Update with configuration from file
                params.update(config_dict)

                # Run comparison
                results = compare_models(**params)

                # Print comparison results
                print(f"\nComparison Results ({len(results)} models):")
                for i, result in enumerate(results):
                    model_name = os.path.basename(result.model_path)

                    if benchmark_type == BenchmarkType.LATENCY and result.latency_ms:
                        latency_stats = result.get_latency_stats()
                        print(f"{i + 1}. {model_name}: {latency_stats.get('mean', 
                            0):.2f} ms (mean)")

                    elif benchmark_type == \
                        BenchmarkType.THROUGHPUT and result.throughput:
                        print(f"{i + \
                            1}. {model_name}: {result.throughput:.2f} tokens / second")

                    elif benchmark_type == \
                        BenchmarkType.MEMORY and result.memory_usage_mb:
                        print(
                            f"{i + 1}. {model_name}: {result.memory_usage_mb.get('total_mb', 
                                0):.2f} MB"
                        )

                    elif benchmark_type == BenchmarkType.ACCURACY and result.accuracy:
                        print(f"{i + 1}. {model_name}: {result.accuracy:.4f} accuracy")

                    elif benchmark_type == \
                        BenchmarkType.PERPLEXITY and result.perplexity:
                        print(f"{i + \
                            1}. {model_name}: {result.perplexity:.4f} perplexity")

                    elif benchmark_type == BenchmarkType.ROUGE and result.rouge_scores:
                        rouge_l = result.rouge_scores.get("rougeL", 0)
                        print(f"{i + 1}. {model_name}: {rouge_l:.4f} ROUGE - L")

                # Generate comparison plot if requested
                if self.args.plot:
                    plot_path = os.path.join(
                        self.args.output_dir,
                        f"model_comparison_{self.args.benchmark_type}.{self.args.plot_format}",
                            
                    )
                    plot_comparison(
                        results,
                        metric=self.args.benchmark_type,
                        output_path=plot_path,
                        show=False,
                    )
                    logger.info(f"Comparison plot saved to {plot_path}")
            else:
                # Run single model benchmark
                logger.info(f"Benchmarking model {self.args.model_path}")

                # Create benchmark parameters
                params = {
                    "model_path": self.args.model_path,
                    "benchmark_type": benchmark_type,
                    "model_type": self.args.model_type,
                    "output_dir": self.args.output_dir,
                    "device": self.args.device,
                }

                # Add benchmark - specific parameters
                if benchmark_type == BenchmarkType.LATENCY:
                    params.update(
                        {
                            "num_runs": self.args.num_runs,
                            "max_tokens": self.args.max_tokens,
                        }
                    )
                elif benchmark_type == BenchmarkType.THROUGHPUT:
                    params.update(
                        {
                            "batch_size": self.args.batch_size,
                            "max_tokens": self.args.max_tokens,
                        }
                    )
                elif benchmark_type in [
                    BenchmarkType.ACCURACY,
                    BenchmarkType.PERPLEXITY,
                    BenchmarkType.ROUGE,
                ]:
                    params.update(
                        {
                            "input_file": self.args.input_file,
                            "num_samples": self.args.num_samples,
                        }
                    )

                # Update with configuration from file
                params.update(config_dict)

                # Run benchmark
                result = run_benchmark(**params)

                # Print benchmark results
                if benchmark_type == BenchmarkType.LATENCY and result.latency_ms:
                    latency_stats = result.get_latency_stats()
                    print("\nLatency Statistics:")
                    print(f"Min: {latency_stats.get('min', 0):.2f} ms")
                    print(f"Max: {latency_stats.get('max', 0):.2f} ms")
                    print(f"Mean: {latency_stats.get('mean', 0):.2f} ms")
                    print(f"Median: {latency_stats.get('median', 0):.2f} ms")
                    print(f"P90: {latency_stats.get('p90', 0):.2f} ms")
                    print(f"P95: {latency_stats.get('p95', 0):.2f} ms")
                    print(f"P99: {latency_stats.get('p99', 0):.2f} ms")

                elif benchmark_type == BenchmarkType.THROUGHPUT and result.throughput:
                    print("\nThroughput:")
                    print(f"{result.throughput:.2f} tokens / second")

                elif benchmark_type == BenchmarkType.MEMORY and result.memory_usage_mb:
                    print("\nMemory Usage:")
                    print(f"Tokenizer: {result.memory_usage_mb.get('tokenizer_mb', 
                        0):.2f} MB")
                    print(f"Model: {result.memory_usage_mb.get('model_mb', 0):.2f} MB")
                    print(f"Inference: {result.memory_usage_mb.get('inference_mb', 
                        0):.2f} MB")
                    print(f"Total: {result.memory_usage_mb.get('total_mb', 0):.2f} MB")

                elif benchmark_type == BenchmarkType.ACCURACY and result.accuracy:
                    print("\nAccuracy:")
                    print(f"{result.accuracy:.4f}")

                elif benchmark_type == BenchmarkType.PERPLEXITY and result.perplexity:
                    print("\nPerplexity:")
                    print(f"{result.perplexity:.4f}")

                elif benchmark_type == BenchmarkType.ROUGE and result.rouge_scores:
                    print("\nROUGE Scores:")
                    for rouge_type, score in result.rouge_scores.items():
                        print(f"{rouge_type}: {score:.4f}")

                # Generate plots if requested
                if self.args.plot:
                    # Generate benchmark plot
                    plot_path = os.path.join(
                        self.args.output_dir,
                        f"{os.path.basename(self.args.model_path)}_{self.args.benchmark_type}.{self.args.plot_format}",
                            
                    )
                    plot_benchmark_results(result, output_path=plot_path, show=False)
                    logger.info(f"Benchmark plot saved to {plot_path}")

                    # Generate additional plots based on benchmark type
                    if benchmark_type == BenchmarkType.LATENCY:
                        dist_plot_path = os.path.join(
                            self.args.output_dir,
                            f"{os.path.basename(self.args.model_path)}_latency_dist.{self.args.plot_format}",
                                
                        )
                        plot_latency_distribution(result, output_path=dist_plot_path, 
                            show=False)
                        logger.info(
                            f"Latency distribution plot saved to {dist_plot_path}")

                    elif benchmark_type == BenchmarkType.MEMORY:
                        memory_plot_path = os.path.join(
                            self.args.output_dir,
                            f"{os.path.basename(self.args.model_path)}_memory_breakdown.{self.args.plot_format}",
                                
                        )
                        plot_memory_usage(result, output_path=memory_plot_path, 
                            show=False)
                        logger.info(
                            f"Memory breakdown plot saved to {memory_plot_path}")

            return 0

        except Exception as e:
            logger.error(f"Error benchmarking model: {e}", exc_info=True)
            return 1
