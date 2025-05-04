"""
"""
Utility functions for benchmarking AI models.
Utility functions for benchmarking AI models.


This module provides utility functions for running benchmarks and analyzing results.
This module provides utility functions for running benchmarks and analyzing results.
"""
"""




import logging
import logging
import os
import os
from typing import List, Optional, Union
from typing import List, Optional, Union


from .benchmark_config import BenchmarkConfig, BenchmarkType
from .benchmark_config import BenchmarkConfig, BenchmarkType
from .benchmark_result import BenchmarkResult
from .benchmark_result import BenchmarkResult
from .benchmark_runner import BenchmarkRunner
from .benchmark_runner import BenchmarkRunner


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




def run_benchmark(
def run_benchmark(
model_path: str,
model_path: str,
benchmark_type: Union[str, BenchmarkType] = BenchmarkType.LATENCY,
benchmark_type: Union[str, BenchmarkType] = BenchmarkType.LATENCY,
model_type: str = "text-generation",
model_type: str = "text-generation",
output_dir: Optional[str] = None,
output_dir: Optional[str] = None,
**kwargs,
**kwargs,
) -> BenchmarkResult:
    ) -> BenchmarkResult:
    """
    """
    Run a benchmark on a model.
    Run a benchmark on a model.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    benchmark_type: Type of benchmark to run
    benchmark_type: Type of benchmark to run
    model_type: Type of the model
    model_type: Type of the model
    output_dir: Directory to save the results
    output_dir: Directory to save the results
    **kwargs: Additional parameters for the benchmark
    **kwargs: Additional parameters for the benchmark


    Returns:
    Returns:
    Benchmark result
    Benchmark result
    """
    """
    # Convert benchmark type to enum if it's a string
    # Convert benchmark type to enum if it's a string
    if isinstance(benchmark_type, str):
    if isinstance(benchmark_type, str):
    try:
    try:
    benchmark_type = BenchmarkType(benchmark_type)
    benchmark_type = BenchmarkType(benchmark_type)
except ValueError:
except ValueError:
    raise ValueError(f"Unknown benchmark type: {benchmark_type}")
    raise ValueError(f"Unknown benchmark type: {benchmark_type}")


    # Create benchmark configuration
    # Create benchmark configuration
    config = BenchmarkConfig(
    config = BenchmarkConfig(
    model_path=model_path,
    model_path=model_path,
    model_type=model_type,
    model_type=model_type,
    benchmark_type=benchmark_type,
    benchmark_type=benchmark_type,
    output_dir=output_dir,
    output_dir=output_dir,
    **kwargs,
    **kwargs,
    )
    )


    # Create benchmark runner
    # Create benchmark runner
    runner = BenchmarkRunner(config)
    runner = BenchmarkRunner(config)


    # Run benchmark
    # Run benchmark
    result = runner.run()
    result = runner.run()


    return result
    return result




    def compare_models(
    def compare_models(
    model_paths: List[str],
    model_paths: List[str],
    benchmark_type: Union[str, BenchmarkType] = BenchmarkType.LATENCY,
    benchmark_type: Union[str, BenchmarkType] = BenchmarkType.LATENCY,
    model_type: str = "text-generation",
    model_type: str = "text-generation",
    output_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    **kwargs,
    **kwargs,
    ) -> List[BenchmarkResult]:
    ) -> List[BenchmarkResult]:
    """
    """
    Compare multiple models using the same benchmark.
    Compare multiple models using the same benchmark.


    Args:
    Args:
    model_paths: List of paths to the models
    model_paths: List of paths to the models
    benchmark_type: Type of benchmark to run
    benchmark_type: Type of benchmark to run
    model_type: Type of the models
    model_type: Type of the models
    output_dir: Directory to save the results
    output_dir: Directory to save the results
    **kwargs: Additional parameters for the benchmark
    **kwargs: Additional parameters for the benchmark


    Returns:
    Returns:
    List of benchmark results
    List of benchmark results
    """
    """
    results = []
    results = []


    for model_path in model_paths:
    for model_path in model_paths:
    logger.info(f"Benchmarking model: {model_path}")
    logger.info(f"Benchmarking model: {model_path}")


    try:
    try:
    # Run benchmark
    # Run benchmark
    result = run_benchmark(
    result = run_benchmark(
    model_path=model_path,
    model_path=model_path,
    benchmark_type=benchmark_type,
    benchmark_type=benchmark_type,
    model_type=model_type,
    model_type=model_type,
    output_dir=output_dir,
    output_dir=output_dir,
    **kwargs,
    **kwargs,
    )
    )


    results.append(result)
    results.append(result)


except Exception as e:
except Exception as e:
    logger.error(f"Error benchmarking model {model_path}: {e}")
    logger.error(f"Error benchmarking model {model_path}: {e}")


    return results
    return results




    def save_benchmark_results(
    def save_benchmark_results(
    results: Union[BenchmarkResult, List[BenchmarkResult]], output_dir: str
    results: Union[BenchmarkResult, List[BenchmarkResult]], output_dir: str
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    Save benchmark results to files.
    Save benchmark results to files.


    Args:
    Args:
    results: Benchmark result or list of results
    results: Benchmark result or list of results
    output_dir: Directory to save the results
    output_dir: Directory to save the results


    Returns:
    Returns:
    List of paths to the saved files
    List of paths to the saved files
    """
    """
    # Create output directory
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Convert single result to list
    # Convert single result to list
    if isinstance(results, BenchmarkResult):
    if isinstance(results, BenchmarkResult):
    results = [results]
    results = [results]


    # Save results
    # Save results
    output_paths = []
    output_paths = []
    for result in results:
    for result in results:
    # Generate output path
    # Generate output path
    output_path = os.path.join(
    output_path = os.path.join(
    output_dir,
    output_dir,
    f"{os.path.basename(result.model_path)}_{result.benchmark_type.value}_{int(result.timestamp)}.json",
    f"{os.path.basename(result.model_path)}_{result.benchmark_type.value}_{int(result.timestamp)}.json",
    )
    )


    # Save result
    # Save result
    result.save(output_path)
    result.save(output_path)
    output_paths.append(output_path)
    output_paths.append(output_path)


    return output_paths
    return output_paths




    def load_benchmark_results(input_paths: Union[str, List[str]]) -> List[BenchmarkResult]:
    def load_benchmark_results(input_paths: Union[str, List[str]]) -> List[BenchmarkResult]:
    """
    """
    Load benchmark results from files.
    Load benchmark results from files.


    Args:
    Args:
    input_paths: Path or list of paths to the result files
    input_paths: Path or list of paths to the result files


    Returns:
    Returns:
    List of benchmark results
    List of benchmark results
    """
    """
    # Convert single path to list
    # Convert single path to list
    if isinstance(input_paths, str):
    if isinstance(input_paths, str):
    input_paths = [input_paths]
    input_paths = [input_paths]


    # Load results
    # Load results
    results = []
    results = []
    for input_path in input_paths:
    for input_path in input_paths:
    try:
    try:
    # Load result
    # Load result
    result = BenchmarkResult.load(input_path)
    result = BenchmarkResult.load(input_path)
    results.append(result)
    results.append(result)


except Exception as e:
except Exception as e:
    logger.error(f"Error loading result from {input_path}: {e}")
    logger.error(f"Error loading result from {input_path}: {e}")


    return results
    return results