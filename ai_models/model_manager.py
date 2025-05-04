try:
    import torch
except ImportError:
    pass


    import asyncio
    import hashlib
    import json
    import logging
    import os
    import sys
    import threading
    from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    from interfaces.model_interfaces import IModelManager

    from .model_base_types import ModelInfo
    from .model_config import ModelConfig
    from .model_versioning import ModelVersion, VersionedModelManager

    TRANSFORMERS_AVAILABLE
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE
    from llama_cpp import Llama

    LLAMA_CPP_AVAILABLE
    import onnxruntime

    from tests.mocks.mock_model_providers import create_mock_provider

    return create_mock_provider

    (
    ConfigurationError,
    ModelError,
    ModelLoadError,
    ModelNotFoundError,
    ValidationError,
    handle_exception,
    )
    """
    Model manager for the AI Models module.

    This module provides a central system for managing AI models, including
    model discovery, loading, caching, and monitoring.
    """

    # Set up logging
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Import only for type checking to avoid circular imports
    if TYPE_CHECKING:
    from .performance_monitor import PerformanceMonitor

    # Set up logging
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Try to import optional dependencies
    try:


    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. GPU acceleration will be limited.")
    TORCH_AVAILABLE = False

    try:

    = True
except ImportError:
    logger.warning(
    "Transformers not available. Hugging Face models will not be available."
    )
    TRANSFORMERS_AVAILABLE = False

    try:
    = True
except ImportError:
    logger.warning(
    "Sentence Transformers not available. Embedding models will be limited."
    )
    SENTENCE_TRANSFORMERS_AVAILABLE = False

    try:
    = True
except ImportError:
    logger.warning(
    "llama-cpp-python not available. Llama model support will be limited."
    )
    LLAMA_CPP_AVAILABLE = False

    try:
    as ort

    ONNX_AVAILABLE = True
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False


    class ModelManager(IModelManager):
    """
    Central manager for AI models.
    """

    def __init__(
    self,
    config: Optional[ModelConfig] = None,
    performance_monitor: Optional["PerformanceMonitor"] = None,
    ):
    """
    Initialize the model manager.

    Args:
    config: Optional model configuration
    performance_monitor: Optional performance monitor
    """
    self.config = config or ModelConfig.get_default()
    self.models: Dict[str, ModelInfo] = {}
    self.loaded_models: Dict[str, Any] = {}
    self.model_lock = threading.Lock()
    self.performance_monitor = performance_monitor

    # Create necessary directories
    os.makedirs(self.config.models_dir, exist_ok=True)
    os.makedirs(self.config.cache_dir, exist_ok=True)

    # Initialize model registry
    self._init_model_registry()

    # Initialize versioned model manager
    self.versioned_manager = VersionedModelManager(self, self.config.models_dir)

    # Discover models if auto-discover is enabled
    if self.config.auto_discover:
    self.discover_models()

    def _init_model_registry(self) -> None:
    """
    Initialize the model registry.
    """
    registry_path = os.path.join(self.config.models_dir, "registry.json")

    if os.path.exists(registry_path):
    try:
    with open(registry_path, "r") as f:
    registry_data = json.load(f)

    for model_data in registry_data.get("models", []):
    model_info = ModelInfo.from_dict(model_data)
    self.models[model_info.id] = model_info

    logger.info(f"Loaded {len(self.models)} models from registry")
except json.JSONDecodeError as e:
    error = ConfigurationError(
    message=f"Invalid JSON format in model registry: {e}",
    config_key="registry.json",
    original_exception=e,
    )
    error.log()
    # Create a new registry
    self._save_model_registry()
except Exception as e:
    error = handle_exception(
    e, error_class=ConfigurationError, reraise=False
    )
    # Create a new registry
    self._save_model_registry()
    else:
    # Create a new registry
    self._save_model_registry()

    def _save_model_registry(self) -> None:
    """
    Save the model registry to disk.
    """
    registry_path = os.path.join(self.config.models_dir, "registry.json")

    try:
    registry_data = {
    "models": [model.to_dict() for model in self.models.values()]
    }

    with open(registry_path, "w") as f:
    json.dump(registry_data, f, indent=2)

    logger.info(f"Saved {len(self.models)} models to registry")
except (IOError, OSError) as e:
    error = ConfigurationError(
    message=f"Failed to write model registry to {registry_path}: {e}",
    config_key="models_dir",
    original_exception=e,
    )
    error.log()
