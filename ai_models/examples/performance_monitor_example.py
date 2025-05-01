"""
Example usage of the PerformanceMonitor.

This script demonstrates how to use the PerformanceMonitor to track
and analyze model performance.
"""

import logging
import os
import random
import sys
import time

# Add the parent directory to the path to import the ai_models module
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from ai_models import InferenceTracker, ModelInfo, ModelManager, PerformanceMonitor

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def simulate_inference(tracker, tokens=20, delay=0.5):
    """
    Simulate an inference run.

    Args:
        tracker: InferenceTracker instance
        tokens: Number of tokens to generate
        delay: Delay in seconds for the first token
    """
    # Simulate time to first token
    time.sleep(delay)
    tracker.record_first_token()

    # Simulate token generation
    for i in range(tokens):
        # Simulate variable token generation time
        time.sleep(random.uniform(0.05, 0.15))

        # Update token count
        tracker.update_output_tokens(i + 1)

    # Add some metadata
    tracker.add_metadata("temperature", 0.7)
    tracker.add_metadata("top_p", 0.9)


def main():
    """
    Main function to demonstrate the PerformanceMonitor.
    """
    print("=" * 80)
    print("PerformanceMonitor Example")
    print("=" * 80)

    # Create a performance monitor
    monitor = PerformanceMonitor()

    # Create a model manager with the performance monitor
    manager = ModelManager(performance_monitor=monitor)

    # Register a test model
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        type="huggingface",
        path="test-model",
        description="Test model for performance monitoring",
    )
    manager.register_model(model_info)

    print("\nRunning inference simulations...")

    # Run multiple inference simulations
    for i in range(5):
        print(f"\nInference run {i+1}:")

        # Track inference using the model manager
        with manager.track_inference("test-model", input_tokens=10) as tracker:
            # Simulate inference
            tokens = random.randint(15, 30)
            delay = random.uniform(0.3, 0.7)

            print(
                f"  Generating {tokens} tokens with {delay:.2f}s delay to first token..."
            )
            simulate_inference(tracker, tokens=tokens, delay=delay)

    # Generate a performance report
    report = manager.generate_performance_report("test-model")

    print("\nPerformance Report:")
    print(f"Model: {report.model_name}")
    print(f"Number of inferences: {report.num_inferences}")
    print(f"Average inference time: {report.avg_inference_time:.4f} seconds")
    print(f"Average tokens per second: {report.avg_tokens_per_second:.2f}")
    print(f"Average time to first token: {report.avg_time_to_first_token:.4f} seconds")

    if report.avg_peak_cpu_memory_mb > 0:
        print(f"Average peak CPU memory: {report.avg_peak_cpu_memory_mb:.2f} MB")

    if report.avg_peak_gpu_memory_mb > 0:
        print(f"Average peak GPU memory: {report.avg_peak_gpu_memory_mb:.2f} MB")

    # Get detailed metrics
    metrics = manager.get_model_performance_metrics("test-model")

    print("\nDetailed Metrics:")
    for i, metric in enumerate(metrics):
        print(f"Run {i+1}:")
        print(f"  Total time: {metric.total_time:.4f} seconds")
        print(f"  Tokens per second: {metric.tokens_per_second:.2f}")
        print(f"  Time to first token: {metric.time_to_first_token:.4f} seconds")
        print(f"  Output tokens: {metric.output_tokens}")

    # Get system performance
    system_perf = monitor.get_system_performance()

    print("\nSystem Performance:")
    if "cpu" in system_perf and "percent" in system_perf["cpu"]:
        print(f"CPU Usage: {system_perf['cpu']['percent']}%")

    if "memory" in system_perf and "percent" in system_perf["memory"]:
        print(f"Memory Usage: {system_perf['memory']['percent']}%")
        print(f"Total Memory: {system_perf['memory'].get('total_gb', 0):.2f} GB")
        print(
            f"Available Memory: {system_perf['memory'].get('available_gb', 0):.2f} GB"
        )

    if (
        "gpu" in system_perf
        and "devices" in system_perf["gpu"]
        and system_perf["gpu"]["devices"]
    ):
        gpu = system_perf["gpu"]["devices"][0]
        print(f"GPU: {gpu.get('name', 'Unknown')}")
        print(f"GPU Memory Allocated: {gpu.get('memory_allocated_mb', 0):.2f} MB")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
