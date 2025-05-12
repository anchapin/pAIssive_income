# AI Models Module

This module provides a comprehensive system for managing and using local AI models for various tasks such as content generation, data analysis, and more.

## Overview

The AI Models module includes the following components:

1. **ModelManager**: Central system for managing AI models, including model discovery, loading, caching, and monitoring.
2. **ModelConfig**: Configuration for AI models, including settings for model paths, cache, and performance options.
3. **ModelInfo**: Information about AI models, including metadata and capabilities.

## Features

- **Model Discovery**: Automatically discover available models on the system.
- **Model Loading**: Load models from various sources (local files, Hugging Face, etc.).
- **Model Caching**: Cache model responses to improve performance.
- **Model Downloading**: Download models from Hugging Face Hub and other sources.
- **Performance Monitoring**: Track and analyze model performance metrics.
- **Model Benchmarking**: Compare performance across different models.
- **Hardware Optimization**: Automatically select the best device for model inference.
- **System Information**: Get information about the system's hardware and installed dependencies.
- **Agent Integration**: Assign models to different agents based on their tasks.

## Installation

To install the required dependencies, run:

```bash
uv pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from ai_models import ModelManager

# Create a model manager with default configuration
manager = ModelManager()

# Discover available models
discovered_models = manager.discover_models()
print(f"Discovered {len(discovered_models)} models")

# Get all registered models
all_models = manager.get_all_models()
for model in all_models:
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")

# Load a model
if all_models:
    model_to_load = all_models[0]
    loaded_model = manager.load_model(model_to_load.id)

    # Use the model
    # ...

    # Unload the model when done
    manager.unload_model(model_to_load.id)
```

### Downloading Models

```python
from ai_models import ModelManager, ModelDownloader

# Create a model manager
manager = ModelManager()

# Create a model downloader with the model manager
downloader = ModelDownloader(model_manager=manager)

# Download a model from Hugging Face Hub
task = downloader.download_from_huggingface(
    model_id="gpt2",  # Model ID on Hugging Face Hub
    file_name="config.json",  # Optional: download a specific file
    auto_register=True  # Automatically register the model with the manager
)

# Wait for the download to complete
task.wait()

# Download a model from a URL
task = downloader.download_from_url(
    url="https://example.com/model.bin",
    model_id="example-model",
    model_type="llama",
    auto_register=True
)

# Check download progress
print(f"Status: {task.progress.status}")
print(f"Progress: {task.progress.percentage}%")
print(f"Speed: {task.progress.speed / 1024 / 1024:.2f} MB/s")
```

### Custom Configuration

```python
from ai_models import ModelManager, ModelConfig

# Create a custom configuration
config = ModelConfig(
    models_dir="/path/to/models",
    cache_dir="/path/to/cache",
    cache_enabled=True,
    default_device="cuda"
)

# Create a model manager with custom configuration
manager = ModelManager(config)
```

### Registering a New Model

```python
from ai_models import ModelManager, ModelInfo

# Create a model manager
manager = ModelManager()

# Create model info
model_info = ModelInfo(
    id="my-model-id",
    name="My Model",
    type="huggingface",
    path="/path/to/model",
    description="My custom model",
    format="pytorch"
)

# Register the model
manager.register_model(model_info)
```

## Examples

See the `examples` directory for more examples of how to use the AI Models module.

### Performance Monitoring

```python
from ai_models import ModelManager, PerformanceMonitor, InferenceTracker

# Create a performance monitor
monitor = PerformanceMonitor()

# Create a model manager with the performance monitor
manager = ModelManager(performance_monitor=monitor)

# Track inference performance using a context manager
with manager.track_inference("model-id", input_tokens=10) as tracker:
    # Record when the first token is generated
    tracker.record_first_token()

    # Update the number of output tokens
    tracker.update_output_tokens(20)

    # Add metadata
    tracker.add_metadata("temperature", 0.7)

# Generate a performance report
report = manager.generate_performance_report("model-id")
print(f"Average inference time: {report.avg_inference_time:.4f} seconds")
print(f"Average tokens per second: {report.avg_tokens_per_second:.2f}")

# Get system performance
system_perf = monitor.get_system_performance()
print(f"CPU Usage: {system_perf['cpu']['percent']}%")
```

### Specialized Model Types