except Exception as e:
    handle_exception(e, error_class=ConfigurationError, reraise=False)

    def discover_models(self) -> List[ModelInfo]:
    """
    Discover available models.

    Returns:
    List of discovered model info
    """
    discovered_models = []

    # Discover local models
    if "local" in self.config.model_sources:
    local_models = self._discover_local_models()
    discovered_models.extend(local_models)

    # Discover Hugging Face models
    if "huggingface" in self.config.model_sources and TRANSFORMERS_AVAILABLE:
    hf_models = self._discover_huggingface_models()
    discovered_models.extend(hf_models)

    # Add discovered models to registry
    for model in discovered_models:
    self.models[model.id] = model

    # Save the updated registry
    self._save_model_registry()

    return discovered_models

    def _discover_local_models(self) -> List[ModelInfo]:
    """
    Discover local models in the models directory.

    Returns:
    List of discovered model info

    Raises:
    ConfigurationError: If there's an issue with the models directory
    """
    discovered_models = []

    # Check if models directory exists
    if not os.path.exists(self.config.models_dir):
    error = ConfigurationError(
    message=f"Models directory {self.config.models_dir} does not exist",
    config_key="models_dir",
    )
    error.log(level=logging.WARNING)
    return discovered_models

    try:
    # Look for model files in the models directory
    for root, dirs, files in os.walk(self.config.models_dir):
    for file in files:
    file_path = os.path.join(root, file)

    # Skip registry file and other non-model files
    if file == "registry.json" or file.startswith("."):
    continue

    # Determine model type and format based on file extension
    model_type, model_format, quantization = self._detect_model_type(
    file_path
    )

    if model_type:
    # Generate a unique ID for the model
    model_id = hashlib.md5(file_path.encode()).hexdigest()

    # Create model info
    model_info = ModelInfo(
    id=model_id,
    name=os.path.basename(file_path),
    type=model_type,
    path=file_path,
    format=model_format,
    quantization=quantization,
    )

    discovered_models.append(model_info)
    logger.info(
    f"Discovered local model: {model_info.name} ({model_info.type})"
    )

    return discovered_models

except (IOError, OSError) as e:
    error = ConfigurationError(
    message=f"Error accessing models directory {self.config.models_dir}: {e}",
    config_key="models_dir",
    original_exception=e,
    )
    error.log()
    return discovered_models
except Exception as e:
    error = handle_exception(e, error_class=ConfigurationError, reraise=False)
    return discovered_models

    def _discover_huggingface_models(self) -> List[ModelInfo]:
    """
    Discover pre-installed Hugging Face models.

    Returns:
    List of discovered model info

    Raises:
    ModelError: If there's an issue with the Hugging Face models
    """
    discovered_models = []

    if not TRANSFORMERS_AVAILABLE:
    error = ModelError(
    message="Transformers not available. Cannot discover Hugging Face models.",
    code="transformers_not_available",
    )
    error.log(level=logging.WARNING)
    return discovered_models

    try:
    # Define a list of common small models for testing
    common_models = [
    {
    "name": "gpt2",
    "type": "text-generation",
    "description": "Small GPT-2 model for text generation",
    },
    {
    "name": "distilbert-base-uncased",
    "type": "text-classification",
    "description": "Small DistilBERT model for text classification",
    },
    {
    "name": "all-MiniLM-L6-v2",
    "type": "embedding",
    "description": "Small embedding model for text similarity",
    },
    ]

    for model_data in common_models:
    model_id = hashlib.md5(model_data["name"].encode()).hexdigest()

    model_info = ModelInfo(
    id=model_id,
    name=model_data["name"],
    type=model_data["type"],
    path=model_data[
    "name"
    ],  # For Hugging Face models, path is the model name
    description=model_data["description"],
    format="huggingface",
    )

    discovered_models.append(model_info)
    logger.info(
    f"Added Hugging Face model: {model_info.name} ({model_info.type})"
    )

    return discovered_models

