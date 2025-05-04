"""
"""
AI Models module for pAIssive Income project.
AI Models module for pAIssive Income project.


This module provides a comprehensive system for managing and using local AI models
This module provides a comprehensive system for managing and using local AI models
for various tasks such as content generation, data analysis, and more.
for various tasks such as content generation, data analysis, and more.
"""
"""


from .adapters import LMStudioAdapter, OllamaAdapter, OpenAICompatibleAdapter
from .adapters import LMStudioAdapter, OllamaAdapter, OpenAICompatibleAdapter
from .agent_integration import AgentModelProvider
from .agent_integration import AgentModelProvider
from .batch_inference import (BatchInferenceProcessor, BatchInferenceRequest,
from .batch_inference import (BatchInferenceProcessor, BatchInferenceRequest,
BatchInferenceResult, generate_embeddings_batch,
BatchInferenceResult, generate_embeddings_batch,
generate_text_batch)
generate_text_batch)
from .model_base_types import ModelInfo
from .model_base_types import ModelInfo
from .model_config import ModelConfig
from .model_config import ModelConfig
from .model_downloader import DownloadProgress, DownloadTask, ModelDownloader
from .model_downloader import DownloadProgress, DownloadTask, ModelDownloader
from .model_manager import ModelManager
from .model_manager import ModelManager
from .model_types import AudioModel, ONNXModel, QuantizedModel, VisionModel
from .model_types import AudioModel, ONNXModel, QuantizedModel, VisionModel
from .performance_monitor import (InferenceMetrics, InferenceTracker,
from .performance_monitor import (InferenceMetrics, InferenceTracker,
ModelPerformanceReport, PerformanceMonitor)
ModelPerformanceReport, PerformanceMonitor)


# Import TensorRT adapter if available
# Import TensorRT adapter if available
try:
    try:
    from .adapters import TensorRTAdapter
    from .adapters import TensorRTAdapter


    TENSORRT_AVAILABLE = True
    TENSORRT_AVAILABLE = True
except ImportError:
except ImportError:
    TENSORRT_AVAILABLE = False
    TENSORRT_AVAILABLE = False


    from .caching.cache_integration import (cache_model_result,
    from .caching.cache_integration import (cache_model_result,
    invalidate_model_cache)
    invalidate_model_cache)


    # Import Redis cache if available
    # Import Redis cache if available
    try:
    try:
    from .caching import RedisCache
    from .caching import RedisCache


    REDIS_CACHE_AVAILABLE = True
    REDIS_CACHE_AVAILABLE = True
