# AI Models

The AI Models module is a comprehensive system for managing and using local AI models for various tasks such as content generation, data analysis, and more. It provides a unified interface for working with different types of models and adapters.

## Overview

The AI Models module consists of several key components:

1. **Model Manager**: Central manager for AI models, handling registration, discovery, loading, and unloading.
2. **Model Config**: Configuration for AI models, including directories, cache settings, and performance settings.
3. **Agent Integration**: Integration with the agent team, allowing agents to use local AI models for their tasks.
4. **Model Downloader**: Tools for downloading models from various sources.
5. **Performance Monitor**: Tools for monitoring model performance and tracking inference metrics.
6. **Model Types**: Specialized model types for different use cases (ONNX, Quantized, Vision, Audio).
7. **Adapters**: Adapters for different model backends (Ollama, LM Studio, OpenAI-compatible).
8. **Caching System**: System for caching model outputs to improve performance.
9. **Optimization Tools**: Tools for optimizing models through quantization and other techniques.
10. **Serving and Deployment**: Tools for serving models through REST and gRPC interfaces and deploying them to various environments.

## Model Manager

The `ModelManager` class is the central component of the AI Models module. It manages the registration, discovery, loading, and unloading of AI models.

```python
from ai_models import ModelManager, ModelInfo

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

### Model Info

The `ModelInfo` class represents information about an AI model, including its ID, name, type, path, and other metadata.

```python
from ai_models import ModelInfo

# Create model info
model_info = ModelInfo(
    id="my-model-id",
    name="My Model",
    type="huggingface",
    path="/path/to/model",
    description="My custom model",
    format="pytorch"
)

# Register the model with the model manager
manager.register_model(model_info)
```

### Model Discovery

The `ModelManager` can discover models from various sources, including local directories and Hugging Face.

```python
# Discover models
discovered_models = manager.discover_models()

# Discover models from specific sources
local_models = manager._discover_local_models()
hf_models = manager._discover_huggingface_models()
```

### Model Loading and Unloading

The `ModelManager` can load models into memory for use and unload them when they're no longer needed.

```python
# Load a model
model = manager.load_model("model-id")

# Use the model
# ...

# Unload the model
manager.unload_model("model-id")
```

## Model Config

The `ModelConfig` class represents the configuration for AI models, including directories, cache settings, and performance settings.

```python
from ai_models import ModelConfig

# Create a model configuration
config = ModelConfig(
    models_dir="/path/to/models",
    cache_dir="/path/to/cache",
    cache_enabled=True,
    cache_ttl=86400,  # 24 hours in seconds
    max_cache_size=1000,
    default_device="auto",
    max_threads=None,  # None means use all available threads
    auto_discover=True,
    model_sources=["local", "huggingface"],
    default_text_model="gpt2",
    default_embedding_model="all-MiniLM-L6-v2"
)

# Save the configuration
config.save("/path/to/config.json")

# Load the configuration
loaded_config = ModelConfig.load("/path/to/config.json")

# Get the default configuration
default_config = ModelConfig.get_default()
```

## Agent Integration

The `AgentModelProvider` class integrates the AI Models module with the agent team, allowing agents to use local AI models for their tasks.

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

### Model Selection

The `AgentModelProvider` selects models for agents based on agent type and task type. It uses a set of preferences to determine the best model for each agent and task.

```python
# Agent preferences
agent_preferences = {
    "researcher": ["huggingface", "llama"],
    "developer": ["huggingface", "llama"],
    "monetization": ["huggingface", "llama"],
    "marketing": ["huggingface", "llama"],
    "feedback": ["huggingface", "llama"]
}

# Task preferences
task_preferences = {
    "text-generation": ["huggingface", "llama"],
    "code-generation": ["huggingface", "llama"],
    "embedding": ["huggingface", "embedding"],
    "classification": ["huggingface", "llama"],
    "summarization": ["huggingface", "llama"]
}
```

## Model Downloader

The `ModelDownloader` class provides tools for downloading models from various sources, including Hugging Face and other repositories.

```python
from ai_models import ModelManager, ModelDownloader

# Create a model manager
manager = ModelManager()

# Create a model downloader
downloader = ModelDownloader(manager)

# Download a model
download_task = downloader.download_model(
    model_id="gpt2",
    source="huggingface",
    destination="/path/to/models/gpt2"
)

# Track download progress
progress = downloader.get_download_progress(download_task.id)
print(f"Download progress: {progress.percentage}%")

# Wait for download to complete
downloader.wait_for_download(download_task.id)