except Exception as e:
    error = handle_exception(e, error_class=ModelError, reraise=False)
    return discovered_models

    def _detect_model_type(self, file_path: str) -> Tuple[str, str, str]:
    """
    Detect the type, format, and quantization of a model file.

    Args:
    file_path: Path to the model file

    Returns:
    Tuple of (model_type, model_format, quantization)
    """
    file_name = os.path.basename(file_path).lower()

    # Check for GGUF models (Llama)
    if file_name.endswith(".ggu"):
    quantization = "unknown"

    # Try to detect quantization from filename
    if "q4_k_m" in file_name:
    quantization = "4-bit"
    elif "q5_k_m" in file_name:
    quantization = "5-bit"
    elif "q8_0" in file_name:
    quantization = "8-bit"

    return "llama", "ggu", quantization

    # Check for ONNX models
    elif file_name.endswith(".onnx") or (
    os.path.isdir(file_path)
    and any(f.endswith(".onnx") for f in os.listdir(file_path))
    ):
    return "onnx", "onnx", "unknown"

    # Check for PyTorch models
    elif (
    file_name.endswith(".pt")
    or file_name.endswith(".pth")
    or file_name.endswith(".bin")
    ):
    return "pytorch", "pytorch", "unknown"

    # Check for TensorFlow models
    elif file_name.endswith(".pb") or (
    os.path.isdir(file_path)
    and any(f.endswith(".pb") for f in os.listdir(file_path))
    ):
    return "tensorflow", "tensorflow", "unknown"

    # Check for Hugging Face models (directory with config.json)
    elif os.path.isdir(file_path) and os.path.exists(
    os.path.join(file_path, "config.json")
    ):
    return "huggingface", "huggingface", "unknown"

    # Unknown model type
    return "", "", ""

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
    """
    Get information about a model.

    Args:
    model_id: ID of the model

    Returns:
    ModelInfo instance or None if not found
    """
    return self.models.get(model_id)

    def get_model_by_name(self, model_name: str) -> Optional[ModelInfo]:
    """
    Get a model by name.

    Args:
    model_name: Name of the model

    Returns:
    ModelInfo instance or None if not found
    """
    for model in self.models.values():
    if model.name == model_name:
    return model
    return None

    def get_models_by_type(self, model_type: str) -> List[ModelInfo]:
    """
    Get models by type.

    Args:
    model_type: Type of models to get

    Returns:
    List of ModelInfo instances
    """
    return [model for model in self.models.values() if model.type == model_type]

    def get_all_models(self) -> List[ModelInfo]:
    """
    Get all registered models.

    Returns:
    List of all ModelInfo instances
    """
    return list(self.models.values())

    def register_model(self, model_info: ModelInfo) -> None:
    """
    Register a new model.

    Args:
    model_info: Information about the model
    """
    with self.model_lock:
    self.models[model_info.id] = model_info
    self._save_model_registry()

    def unregister_model(self, model_id: str) -> bool:
    """
    Unregister a model.

    Args:
    model_id: ID of the model to unregister

    Returns:
    True if the model was unregistered, False otherwise
    """
    with self.model_lock:
    if model_id in self.models:
    del self.models[model_id]
    self._save_model_registry()
    return True
    return False

    def load_model(self, model_id: str, version: str = None, **kwargs) -> Any:
    """
    Load a model (synchronous version).

    This is a wrapper around load_model_async that runs the async function in the event loop.

    Args:
    model_id: ID of the model to load
    version: Optional version of the model to load
    **kwargs: Additional parameters for model loading

    Returns:
    Loaded model instance

    Raises:
    ModelNotFoundError: If the model is not found
    ModelLoadError: If the model cannot be loaded
    ValidationError: If the model type is not supported
    """
    # Check if the model is already loaded for quick return
    if model_id in self.loaded_models:
    return self.loaded_models[model_id]

    # If we're already in an event loop, use it
    try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
    return asyncio.run_coroutine_threadsafe(
    self.load_model_async(model_id, version, **kwargs), loop
    ).result()
    else:
    return loop.run_until_complete(
    self.load_model_async(model_id, version, **kwargs)
    )
    # If no event loop is available, create a new one
except RuntimeError:
    return asyncio.run(self.load_model_async(model_id, version, **kwargs))

    async def load_model_async(
    self, model_id: str, version: str = None, **kwargs
    ) -> Any:
    """
    Load a model asynchronously.

    Args:
    model_id: ID of the model to load
    version: Optional version of the model to load
    **kwargs: Additional parameters for model loading

    Returns:
    Loaded model instance

    Raises:
    ModelNotFoundError: If the model is not found
    ModelLoadError: If the model cannot be loaded
    ValidationError: If the model type is not supported
    """
    # If version is specified, use versioned model manager
    if version:
    try:
    # Run in a thread pool executor since versioned_manager's methods are synchronous
    return await asyncio.get_event_loop().run_in_executor(
    None,
    lambda: self.versioned_manager.load_model_version(
    model_id, version, **kwargs
    ),
    )