```python
from ai_models.model_types import ONNXModel, QuantizedModel, VisionModel, AudioModel

# Use an ONNX model for text generation
onnx_model = ONNXModel(
    model_path="path/to/model.onnx",
    model_type="text-generation"
)
onnx_model.load()
output = onnx_model.generate_text("Hello, world!")

# Use a quantized model for efficient inference
quantized_model = QuantizedModel(
    model_path="path/to/model",
    model_type="text-generation",
    quantization="4bit"
)
quantized_model.load()
output = quantized_model.generate_text("Hello, world!")

# Use a vision model for image classification
vision_model = VisionModel(
    model_path="path/to/model",
    model_type="image-classification"
)
vision_model.load()
results = vision_model.classify_image("path/to/image.jpg")

# Use an audio model for speech recognition
audio_model = AudioModel(
    model_path="path/to/model",
    model_type="speech-recognition"
)
audio_model.load()
transcription = audio_model.transcribe("path/to/audio.wav")
```

### Model Adapters

```python
from ai_models.adapters import OllamaAdapter, LMStudioAdapter, OpenAICompatibleAdapter

# Use Ollama for text generation
ollama = OllamaAdapter(base_url="http://localhost:11434")
models = ollama.list_models()
response = ollama.generate_text("llama2", "Hello, world!")

# Use LM Studio for chat
lmstudio = LMStudioAdapter(base_url="http://localhost:1234/v1")
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
]
response = lmstudio.generate_chat_completions("model-id", messages)

# Use OpenAI-compatible API
openai_api = OpenAICompatibleAdapter(
    base_url="http://localhost:8000/v1",
    api_key="sk-"
)
response = openai_api.create_chat_completion(
    "model-id",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Use TensorRT for GPU-accelerated inference (if available)
try:
    from ai_models.adapters import TensorRTAdapter
    tensorrt = TensorRTAdapter(
        engine_path="path/to/engine.trt",
        model_type="text-generation",
        tokenizer_path="path/to/tokenizer"
    )
    output = tensorrt.generate_text("Hello, world!")
except ImportError:
    print("TensorRT not available")
```

### Model Caching

```python
from ai_models.caching import CacheManager, CacheConfig, MemoryCache

# Create a cache configuration
config = CacheConfig(
    enabled=True,
    backend="memory",
    ttl=3600,  # 1 hour
    max_size=1000,
    eviction_policy="lru"
)

# Create a cache manager
cache_manager = CacheManager(config)

# Define model and operation
model_id = "gpt2"
operation = "generate"
inputs = "Hello, world!"
parameters = {"temperature": 0.7, "max_tokens": 100}

# Check if response is in cache
cached_response = cache_manager.get(model_id, operation, inputs, parameters)

if cached_response:
    print("Cache hit!")
    response = cached_response
else:
    print("Cache miss!")
    # Run model inference
    response = model.generate_text(inputs, **parameters)

    # Cache the response
    cache_manager.set(model_id, operation, inputs, response, parameters)

# Get cache statistics
stats = cache_manager.get_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
```

### Model Optimization

```python
from ai_models.optimization import (
    quantize_model, analyze_quantization,
    prune_model, analyze_pruning
)

# Quantize a model
quantized_path = quantize_model(
    model_path="path/to/model",
    output_path="path/to/output",
    method="bitsandbytes-4bit",
    bits=4,
    model_type="text-generation"
)

# Analyze quantization effects
quantization_analysis = analyze_quantization(
    original_model_path="path/to/model",
    quantized_model_path=quantized_path,
    num_samples=5,
    max_tokens=100
)

print(f"Size reduction: {quantization_analysis['comparison']['size_reduction_percent']:.2f}%")
print(f"Speed improvement: {quantization_analysis['comparison']['speed_improvement_percent']:.2f}%")

# Prune a model
pruned_path = prune_model(
    model_path="path/to/model",
    output_path="path/to/output",
    method="magnitude",
    sparsity=0.5,
    model_type="text-generation"
)

# Analyze pruning effects
pruning_analysis = analyze_pruning(
    original_model_path="path/to/model",
    pruned_model_path=pruned_path,
    num_samples=5,
    max_tokens=100
)

print(f"Sparsity: {pruning_analysis['pruned_model']['sparsity']:.4f}")
print(f"Size reduction: {pruning_analysis['comparison']['size_reduction_percent']:.2f}%")
print(f"Speed improvement: {pruning_analysis['comparison']['speed_improvement_percent']:.2f}%")
```

### Model Benchmarking