except ImportError:
except ImportError:
    REDIS_CACHE_AVAILABLE = False
    REDIS_CACHE_AVAILABLE = False


    # Import benchmarking tools
    # Import benchmarking tools
    from .benchmarking import (AccuracyMetric, BenchmarkConfig, BenchmarkResult,
    from .benchmarking import (AccuracyMetric, BenchmarkConfig, BenchmarkResult,
    BenchmarkRunner, BenchmarkType, LatencyMetric,
    BenchmarkRunner, BenchmarkType, LatencyMetric,
    MemoryMetric, PerplexityMetric, RougeMetric,
    MemoryMetric, PerplexityMetric, RougeMetric,
    ThroughputMetric, compare_models,
    ThroughputMetric, compare_models,
    load_benchmark_results, plot_benchmark_results,
    load_benchmark_results, plot_benchmark_results,
    plot_comparison, plot_latency_distribution,
    plot_comparison, plot_latency_distribution,
    plot_memory_usage, run_benchmark,
    plot_memory_usage, run_benchmark,
    save_benchmark_results)
    save_benchmark_results)
    # Import caching system
    # Import caching system
    from .caching import (CacheConfig, CacheKey, CacheManager, DiskCache,
    from .caching import (CacheConfig, CacheKey, CacheManager, DiskCache,
    MemoryCache, SQLiteCache, generate_cache_key)
    MemoryCache, SQLiteCache, generate_cache_key)
    from .cli import main as cli_main
    from .cli import main as cli_main
    # Import CLI tools
    # Import CLI tools
    # Import optimization utilities
    # Import optimization utilities
    from .optimization import (AWQQuantizer,  # Quantization; Pruning
    from .optimization import (AWQQuantizer,  # Quantization; Pruning
    BitsAndBytesQuantizer, GPTQQuantizer,
    BitsAndBytesQuantizer, GPTQQuantizer,
    MagnitudePruner, Pruner, PruningConfig,
    MagnitudePruner, Pruner, PruningConfig,
    PruningMethod, QuantizationConfig,
    PruningMethod, QuantizationConfig,
    QuantizationMethod, Quantizer, StructuredPruner,
    QuantizationMethod, Quantizer, StructuredPruner,
    analyze_pruning, analyze_quantization, prune_model,
    analyze_pruning, analyze_quantization, prune_model,
    quantize_model)
    quantize_model)
    # Import serving and deployment utilities
    # Import serving and deployment utilities
    from .serving import (  # Server interfaces; REST API server; gRPC server; Deployment utilities
    from .serving import (  # Server interfaces; REST API server; gRPC server; Deployment utilities
    CloudConfig, CloudProvider, DockerConfig, GRPCConfig, GRPCServer,
    CloudConfig, CloudProvider, DockerConfig, GRPCConfig, GRPCServer,
    KubernetesConfig, ModelServer, RESTConfig, RESTServer, ServerConfig,
    KubernetesConfig, ModelServer, RESTConfig, RESTServer, ServerConfig,
    ServerProtocol, generate_cloud_config, generate_docker_config,
    ServerProtocol, generate_cloud_config, generate_docker_config,
    generate_kubernetes_config)
    generate_kubernetes_config)


    # These imports are already handled above
    # These imports are already handled above




    # Redis cache import is already handled above
    # Redis cache import is already handled above








    __all__ = [
    __all__ = [
    # Core components
    # Core components
    "ModelManager",
    "ModelManager",
    "ModelInfo",
    "ModelInfo",
    "ModelConfig",
    "ModelConfig",
    "AgentModelProvider",
    "AgentModelProvider",
    "ModelDownloader",
    "ModelDownloader",
    "DownloadTask",
    "DownloadTask",
    "DownloadProgress",
    "DownloadProgress",
    "PerformanceMonitor",
    "PerformanceMonitor",
    "InferenceTracker",
    "InferenceTracker",
    "InferenceMetrics",
    "InferenceMetrics",
    "ModelPerformanceReport",
    "ModelPerformanceReport",
    # Batch processing
    # Batch processing
    "BatchInferenceProcessor",
    "BatchInferenceProcessor",
    "BatchInferenceRequest",
    "BatchInferenceRequest",
    "BatchInferenceResult",
    "BatchInferenceResult",
    "generate_text_batch",
    "generate_text_batch",
    "generate_embeddings_batch",
    "generate_embeddings_batch",
    # Model types
    # Model types
    "ONNXModel",
    "ONNXModel",
    "QuantizedModel",
    "QuantizedModel",
    "VisionModel",
    "VisionModel",
    "AudioModel",
    "AudioModel",
    # Adapters
    # Adapters
    "OllamaAdapter",
    "OllamaAdapter",
    "LMStudioAdapter",
    "LMStudioAdapter",
    "OpenAICompatibleAdapter",
    "OpenAICompatibleAdapter",
    # Caching system
    # Caching system
    "CacheManager",
    "CacheManager",
    "CacheConfig",
    "CacheConfig",
    "CacheKey",
    "CacheKey",
    "generate_cache_key",
    "generate_cache_key",
    "MemoryCache",
    "MemoryCache",
    "DiskCache",
    "DiskCache",
    "SQLiteCache",
    "SQLiteCache",
    "cache_model_result",
    "cache_model_result",
    "invalidate_model_cache",
    "invalidate_model_cache",
    # Optimization - Quantization
    # Optimization - Quantization
    "Quantizer",
    "Quantizer",
    "QuantizationConfig",
    "QuantizationConfig",
    "QuantizationMethod",
    "QuantizationMethod",
    "BitsAndBytesQuantizer",
    "BitsAndBytesQuantizer",
    "AWQQuantizer",
    "AWQQuantizer",
    "GPTQQuantizer",
    "GPTQQuantizer",
    "quantize_model",
    "quantize_model",
    "analyze_quantization",
    "analyze_quantization",
    # Optimization - Pruning
    # Optimization - Pruning
    "Pruner",
    "Pruner",
    "PruningConfig",
    "PruningConfig",
    "PruningMethod",
    "PruningMethod",
    "MagnitudePruner",
    "MagnitudePruner",
    "StructuredPruner",
    "StructuredPruner",
    "prune_model",
    "prune_model",
    "analyze_pruning",
    "analyze_pruning",
    # Benchmarking
    # Benchmarking
    "BenchmarkRunner",
    "BenchmarkRunner",
    "BenchmarkConfig",
    "BenchmarkConfig",
    "BenchmarkResult",
    "BenchmarkResult",
    "BenchmarkType",
    "BenchmarkType",
    "LatencyMetric",
    "LatencyMetric",
    "ThroughputMetric",
    "ThroughputMetric",
    "MemoryMetric",
    "MemoryMetric",
    "AccuracyMetric",
    "AccuracyMetric",
    "PerplexityMetric",
    "PerplexityMetric",
    "RougeMetric",
    "RougeMetric",
    "plot_benchmark_results",
    "plot_benchmark_results",
    "plot_comparison",
    "plot_comparison",
    "plot_latency_distribution",
    "plot_latency_distribution",
    "plot_memory_usage",
    "plot_memory_usage",
    "run_benchmark",
    "run_benchmark",
    "compare_models",
    "compare_models",
    "save_benchmark_results",
    "save_benchmark_results",
    "load_benchmark_results",
    "load_benchmark_results",
    # Serving
    # Serving
    "ModelServer",
    "ModelServer",
    "ServerConfig",
    "ServerConfig",
    "ServerProtocol",
    "ServerProtocol",
    "RESTServer",
    "RESTServer",
    "RESTConfig",
    "RESTConfig",
    "GRPCServer",
    "GRPCServer",
    "GRPCConfig",
    "GRPCConfig",
    # Deployment
    # Deployment
    "DockerConfig",
    "DockerConfig",
    "KubernetesConfig",
    "KubernetesConfig",
    "CloudConfig",
    "CloudConfig",
    "CloudProvider",
    "CloudProvider",
    "generate_docker_config",
    "generate_docker_config",
    "generate_kubernetes_config",
    "generate_kubernetes_config",
    "generate_cloud_config",
    "generate_cloud_config",
    # CLI
    # CLI
    "cli_main",
    "cli_main",
    ]
    ]


    # Add TensorRT adapter if available
    # Add TensorRT adapter if available
    if TENSORRT_AVAILABLE:
    if TENSORRT_AVAILABLE:
    __all__.append("TensorRTAdapter")
    __all__.append("TensorRTAdapter")


    # Add Redis cache if available
    # Add Redis cache if available
    if REDIS_CACHE_AVAILABLE:
    if REDIS_CACHE_AVAILABLE:
    __all__.append("RedisCache")
    __all__.append("RedisCache")

