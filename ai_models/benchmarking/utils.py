"""
Utility functions for benchmarking AI models.

This module provides utility functions for running benchmarks and analyzing results.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union, Tuple

from .benchmark_config import BenchmarkConfig, BenchmarkType
from .benchmark_result import BenchmarkResult
from .benchmark_runner import BenchmarkRunner

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_benchmark(
    model_path: str,
    benchmark_type: Union[str, BenchmarkType] = BenchmarkType.LATENCY,
    model_type: str = "text-generation",
    output_dir: Optional[str] = None,
    **kwargs
) -> BenchmarkResult:
    """
    Run a benchmark on a model.
    
    Args:
        model_path: Path to the model
        benchmark_type: Type of benchmark to run
        model_type: Type of the model
        output_dir: Directory to save the results
        **kwargs: Additional parameters for the benchmark
        
    Returns:
        Benchmark result
    """
    # Convert benchmark type to enum if it's a string
    if isinstance(benchmark_type, str):
        try:
            benchmark_type = BenchmarkType(benchmark_type)
        except ValueError:
            raise ValueError(f"Unknown benchmark type: {benchmark_type}")
    
    # Create benchmark configuration
    config = BenchmarkConfig(
        model_path=model_path,
        model_type=model_type,
        benchmark_type=benchmark_type,
        output_dir=output_dir,
        **kwargs
    )
    
    # Create benchmark runner
    runner = BenchmarkRunner(config)
    
    # Run benchmark
    result = runner.run()
    
    return result


def compare_models(
    model_paths: List[str],
    benchmark_type: Union[str, BenchmarkType] = BenchmarkType.LATENCY,
    model_type: str = "text-generation",
    output_dir: Optional[str] = None,
    **kwargs
) -> List[BenchmarkResult]:
    """
    Compare multiple models using the same benchmark.
    
    Args:
        model_paths: List of paths to the models
        benchmark_type: Type of benchmark to run
        model_type: Type of the models
        output_dir: Directory to save the results
        **kwargs: Additional parameters for the benchmark
        
    Returns:
        List of benchmark results
    """
    results = []
    
    for model_path in model_paths:
        logger.info(f"Benchmarking model: {model_path}")
        
        try:
            # Run benchmark
            result = run_benchmark(
                model_path=model_path,
                benchmark_type=benchmark_type,
                model_type=model_type,
                output_dir=output_dir,
                **kwargs
            )
            
            results.append(result)
        
        except Exception as e:
            logger.error(f"Error benchmarking model {model_path}: {e}")
    
    return results


def save_benchmark_results(
    results: Union[BenchmarkResult, List[BenchmarkResult]],
    output_dir: str
) -> List[str]:
    """
    Save benchmark results to files.
    
    Args:
        results: Benchmark result or list of results
        output_dir: Directory to save the results
        
    Returns:
        List of paths to the saved files
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert single result to list
    if isinstance(results, BenchmarkResult):
        results = [results]
    
    # Save results
    output_paths = []
    for result in results:
        # Generate output path
        output_path = os.path.join(
            output_dir,
            f"{os.path.basename(result.model_path)}_{result.benchmark_type.value}_{int(result.timestamp)}.json"
        )
        
        # Save result
        result.save(output_path)
        output_paths.append(output_path)
    
    return output_paths


def load_benchmark_results(
    input_paths: Union[str, List[str]]
) -> List[BenchmarkResult]:
    """
    Load benchmark results from files.
    
    Args:
        input_paths: Path or list of paths to the result files
        
    Returns:
        List of benchmark results
    """
    # Convert single path to list
    if isinstance(input_paths, str):
        input_paths = [input_paths]
    
    # Load results
    results = []
    for input_path in input_paths:
        try:
            # Load result
            result = BenchmarkResult.load(input_path)
            results.append(result)
        
        except Exception as e:
            logger.error(f"Error loading result from {input_path}: {e}")
    
    return results