```python
from ai_models.benchmarking import (
    run_benchmark, compare_models, BenchmarkType,
    plot_benchmark_results, plot_comparison
)

# Run a latency benchmark
latency_result = run_benchmark(
    model_path="path/to/model",
    benchmark_type=BenchmarkType.LATENCY,
    model_type="text-generation",
    num_runs=20,
    max_tokens=100
)

# Get latency statistics
latency_stats = latency_result.get_latency_stats()
print(f"Mean latency: {latency_stats['mean']:.2f} ms")
print(f"P95 latency: {latency_stats['p95']:.2f} ms")

# Run a throughput benchmark
throughput_result = run_benchmark(
    model_path="path/to/model",
    benchmark_type=BenchmarkType.THROUGHPUT,
    model_type="text-generation",
    batch_size=4,
    max_tokens=100
)

print(f"Throughput: {throughput_result.throughput:.2f} tokens/second")

# Compare multiple models
results = compare_models(
    model_paths=["path/to/model1", "path/to/model2", "path/to/model3"],
    benchmark_type=BenchmarkType.LATENCY,
    model_type="text-generation",
    num_runs=10
)

# Plot comparison
plot_comparison(results, metric="latency", output_path="comparison.png")
```

### Model Serving

```python
from ai_models.serving import RESTServer, RESTConfig, ServerProtocol

# Create server configuration
config = RESTConfig(
    model_path="path/to/model",
    model_type="text-generation",
    host="127.0.0.1",  # Bind to localhost for security
    port=8000,
    enable_text_generation=True,
    enable_embedding=True,
    enable_auth=True,
    api_keys=["sk-12345"],
    enable_rate_limit=True,
    rate_limit=60
)

# Create and start server
server = RESTServer(config)
server.load_model()
server.start()

# Server is now running at http://127.0.0.1:8000
# Stop the server when done
server.stop()
```

### Model Deployment

```python
from ai_models.serving import (
    DockerConfig, KubernetesConfig, CloudConfig, CloudProvider,
    generate_docker_config, generate_kubernetes_config, generate_cloud_config
)

# Generate Docker configuration
docker_config = DockerConfig(
    image_name="my-model-server",
    model_path="/models/my-model",
    model_type="text-generation",
    server_type="rest",
    port=8000,
    gpu_count=1
)

dockerfile_path = generate_docker_config(docker_config, "docker")

# Generate Kubernetes configuration
k8s_config = KubernetesConfig(
    name="my-model-server",
    namespace="ai-models",
    image="my-model-server:latest",
    replicas=2,
    enable_hpa=True,
    min_replicas=1,
    max_replicas=5
)

k8s_path = generate_kubernetes_config(k8s_config, "kubernetes")

# Generate AWS deployment configuration
cloud_config = CloudConfig(
    provider=CloudProvider.AWS,
    name="my-model-server",
    region="us-west-2",
    instance_type="ml.g4dn.xlarge",
    gpu_count=1
)

aws_path = generate_cloud_config(cloud_config, "aws")
```

### Command-Line Interface

```bash
# Download a model
python -m ai_models download --model-id gpt2 --output-dir models

# List available models
python -m ai_models list --model-dir models

# Get model information
python -m ai_models info --model-path models/gpt2

# Optimize a model
python -m ai_models optimize --model-path models/gpt2 --output-path models/gpt2-optimized --method quantize

# Benchmark a model
python -m ai_models benchmark --model-path models/gpt2 --benchmark-type latency --num-runs 20

# Serve a model with REST API
python -m ai_models serve-rest --model-path models/gpt2 --host 127.0.0.1 --port 8000

# Deploy a model
python -m ai_models deploy --model-path models/gpt2 --deployment-type docker --output-dir deployment
```

### Agent Integration

```python
from ai_models import ModelManager, AgentModelProvider

# Create a model manager
manager = ModelManager()

# Create an agent model provider
provider = AgentModelProvider(manager)

# Get a model for a specific agent and task
researcher_model = provider.get_model_for_agent("researcher", "text-generation")

# Assign a specific model to an agent
model_info = manager.get_models_by_type("huggingface")[0]
provider.assign_model_to_agent("developer", model_info.id, "code-generation")

# Get all agent model assignments
assignments = provider.get_agent_model_assignments()
```

## Supported Model Types

- **Hugging Face Models**: Models from the Hugging Face Hub or local Hugging Face models.
- **Llama Models**: Models in GGUF format for use with llama.cpp.
- **Embedding Models**: Models for generating text embeddings.
- **ONNX Models**: Models in ONNX format.
- **Quantized Models**: 4-bit and 8-bit quantized models for efficient inference.
- **Vision Models**: Models for image classification, object detection, and image segmentation.
- **Audio Models**: Models for speech recognition, text-to-speech, and audio classification.

