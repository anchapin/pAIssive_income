"""
Model benchmarking tool.

This script provides a tool for benchmarking and comparing the performance
of different AI models.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Add the parent directory to the path to import the ai_models module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_models import ModelConfig, ModelInfo, ModelManager, PerformanceMonitor

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelBenchmark:
    """
    Tool for benchmarking AI models.
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize the model benchmark.

        Args:
            config: Optional model configuration
        """
        self.config = config or ModelConfig.get_default()
        self.monitor = PerformanceMonitor(self.config)
        self.manager = ModelManager(config=self.config, performance_monitor=self.monitor)

        # Discover models
        self.manager.discover_models()

    def run_benchmark(
        self,
        model_ids: List[str],
        prompt: str,
        num_runs: int = 3,
        max_tokens: int = 100,
        temperature: float = 0.7,
        output_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a benchmark on multiple models.

        Args:
            model_ids: List of model IDs to benchmark
            prompt: Prompt to use for the benchmark
            num_runs: Number of runs per model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for text generation
            output_file: Optional file to save the results

        Returns:
            Dictionary with benchmark results
        """
        results = {
            "timestamp": time.time(),
            "prompt": prompt,
            "num_runs": num_runs,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "models": {},
        }

        for model_id in model_ids:
            model_info = self.manager.get_model_info(model_id)
            if not model_info:
                logger.warning(f"Model with ID {model_id} not found, skipping")
                continue

            logger.info(f"Benchmarking model: {model_info.name}")

            try:
                # Load the model
                model = self.manager.load_model(model_id)

                # Run the benchmark
                model_results = self._benchmark_model(
                    model=model,
                    model_info=model_info,
                    prompt=prompt,
                    num_runs=num_runs,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Add to results
                results["models"][model_id] = {
                    "name": model_info.name,
                    "type": model_info.type,
                    "format": model_info.format,
                    "quantization": model_info.quantization,
                    "results": model_results,
                }

                # Unload the model
                self.manager.unload_model(model_id)

            except Exception as e:
                logger.error(f"Error benchmarking model {model_info.name}: {e}")
                results["models"][model_id] = {"name": model_info.name, "error": str(e)}

        # Generate a comparison
        results["comparison"] = self._generate_comparison(results["models"])

        # Save results if output file is provided
        if output_file:
            try:
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Saved benchmark results to {output_file}")
            except Exception as e:
                logger.error(f"Error saving benchmark results: {e}")

        return results

    def _benchmark_model(
        self,
        model: Any,
        model_info: ModelInfo,
        prompt: str,
        num_runs: int,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """
        Benchmark a single model.

        Args:
            model: Model instance
            model_info: ModelInfo instance
            prompt: Prompt to use for the benchmark
            num_runs: Number of runs
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for text generation

        Returns:
            Dictionary with benchmark results
        """
        results = {
            "runs": [],
            "avg_inference_time": 0.0,
            "avg_tokens_per_second": 0.0,
            "avg_time_to_first_token": 0.0,
            "avg_peak_cpu_memory_mb": 0.0,
            "avg_peak_gpu_memory_mb": 0.0,
        }

        # Determine the model type and generation method
        if model_info.type == "huggingface":
            generation_method = self._generate_text_huggingface
        elif model_info.type == "llama":
            generation_method = self._generate_text_llama
        else:
            raise ValueError(f"Unsupported model type for benchmarking: {model_info.type}")

        # Run the benchmark multiple times
        for i in range(num_runs):
            logger.info(f"Run {i + 1}/{num_runs}")

            # Track inference
            with self.manager.track_inference(
                model_id=model_info.id,
                input_tokens=len(prompt.split()),
                parameters={"max_tokens": max_tokens, "temperature": temperature},
            ) as tracker:
                # Generate text
                output = generation_method(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    tracker=tracker,
                )

                # Add metadata
                tracker.add_metadata("output_length", len(output))
                tracker.add_metadata("run_number", i + 1)

        # Generate a performance report
        report = self.manager.generate_performance_report(model_info.id)

        # Add report data to results
        if report:
            results["avg_inference_time"] = report.avg_inference_time
            results["avg_tokens_per_second"] = report.avg_tokens_per_second
            results["avg_time_to_first_token"] = report.avg_time_to_first_token
            results["avg_peak_cpu_memory_mb"] = report.avg_peak_cpu_memory_mb
            results["avg_peak_gpu_memory_mb"] = report.avg_peak_gpu_memory_mb

            # Add detailed run data
            for metric in report.metrics:
                run_data = {
                    "inference_time": metric.total_time,
                    "tokens_per_second": metric.tokens_per_second,
                    "time_to_first_token": metric.time_to_first_token,
                    "output_tokens": metric.output_tokens,
                    "peak_cpu_memory_mb": metric.peak_cpu_memory_mb,
                    "peak_gpu_memory_mb": metric.peak_gpu_memory_mb,
                }
                results["runs"].append(run_data)

        return results

    def _generate_text_huggingface(
        self, model: Any, prompt: str, max_tokens: int, temperature: float, tracker: Any
    ) -> str:
        """
        Generate text using a Hugging Face model.

        Args:
            model: Hugging Face model instance
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for text generation
            tracker: InferenceTracker instance

        Returns:
            Generated text
        """
        # Generate text
        outputs = model(
            prompt,
            max_length=len(prompt.split()) + max_tokens,
            temperature=temperature,
            do_sample=True,
        )

        # Record first token time (this is approximate since we can't hook into the model)
        tracker.record_first_token()

        # Get the generated text
        if isinstance(outputs, list):
            output = outputs[0]["generated_text"]
        else:
            output = outputs["generated_text"]

        # Update token count (approximate)
        output_text = output[len(prompt) :]
        output_tokens = len(output_text.split())
        tracker.update_output_tokens(output_tokens)

        return output

    def _generate_text_llama(
        self, model: Any, prompt: str, max_tokens: int, temperature: float, tracker: Any
    ) -> str:
        """
        Generate text using a Llama model.

        Args:
            model: Llama model instance
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for text generation
            tracker: InferenceTracker instance

        Returns:
            Generated text
        """
        # Generate text
        output = model(prompt, max_tokens=max_tokens, temperature=temperature)

        # Record first token time (this is approximate since we can't hook into the model)
        tracker.record_first_token()

        # Get the generated text
        if isinstance(output, dict) and "choices" in output:
            text = output["choices"][0]["text"]
        else:
            text = str(output)

        # Update token count (approximate)
        output_tokens = len(text.split())
        tracker.update_output_tokens(output_tokens)

        return text

    def _generate_comparison(self, model_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comparison of model results.

        Args:
            model_results: Dictionary with model results

        Returns:
            Dictionary with comparison data
        """
        comparison = {
            "fastest_inference": {"model": None, "time": float("inf")},
            "highest_throughput": {"model": None, "tokens_per_second": 0},
            "lowest_latency": {"model": None, "time_to_first_token": float("inf")},
            "lowest_memory": {"model": None, "memory_mb": float("inf")},
            "ranking": [],
        }

        # Find the best models in each category
        for model_id, data in model_results.items():
            if "error" in data:
                continue

            results = data["results"]
            model_name = data["name"]

            # Check inference time
            if results["avg_inference_time"] < comparison["fastest_inference"]["time"]:
                comparison["fastest_inference"]["model"] = model_name
                comparison["fastest_inference"]["time"] = results["avg_inference_time"]

            # Check throughput
            if (
                results["avg_tokens_per_second"]
                > comparison["highest_throughput"]["tokens_per_second"]
            ):
                comparison["highest_throughput"]["model"] = model_name
                comparison["highest_throughput"]["tokens_per_second"] = results[
                    "avg_tokens_per_second"
                ]

            # Check latency
            if (
                results["avg_time_to_first_token"]
                < comparison["lowest_latency"]["time_to_first_token"]
            ):
                comparison["lowest_latency"]["model"] = model_name
                comparison["lowest_latency"]["time_to_first_token"] = results[
                    "avg_time_to_first_token"
                ]

            # Check memory usage
            memory_usage = results["avg_peak_cpu_memory_mb"]
            if results["avg_peak_gpu_memory_mb"] > 0:
                memory_usage += results["avg_peak_gpu_memory_mb"]

            if memory_usage < comparison["lowest_memory"]["memory_mb"]:
                comparison["lowest_memory"]["model"] = model_name
                comparison["lowest_memory"]["memory_mb"] = memory_usage

        # Create a ranking based on a weighted score
        models = []
        for model_id, data in model_results.items():
            if "error" in data:
                continue

            results = data["results"]
            model_name = data["name"]

            # Calculate a score (lower is better)
            # Normalize each metric to a 0 - 1 scale and apply weights
            score = 0

            if comparison["fastest_inference"]["time"] > 0:
                score += 0.3 * (
                    results["avg_inference_time"] / comparison["fastest_inference"]["time"]
                )

            if comparison["highest_throughput"]["tokens_per_second"] > 0:
                score += 0.3 * (
                    1
                    - (
                        results["avg_tokens_per_second"]
                        / comparison["highest_throughput"]["tokens_per_second"]
                    )
                )

            if comparison["lowest_latency"]["time_to_first_token"] > 0:
                score += 0.2 * (
                    results["avg_time_to_first_token"]
                    / comparison["lowest_latency"]["time_to_first_token"]
                )

            memory_usage = results["avg_peak_cpu_memory_mb"]
            if results["avg_peak_gpu_memory_mb"] > 0:
                memory_usage += results["avg_peak_gpu_memory_mb"]

            if comparison["lowest_memory"]["memory_mb"] > 0:
                score += 0.2 * (memory_usage / comparison["lowest_memory"]["memory_mb"])

            models.append(
                {
                    "model": model_name,
                    "score": score,
                    "inference_time": results["avg_inference_time"],
                    "tokens_per_second": results["avg_tokens_per_second"],
                    "time_to_first_token": results["avg_time_to_first_token"],
                    "memory_usage_mb": memory_usage,
                }
            )

        # Sort by score (lower is better)
        models.sort(key=lambda x: x["score"])
        comparison["ranking"] = models

        return comparison


def main():
    """
    Main function for the model benchmark tool.
    """
    parser = argparse.ArgumentParser(description="Benchmark AI models")
    parser.add_argument("--models", type=str, nargs=" + ", help="Model IDs to benchmark")
    parser.add_argument(
        "--prompt",
        type=str,
        default="The quick brown fox jumps over the lazy dog",
        help="Prompt to use for the benchmark",
    )
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per model")
    parser.add_argument(
        "--max - tokens",
        type=int,
        default=100,
        help="Maximum number of tokens to generate",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature for text generation"
    )
    parser.add_argument("--output", type=str, help="Output file for benchmark results")

    args = parser.parse_args()

    # Create a model benchmark
    benchmark = ModelBenchmark()

    # Get available models if none specified
    if not args.models:
        all_models = benchmark.manager.get_all_models()
        if not all_models:
            print("No models found. Please specify model IDs or discover models first.")
            return

        print("Available models:")
        for i, model in enumerate(all_models):
            print(f"{i + 1}. {model.name} (ID: {model.id}, Type: {model.type})")

        # Ask the user which models to benchmark
        selection = input("\nEnter model numbers to benchmark (comma - separated): ")
        selected_indices = [int(i.strip()) - 1 for i in selection.split(",")]

        args.models = [all_models[i].id for i in selected_indices if 0 <= i < len(all_models)]

    if not args.models:
        print("No models selected for benchmarking.")
        return

    # Run the benchmark
    results = benchmark.run_benchmark(
        model_ids=args.models,
        prompt=args.prompt,
        num_runs=args.runs,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        output_file=args.output,
    )

    # Print the results
    print("\nBenchmark Results:")
    print(f"Prompt: {args.prompt}")
    print(f"Runs per model: {args.runs}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Temperature: {args.temperature}")

    print("\nModel Results:")
    for model_id, data in results["models"].items():
        if "error" in data:
            print(f"\n{data['name']}:")
            print(f"  Error: {data['error']}")
            continue

        print(f"\n{data['name']}:")
        print(f"  Type: {data['type']}")
        print(f"  Format: {data['format']}")
        if data["quantization"]:
            print(f"  Quantization: {data['quantization']}")

        results_data = data["results"]
        print(f"  Average inference time: {results_data['avg_inference_time']:.4f} seconds")
        print(f"  Average tokens per second: {results_data['avg_tokens_per_second']:.2f}")
        print(
            f"  Average time to first token: {results_data['avg_time_to_first_token']:.4f} seconds"
        )

        if results_data["avg_peak_cpu_memory_mb"] > 0:
            print(f"  Average peak CPU memory: {results_data['avg_peak_cpu_memory_mb']:.2f} MB")

        if results_data["avg_peak_gpu_memory_mb"] > 0:
            print(f"  Average peak GPU memory: {results_data['avg_peak_gpu_memory_mb']:.2f} MB")

    # Print comparison
    comparison = results["comparison"]

    print("\nComparison:")
    if comparison["fastest_inference"]["model"]:
        print(
            f"Fastest inference: {comparison['fastest_inference']['model']} ({comparison['fastest_inference']['time']:.4f} seconds)"
        )

    if comparison["highest_throughput"]["model"]:
        print(
            f"Highest throughput: {comparison['highest_throughput']['model']} ({comparison['highest_throughput']['tokens_per_second']:.2f} tokens / second)"
        )

    if comparison["lowest_latency"]["model"]:
        print(
            f"Lowest latency: {comparison['lowest_latency']['model']} ({comparison['lowest_latency']['time_to_first_token']:.4f} seconds)"
        )

    if comparison["lowest_memory"]["model"]:
        print(
            f"Lowest memory usage: {comparison['lowest_memory']['model']} ({comparison['lowest_memory']['memory_mb']:.2f} MB)"
        )

    print("\nRanking (best to worst):")
    for i, model in enumerate(comparison["ranking"]):
        print(f"{i + 1}. {model['model']} (Score: {model['score']:.4f})")

    if args.output:
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
