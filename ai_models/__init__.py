"""
AI Models module for pAIssive Income project.

This module provides a comprehensive system for managing and using local AI models
for various tasks such as content generation, data analysis, and more.
"""

from .model_manager import ModelManager, ModelInfo
from .model_config import ModelConfig
from .agent_integration import AgentModelProvider
from .model_downloader import ModelDownloader, DownloadTask, DownloadProgress
from .performance_monitor import PerformanceMonitor, InferenceTracker, InferenceMetrics, ModelPerformanceReport

# Import model types
from .model_types import ONNXModel, QuantizedModel, VisionModel, AudioModel

# Import adapters
from .adapters import OllamaAdapter, LMStudioAdapter, OpenAICompatibleAdapter

# Import TensorRT adapter if available
try:
    from .adapters import TensorRTAdapter
    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False

# Import caching system
from .caching import (
    CacheManager, CacheConfig, CacheKey, generate_cache_key,
    MemoryCache, DiskCache, SQLiteCache
)

# Import Redis cache if available
try:
    from .caching import RedisCache
    REDIS_CACHE_AVAILABLE = True
except ImportError:
    REDIS_CACHE_AVAILABLE = False

# Import optimization utilities
from .optimization import (
    # Quantization
    Quantizer, QuantizationConfig, QuantizationMethod,
    BitsAndBytesQuantizer, AWQQuantizer, GPTQQuantizer,
    quantize_model, analyze_quantization,

    # Pruning
    Pruner, PruningConfig, PruningMethod,
    MagnitudePruner, StructuredPruner,
    prune_model, analyze_pruning
)

# Import benchmarking tools
from .benchmarking import (
    BenchmarkRunner, BenchmarkConfig, BenchmarkResult, BenchmarkType,
    LatencyMetric, ThroughputMetric, MemoryMetric,
    AccuracyMetric, PerplexityMetric, RougeMetric,
    plot_benchmark_results, plot_comparison,
    plot_latency_distribution, plot_memory_usage,
    run_benchmark, compare_models,
    save_benchmark_results, load_benchmark_results
)

# Import serving and deployment utilities
from .serving import (
    # Server interfaces
    ModelServer, ServerConfig, ServerProtocol,

    # REST API server
    RESTServer, RESTConfig,

    # gRPC server
    GRPCServer, GRPCConfig,

    # Deployment utilities
    DockerConfig, KubernetesConfig, CloudConfig, CloudProvider,
    generate_docker_config, generate_kubernetes_config, generate_cloud_config
)

# Import CLI tools
from .cli import main as cli_main

__all__ = [
    # Core components
    'ModelManager',
    'ModelInfo',
    'ModelConfig',
    'AgentModelProvider',
    'ModelDownloader',
    'DownloadTask',
    'DownloadProgress',
    'PerformanceMonitor',
    'InferenceTracker',
    'InferenceMetrics',
    'ModelPerformanceReport',

    # Model types
    'ONNXModel',
    'QuantizedModel',
    'VisionModel',
    'AudioModel',

    # Adapters
    'OllamaAdapter',
    'LMStudioAdapter',
    'OpenAICompatibleAdapter',

    # Caching system
    'CacheManager',
    'CacheConfig',
    'CacheKey',
    'generate_cache_key',
    'MemoryCache',
    'DiskCache',
    'SQLiteCache',

    # Optimization - Quantization
    'Quantizer',
    'QuantizationConfig',
    'QuantizationMethod',
    'BitsAndBytesQuantizer',
    'AWQQuantizer',
    'GPTQQuantizer',
    'quantize_model',
    'analyze_quantization',

    # Optimization - Pruning
    'Pruner',
    'PruningConfig',
    'PruningMethod',
    'MagnitudePruner',
    'StructuredPruner',
    'prune_model',
    'analyze_pruning',

    # Benchmarking
    'BenchmarkRunner',
    'BenchmarkConfig',
    'BenchmarkResult',
    'BenchmarkType',
    'LatencyMetric',
    'ThroughputMetric',
    'MemoryMetric',
    'AccuracyMetric',
    'PerplexityMetric',
    'RougeMetric',
    'plot_benchmark_results',
    'plot_comparison',
    'plot_latency_distribution',
    'plot_memory_usage',
    'run_benchmark',
    'compare_models',
    'save_benchmark_results',
    'load_benchmark_results',

    # Serving
    'ModelServer',
    'ServerConfig',
    'ServerProtocol',
    'RESTServer',
    'RESTConfig',
    'GRPCServer',
    'GRPCConfig',

    # Deployment
    'DockerConfig',
    'KubernetesConfig',
    'CloudConfig',
    'CloudProvider',
    'generate_docker_config',
    'generate_kubernetes_config',
    'generate_cloud_config',

    # CLI
    'cli_main',
]

# Add TensorRT adapter if available
if TENSORRT_AVAILABLE:
    __all__.append('TensorRTAdapter')

# Add Redis cache if available
if REDIS_CACHE_AVAILABLE:
    __all__.append('RedisCache')
