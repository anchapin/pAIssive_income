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
... (TRUNCATED: Full content copied as in ai_models/README.md)