except ValueError as e:
    raise ModelNotFoundError(message=str(e), model_id=model_id)

    # Check if the model is already loaded
    if model_id in self.loaded_models:
    return self.loaded_models[model_id]

    # Get model info
    model_info = self.get_model_info(model_id)
    if not model_info:
    raise ModelNotFoundError(
    message=f"Model with ID {model_id} not found", model_id=model_id
    )

    # Load the model based on its type
    model = None

    try:
    if model_info.type == "huggingface":
    model = await self._load_huggingface_model_async(model_info, **kwargs)
    elif model_info.type == "llama":
    model = await self._load_llama_model_async(model_info, **kwargs)
    elif model_info.type == "embedding":
    model = await self._load_embedding_model_async(model_info, **kwargs)
    elif model_info.type == "onnx":
    model = await self._load_onnx_model_async(model_info, **kwargs)
    else:
    raise ValidationError(
    message=f"Unsupported model type: {model_info.type}",
    field="model_type",
    validation_errors=[
    {
    "field": "model_type",
    "value": model_info.type,
    "error": "Unsupported model type",
    }
    ],
    )

    # Store the loaded model
    self.loaded_models[model_id] = model

    return model

except ImportError as e:
    # Handle missing dependencies
    raise ModelLoadError(
    message=f"Missing dependency for loading model {model_info.name}: {e}",
    model_id=model_id,
    details={"dependency_error": str(e)},
    original_exception=e,
    )
except (ValidationError, ModelError):
    # Re-raise custom errors
    raise
except Exception as e:
    # Handle other errors
    logger.error(f"Error loading model {model_info.name}: {e}")
    raise ModelLoadError(
    message=f"Failed to load model {model_info.name}: {e}",
    model_id=model_id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    )

    async def _load_huggingface_model_async(
    self, model_info: ModelInfo, **kwargs
    ) -> Any:
    """
    Load a Hugging Face model asynchronously.

    Args:
    model_info: Information about the model
    **kwargs: Additional parameters for model loading

    Returns:
    Loaded model instance

    Raises:
    ModelLoadError: If the model cannot be loaded
    """
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    try:
    return await loop.run_in_executor(
    None, lambda: self._load_huggingface_model(model_info, **kwargs)
    )
