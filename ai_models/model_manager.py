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
    """
    Model manager for the AI Models module.
    Model manager for the AI Models module.


    This module provides a central system for managing AI models, including
    This module provides a central system for managing AI models, including
    model discovery, loading, caching, and monitoring.
    model discovery, loading, caching, and monitoring.
    """
    """


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


    # Import only for type checking to avoid circular imports
    # Import only for type checking to avoid circular imports
    if TYPE_CHECKING:
    if TYPE_CHECKING:
    from .performance_monitor import PerformanceMonitor
    from .performance_monitor import PerformanceMonitor


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


    # Try to import optional dependencies
    # Try to import optional dependencies
    try:
    try:




    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("PyTorch not available. GPU acceleration will be limited.")
    logger.warning("PyTorch not available. GPU acceleration will be limited.")
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Transformers not available. Hugging Face models will not be available."
    "Transformers not available. Hugging Face models will not be available."
    )
    )
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Sentence Transformers not available. Embedding models will be limited."
    "Sentence Transformers not available. Embedding models will be limited."
    )
    )
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SENTENCE_TRANSFORMERS_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "llama-cpp-python not available. Llama model support will be limited."
    "llama-cpp-python not available. Llama model support will be limited."
    )
    )
    LLAMA_CPP_AVAILABLE = False
    LLAMA_CPP_AVAILABLE = False


    try:
    try:
    as ort
    as ort


    ONNX_AVAILABLE = True
    ONNX_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False
    ONNX_AVAILABLE = False




    class ModelManager(IModelManager):
    class ModelManager(IModelManager):
    """
    """
    Central manager for AI models.
    Central manager for AI models.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    config: Optional[ModelConfig] = None,
    config: Optional[ModelConfig] = None,
    performance_monitor: Optional["PerformanceMonitor"] = None,
    performance_monitor: Optional["PerformanceMonitor"] = None,
    ):
    ):
    """
    """
    Initialize the model manager.
    Initialize the model manager.


    Args:
    Args:
    config: Optional model configuration
    config: Optional model configuration
    performance_monitor: Optional performance monitor
    performance_monitor: Optional performance monitor
    """
    """
    self.config = config or ModelConfig.get_default()
    self.config = config or ModelConfig.get_default()
    self.models: Dict[str, ModelInfo] = {}
    self.models: Dict[str, ModelInfo] = {}
    self.loaded_models: Dict[str, Any] = {}
    self.loaded_models: Dict[str, Any] = {}
    self.model_lock = threading.Lock()
    self.model_lock = threading.Lock()
    self.performance_monitor = performance_monitor
    self.performance_monitor = performance_monitor


    # Create necessary directories
    # Create necessary directories
    os.makedirs(self.config.models_dir, exist_ok=True)
    os.makedirs(self.config.models_dir, exist_ok=True)
    os.makedirs(self.config.cache_dir, exist_ok=True)
    os.makedirs(self.config.cache_dir, exist_ok=True)


    # Initialize model registry
    # Initialize model registry
    self._init_model_registry()
    self._init_model_registry()


    # Initialize versioned model manager
    # Initialize versioned model manager
    self.versioned_manager = VersionedModelManager(self, self.config.models_dir)
    self.versioned_manager = VersionedModelManager(self, self.config.models_dir)


    # Discover models if auto-discover is enabled
    # Discover models if auto-discover is enabled
    if self.config.auto_discover:
    if self.config.auto_discover:
    self.discover_models()
    self.discover_models()


    def _init_model_registry(self) -> None:
    def _init_model_registry(self) -> None:
    """
    """
    Initialize the model registry.
    Initialize the model registry.
    """
    """
    registry_path = os.path.join(self.config.models_dir, "registry.json")
    registry_path = os.path.join(self.config.models_dir, "registry.json")


    if os.path.exists(registry_path):
    if os.path.exists(registry_path):
    try:
    try:
    with open(registry_path, "r") as f:
    with open(registry_path, "r") as f:
    registry_data = json.load(f)
    registry_data = json.load(f)


    for model_data in registry_data.get("models", []):
    for model_data in registry_data.get("models", []):
    model_info = ModelInfo.from_dict(model_data)
    model_info = ModelInfo.from_dict(model_data)
    self.models[model_info.id] = model_info
    self.models[model_info.id] = model_info


    logger.info(f"Loaded {len(self.models)} models from registry")
    logger.info(f"Loaded {len(self.models)} models from registry")
except json.JSONDecodeError as e:
except json.JSONDecodeError as e:
    error = ConfigurationError(
    error = ConfigurationError(
    message=f"Invalid JSON format in model registry: {e}",
    message=f"Invalid JSON format in model registry: {e}",
    config_key="registry.json",
    config_key="registry.json",
    original_exception=e,
    original_exception=e,
    )
    )
    error.log()
    error.log()
    # Create a new registry
    # Create a new registry
    self._save_model_registry()
    self._save_model_registry()
except Exception as e:
except Exception as e:
    error = handle_exception(
    error = handle_exception(
    e, error_class=ConfigurationError, reraise=False
    e, error_class=ConfigurationError, reraise=False
    )
    )
    # Create a new registry
    # Create a new registry
    self._save_model_registry()
    self._save_model_registry()
    else:
    else:
    # Create a new registry
    # Create a new registry
    self._save_model_registry()
    self._save_model_registry()


    def _save_model_registry(self) -> None:
    def _save_model_registry(self) -> None:
    """
    """
    Save the model registry to disk.
    Save the model registry to disk.
    """
    """
    registry_path = os.path.join(self.config.models_dir, "registry.json")
    registry_path = os.path.join(self.config.models_dir, "registry.json")


    try:
    try:
    registry_data = {
    registry_data = {
    "models": [model.to_dict() for model in self.models.values()]
    "models": [model.to_dict() for model in self.models.values()]
    }
    }


    with open(registry_path, "w") as f:
    with open(registry_path, "w") as f:
    json.dump(registry_data, f, indent=2)
    json.dump(registry_data, f, indent=2)


    logger.info(f"Saved {len(self.models)} models to registry")
    logger.info(f"Saved {len(self.models)} models to registry")
except (IOError, OSError) as e:
except (IOError, OSError) as e:
    error = ConfigurationError(
    error = ConfigurationError(
    message=f"Failed to write model registry to {registry_path}: {e}",
    message=f"Failed to write model registry to {registry_path}: {e}",
    config_key="models_dir",
    config_key="models_dir",
    original_exception=e,
    original_exception=e,
    )
    )
    error.log()
    error.log()
except Exception as e:
except Exception as e:
    handle_exception(e, error_class=ConfigurationError, reraise=False)
    handle_exception(e, error_class=ConfigurationError, reraise=False)


    def discover_models(self) -> List[ModelInfo]:
    def discover_models(self) -> List[ModelInfo]:
    """
    """
    Discover available models.
    Discover available models.


    Returns:
    Returns:
    List of discovered model info
    List of discovered model info
    """
    """
    discovered_models = []
    discovered_models = []


    # Discover local models
    # Discover local models
    if "local" in self.config.model_sources:
    if "local" in self.config.model_sources:
    local_models = self._discover_local_models()
    local_models = self._discover_local_models()
    discovered_models.extend(local_models)
    discovered_models.extend(local_models)


    # Discover Hugging Face models
    # Discover Hugging Face models
    if "huggingface" in self.config.model_sources and TRANSFORMERS_AVAILABLE:
    if "huggingface" in self.config.model_sources and TRANSFORMERS_AVAILABLE:
    hf_models = self._discover_huggingface_models()
    hf_models = self._discover_huggingface_models()
    discovered_models.extend(hf_models)
    discovered_models.extend(hf_models)


    # Add discovered models to registry
    # Add discovered models to registry
    for model in discovered_models:
    for model in discovered_models:
    self.models[model.id] = model
    self.models[model.id] = model


    # Save the updated registry
    # Save the updated registry
    self._save_model_registry()
    self._save_model_registry()


    return discovered_models
    return discovered_models


    def _discover_local_models(self) -> List[ModelInfo]:
    def _discover_local_models(self) -> List[ModelInfo]:
    """
    """
    Discover local models in the models directory.
    Discover local models in the models directory.


    Returns:
    Returns:
    List of discovered model info
    List of discovered model info


    Raises:
    Raises:
    ConfigurationError: If there's an issue with the models directory
    ConfigurationError: If there's an issue with the models directory
    """
    """
    discovered_models = []
    discovered_models = []


    # Check if models directory exists
    # Check if models directory exists
    if not os.path.exists(self.config.models_dir):
    if not os.path.exists(self.config.models_dir):
    error = ConfigurationError(
    error = ConfigurationError(
    message=f"Models directory {self.config.models_dir} does not exist",
    message=f"Models directory {self.config.models_dir} does not exist",
    config_key="models_dir",
    config_key="models_dir",
    )
    )
    error.log(level=logging.WARNING)
    error.log(level=logging.WARNING)
    return discovered_models
    return discovered_models


    try:
    try:
    # Look for model files in the models directory
    # Look for model files in the models directory
    for root, dirs, files in os.walk(self.config.models_dir):
    for root, dirs, files in os.walk(self.config.models_dir):
    for file in files:
    for file in files:
    file_path = os.path.join(root, file)
    file_path = os.path.join(root, file)


    # Skip registry file and other non-model files
    # Skip registry file and other non-model files
    if file == "registry.json" or file.startswith("."):
    if file == "registry.json" or file.startswith("."):
    continue
    continue


    # Determine model type and format based on file extension
    # Determine model type and format based on file extension
    model_type, model_format, quantization = self._detect_model_type(
    model_type, model_format, quantization = self._detect_model_type(
    file_path
    file_path
    )
    )


    if model_type:
    if model_type:
    # Generate a unique ID for the model
    # Generate a unique ID for the model
    model_id = hashlib.md5(file_path.encode()).hexdigest()
    model_id = hashlib.md5(file_path.encode()).hexdigest()


    # Create model info
    # Create model info
    model_info = ModelInfo(
    model_info = ModelInfo(
    id=model_id,
    id=model_id,
    name=os.path.basename(file_path),
    name=os.path.basename(file_path),
    type=model_type,
    type=model_type,
    path=file_path,
    path=file_path,
    format=model_format,
    format=model_format,
    quantization=quantization,
    quantization=quantization,
    )
    )


    discovered_models.append(model_info)
    discovered_models.append(model_info)
    logger.info(
    logger.info(
    f"Discovered local model: {model_info.name} ({model_info.type})"
    f"Discovered local model: {model_info.name} ({model_info.type})"
    )
    )


    return discovered_models
    return discovered_models


except (IOError, OSError) as e:
except (IOError, OSError) as e:
    error = ConfigurationError(
    error = ConfigurationError(
    message=f"Error accessing models directory {self.config.models_dir}: {e}",
    message=f"Error accessing models directory {self.config.models_dir}: {e}",
    config_key="models_dir",
    config_key="models_dir",
    original_exception=e,
    original_exception=e,
    )
    )
    error.log()
    error.log()
    return discovered_models
    return discovered_models
except Exception as e:
except Exception as e:
    error = handle_exception(e, error_class=ConfigurationError, reraise=False)
    error = handle_exception(e, error_class=ConfigurationError, reraise=False)
    return discovered_models
    return discovered_models


    def _discover_huggingface_models(self) -> List[ModelInfo]:
    def _discover_huggingface_models(self) -> List[ModelInfo]:
    """
    """
    Discover pre-installed Hugging Face models.
    Discover pre-installed Hugging Face models.


    Returns:
    Returns:
    List of discovered model info
    List of discovered model info


    Raises:
    Raises:
    ModelError: If there's an issue with the Hugging Face models
    ModelError: If there's an issue with the Hugging Face models
    """
    """
    discovered_models = []
    discovered_models = []


    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    error = ModelError(
    error = ModelError(
    message="Transformers not available. Cannot discover Hugging Face models.",
    message="Transformers not available. Cannot discover Hugging Face models.",
    code="transformers_not_available",
    code="transformers_not_available",
    )
    )
    error.log(level=logging.WARNING)
    error.log(level=logging.WARNING)
    return discovered_models
    return discovered_models


    try:
    try:
    # Define a list of common small models for testing
    # Define a list of common small models for testing
    common_models = [
    common_models = [
    {
    {
    "name": "gpt2",
    "name": "gpt2",
    "type": "text-generation",
    "type": "text-generation",
    "description": "Small GPT-2 model for text generation",
    "description": "Small GPT-2 model for text generation",
    },
    },
    {
    {
    "name": "distilbert-base-uncased",
    "name": "distilbert-base-uncased",
    "type": "text-classification",
    "type": "text-classification",
    "description": "Small DistilBERT model for text classification",
    "description": "Small DistilBERT model for text classification",
    },
    },
    {
    {
    "name": "all-MiniLM-L6-v2",
    "name": "all-MiniLM-L6-v2",
    "type": "embedding",
    "type": "embedding",
    "description": "Small embedding model for text similarity",
    "description": "Small embedding model for text similarity",
    },
    },
    ]
    ]


    for model_data in common_models:
    for model_data in common_models:
    model_id = hashlib.md5(model_data["name"].encode()).hexdigest()
    model_id = hashlib.md5(model_data["name"].encode()).hexdigest()


    model_info = ModelInfo(
    model_info = ModelInfo(
    id=model_id,
    id=model_id,
    name=model_data["name"],
    name=model_data["name"],
    type=model_data["type"],
    type=model_data["type"],
    path=model_data[
    path=model_data[
    "name"
    "name"
    ],  # For Hugging Face models, path is the model name
    ],  # For Hugging Face models, path is the model name
    description=model_data["description"],
    description=model_data["description"],
    format="huggingface",
    format="huggingface",
    )
    )


    discovered_models.append(model_info)
    discovered_models.append(model_info)
    logger.info(
    logger.info(
    f"Added Hugging Face model: {model_info.name} ({model_info.type})"
    f"Added Hugging Face model: {model_info.name} ({model_info.type})"
    )
    )


    return discovered_models
    return discovered_models


except Exception as e:
except Exception as e:
    error = handle_exception(e, error_class=ModelError, reraise=False)
    error = handle_exception(e, error_class=ModelError, reraise=False)
    return discovered_models
    return discovered_models


    def _detect_model_type(self, file_path: str) -> Tuple[str, str, str]:
    def _detect_model_type(self, file_path: str) -> Tuple[str, str, str]:
    """
    """
    Detect the type, format, and quantization of a model file.
    Detect the type, format, and quantization of a model file.


    Args:
    Args:
    file_path: Path to the model file
    file_path: Path to the model file


    Returns:
    Returns:
    Tuple of (model_type, model_format, quantization)
    Tuple of (model_type, model_format, quantization)
    """
    """
    file_name = os.path.basename(file_path).lower()
    file_name = os.path.basename(file_path).lower()


    # Check for GGUF models (Llama)
    # Check for GGUF models (Llama)
    if file_name.endswith(".ggu"):
    if file_name.endswith(".ggu"):
    quantization = "unknown"
    quantization = "unknown"


    # Try to detect quantization from filename
    # Try to detect quantization from filename
    if "q4_k_m" in file_name:
    if "q4_k_m" in file_name:
    quantization = "4-bit"
    quantization = "4-bit"
    elif "q5_k_m" in file_name:
    elif "q5_k_m" in file_name:
    quantization = "5-bit"
    quantization = "5-bit"
    elif "q8_0" in file_name:
    elif "q8_0" in file_name:
    quantization = "8-bit"
    quantization = "8-bit"


    return "llama", "ggu", quantization
    return "llama", "ggu", quantization


    # Check for ONNX models
    # Check for ONNX models
    elif file_name.endswith(".onnx") or (
    elif file_name.endswith(".onnx") or (
    os.path.isdir(file_path)
    os.path.isdir(file_path)
    and any(f.endswith(".onnx") for f in os.listdir(file_path))
    and any(f.endswith(".onnx") for f in os.listdir(file_path))
    ):
    ):
    return "onnx", "onnx", "unknown"
    return "onnx", "onnx", "unknown"


    # Check for PyTorch models
    # Check for PyTorch models
    elif (
    elif (
    file_name.endswith(".pt")
    file_name.endswith(".pt")
    or file_name.endswith(".pth")
    or file_name.endswith(".pth")
    or file_name.endswith(".bin")
    or file_name.endswith(".bin")
    ):
    ):
    return "pytorch", "pytorch", "unknown"
    return "pytorch", "pytorch", "unknown"


    # Check for TensorFlow models
    # Check for TensorFlow models
    elif file_name.endswith(".pb") or (
    elif file_name.endswith(".pb") or (
    os.path.isdir(file_path)
    os.path.isdir(file_path)
    and any(f.endswith(".pb") for f in os.listdir(file_path))
    and any(f.endswith(".pb") for f in os.listdir(file_path))
    ):
    ):
    return "tensorflow", "tensorflow", "unknown"
    return "tensorflow", "tensorflow", "unknown"


    # Check for Hugging Face models (directory with config.json)
    # Check for Hugging Face models (directory with config.json)
    elif os.path.isdir(file_path) and os.path.exists(
    elif os.path.isdir(file_path) and os.path.exists(
    os.path.join(file_path, "config.json")
    os.path.join(file_path, "config.json")
    ):
    ):
    return "huggingface", "huggingface", "unknown"
    return "huggingface", "huggingface", "unknown"


    # Unknown model type
    # Unknown model type
    return "", "", ""
    return "", "", ""


    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
    """
    """
    Get information about a model.
    Get information about a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    ModelInfo instance or None if not found
    ModelInfo instance or None if not found
    """
    """
    return self.models.get(model_id)
    return self.models.get(model_id)


    def get_model_by_name(self, model_name: str) -> Optional[ModelInfo]:
    def get_model_by_name(self, model_name: str) -> Optional[ModelInfo]:
    """
    """
    Get a model by name.
    Get a model by name.


    Args:
    Args:
    model_name: Name of the model
    model_name: Name of the model


    Returns:
    Returns:
    ModelInfo instance or None if not found
    ModelInfo instance or None if not found
    """
    """
    for model in self.models.values():
    for model in self.models.values():
    if model.name == model_name:
    if model.name == model_name:
    return model
    return model
    return None
    return None


    def get_models_by_type(self, model_type: str) -> List[ModelInfo]:
    def get_models_by_type(self, model_type: str) -> List[ModelInfo]:
    """
    """
    Get models by type.
    Get models by type.


    Args:
    Args:
    model_type: Type of models to get
    model_type: Type of models to get


    Returns:
    Returns:
    List of ModelInfo instances
    List of ModelInfo instances
    """
    """
    return [model for model in self.models.values() if model.type == model_type]
    return [model for model in self.models.values() if model.type == model_type]


    def get_all_models(self) -> List[ModelInfo]:
    def get_all_models(self) -> List[ModelInfo]:
    """
    """
    Get all registered models.
    Get all registered models.


    Returns:
    Returns:
    List of all ModelInfo instances
    List of all ModelInfo instances
    """
    """
    return list(self.models.values())
    return list(self.models.values())


    def register_model(self, model_info: ModelInfo) -> None:
    def register_model(self, model_info: ModelInfo) -> None:
    """
    """
    Register a new model.
    Register a new model.


    Args:
    Args:
    model_info: Information about the model
    model_info: Information about the model
    """
    """
    with self.model_lock:
    with self.model_lock:
    self.models[model_info.id] = model_info
    self.models[model_info.id] = model_info
    self._save_model_registry()
    self._save_model_registry()


    def unregister_model(self, model_id: str) -> bool:
    def unregister_model(self, model_id: str) -> bool:
    """
    """
    Unregister a model.
    Unregister a model.


    Args:
    Args:
    model_id: ID of the model to unregister
    model_id: ID of the model to unregister


    Returns:
    Returns:
    True if the model was unregistered, False otherwise
    True if the model was unregistered, False otherwise
    """
    """
    with self.model_lock:
    with self.model_lock:
    if model_id in self.models:
    if model_id in self.models:
    del self.models[model_id]
    del self.models[model_id]
    self._save_model_registry()
    self._save_model_registry()
    return True
    return True
    return False
    return False


    def load_model(self, model_id: str, version: str = None, **kwargs) -> Any:
    def load_model(self, model_id: str, version: str = None, **kwargs) -> Any:
    """
    """
    Load a model (synchronous version).
    Load a model (synchronous version).


    This is a wrapper around load_model_async that runs the async function in the event loop.
    This is a wrapper around load_model_async that runs the async function in the event loop.


    Args:
    Args:
    model_id: ID of the model to load
    model_id: ID of the model to load
    version: Optional version of the model to load
    version: Optional version of the model to load
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ModelNotFoundError: If the model is not found
    ModelNotFoundError: If the model is not found
    ModelLoadError: If the model cannot be loaded
    ModelLoadError: If the model cannot be loaded
    ValidationError: If the model type is not supported
    ValidationError: If the model type is not supported
    """
    """
    # Check if the model is already loaded for quick return
    # Check if the model is already loaded for quick return
    if model_id in self.loaded_models:
    if model_id in self.loaded_models:
    return self.loaded_models[model_id]
    return self.loaded_models[model_id]


    # If we're already in an event loop, use it
    # If we're already in an event loop, use it
    try:
    try:
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    if loop.is_running():
    if loop.is_running():
    return asyncio.run_coroutine_threadsafe(
    return asyncio.run_coroutine_threadsafe(
    self.load_model_async(model_id, version, **kwargs), loop
    self.load_model_async(model_id, version, **kwargs), loop
    ).result()
    ).result()
    else:
    else:
    return loop.run_until_complete(
    return loop.run_until_complete(
    self.load_model_async(model_id, version, **kwargs)
    self.load_model_async(model_id, version, **kwargs)
    )
    )
    # If no event loop is available, create a new one
    # If no event loop is available, create a new one
except RuntimeError:
except RuntimeError:
    return asyncio.run(self.load_model_async(model_id, version, **kwargs))
    return asyncio.run(self.load_model_async(model_id, version, **kwargs))


    async def load_model_async(
    async def load_model_async(
    self, model_id: str, version: str = None, **kwargs
    self, model_id: str, version: str = None, **kwargs
    ) -> Any:
    ) -> Any:
    """
    """
    Load a model asynchronously.
    Load a model asynchronously.


    Args:
    Args:
    model_id: ID of the model to load
    model_id: ID of the model to load
    version: Optional version of the model to load
    version: Optional version of the model to load
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ModelNotFoundError: If the model is not found
    ModelNotFoundError: If the model is not found
    ModelLoadError: If the model cannot be loaded
    ModelLoadError: If the model cannot be loaded
    ValidationError: If the model type is not supported
    ValidationError: If the model type is not supported
    """
    """
    # If version is specified, use versioned model manager
    # If version is specified, use versioned model manager
    if version:
    if version:
    try:
    try:
    # Run in a thread pool executor since versioned_manager's methods are synchronous
    # Run in a thread pool executor since versioned_manager's methods are synchronous
    return await asyncio.get_event_loop().run_in_executor(
    return await asyncio.get_event_loop().run_in_executor(
    None,
    None,
    lambda: self.versioned_manager.load_model_version(
    lambda: self.versioned_manager.load_model_version(
    model_id, version, **kwargs
    model_id, version, **kwargs
    ),
    ),
    )
    )
except ValueError as e:
except ValueError as e:
    raise ModelNotFoundError(message=str(e), model_id=model_id)
    raise ModelNotFoundError(message=str(e), model_id=model_id)


    # Check if the model is already loaded
    # Check if the model is already loaded
    if model_id in self.loaded_models:
    if model_id in self.loaded_models:
    return self.loaded_models[model_id]
    return self.loaded_models[model_id]


    # Get model info
    # Get model info
    model_info = self.get_model_info(model_id)
    model_info = self.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ModelNotFoundError(
    raise ModelNotFoundError(
    message=f"Model with ID {model_id} not found", model_id=model_id
    message=f"Model with ID {model_id} not found", model_id=model_id
    )
    )


    # Load the model based on its type
    # Load the model based on its type
    model = None
    model = None


    try:
    try:
    if model_info.type == "huggingface":
    if model_info.type == "huggingface":
    model = await self._load_huggingface_model_async(model_info, **kwargs)
    model = await self._load_huggingface_model_async(model_info, **kwargs)
    elif model_info.type == "llama":
    elif model_info.type == "llama":
    model = await self._load_llama_model_async(model_info, **kwargs)
    model = await self._load_llama_model_async(model_info, **kwargs)
    elif model_info.type == "embedding":
    elif model_info.type == "embedding":
    model = await self._load_embedding_model_async(model_info, **kwargs)
    model = await self._load_embedding_model_async(model_info, **kwargs)
    elif model_info.type == "onnx":
    elif model_info.type == "onnx":
    model = await self._load_onnx_model_async(model_info, **kwargs)
    model = await self._load_onnx_model_async(model_info, **kwargs)
    else:
    else:
    raise ValidationError(
    raise ValidationError(
    message=f"Unsupported model type: {model_info.type}",
    message=f"Unsupported model type: {model_info.type}",
    field="model_type",
    field="model_type",
    validation_errors=[
    validation_errors=[
    {
    {
    "field": "model_type",
    "field": "model_type",
    "value": model_info.type,
    "value": model_info.type,
    "error": "Unsupported model type",
    "error": "Unsupported model type",
    }
    }
    ],
    ],
    )
    )


    # Store the loaded model
    # Store the loaded model
    self.loaded_models[model_id] = model
    self.loaded_models[model_id] = model


    return model
    return model


except ImportError as e:
except ImportError as e:
    # Handle missing dependencies
    # Handle missing dependencies
    raise ModelLoadError(
    raise ModelLoadError(
    message=f"Missing dependency for loading model {model_info.name}: {e}",
    message=f"Missing dependency for loading model {model_info.name}: {e}",
    model_id=model_id,
    model_id=model_id,
    details={"dependency_error": str(e)},
    details={"dependency_error": str(e)},
    original_exception=e,
    original_exception=e,
    )
    )
except (ValidationError, ModelError):
except (ValidationError, ModelError):
    # Re-raise custom errors
    # Re-raise custom errors
    raise
    raise
except Exception as e:
except Exception as e:
    # Handle other errors
    # Handle other errors
    logger.error(f"Error loading model {model_info.name}: {e}")
    logger.error(f"Error loading model {model_info.name}: {e}")
    raise ModelLoadError(
    raise ModelLoadError(
    message=f"Failed to load model {model_info.name}: {e}",
    message=f"Failed to load model {model_info.name}: {e}",
    model_id=model_id,
    model_id=model_id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    original_exception=e,
    )
    )


    async def _load_huggingface_model_async(
    async def _load_huggingface_model_async(
    self, model_info: ModelInfo, **kwargs
    self, model_info: ModelInfo, **kwargs
    ) -> Any:
    ) -> Any:
    """
    """
    Load a Hugging Face model asynchronously.
    Load a Hugging Face model asynchronously.


    Args:
    Args:
    model_info: Information about the model
    model_info: Information about the model
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ModelLoadError: If the model cannot be loaded
    ModelLoadError: If the model cannot be loaded
    """
    """
    # Run the CPU-intensive model loading in a thread pool
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    try:
    try:
    return await loop.run_in_executor(
    return await loop.run_in_executor(
    None, lambda: self._load_huggingface_model(model_info, **kwargs)
    None, lambda: self._load_huggingface_model(model_info, **kwargs)
    )
    )
except Exception as e:
except Exception as e:
    # Convert any exceptions to ModelLoadError
    # Convert any exceptions to ModelLoadError
    logger.error(
    logger.error(
    f"Error loading Hugging Face model {model_info.name} asynchronously: {e}"
    f"Error loading Hugging Face model {model_info.name} asynchronously: {e}"
    )
    )
    raise ModelLoadError(
    raise ModelLoadError(
    message=f"Failed to load Hugging Face model {model_info.name} asynchronously: {e}",
    message=f"Failed to load Hugging Face model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    original_exception=e,
    )
    )


    async def _load_llama_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    async def _load_llama_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    """
    """
    Load a Llama model asynchronously.
    Load a Llama model asynchronously.


    Args:
    Args:
    model_info: Information about the model
    model_info: Information about the model
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ModelLoadError: If the model cannot be loaded
    ModelLoadError: If the model cannot be loaded
    """
    """
    # Run the CPU-intensive model loading in a thread pool
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    try:
    try:
    return await loop.run_in_executor(
    return await loop.run_in_executor(
    None, lambda: self._load_llama_model(model_info, **kwargs)
    None, lambda: self._load_llama_model(model_info, **kwargs)
    )
    )
except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error loading Llama model {model_info.name} asynchronously: {e}"
    f"Error loading Llama model {model_info.name} asynchronously: {e}"
    )
    )
    raise ModelLoadError(
    raise ModelLoadError(
    message=f"Failed to load Llama model {model_info.name} asynchronously: {e}",
    message=f"Failed to load Llama model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    original_exception=e,
    )
    )


    async def _load_embedding_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    async def _load_embedding_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    """
    """
    Load an embedding model asynchronously.
    Load an embedding model asynchronously.


    Args:
    Args:
    model_info: Information about the model
    model_info: Information about the model
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ModelLoadError: If the model cannot be loaded
    ModelLoadError: If the model cannot be loaded
    """
    """
    # Run the CPU-intensive model loading in a thread pool
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    try:
    try:
    return await loop.run_in_executor(
    return await loop.run_in_executor(
    None, lambda: self._load_embedding_model(model_info, **kwargs)
    None, lambda: self._load_embedding_model(model_info, **kwargs)
    )
    )
except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error loading embedding model {model_info.name} asynchronously: {e}"
    f"Error loading embedding model {model_info.name} asynchronously: {e}"
    )
    )
    raise ModelLoadError(
    raise ModelLoadError(
    message=f"Failed to load embedding model {model_info.name} asynchronously: {e}",
    message=f"Failed to load embedding model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    original_exception=e,
    )
    )


    async def _load_onnx_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    async def _load_onnx_model_async(self, model_info: ModelInfo, **kwargs) -> Any:
    """
    """
    Load an ONNX model asynchronously.
    Load an ONNX model asynchronously.


    Args:
    Args:
    model_info: Information about the model
    model_info: Information about the model
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    Loaded model instance
    Loaded model instance


    Raises:
    Raises:
    ModelLoadError: If the model cannot be loaded
    ModelLoadError: If the model cannot be loaded
    """
    """
    # Run the CPU-intensive model loading in a thread pool
    # Run the CPU-intensive model loading in a thread pool
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    try:
    try:
    return await loop.run_in_executor(
    return await loop.run_in_executor(
    None, lambda: self._load_onnx_model(model_info, **kwargs)
    None, lambda: self._load_onnx_model(model_info, **kwargs)
    )
    )
except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error loading ONNX model {model_info.name} asynchronously: {e}"
    f"Error loading ONNX model {model_info.name} asynchronously: {e}"
    )
    )
    raise ModelLoadError(
    raise ModelLoadError(
    message=f"Failed to load ONNX model {model_info.name} asynchronously: {e}",
    message=f"Failed to load ONNX model {model_info.name} asynchronously: {e}",
    model_id=model_info.id,
    model_id=model_info.id,
    details={"model_type": model_info.type, "model_path": model_info.path},
    details={"model_type": model_info.type, "model_path": model_info.path},
    original_exception=e,
    original_exception=e,
    )
    )


    def get_model_versions(self, model_id: str) -> List[ModelVersion]:
    def get_model_versions(self, model_id: str) -> List[ModelVersion]:
    """
    """
    Get all versions of a model.
    Get all versions of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    List of ModelVersion instances sorted in descending order
    List of ModelVersion instances sorted in descending order
    """
    """
    return self.versioned_manager.get_all_model_versions(model_id)
    return self.versioned_manager.get_all_model_versions(model_id)


    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
    """
    """
    Get the latest version of a model.
    Get the latest version of a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model


    Returns:
    Returns:
    Latest ModelVersion instance or None if no versions exist
    Latest ModelVersion instance or None if no versions exist
    """
    """
    return self.versioned_manager.get_model_version(model_id)
    return self.versioned_manager.get_model_version(model_id)


    def get_model_provider(self, provider_type: str = "openai", **kwargs):
    def get_model_provider(self, provider_type: str = "openai", **kwargs):
    """
    """
    Get a model provider of the specified type.
    Get a model provider of the specified type.


    Args:
    Args:
    provider_type: Type of provider to get (e.g., "openai", "huggingface")
    provider_type: Type of provider to get (e.g., "openai", "huggingface")
    **kwargs: Additional parameters for the provider
    **kwargs: Additional parameters for the provider


    Returns:
    Returns:
    A model provider instance
    A model provider instance
    """
    """
    (provider_type, kwargs.get("config"))
    (provider_type, kwargs.get("config"))


    def generate_text(self, prompt: str, model_id: str = "gpt-3.5-turbo", **kwargs):
    def generate_text(self, prompt: str, model_id: str = "gpt-3.5-turbo", **kwargs):
    """
    """
    Generate text using the specified model.
    Generate text using the specified model.


    Args:
    Args:
    prompt: Text prompt to generate from
    prompt: Text prompt to generate from
    model_id: ID of the model to use
    model_id: ID of the model to use
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    provider = self.get_model_provider("openai")
    provider = self.get_model_provider("openai")
    response = provider.create_chat_completion(
    response = provider.create_chat_completion(
    model=model_id, messages=[{"role": "user", "content": prompt}], **kwargs
    model=model_id, messages=[{"role": "user", "content": prompt}], **kwargs
    )
    )
    return response["choices"][0]["message"]["content"]
    return response["choices"][0]["message"]["content"]


    def create_model_version(
    def create_model_version(
    self,
    self,
    model_id: str,
    model_id: str,
    version: str,
    version: str,
    features: List[str] = None,
    features: List[str] = None,
    dependencies: Dict[str, str] = None,
    dependencies: Dict[str, str] = None,
    compatibility: List[str] = None,
    compatibility: List[str] = None,
    metadata: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None,
    ) -> ModelVersion:
    ) -> ModelVersion:
    """
    """
    Create a new version for a model.
    Create a new version for a model.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    version: Version string (e.g., "1.0.0")
    version: Version string (e.g., "1.0.0")
    features: Optional list of features this version supports
    features: Optional list of features this version supports
    dependencies: Optional dependencies required by this version
    dependencies: Optional dependencies required by this version
    compatibility: Optional list of other model versions this is compatible with
    compatibility: Optional list of other model versions this is compatible with
    metadata: Optional additional metadata for this version
    metadata: Optional additional metadata for this version


    Returns:
    Returns:
    ModelVersion instance
    ModelVersion instance


    Raises:
    Raises:
    ModelNotFoundError: If the model is not found
    ModelNotFoundError: If the model is not found
    """
    """
    # Get model info
    # Get model info
    model_info = self.get_model_info(model_id)
    model_info = self.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ModelNotFoundError(
    raise ModelNotFoundError(
    message=f"Model with ID {model_id} not found", model_id=model_id
    message=f"Model with ID {model_id} not found", model_id=model_id
    )
    )


    # Create version
    # Create version
    version_obj = self.versioned_manager.register_model_version(
    version_obj = self.versioned_manager.register_model_version(
    model_info=model_info,
    model_info=model_info,
    version_str=version,
    version_str=version,
    features=features,
    features=features,
    dependencies=dependencies,
    dependencies=dependencies,
    compatibility=compatibility,
    compatibility=compatibility,
    metadata=metadata,
    metadata=metadata,
    )
    )


    # Update model info with the new version
    # Update model info with the new version
    model_info.set_version(version)
    model_info.set_version(version)


    return version_obj
    return version_obj


    def check_version_compatibility(
    def check_version_compatibility(
    self, model_id1: str, version1: str, model_id2: str, version2: str
    self, model_id1: str, version1: str, model_id2: str, version2: str
    ) -> bool:
    ) -> bool:
    """
    """
    Check if two model versions are compatible.
    Check if two model versions are compatible.


    Args:
    Args:
    model_id1: ID of the first model
    model_id1: ID of the first model
    version1: Version of the first model
    version1: Version of the first model
    model_id2: ID of the second model
    model_id2: ID of the second model
    version2: Version of the second model
    version2: Version of the second model


    Returns:
    Returns:
    True if compatible, False otherwise
    True if compatible, False otherwise
    """
    """
    return self.versioned_manager.check_compatibility(
    return self.versioned_manager.check_compatibility(
    model_id1, version1, model_id2, version2
    model_id1, version1, model_id2, version2
    )
    )


    def register_migration(
    def register_migration(
    self,
    self,
    model_id: str,
    model_id: str,
    source_version: str,
    source_version: str,
    target_version: str,
    target_version: str,
    migration_fn: Callable,
    migration_fn: Callable,
    ) -> None:
    ) -> None:
    """
    """
    Register a migration function for version transitions.
    Register a migration function for version transitions.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    source_version: Source version string
    source_version: Source version string
    target_version: Target version string
    target_version: Target version string
    migration_fn: Function that handles the migration
    migration_fn: Function that handles the migration
    """
    """
    self.versioned_manager.register_migration_function(
    self.versioned_manager.register_migration_function(
    model_id, source_version, target_version, migration_fn
    model_id, source_version, target_version, migration_fn
    )
    )


    def migrate_model(self, model_id: str, target_version: str, **kwargs) -> ModelInfo:
    def migrate_model(self, model_id: str, target_version: str, **kwargs) -> ModelInfo:
    """
    """
    Migrate a model to a specific version.
    Migrate a model to a specific version.


    Args:
    Args:
    model_id: ID of the model to migrate
    model_id: ID of the model to migrate
    target_version: Target version string
    target_version: Target version string
    **kwargs: Additional parameters for the migration
    **kwargs: Additional parameters for the migration


    Returns:
    Returns:
    Updated ModelInfo instance
    Updated ModelInfo instance


    Raises:
    Raises:
    ModelNotFoundError: If the model is not found
    ModelNotFoundError: If the model is not found
    ValueError: If migration is not possible
    ValueError: If migration is not possible
    """
    """
    # Get model info
    # Get model info
    model_info = self.get_model_info(model_id)
    model_info = self.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ModelNotFoundError(
    raise ModelNotFoundError(
    message=f"Model with ID {model_id} not found", model_id=model_id
    message=f"Model with ID {model_id} not found", model_id=model_id
    )
    )


    try:
    try:
    # Perform migration
    # Perform migration
    updated_info = self.versioned_manager.migrate_model(
    updated_info = self.versioned_manager.migrate_model(
    model_info, target_version, **kwargs
    model_info, target_version, **kwargs
    )
    )


    # Update model registry with the migrated model info
    # Update model registry with the migrated model info
    self.models[model_id] = updated_info
    self.models[model_id] = updated_info
    self._save_model_registry()
    self._save_model_registry()


    return updated_info
    return updated_info
except ValueError as e:
except ValueError as e:
    logger.error(
    logger.error(
    f"Error migrating model {model_id} to version {target_version}: {e}"
    f"Error migrating model {model_id} to version {target_version}: {e}"
    )
    )
    raise
    raise