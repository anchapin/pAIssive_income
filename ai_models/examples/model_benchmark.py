"""
"""
Model benchmarking tool.
Model benchmarking tool.


This script provides a tool for benchmarking and comparing the performance
This script provides a tool for benchmarking and comparing the performance
of different AI models.
of different AI models.
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
import sys
import sys
import time
import time
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from ai_models import ModelConfig, ModelInfo, ModelManager, PerformanceMonitor
from ai_models import ModelConfig, ModelInfo, ModelManager, PerformanceMonitor


# Add the parent directory to the path to import the ai_models module
# Add the parent directory to the path to import the ai_models module
sys.path.append(
sys.path.append(
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
)
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




class ModelBenchmark:
    class ModelBenchmark:
    """
    """
    Tool for benchmarking AI models.
    Tool for benchmarking AI models.
    """
    """


    def __init__(self, config: Optional[ModelConfig] = None):
    def __init__(self, config: Optional[ModelConfig] = None):
    """
    """
    Initialize the model benchmark.
    Initialize the model benchmark.


    Args:
    Args:
    config: Optional model configuration
    config: Optional model configuration
    """
    """
    self.config = config or ModelConfig.get_default()
    self.config = config or ModelConfig.get_default()
    self.monitor = PerformanceMonitor(self.config)
    self.monitor = PerformanceMonitor(self.config)
    self.manager = ModelManager(
    self.manager = ModelManager(
    config=self.config, performance_monitor=self.monitor
    config=self.config, performance_monitor=self.monitor
    )
    )


    # Discover models
    # Discover models
    self.manager.discover_models()
    self.manager.discover_models()


    def run_benchmark(
    def run_benchmark(
    self,
    self,
    model_ids: List[str],
    model_ids: List[str],
    prompt: str,
    prompt: str,
    num_runs: int = 3,
    num_runs: int = 3,
    max_tokens: int = 100,
    max_tokens: int = 100,
    temperature: float = 0.7,
    temperature: float = 0.7,
    output_file: Optional[str] = None,
    output_file: Optional[str] = None,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Run a benchmark on multiple models.
    Run a benchmark on multiple models.


    Args:
    Args:
    model_ids: List of model IDs to benchmark
    model_ids: List of model IDs to benchmark
    prompt: Prompt to use for the benchmark
    prompt: Prompt to use for the benchmark
    num_runs: Number of runs per model
    num_runs: Number of runs per model
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    temperature: Temperature for text generation
    temperature: Temperature for text generation
    output_file: Optional file to save the results
    output_file: Optional file to save the results


    Returns:
    Returns:
    Dictionary with benchmark results
    Dictionary with benchmark results
    """
    """
    results = {
    results = {
    "timestamp": time.time(),
    "timestamp": time.time(),
    "prompt": prompt,
    "prompt": prompt,
    "num_runs": num_runs,
    "num_runs": num_runs,
    "max_tokens": max_tokens,
    "max_tokens": max_tokens,
    "temperature": temperature,
    "temperature": temperature,
    "models": {},
    "models": {},
    }
    }


    for model_id in model_ids:
    for model_id in model_ids:
    model_info = self.manager.get_model_info(model_id)
    model_info = self.manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    logger.warning(f"Model with ID {model_id} not found, skipping")
    logger.warning(f"Model with ID {model_id} not found, skipping")
    continue
    continue


    logger.info(f"Benchmarking model: {model_info.name}")
    logger.info(f"Benchmarking model: {model_info.name}")


    try:
    try:
    # Load the model
    # Load the model
    model = self.manager.load_model(model_id)
    model = self.manager.load_model(model_id)


    # Run the benchmark
    # Run the benchmark
    model_results = self._benchmark_model(
    model_results = self._benchmark_model(
    model=model,
    model=model,
    model_info=model_info,
    model_info=model_info,
    prompt=prompt,
    prompt=prompt,
    num_runs=num_runs,
    num_runs=num_runs,
    max_tokens=max_tokens,
    max_tokens=max_tokens,
    temperature=temperature,
    temperature=temperature,
    )
    )


    # Add to results
    # Add to results
    results["models"][model_id] = {
    results["models"][model_id] = {
    "name": model_info.name,
    "name": model_info.name,
    "type": model_info.type,
    "type": model_info.type,
    "format": model_info.format,
    "format": model_info.format,
    "quantization": model_info.quantization,
    "quantization": model_info.quantization,
    "results": model_results,
    "results": model_results,
    }
    }


    # Unload the model
    # Unload the model
    self.manager.unload_model(model_id)
    self.manager.unload_model(model_id)


except Exception as e:
except Exception as e:
    logger.error(f"Error benchmarking model {model_info.name}: {e}")
    logger.error(f"Error benchmarking model {model_info.name}: {e}")
    results["models"][model_id] = {"name": model_info.name, "error": str(e)}
    results["models"][model_id] = {"name": model_info.name, "error": str(e)}


    # Generate a comparison
    # Generate a comparison
    results["comparison"] = self._generate_comparison(results["models"])
    results["comparison"] = self._generate_comparison(results["models"])


    # Save results if output file is provided
    # Save results if output file is provided
    if output_file:
    if output_file:
    try:
    try:
    with open(output_file, "w") as f:
    with open(output_file, "w") as f:
    json.dump(results, f, indent=2)
    json.dump(results, f, indent=2)
    logger.info(f"Saved benchmark results to {output_file}")
    logger.info(f"Saved benchmark results to {output_file}")
except Exception as e:
except Exception as e:
    logger.error(f"Error saving benchmark results: {e}")
    logger.error(f"Error saving benchmark results: {e}")


    return results
    return results


    def _benchmark_model(
    def _benchmark_model(
    self,
    self,
    model: Any,
    model: Any,
    model_info: ModelInfo,
    model_info: ModelInfo,
    prompt: str,
    prompt: str,
    num_runs: int,
    num_runs: int,
    max_tokens: int,
    max_tokens: int,
    temperature: float,
    temperature: float,
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    Benchmark a single model.
    Benchmark a single model.


    Args:
    Args:
    model: Model instance
    model: Model instance
    model_info: ModelInfo instance
    model_info: ModelInfo instance
    prompt: Prompt to use for the benchmark
    prompt: Prompt to use for the benchmark
    num_runs: Number of runs
    num_runs: Number of runs
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    temperature: Temperature for text generation
    temperature: Temperature for text generation


    Returns:
    Returns:
    Dictionary with benchmark results
    Dictionary with benchmark results
    """
    """
    results = {
    results = {
    "runs": [],
    "runs": [],
    "avg_inference_time": 0.0,
    "avg_inference_time": 0.0,
    "avg_tokens_per_second": 0.0,
    "avg_tokens_per_second": 0.0,
    "avg_time_to_first_token": 0.0,
    "avg_time_to_first_token": 0.0,
    "avg_peak_cpu_memory_mb": 0.0,
    "avg_peak_cpu_memory_mb": 0.0,
    "avg_peak_gpu_memory_mb": 0.0,
    "avg_peak_gpu_memory_mb": 0.0,
    }
    }


    # Determine the model type and generation method
    # Determine the model type and generation method
    if model_info.type == "huggingface":
    if model_info.type == "huggingface":
    generation_method = self._generate_text_huggingface
    generation_method = self._generate_text_huggingface
    elif model_info.type == "llama":
    elif model_info.type == "llama":
    generation_method = self._generate_text_llama
    generation_method = self._generate_text_llama
    else:
    else:
    raise ValueError(
    raise ValueError(
    f"Unsupported model type for benchmarking: {model_info.type}"
    f"Unsupported model type for benchmarking: {model_info.type}"
    )
    )


    # Run the benchmark multiple times
    # Run the benchmark multiple times
    for i in range(num_runs):
    for i in range(num_runs):
    logger.info(f"Run {i+1}/{num_runs}")
    logger.info(f"Run {i+1}/{num_runs}")


    # Track inference
    # Track inference
    with self.manager.track_inference(
    with self.manager.track_inference(
    model_id=model_info.id,
    model_id=model_info.id,
    input_tokens=len(prompt.split()),
    input_tokens=len(prompt.split()),
    parameters={"max_tokens": max_tokens, "temperature": temperature},
    parameters={"max_tokens": max_tokens, "temperature": temperature},
    ) as tracker:
    ) as tracker:
    # Generate text
    # Generate text
    output = generation_method(
    output = generation_method(
    model=model,
    model=model,
    prompt=prompt,
    prompt=prompt,
    max_tokens=max_tokens,
    max_tokens=max_tokens,
    temperature=temperature,
    temperature=temperature,
    tracker=tracker,
    tracker=tracker,
    )
    )


    # Add metadata
    # Add metadata
    tracker.add_metadata("output_length", len(output))
    tracker.add_metadata("output_length", len(output))
    tracker.add_metadata("run_number", i + 1)
    tracker.add_metadata("run_number", i + 1)


    # Generate a performance report
    # Generate a performance report
    report = self.manager.generate_performance_report(model_info.id)
    report = self.manager.generate_performance_report(model_info.id)


    # Add report data to results
    # Add report data to results
    if report:
    if report:
    results["avg_inference_time"] = report.avg_inference_time
    results["avg_inference_time"] = report.avg_inference_time
    results["avg_tokens_per_second"] = report.avg_tokens_per_second
    results["avg_tokens_per_second"] = report.avg_tokens_per_second
    results["avg_time_to_first_token"] = report.avg_time_to_first_token
    results["avg_time_to_first_token"] = report.avg_time_to_first_token
    results["avg_peak_cpu_memory_mb"] = report.avg_peak_cpu_memory_mb
    results["avg_peak_cpu_memory_mb"] = report.avg_peak_cpu_memory_mb
    results["avg_peak_gpu_memory_mb"] = report.avg_peak_gpu_memory_mb
    results["avg_peak_gpu_memory_mb"] = report.avg_peak_gpu_memory_mb


    # Add detailed run data
    # Add detailed run data
    for metric in report.metrics:
    for metric in report.metrics:
    run_data = {
    run_data = {
    "inference_time": metric.total_time,
    "inference_time": metric.total_time,
    "tokens_per_second": metric.tokens_per_second,
    "tokens_per_second": metric.tokens_per_second,
    "time_to_first_token": metric.time_to_first_token,
    "time_to_first_token": metric.time_to_first_token,
    "output_tokens": metric.output_tokens,
    "output_tokens": metric.output_tokens,
    "peak_cpu_memory_mb": metric.peak_cpu_memory_mb,
    "peak_cpu_memory_mb": metric.peak_cpu_memory_mb,
    "peak_gpu_memory_mb": metric.peak_gpu_memory_mb,
    "peak_gpu_memory_mb": metric.peak_gpu_memory_mb,
    }
    }
    results["runs"].append(run_data)
    results["runs"].append(run_data)


    return results
    return results


    def _generate_text_huggingface(
    def _generate_text_huggingface(
    self, model: Any, prompt: str, max_tokens: int, temperature: float, tracker: Any
    self, model: Any, prompt: str, max_tokens: int, temperature: float, tracker: Any
    ) -> str:
    ) -> str:
    """
    """
    Generate text using a Hugging Face model.
    Generate text using a Hugging Face model.


    Args:
    Args:
    model: Hugging Face model instance
    model: Hugging Face model instance
    prompt: Input prompt
    prompt: Input prompt
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    temperature: Temperature for text generation
    temperature: Temperature for text generation
    tracker: InferenceTracker instance
    tracker: InferenceTracker instance


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    # Generate text
    # Generate text
    outputs = model(
    outputs = model(
    prompt,
    prompt,
    max_length=len(prompt.split()) + max_tokens,
    max_length=len(prompt.split()) + max_tokens,
    temperature=temperature,
    temperature=temperature,
    do_sample=True,
    do_sample=True,
    )
    )


    # Record first token time (this is approximate since we can't hook into the model)
    # Record first token time (this is approximate since we can't hook into the model)
    tracker.record_first_token()
    tracker.record_first_token()


    # Get the generated text
    # Get the generated text
    if isinstance(outputs, list):
    if isinstance(outputs, list):
    output = outputs[0]["generated_text"]
    output = outputs[0]["generated_text"]
    else:
    else:
    output = outputs["generated_text"]
    output = outputs["generated_text"]


    # Update token count (approximate)
    # Update token count (approximate)
    output_text = output[len(prompt) :]
    output_text = output[len(prompt) :]
    output_tokens = len(output_text.split())
    output_tokens = len(output_text.split())
    tracker.update_output_tokens(output_tokens)
    tracker.update_output_tokens(output_tokens)


    return output
    return output


    def _generate_text_llama(
    def _generate_text_llama(
    self, model: Any, prompt: str, max_tokens: int, temperature: float, tracker: Any
    self, model: Any, prompt: str, max_tokens: int, temperature: float, tracker: Any
    ) -> str:
    ) -> str:
    """
    """
    Generate text using a Llama model.
    Generate text using a Llama model.


    Args:
    Args:
    model: Llama model instance
    model: Llama model instance
    prompt: Input prompt
    prompt: Input prompt
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    temperature: Temperature for text generation
    temperature: Temperature for text generation
    tracker: InferenceTracker instance
    tracker: InferenceTracker instance


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    # Generate text
    # Generate text
    output = model(prompt, max_tokens=max_tokens, temperature=temperature)
    output = model(prompt, max_tokens=max_tokens, temperature=temperature)


    # Record first token time (this is approximate since we can't hook into the model)
    # Record first token time (this is approximate since we can't hook into the model)
    tracker.record_first_token()
    tracker.record_first_token()


    # Get the generated text
    # Get the generated text
    if isinstance(output, dict) and "choices" in output:
    if isinstance(output, dict) and "choices" in output:
    text = output["choices"][0]["text"]
    text = output["choices"][0]["text"]
    else:
    else:
    text = str(output)
    text = str(output)


    # Update token count (approximate)
    # Update token count (approximate)
    output_tokens = len(text.split())
    output_tokens = len(text.split())
    tracker.update_output_tokens(output_tokens)
    tracker.update_output_tokens(output_tokens)


    return text
    return text


    def _generate_comparison(self, model_results: Dict[str, Any]) -> Dict[str, Any]:
    def _generate_comparison(self, model_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    """
    Generate a comparison of model results.
    Generate a comparison of model results.


    Args:
    Args:
    model_results: Dictionary with model results
    model_results: Dictionary with model results


    Returns:
    Returns:
    Dictionary with comparison data
    Dictionary with comparison data
    """
    """
    comparison = {
    comparison = {
    "fastest_inference": {"model": None, "time": float("in")},
    "fastest_inference": {"model": None, "time": float("in")},
    "highest_throughput": {"model": None, "tokens_per_second": 0},
    "highest_throughput": {"model": None, "tokens_per_second": 0},
    "lowest_latency": {"model": None, "time_to_first_token": float("in")},
    "lowest_latency": {"model": None, "time_to_first_token": float("in")},
    "lowest_memory": {"model": None, "memory_mb": float("in")},
    "lowest_memory": {"model": None, "memory_mb": float("in")},
    "ranking": [],
    "ranking": [],
    }
    }


    # Find the best models in each category
    # Find the best models in each category
    for model_id, data in model_results.items():
    for model_id, data in model_results.items():
    if "error" in data:
    if "error" in data:
    continue
    continue


    results = data["results"]
    results = data["results"]
    model_name = data["name"]
    model_name = data["name"]


    # Check inference time
    # Check inference time
    if results["avg_inference_time"] < comparison["fastest_inference"]["time"]:
    if results["avg_inference_time"] < comparison["fastest_inference"]["time"]:
    comparison["fastest_inference"]["model"] = model_name
    comparison["fastest_inference"]["model"] = model_name
    comparison["fastest_inference"]["time"] = results["avg_inference_time"]
    comparison["fastest_inference"]["time"] = results["avg_inference_time"]


    # Check throughput
    # Check throughput
    if (
    if (
    results["avg_tokens_per_second"]
    results["avg_tokens_per_second"]
    > comparison["highest_throughput"]["tokens_per_second"]
    > comparison["highest_throughput"]["tokens_per_second"]
    ):
    ):
    comparison["highest_throughput"]["model"] = model_name
    comparison["highest_throughput"]["model"] = model_name
    comparison["highest_throughput"]["tokens_per_second"] = results[
    comparison["highest_throughput"]["tokens_per_second"] = results[
    "avg_tokens_per_second"
    "avg_tokens_per_second"
    ]
    ]


    # Check latency
    # Check latency
    if (
    if (
    results["avg_time_to_first_token"]
    results["avg_time_to_first_token"]
    < comparison["lowest_latency"]["time_to_first_token"]
    < comparison["lowest_latency"]["time_to_first_token"]
    ):
    ):
    comparison["lowest_latency"]["model"] = model_name
    comparison["lowest_latency"]["model"] = model_name
    comparison["lowest_latency"]["time_to_first_token"] = results[
    comparison["lowest_latency"]["time_to_first_token"] = results[
    "avg_time_to_first_token"
    "avg_time_to_first_token"
    ]
    ]


    # Check memory usage
    # Check memory usage
    memory_usage = results["avg_peak_cpu_memory_mb"]
    memory_usage = results["avg_peak_cpu_memory_mb"]
    if results["avg_peak_gpu_memory_mb"] > 0:
    if results["avg_peak_gpu_memory_mb"] > 0:
    memory_usage += results["avg_peak_gpu_memory_mb"]
    memory_usage += results["avg_peak_gpu_memory_mb"]


    if memory_usage < comparison["lowest_memory"]["memory_mb"]:
    if memory_usage < comparison["lowest_memory"]["memory_mb"]:
    comparison["lowest_memory"]["model"] = model_name
    comparison["lowest_memory"]["model"] = model_name
    comparison["lowest_memory"]["memory_mb"] = memory_usage
    comparison["lowest_memory"]["memory_mb"] = memory_usage


    # Create a ranking based on a weighted score
    # Create a ranking based on a weighted score
    models = []
    models = []
    for model_id, data in model_results.items():
    for model_id, data in model_results.items():
    if "error" in data:
    if "error" in data:
    continue
    continue


    results = data["results"]
    results = data["results"]
    model_name = data["name"]
    model_name = data["name"]


    # Calculate a score (lower is better)
    # Calculate a score (lower is better)
    # Normalize each metric to a 0-1 scale and apply weights
    # Normalize each metric to a 0-1 scale and apply weights
    score = 0
    score = 0


    if comparison["fastest_inference"]["time"] > 0:
    if comparison["fastest_inference"]["time"] > 0:
    score += 0.3 * (
    score += 0.3 * (
    results["avg_inference_time"]
    results["avg_inference_time"]
    / comparison["fastest_inference"]["time"]
    / comparison["fastest_inference"]["time"]
    )
    )


    if comparison["highest_throughput"]["tokens_per_second"] > 0:
    if comparison["highest_throughput"]["tokens_per_second"] > 0:
    score += 0.3 * (
    score += 0.3 * (
    1
    1
    - (
    - (
    results["avg_tokens_per_second"]
    results["avg_tokens_per_second"]
    / comparison["highest_throughput"]["tokens_per_second"]
    / comparison["highest_throughput"]["tokens_per_second"]
    )
    )
    )
    )


    if comparison["lowest_latency"]["time_to_first_token"] > 0:
    if comparison["lowest_latency"]["time_to_first_token"] > 0:
    score += 0.2 * (
    score += 0.2 * (
    results["avg_time_to_first_token"]
    results["avg_time_to_first_token"]
    / comparison["lowest_latency"]["time_to_first_token"]
    / comparison["lowest_latency"]["time_to_first_token"]
    )
    )


    memory_usage = results["avg_peak_cpu_memory_mb"]
    memory_usage = results["avg_peak_cpu_memory_mb"]
    if results["avg_peak_gpu_memory_mb"] > 0:
    if results["avg_peak_gpu_memory_mb"] > 0:
    memory_usage += results["avg_peak_gpu_memory_mb"]
    memory_usage += results["avg_peak_gpu_memory_mb"]


    if comparison["lowest_memory"]["memory_mb"] > 0:
    if comparison["lowest_memory"]["memory_mb"] > 0:
    score += 0.2 * (memory_usage / comparison["lowest_memory"]["memory_mb"])
    score += 0.2 * (memory_usage / comparison["lowest_memory"]["memory_mb"])


    models.append(
    models.append(
    {
    {
    "model": model_name,
    "model": model_name,
    "score": score,
    "score": score,
    "inference_time": results["avg_inference_time"],
    "inference_time": results["avg_inference_time"],
    "tokens_per_second": results["avg_tokens_per_second"],
    "tokens_per_second": results["avg_tokens_per_second"],
    "time_to_first_token": results["avg_time_to_first_token"],
    "time_to_first_token": results["avg_time_to_first_token"],
    "memory_usage_mb": memory_usage,
    "memory_usage_mb": memory_usage,
    }
    }
    )
    )


    # Sort by score (lower is better)
    # Sort by score (lower is better)
    models.sort(key=lambda x: x["score"])
    models.sort(key=lambda x: x["score"])
    comparison["ranking"] = models
    comparison["ranking"] = models


    return comparison
    return comparison




    def main():
    def main():
    """
    """
    Main function for the model benchmark tool.
    Main function for the model benchmark tool.
    """
    """
    parser = argparse.ArgumentParser(description="Benchmark AI models")
    parser = argparse.ArgumentParser(description="Benchmark AI models")
    parser.add_argument("--models", type=str, nargs="+", help="Model IDs to benchmark")
    parser.add_argument("--models", type=str, nargs="+", help="Model IDs to benchmark")
    parser.add_argument(
    parser.add_argument(
    "--prompt",
    "--prompt",
    type=str,
    type=str,
    default="The quick brown fox jumps over the lazy dog",
    default="The quick brown fox jumps over the lazy dog",
    help="Prompt to use for the benchmark",
    help="Prompt to use for the benchmark",
    )
    )
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per model")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per model")
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
    "--temperature", type=float, default=0.7, help="Temperature for text generation"
    "--temperature", type=float, default=0.7, help="Temperature for text generation"
    )
    )
    parser.add_argument("--output", type=str, help="Output file for benchmark results")
    parser.add_argument("--output", type=str, help="Output file for benchmark results")


    args = parser.parse_args()
    args = parser.parse_args()


    # Create a model benchmark
    # Create a model benchmark
    benchmark = ModelBenchmark()
    benchmark = ModelBenchmark()


    # Get available models if none specified
    # Get available models if none specified
    if not args.models:
    if not args.models:
    all_models = benchmark.manager.get_all_models()
    all_models = benchmark.manager.get_all_models()
    if not all_models:
    if not all_models:
    print("No models found. Please specify model IDs or discover models first.")
    print("No models found. Please specify model IDs or discover models first.")
    return print("Available models:")
    return print("Available models:")
    for i, model in enumerate(all_models):
    for i, model in enumerate(all_models):
    print(f"{i+1}. {model.name} (ID: {model.id}, Type: {model.type})")
    print(f"{i+1}. {model.name} (ID: {model.id}, Type: {model.type})")


    # Ask the user which models to benchmark
    # Ask the user which models to benchmark
    selection = input("\nEnter model numbers to benchmark (comma-separated): ")
    selection = input("\nEnter model numbers to benchmark (comma-separated): ")
    selected_indices = [int(i.strip()) - 1 for i in selection.split(",")]
    selected_indices = [int(i.strip()) - 1 for i in selection.split(",")]


    args.models = [
    args.models = [
    all_models[i].id for i in selected_indices if 0 <= i < len(all_models)
    all_models[i].id for i in selected_indices if 0 <= i < len(all_models)
    ]
    ]


    if not args.models:
    if not args.models:
    print("No models selected for benchmarking.")
    print("No models selected for benchmarking.")
    return # Run the benchmark
    return # Run the benchmark
    results = benchmark.run_benchmark(
    results = benchmark.run_benchmark(
    model_ids=args.models,
    model_ids=args.models,
    prompt=args.prompt,
    prompt=args.prompt,
    num_runs=args.runs,
    num_runs=args.runs,
    max_tokens=args.max_tokens,
    max_tokens=args.max_tokens,
    temperature=args.temperature,
    temperature=args.temperature,
    output_file=args.output,
    output_file=args.output,
    )
    )


    # Print the results
    # Print the results
    print("\nBenchmark Results:")
    print("\nBenchmark Results:")
    print(f"Prompt: {args.prompt}")
    print(f"Prompt: {args.prompt}")
    print(f"Runs per model: {args.runs}")
    print(f"Runs per model: {args.runs}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Temperature: {args.temperature}")
    print(f"Temperature: {args.temperature}")


    print("\nModel Results:")
    print("\nModel Results:")
    for model_id, data in results["models"].items():
    for model_id, data in results["models"].items():
    if "error" in data:
    if "error" in data:
    print(f"\n{data['name']}:")
    print(f"\n{data['name']}:")
    print(f"  Error: {data['error']}")
    print(f"  Error: {data['error']}")
    continue
    continue


    print(f"\n{data['name']}:")
    print(f"\n{data['name']}:")
    print(f"  Type: {data['type']}")
    print(f"  Type: {data['type']}")
    print(f"  Format: {data['format']}")
    print(f"  Format: {data['format']}")
    if data["quantization"]:
    if data["quantization"]:
    print(f"  Quantization: {data['quantization']}")
    print(f"  Quantization: {data['quantization']}")


    results_data = data["results"]
    results_data = data["results"]
    print(
    print(
    f"  Average inference time: {results_data['avg_inference_time']:.4f} seconds"
    f"  Average inference time: {results_data['avg_inference_time']:.4f} seconds"
    )
    )
    print(
    print(
    f"  Average tokens per second: {results_data['avg_tokens_per_second']:.2f}"
    f"  Average tokens per second: {results_data['avg_tokens_per_second']:.2f}"
    )
    )
    print(
    print(
    f"  Average time to first token: {results_data['avg_time_to_first_token']:.4f} seconds"
    f"  Average time to first token: {results_data['avg_time_to_first_token']:.4f} seconds"
    )
    )


    if results_data["avg_peak_cpu_memory_mb"] > 0:
    if results_data["avg_peak_cpu_memory_mb"] > 0:
    print(
    print(
    f"  Average peak CPU memory: {results_data['avg_peak_cpu_memory_mb']:.2f} MB"
    f"  Average peak CPU memory: {results_data['avg_peak_cpu_memory_mb']:.2f} MB"
    )
    )


    if results_data["avg_peak_gpu_memory_mb"] > 0:
    if results_data["avg_peak_gpu_memory_mb"] > 0:
    print(
    print(
    f"  Average peak GPU memory: {results_data['avg_peak_gpu_memory_mb']:.2f} MB"
    f"  Average peak GPU memory: {results_data['avg_peak_gpu_memory_mb']:.2f} MB"
    )
    )


    # Print comparison
    # Print comparison
    comparison = results["comparison"]
    comparison = results["comparison"]


    print("\nComparison:")
    print("\nComparison:")
    if comparison["fastest_inference"]["model"]:
    if comparison["fastest_inference"]["model"]:
    print(
    print(
    f"Fastest inference: {comparison['fastest_inference']['model']} ({comparison['fastest_inference']['time']:.4f} seconds)"
    f"Fastest inference: {comparison['fastest_inference']['model']} ({comparison['fastest_inference']['time']:.4f} seconds)"
    )
    )


    if comparison["highest_throughput"]["model"]:
    if comparison["highest_throughput"]["model"]:
    print(
    print(
    f"Highest throughput: {comparison['highest_throughput']['model']} ({comparison['highest_throughput']['tokens_per_second']:.2f} tokens/second)"
    f"Highest throughput: {comparison['highest_throughput']['model']} ({comparison['highest_throughput']['tokens_per_second']:.2f} tokens/second)"
    )
    )


    if comparison["lowest_latency"]["model"]:
    if comparison["lowest_latency"]["model"]:
    print(
    print(
    f"Lowest latency: {comparison['lowest_latency']['model']} ({comparison['lowest_latency']['time_to_first_token']:.4f} seconds)"
    f"Lowest latency: {comparison['lowest_latency']['model']} ({comparison['lowest_latency']['time_to_first_token']:.4f} seconds)"
    )
    )


    if comparison["lowest_memory"]["model"]:
    if comparison["lowest_memory"]["model"]:
    print(
    print(
    f"Lowest memory usage: {comparison['lowest_memory']['model']} ({comparison['lowest_memory']['memory_mb']:.2f} MB)"
    f"Lowest memory usage: {comparison['lowest_memory']['model']} ({comparison['lowest_memory']['memory_mb']:.2f} MB)"
    )
    )


    print("\nRanking (best to worst):")
    print("\nRanking (best to worst):")
    for i, model in enumerate(comparison["ranking"]):
    for i, model in enumerate(comparison["ranking"]):
    print(f"{i+1}. {model['model']} (Score: {model['score']:.4f})")
    print(f"{i+1}. {model['model']} (Score: {model['score']:.4f})")


    if args.output:
    if args.output:
    print(f"\nResults saved to {args.output}")
    print(f"\nResults saved to {args.output}")




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()