# Register the downloaded model
model_info = manager.register_downloaded_model(
    download_task,
    model_type="huggingface",
    description="GPT-2 model from Hugging Face",
    model_format="pytorch"
)
```

## Performance Monitor

The `PerformanceMonitor` class provides tools for monitoring model performance and tracking inference metrics.

```python
from ai_models import ModelManager, PerformanceMonitor

# Create a model manager
manager = ModelManager()

# Create a performance monitor
monitor = PerformanceMonitor()

# Set the performance monitor for the model manager
manager.set_performance_monitor(monitor)

# Track inference
with monitor.track_inference("model-id") as tracker:
    # Use the model
    result = model.generate("Hello, world!")

    # Set metrics
    tracker.set_metrics(
        input_tokens=len("Hello, world!"),
        output_tokens=len(result),
        inference_time=tracker.elapsed_time
    )

# Get inference metrics
metrics = monitor.get_inference_metrics("model-id")
print(f"Average inference time: {metrics.avg_inference_time:.4f} seconds")
print(f"Average tokens per second: {metrics.avg_tokens_per_second:.2f}")

# Generate a performance report
report = monitor.generate_performance_report("model-id")
print(f"Average inference time: {report.avg_inference_time:.4f} seconds")
print(f"Average tokens per second: {report.avg_tokens_per_second:.2f}")

# Get system performance
system_perf = monitor.get_system_performance()
print(f"CPU Usage: {system_perf['cpu']['percent']}%")
```

## Model Types

The AI Models module includes several specialized model types for different use cases:

### ONNX Model

The `ONNXModel` class represents a model in the ONNX format, which is optimized for inference.

```python
from ai_models.model_types import ONNXModel

# Create an ONNX model
onnx_model = ONNXModel(
    model_path="path/to/model.onnx",
    model_type="text-generation"
)

# Use the model
result = onnx_model.generate("Hello, world!")
```

### Quantized Model

The `QuantizedModel` class represents a quantized model, which is optimized for memory usage and inference speed.

```python
from ai_models.model_types import QuantizedModel

# Create a quantized model
quantized_model = QuantizedModel(
    model_path="path/to/model.bin",
    model_type="text-generation",
    quantization_method="int8"
)

# Use the model
result = quantized_model.generate("Hello, world!")
```

### Vision Model

The `VisionModel` class represents a model for vision tasks, such as image classification and object detection.

```python
from ai_models.model_types import VisionModel

# Create a vision model
vision_model = VisionModel(
    model_path="path/to/model",
    model_type="image-classification"
)

# Use the model
result = vision_model.classify("path/to/image.jpg")
```

### Audio Model

The `AudioModel` class represents a model for audio tasks, such as speech recognition and audio classification.

```python
from ai_models.model_types import AudioModel

# Create an audio model
audio_model = AudioModel(
    model_path="path/to/model",
    model_type="speech-recognition"
)

# Use the model
result = audio_model.transcribe("path/to/audio.wav")
```

## Adapters

The AI Models module includes several adapters for different model backends:

### Ollama Adapter

The `OllamaAdapter` class provides an adapter for the Ollama backend, which is a local model server.

```python
from ai_models.adapters import OllamaAdapter

# Create an Ollama adapter
adapter = OllamaAdapter(
    host="localhost",
    port=11434
)

# Use the adapter
result = adapter.generate("Hello, world!", model="llama2")
```

### LM Studio Adapter

The `LMStudioAdapter` class provides an adapter for the LM Studio backend, which is a local model server.

```python
from ai_models.adapters import LMStudioAdapter

# Create an LM Studio adapter
adapter = LMStudioAdapter(
    host="localhost",
    port=1234
)

# Use the adapter
result = adapter.generate("Hello, world!", model="llama3")
```

### OpenAI-Compatible Adapter

The `OpenAICompatibleAdapter` class provides an adapter for OpenAI-compatible backends, such as local servers that implement the OpenAI API.

```python
from ai_models.adapters import OpenAICompatibleAdapter

# Create an OpenAI-compatible adapter
adapter = OpenAICompatibleAdapter(
    base_url="http://localhost:8000/v1",
    api_key="sk-..."
)

# Use the adapter
result = adapter.generate("Hello, world!", model="gpt-3.5-turbo")
```

## Caching System

The AI Models module includes a caching system for improving performance by caching model outputs.

```python
from ai_models.caching import CacheManager, CacheConfig

# Create a cache configuration
cache_config = CacheConfig(
    cache_dir="/path/to/cache",
    ttl=86400,  # 24 hours in seconds
    max_size=1000
)

# Create a cache manager
cache_manager = CacheManager(cache_config)

# Generate a cache key
cache_key = cache_manager.generate_key(
    model_id="model-id",
    input_text="Hello, world!",
    parameters={"temperature": 0.7, "max_tokens": 100}
)