## Framework Adapters

The AI Models module includes adapters for connecting to various model frameworks:

- **Ollama Adapter**: Connect to Ollama for running local LLMs.
- **LM Studio Adapter**: Connect to LM Studio for running local LLMs.
- **OpenAI-Compatible Adapter**: Connect to any OpenAI-compatible API, including local servers.
- **TensorRT Adapter**: Use NVIDIA TensorRT for GPU-accelerated inference.

## Caching System

The AI Models module includes a comprehensive caching system for model responses:

- **Multiple Backends**: Support for memory, disk, SQLite, and Redis cache backends.
- **Configurable Policies**: Customizable TTL, size limits, and eviction policies.
- **Flexible Filtering**: Cache specific models and operations based on filters.
- **Performance Monitoring**: Track cache hits, misses, and other statistics.

## Optimization Utilities

The AI Models module includes utilities for optimizing models:

### Quantization

- **Multiple Methods**: Support for BitsAndBytes (4-bit, 8-bit), AWQ, and GPTQ quantization.
- **Configurable Parameters**: Customizable quantization parameters for different methods.
- **Analysis Tools**: Analyze the effects of quantization on model size, speed, and quality.

### Pruning

- **Multiple Methods**: Support for magnitude-based and structured pruning.
- **Configurable Sparsity**: Customizable sparsity levels and pruning schedules.
- **Analysis Tools**: Analyze the effects of pruning on model size, speed, and quality.

## Benchmarking Tools

The AI Models module includes tools for benchmarking model performance:

### Performance Metrics

- **Latency**: Measure inference time with detailed statistics (mean, median, percentiles).
- **Throughput**: Measure tokens per second for batch processing.
- **Memory Usage**: Analyze memory consumption of different model components.
- **Accuracy**: Evaluate model accuracy on classification tasks.
- **Perplexity**: Measure language model quality.
- **ROUGE**: Evaluate text generation quality.

### Visualization

- **Interactive Plots**: Visualize benchmark results with customizable plots.
- **Comparison Charts**: Compare performance across different models.
- **Distribution Analysis**: Analyze latency distribution and outliers.

## Serving and Deployment

The AI Models module includes utilities for serving and deploying models:

### Model Servers

- **REST API Server**: Serve models with a REST API compatible with OpenAI's API.
- **gRPC Server**: Serve models with a high-performance gRPC interface.
- **Streaming Support**: Stream responses for real-time inference.
- **Authentication**: Secure your API with API keys and rate limiting.

### Deployment Utilities

- **Docker**: Generate Docker configurations for containerized deployment.
- **Kubernetes**: Generate Kubernetes manifests for orchestrated deployment.
- **Cloud Platforms**: Generate deployment configurations for AWS, GCP, and Azure.

## Command-Line Interface

The AI Models module includes a command-line interface for managing models:

### Model Management

- **Download**: Download models from Hugging Face or other sources.
- **List**: List available models in a directory.
- **Info**: Get detailed information about a model.

### Model Optimization

- **Optimize**: Optimize models using quantization, pruning, or distillation.
- **Benchmark**: Benchmark model performance.
- **Validate**: Validate models for correctness and security.

### Model Serving

- **Serve**: Start a REST or gRPC server for a model.
- **Deploy**: Generate deployment configurations for Docker, Kubernetes, or cloud platforms.

## Dependencies

- **Required**:
  - Python 3.8+
  - PyTorch
  - Transformers
  - Sentence Transformers

- **Optional**:
  - llama-cpp-python (for Llama models)
  - ONNX Runtime (for ONNX models)
  - bitsandbytes (for quantized models)
  - huggingface-hub (for downloading models from Hugging Face)
  - requests (for downloading models from URLs)
  - tqdm (for progress bars)
  - psutil (for system monitoring)
  - numpy (for statistical analysis)
  - matplotlib (for visualization)
  - pandas (for data analysis)
  - pillow (for image processing)
  - torchvision (for vision models)
  - librosa (for audio processing)
  - soundfile (for audio file handling)
  - scipy (for scientific computing)
  - openai (for OpenAI-compatible adapters)
  - tensorrt (for TensorRT adapter)
  - pycuda (for TensorRT adapter)
  - redis (for Redis cache backend)
  - auto-gptq (for GPTQ quantization)
  - autoawq (for AWQ quantization)
  - rouge-score (for ROUGE metrics)
  - matplotlib (for benchmark visualization)

## License

[MIT License](../LICENSE)