except Exception as e:
    # Convert any exceptions to ModelLoadError
    logger.error(
    f"Error loading Hugging Face model {model_info.name} asynchronously: {e}"
    )
    raise ModelLoadError(
    message=f"Failed to load Hugging Face model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    )

    async def _load_llama_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    """
    Load a Llama model asynchronously.

    Args:
    model_info: Information about the model
    **kwargs: Additional parameters for model loading

    Returns:
    Loaded model instance

    Raises:
    ModelLoadError: If the model cannot be loaded
    """
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    try:
    return await loop.run_in_executor(
    None, lambda: self._load_llama_model(model_info, **kwargs)
    )
except Exception as e:
    logger.error(
    f"Error loading Llama model {model_info.name} asynchronously: {e}"
    )
    raise ModelLoadError(
    message=f"Failed to load Llama model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    )

    async def _load_embedding_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    """
    Load an embedding model asynchronously.

    Args:
    model_info: Information about the model
    **kwargs: Additional parameters for model loading

    Returns:
    Loaded model instance

    Raises:
    ModelLoadError: If the model cannot be loaded
    """
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    try:
    return await loop.run_in_executor(
    None, lambda: self._load_embedding_model(model_info, **kwargs)
    )
except Exception as e:
    logger.error(
    f"Error loading embedding model {model_info.name} asynchronously: {e}"
    )
    raise ModelLoadError(
    message=f"Failed to load embedding model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    )

    async def _load_onnx_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    """
    Load an ONNX model asynchronously.

    Args:
    model_info: Information about the model
    **kwargs: Additional parameters for model loading

    Returns:
    Loaded model instance

    Raises:
    ModelLoadError: If the model cannot be loaded
    """
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    try:
    return await loop.run_in_executor(
    None, lambda: self._load_onnx_model(model_info, **kwargs)
    )
except Exception as e:
    logger.error(
    f"Error loading ONNX model {model_info.name} asynchronously: {e}"
    )
    raise ModelLoadError(
    message=f"Failed to load ONNX model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    )

    def get_model_versions(self, model_id: str) -> List[ModelVersion]:
    """
    Get all versions of a model.

    Args:
    model_id: ID of the model

    Returns:
    List of ModelVersion instances sorted in descending order
    """
    return self.versioned_manager.get_all_model_versions(model_id)

    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
    """
    Get the latest version of a model.

    Args:
    model_id: ID of the model

    Returns:
    Latest ModelVersion instance or None if no versions exist
    """
    return self.versioned_manager.get_model_version(model_id)

    def get_model_provider(self, provider_type: str = "openai", **kwargs):
    """
    Get a model provider of the specified type.

    Args:
    provider_type: Type of provider to get (e.g., "openai", "huggingface")
    **kwargs: Additional parameters for the provider

    Returns:
    A model provider instance
    """
    (provider_type, kwargs.get("config"))

    def generate_text(self, prompt: str, model_id: str = "gpt-3.5-turbo", **kwargs):
    """
    Generate text using the specified model.

    Args:
    prompt: Text prompt to generate from
    model_id: ID of the model to use
    **kwargs: Additional parameters for text generation

    Returns:
    Generated text
    """
    provider = self.get_model_provider("openai")
    response = provider.create_chat_completion(
    model=model_id, messages=[{"role": "user", "content": prompt}], **kwargs
    )
    return response["choices"][0]["message"]["content"]

    def create_model_version(
    self,
    model_id: str,
    version: str,
    features: List[str] = None,
    dependencies: Dict[str, str] = None,
    compatibility: List[str] = None,
    metadata: Dict[str, Any] = None,
    ) -> ModelVersion:
    """
    Create a new version for a model.

    Args:
    model_id: ID of the model
    version: Version string (e.g., "1.0.0")
    features: Optional list of features this version supports
    dependencies: Optional dependencies required by this version
    compatibility: Optional list of other model versions this is compatible with
    metadata: Optional additional metadata for this version

    Returns:
    ModelVersion instance

    Raises:
    ModelNotFoundError: If the model is not found
    """
    # Get model info
    model_info = self.get_model_info(model_id)
    if not model_info:
    raise ModelNotFoundError(
    message=f"Model with ID {model_id} not found", model_id=model_id
    )

    # Create version
    version_obj = self.versioned_manager.register_model_version(
    model_info=model_info,
    version_str=version,
    features=features,
    dependencies=dependencies,
    compatibility=compatibility,
    metadata=metadata,
    )

    # Update model info with the new version
    model_info.set_version(version)

    return version_obj

    def check_version_compatibility(
    self, model_id1: str, version1: str, model_id2: str, version2: str
    ) -> bool:
    """
    Check if two model versions are compatible.

    Args:
    model_id1: ID of the first model
    version1: Version of the first model
    model_id2: ID of the second model
    version2: Version of the second model

    Returns:
    True if compatible, False otherwise
    """
    return self.versioned_manager.check_compatibility(
    model_id1, version1, model_id2, version2
    )

    def register_migration(
    self,
    model_id: str,
    source_version: str,
    target_version: str,
    migration_fn: Callable,
    ) -> None:
    """
    Register a migration function for version transitions.

    Args:
    model_id: ID of the model
    source_version: Source version string
    target_version: Target version string
    migration_fn: Function that handles the migration
    """
    self.versioned_manager.register_migration_function(
    model_id, source_version, target_version, migration_fn
    )

    def migrate_model(self, model_id: str, target_version: str, **kwargs) -> ModelInfo:
    """
    Migrate a model to a specific version.

    Args:
    model_id: ID of the model to migrate
    target_version: Target version string
    **kwargs: Additional parameters for the migration

    Returns:
    Updated ModelInfo instance

    Raises:
    ModelNotFoundError: If the model is not found
    ValueError: If migration is not possible
    """
    # Get model info
    model_info = self.get_model_info(model_id)
    if not model_info:
    raise ModelNotFoundError(
    message=f"Model with ID {model_id} not found", model_id=model_id
    )

    try:
    # Perform migration
    updated_info = self.versioned_manager.migrate_model(
    model_info, target_version, **kwargs
    )

    # Update model registry with the migrated model info
    self.models[model_id] = updated_info
    self._save_model_registry()

    return updated_info
except ValueError as e:
    logger.error(
    f"Error migrating model {model_id} to version {target_version}: {e}"
    )
    raise