# Check if a result is cached
if cache_manager.has(cache_key):
    # Get the cached result
    result = cache_manager.get(cache_key)
else:
    # Generate the result
    result = model.generate("Hello, world!")

    # Cache the result
    cache_manager.set(cache_key, result)
```

## Optimization Tools

The AI Models module includes tools for optimizing models through quantization and other techniques.

```python
from ai_models.optimization import Quantizer, QuantizationConfig

# Create a quantization configuration
config = QuantizationConfig(
    method="int8",
    bits=8,
    dataset="path/to/calibration/dataset"
)

# Create a quantizer
quantizer = Quantizer(config)

# Quantize a model
quantized_model = quantizer.quantize("path/to/model")

# Analyze quantization
analysis = quantizer.analyze_quantization(
    original_model="path/to/model",
    quantized_model=quantized_model
)
```

## Serving and Deployment

The AI Models module includes tools for serving models through REST and gRPC interfaces and deploying them to various environments.

```python
from ai_models.serving import ModelServer, ServerConfig, RESTServer, RESTConfig

# Create a server configuration
server_config = ServerConfig(
    protocol="REST",
    host="0.0.0.0",
    port=8000
)

# Create a REST configuration
rest_config = RESTConfig(
    enable_docs=True,
    cors_origins=["*"],
    auth_enabled=False
)

# Create a model server
server = RESTServer(server_config, rest_config)

# Add a model to the server
server.add_model("model-id", model)

# Start the server
server.start()
```

### Deployment

The AI Models module includes tools for deploying models to various environments, including Docker, Kubernetes, and cloud providers.

```python
from ai_models.serving import DockerConfig, generate_docker_config

# Create a Docker configuration
docker_config = DockerConfig(
    base_image="python:3.9",
    expose_port=8000,
    environment={"CUDA_VISIBLE_DEVICES": "0"}
)

# Generate a Docker configuration
docker_files = generate_docker_config(
    model_id="model-id",
    server_type="rest",
    config=docker_config,
    output_dir="path/to/output"
)
```

## CLI Tools

The AI Models module includes command-line tools for managing models, serving them, and deploying them.

```bash
# List all models
python -m ai_models list

# Get information about a model
python -m ai_models info --model-id model-id

# Download a model
python -m ai_models download --model-id gpt2 --source huggingface

# Serve a model
python -m ai_models serve --model-id model-id --port 8000

# Deploy a model
python -m ai_models deploy --model-id model-id --deployment-type docker --output-dir deployment
```

## Integration with Agent Team

The AI Models module is integrated with the Agent Team module through the `AgentModelProvider` class, allowing agents to use local AI models for their tasks.

```python
from agent_team import AgentTeam
from ai_models import ModelManager, AgentModelProvider

# Create a model manager
manager = ModelManager()

# Create an agent model provider
provider = AgentModelProvider(manager)

# Create a team with the agent model provider
team = AgentTeam("My Team", agent_model_provider=provider)

# Now the team will use local AI models for its tasks
```

## Example: Complete Workflow

Here's a complete example that demonstrates how to use the AI Models module:

```python
from ai_models import ModelManager, ModelInfo, AgentModelProvider
from agent_team import AgentTeam

# Create a model manager
manager = ModelManager()

# Discover available models
discovered_models = manager.discover_models()
print(f"Discovered {len(discovered_models)} models")

# If no models are discovered, register some example models
if not discovered_models:
    # Register a Hugging Face model
    hf_model = ModelInfo(
        id="example-hf-model",
        name="Example Hugging Face Model",
        type="huggingface",
        path="gpt2",  # This is a small model for demonstration
        description="Example Hugging Face model for text generation",
        format="pytorch"
    )
    manager.register_model(hf_model)
    print(f"Registered example Hugging Face model: {hf_model.name}")

    # Register an embedding model
    embedding_model = ModelInfo(
        id="example-embedding-model",
        name="Example Embedding Model",
        type="embedding",
        path="all-MiniLM-L6-v2",  # This is a small embedding model
        description="Example embedding model for text similarity",
        format="huggingface"
    )
    manager.register_model(embedding_model)
    print(f"Registered example embedding model: {embedding_model.name}")

# Create an agent model provider
provider = AgentModelProvider(manager)

# Create a team with the agent model provider
team = AgentTeam("My Team", agent_model_provider=provider)

# Run niche analysis
niches = team.run_niche_analysis(["e-commerce", "content creation"])

# Print identified niches
for i, niche in enumerate(niches):
    print(f"{i+1}. {niche['name']} (Score: {niche['opportunity_score']:.2f})")
```
