# ai_models

**Documentation has moved!**  Please see the [central docs](../docs_source/html/index.html) for the up-to-date guide.

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
