"""
"""
Example usage of the PerformanceMonitor.
Example usage of the PerformanceMonitor.


This script demonstrates how to use the PerformanceMonitor to track
This script demonstrates how to use the PerformanceMonitor to track
and analyze model performance.
and analyze model performance.
"""
"""


import logging
import logging
import os
import os
import random
import random
import sys
import sys
import time
import time


from ai_models import ModelInfo, ModelManager, PerformanceMonitor
from ai_models import ModelInfo, ModelManager, PerformanceMonitor


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




def simulate_inference(tracker, tokens=20, delay=0.5):
    def simulate_inference(tracker, tokens=20, delay=0.5):
    """
    """
    Simulate an inference run.
    Simulate an inference run.


    Args:
    Args:
    tracker: InferenceTracker instance
    tracker: InferenceTracker instance
    tokens: Number of tokens to generate
    tokens: Number of tokens to generate
    delay: Delay in seconds for the first token
    delay: Delay in seconds for the first token
    """
    """
    # Simulate time to first token
    # Simulate time to first token
    time.sleep(delay)
    time.sleep(delay)
    tracker.record_first_token()
    tracker.record_first_token()


    # Simulate token generation
    # Simulate token generation
    for i in range(tokens):
    for i in range(tokens):
    # Simulate variable token generation time
    # Simulate variable token generation time
    time.sleep(random.uniform(0.05, 0.15))
    time.sleep(random.uniform(0.05, 0.15))


    # Update token count
    # Update token count
    tracker.update_output_tokens(i + 1)
    tracker.update_output_tokens(i + 1)


    # Add some metadata
    # Add some metadata
    tracker.add_metadata("temperature", 0.7)
    tracker.add_metadata("temperature", 0.7)
    tracker.add_metadata("top_p", 0.9)
    tracker.add_metadata("top_p", 0.9)




    def main():
    def main():
    """
    """
    Main function to demonstrate the PerformanceMonitor.
    Main function to demonstrate the PerformanceMonitor.
    """
    """
    print("=" * 80)
    print("=" * 80)
    print("PerformanceMonitor Example")
    print("PerformanceMonitor Example")
    print("=" * 80)
    print("=" * 80)


    # Create a performance monitor
    # Create a performance monitor
    monitor = PerformanceMonitor()
    monitor = PerformanceMonitor()


    # Create a model manager with the performance monitor
    # Create a model manager with the performance monitor
    manager = ModelManager(performance_monitor=monitor)
    manager = ModelManager(performance_monitor=monitor)


    # Register a test model
    # Register a test model
    model_info = ModelInfo(
    model_info = ModelInfo(
    id="test-model",
    id="test-model",
    name="Test Model",
    name="Test Model",
    type="huggingface",
    type="huggingface",
    path="test-model",
    path="test-model",
    description="Test model for performance monitoring",
    description="Test model for performance monitoring",
    )
    )
    manager.register_model(model_info)
    manager.register_model(model_info)


    print("\nRunning inference simulations...")
    print("\nRunning inference simulations...")


    # Run multiple inference simulations
    # Run multiple inference simulations
    for i in range(5):
    for i in range(5):
    print(f"\nInference run {i+1}:")
    print(f"\nInference run {i+1}:")


    # Track inference using the model manager
    # Track inference using the model manager
    with manager.track_inference("test-model", input_tokens=10) as tracker:
    with manager.track_inference("test-model", input_tokens=10) as tracker:
    # Simulate inference
    # Simulate inference
    tokens = random.randint(15, 30)
    tokens = random.randint(15, 30)
    delay = random.uniform(0.3, 0.7)
    delay = random.uniform(0.3, 0.7)


    print(
    print(
    f"  Generating {tokens} tokens with {delay:.2f}s delay to first token..."
    f"  Generating {tokens} tokens with {delay:.2f}s delay to first token..."
    )
    )
    simulate_inference(tracker, tokens=tokens, delay=delay)
    simulate_inference(tracker, tokens=tokens, delay=delay)


    # Generate a performance report
    # Generate a performance report
    report = manager.generate_performance_report("test-model")
    report = manager.generate_performance_report("test-model")


    print("\nPerformance Report:")
    print("\nPerformance Report:")
    print(f"Model: {report.model_name}")
    print(f"Model: {report.model_name}")
    print(f"Number of inferences: {report.num_inferences}")
    print(f"Number of inferences: {report.num_inferences}")
    print(f"Average inference time: {report.avg_inference_time:.4f} seconds")
    print(f"Average inference time: {report.avg_inference_time:.4f} seconds")
    print(f"Average tokens per second: {report.avg_tokens_per_second:.2f}")
    print(f"Average tokens per second: {report.avg_tokens_per_second:.2f}")
    print(f"Average time to first token: {report.avg_time_to_first_token:.4f} seconds")
    print(f"Average time to first token: {report.avg_time_to_first_token:.4f} seconds")


    if report.avg_peak_cpu_memory_mb > 0:
    if report.avg_peak_cpu_memory_mb > 0:
    print(f"Average peak CPU memory: {report.avg_peak_cpu_memory_mb:.2f} MB")
    print(f"Average peak CPU memory: {report.avg_peak_cpu_memory_mb:.2f} MB")


    if report.avg_peak_gpu_memory_mb > 0:
    if report.avg_peak_gpu_memory_mb > 0:
    print(f"Average peak GPU memory: {report.avg_peak_gpu_memory_mb:.2f} MB")
    print(f"Average peak GPU memory: {report.avg_peak_gpu_memory_mb:.2f} MB")


    # Get detailed metrics
    # Get detailed metrics
    metrics = manager.get_model_performance_metrics("test-model")
    metrics = manager.get_model_performance_metrics("test-model")


    print("\nDetailed Metrics:")
    print("\nDetailed Metrics:")
    for i, metric in enumerate(metrics):
    for i, metric in enumerate(metrics):
    print(f"Run {i+1}:")
    print(f"Run {i+1}:")
    print(f"  Total time: {metric.total_time:.4f} seconds")
    print(f"  Total time: {metric.total_time:.4f} seconds")
    print(f"  Tokens per second: {metric.tokens_per_second:.2f}")
    print(f"  Tokens per second: {metric.tokens_per_second:.2f}")
    print(f"  Time to first token: {metric.time_to_first_token:.4f} seconds")
    print(f"  Time to first token: {metric.time_to_first_token:.4f} seconds")
    print(f"  Output tokens: {metric.output_tokens}")
    print(f"  Output tokens: {metric.output_tokens}")


    # Get system performance
    # Get system performance
    system_perf = monitor.get_system_performance()
    system_perf = monitor.get_system_performance()


    print("\nSystem Performance:")
    print("\nSystem Performance:")
    if "cpu" in system_perf and "percent" in system_perf["cpu"]:
    if "cpu" in system_perf and "percent" in system_perf["cpu"]:
    print(f"CPU Usage: {system_perf['cpu']['percent']}%")
    print(f"CPU Usage: {system_perf['cpu']['percent']}%")


    if "memory" in system_perf and "percent" in system_perf["memory"]:
    if "memory" in system_perf and "percent" in system_perf["memory"]:
    print(f"Memory Usage: {system_perf['memory']['percent']}%")
    print(f"Memory Usage: {system_perf['memory']['percent']}%")
    print(f"Total Memory: {system_perf['memory'].get('total_gb', 0):.2f} GB")
    print(f"Total Memory: {system_perf['memory'].get('total_gb', 0):.2f} GB")
    print(
    print(
    f"Available Memory: {system_perf['memory'].get('available_gb', 0):.2f} GB"
    f"Available Memory: {system_perf['memory'].get('available_gb', 0):.2f} GB"
    )
    )


    if (
    if (
    "gpu" in system_perf
    "gpu" in system_perf
    and "devices" in system_perf["gpu"]
    and "devices" in system_perf["gpu"]
    and system_perf["gpu"]["devices"]
    and system_perf["gpu"]["devices"]
    ):
    ):
    gpu = system_perf["gpu"]["devices"][0]
    gpu = system_perf["gpu"]["devices"][0]
    print(f"GPU: {gpu.get('name', 'Unknown')}")
    print(f"GPU: {gpu.get('name', 'Unknown')}")
    print(f"GPU Memory Allocated: {gpu.get('memory_allocated_mb', 0):.2f} MB")
    print(f"GPU Memory Allocated: {gpu.get('memory_allocated_mb', 0):.2f} MB")


    print("\nExample completed successfully!")
    print("\nExample completed successfully!")




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()

