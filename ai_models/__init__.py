"""
AI Models module for pAIssive Income project.

This module provides a comprehensive system for managing and using local AI models
for various tasks such as content generation, data analysis, and more.
"""

# Import adapters
from .adapters import LMStudioAdapter, OllamaAdapter, OpenAICompatibleAdapter
from .agent_integration import AgentModelProvider
from .batch_inference import (
    BatchInferenceProcessor,
    BatchInferenceRequest,
    BatchInferenceResult,
    generate_embeddings_batch,
    generate_text_batch,
)
from .model_base_types import ModelInfo
from .model_config import ModelConfig
from .model_downloader import DownloadProgress, DownloadTask, ModelDownloader
from .model_manager import ModelManager

# Import specialized model types
from .model_types import AudioModel, ONNXModel, QuantizedModel, VisionModel
from .performance_monitor import (
    InferenceMetrics,
    InferenceTracker,
    ModelPerformanceReport,
    PerformanceMonitor,
)

# Import TensorRT adapter if available
try:
    from .adapters import TensorRTAdapter

    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False

# Import caching system
from .caching import (
    CacheConfig,
    CacheKey,
    CacheManager,
    DiskCache,
    MemoryCache,
    SQLiteCache,
    generate_cache_key,
)

# Import cache integration
from .caching.cache_integration import cache_model_result, invalidate_model_cache

# Import Redis cache if available
try:
    from .caching import RedisCache

    REDIS_CACHE_AVAILABLE = True
except ImportError:
    REDIS_CACHE_AVAILABLE = False

# Import benchmarking tools
from .benchmarking import (
    AccuracyMetric,
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkRunner,
    BenchmarkType,
    LatencyMetric,
    MemoryMetric,
    PerplexityMetric,
    RougeMetric,
    ThroughputMetric,
    compare_models,
    load_benchmark_results,
    plot_benchmark_results,
    plot_comparison,
    plot_latency_distribution,
    plot_memory_usage,
    run_benchmark,
    save_benchmark_results,
)

# Import CLI tools
from .cli import main as cli_main

# Import optimization utilities
from .optimization import (  # Quantization; Pruning
    AWQQuantizer,
    BitsAndBytesQuantizer,
    GPTQQuantizer,
    MagnitudePruner,
    Pruner,
    PruningConfig,
    PruningMethod,
    QuantizationConfig,
    QuantizationMethod,
    Quantizer,
    StructuredPruner,
    analyze_pruning,
    analyze_quantization,
    prune_model,
    quantize_model,
)

# Import serving and deployment utilities
from .serving import (  # Server interfaces; REST API server; gRPC server; Deployment utilities
    CloudConfig,
    CloudProvider,
    DockerConfig,
    GRPCConfig,
    GRPCServer,
    KubernetesConfig,
    ModelServer,
    RESTConfig,
    RESTServer,
    ServerConfig,
    ServerProtocol,
    generate_cloud_config,
    generate_docker_config,
    generate_kubernetes_config,
)

__all__ = [
    # Core components
    "ModelManager",
    "ModelInfo",
    "ModelConfig",
    "AgentModelProvider",
    "ModelDownloader",
    "DownloadTask",
    "DownloadProgress",
    "PerformanceMonitor",
    "InferenceTracker",
    "InferenceMetrics",
    "ModelPerformanceReport",
    # Batch processing
    "BatchInferenceProcessor",
    "BatchInferenceRequest",
    "BatchInferenceResult",
    "generate_text_batch",
    "generate_embeddings_batch",
    # Model types
    "ONNXModel",
    "QuantizedModel",
    "VisionModel",
    "AudioModel",
    # Adapters
    "OllamaAdapter",
    "LMStudioAdapter",
    "OpenAICompatibleAdapter",
    # Caching system
    "CacheManager",
    "CacheConfig",
    "CacheKey",
    "generate_cache_key",
    "MemoryCache",
    "DiskCache",
    "SQLiteCache",
    "cache_model_result",
    "invalidate_model_cache",
    # Optimization - Quantization
    "Quantizer",
    "QuantizationConfig",
    "QuantizationMethod",
    "BitsAndBytesQuantizer",
    "AWQQuantizer",
    "GPTQQuantizer",
    "quantize_model",
    "analyze_quantization",
    # Optimization - Pruning
    "Pruner",
    "PruningConfig",
    "PruningMethod",
    "MagnitudePruner",
    "StructuredPruner",
    "prune_model",
    "analyze_pruning",
    # Benchmarking
    "BenchmarkRunner",
    "BenchmarkConfig",
    "BenchmarkResult",
    "BenchmarkType",
    "LatencyMetric",
    "ThroughputMetric",
    "MemoryMetric",
    "AccuracyMetric",
    "PerplexityMetric",
    "RougeMetric",
    "plot_benchmark_results",
    "plot_comparison",
    "plot_latency_distribution",
    "plot_memory_usage",
    "run_benchmark",
    "compare_models",
    "save_benchmark_results",
    "load_benchmark_results",
    # Serving
    "ModelServer",
    "ServerConfig",
    "ServerProtocol",
    "RESTServer",
    "RESTConfig",
    "GRPCServer",
    "GRPCConfig",
    # Deployment
    "DockerConfig",
    "KubernetesConfig",
    "CloudConfig",
    "CloudProvider",
    "generate_docker_config",
    "generate_kubernetes_config",
    "generate_cloud_config",
    # CLI
    "cli_main",
]

# Add TensorRT adapter if available
if TENSORRT_AVAILABLE:
    __all__.append("TensorRTAdapter")

# Add Redis cache if available
if REDIS_CACHE_AVAILABLE:
    __all__.append("RedisCache")
