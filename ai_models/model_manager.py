"""
Model manager for the AI Models module.

This module provides a central system for managing AI models, including
model discovery, loading, caching, and monitoring.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import platform
import shutil
import hashlib

from .model_config import ModelConfig
from typing import TYPE_CHECKING
import sys

# Add the project root to the Python path to import the errors module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from errors import (
    ModelError, ModelNotFoundError, ModelLoadError,
    ConfigurationError, ValidationError, handle_exception
)
from interfaces.model_interfaces import IModelInfo, IModelManager

# Import only for type checking to avoid circular imports
if TYPE_CHECKING:
    from .model_downloader import ModelDownloader, DownloadProgress
    from .performance_monitor import PerformanceMonitor, InferenceMetrics, ModelPerformanceReport

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available. GPU acceleration will be limited.")
    TORCH_AVAILABLE = False

try:
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Hugging Face models will not be available.")
    TRANSFORMERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Sentence Transformers not available. Embedding models will be limited.")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    logger.warning("llama-cpp-python not available. Llama model support will be limited.")
    LLAMA_CPP_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False


@dataclass
class ModelInfo(IModelInfo):
    """
    Information about an AI model.
    """
    _id: str
    _name: str
    _type: str  # huggingface, llama, embedding, etc.
    _path: str
    _description: str = ""
    size_mb: float = 0.0
    format: str = ""  # gguf, onnx, pytorch, etc.
    quantization: str = ""  # 4-bit, 8-bit, etc.
    capabilities: List[str] = None
    _metadata: Dict[str, Any] = None
    performance: Dict[str, Any] = None
    last_updated: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        path: str,
        description: str = "",
        size_mb: float = 0.0,
        format: str = "",
        quantization: str = "",
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None,
        performance: Dict[str, Any] = None,
        last_updated: str = "",
        created_at: str = "",
        updated_at: str = ""
    ):
        """Initialize a new ModelInfo object."""
        self._id = id
        self._name = name
        self._type = type
        self._path = path
        self._description = description
        self.size_mb = size_mb
        self.format = format
        self.quantization = quantization
        self.capabilities = capabilities if capabilities else []
        self._metadata = metadata if metadata else {}
        self.performance = performance if performance else {}
        self.last_updated = last_updated
        self.created_at = created_at
        self.updated_at = updated_at

        # Run post-initialization logic
        self.__post_init__()
    
    @property
    def id(self) -> str:
        """Get the model ID."""
        return self._id
    
    @property
    def name(self) -> str:
        """Get the model name."""
        return self._name
        
    @property
    def description(self) -> str:
        """Get the model description."""
        return self._description
        
    @property
    def type(self) -> str:
        """Get the model type."""
        return self._type
        
    @property
    def path(self) -> str:
        """Get the model path."""
        return self._path
        
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the model metadata."""
        return self._metadata if self._metadata is not None else {}

    def __post_init__(self):
        """
        Initialize default values after creation.
        """
        if self.capabilities is None:
            self.capabilities = []

        if self._metadata is None:
            self._metadata = {}

        if self.performance is None:
            self.performance = {}

        # Set timestamps if not provided
        current_time = time.strftime("%Y-%m-%dT%H:%M:%S")

        if not self.created_at:
            self.created_at = current_time

        if not self.updated_at:
            self.updated_at = current_time

        if not self.last_updated:
            self.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate size if path exists and size is not provided
        if self.size_mb == 0.0 and os.path.exists(self._path):
            try:
                self.size_mb = os.path.getsize(self._path) / (1024 * 1024)
            except (OSError, IOError):
                pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model info to a dictionary.

        Returns:
            Dictionary representation of the model info
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "description": self.description,
            "size_mb": self.size_mb,
            "format": self.format,
            "quantization": self.quantization,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "performance": self.performance,
            "last_updated": self.last_updated,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the model info to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the model info
        """
        return json.dumps(self.to_dict(), indent=indent)

    def update_performance(self, metrics: Dict[str, Any]) -> None:
        """
        Update performance metrics for the model.

        Args:
            metrics: Dictionary of performance metrics
        """
        if self.performance is None:
            self.performance = {}

        self.performance.update(metrics)
        self.update_timestamp()

    def update_timestamp(self) -> None:
        """
        Update the last_updated and updated_at timestamps.
        """
        self.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")

        # For compatibility with datetime.now().isoformat() in tests
        if hasattr(datetime, 'now'):
            self.updated_at = datetime.now().isoformat()

    def has_capability(self, capability: str) -> bool:
        """
        Check if the model has a specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if the model has the capability, False otherwise
        """
        return capability in self.capabilities

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':
        """
        Create a ModelInfo instance from a dictionary.

        Args:
            data: Dictionary containing model information

        Returns:
            ModelInfo instance
        """
        return cls(**data)


class ModelManager(IModelManager):
    """
    Central manager for AI models.
    """

    def __init__(self, config: Optional[ModelConfig] = None, performance_monitor: Optional['PerformanceMonitor'] = None):
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
                with open(registry_path, 'r') as f:
                    registry_data = json.load(f)

                for model_data in registry_data.get("models", []):
                    model_info = ModelInfo.from_dict(model_data)
                    self.models[model_info.id] = model_info

                logger.info(f"Loaded {len(self.models)} models from registry")
            except json.JSONDecodeError as e:
                error = ConfigurationError(
                    message=f"Invalid JSON format in model registry: {e}",
                    config_key="registry.json",
                    original_exception=e
                )
                error.log()
                # Create a new registry
                self._save_model_registry()
            except Exception as e:
                error = handle_exception(
                    e,
                    error_class=ConfigurationError,
                    reraise=False
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

            with open(registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2)

            logger.info(f"Saved {len(self.models)} models to registry")
        except (IOError, OSError) as e:
            error = ConfigurationError(
                message=f"Failed to write model registry to {registry_path}: {e}",
                config_key="models_dir",
                original_exception=e
            )
            error.log()
        except Exception as e:
            handle_exception(
                e,
                error_class=ConfigurationError,
                reraise=False
            )

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
                config_key="models_dir"
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
                    model_type, model_format, quantization = self._detect_model_type(file_path)

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
                            quantization=quantization
                        )

                        discovered_models.append(model_info)
                        logger.info(f"Discovered local model: {model_info.name} ({model_info.type})")

            return discovered_models

        except (IOError, OSError) as e:
            error = ConfigurationError(
                message=f"Error accessing models directory {self.config.models_dir}: {e}",
                config_key="models_dir",
                original_exception=e
            )
            error.log()
            return discovered_models
        except Exception as e:
            error = handle_exception(
                e,
                error_class=ConfigurationError,
                reraise=False
            )
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
                code="transformers_not_available"
            )
            error.log(level=logging.WARNING)
            return discovered_models

        try:
            # Define a list of common small models for testing
            common_models = [
                {"name": "gpt2", "type": "text-generation", "description": "Small GPT-2 model for text generation"},
                {"name": "distilbert-base-uncased", "type": "text-classification", "description": "Small DistilBERT model for text classification"},
                {"name": "all-MiniLM-L6-v2", "type": "embedding", "description": "Small embedding model for text similarity"}
            ]

            for model_data in common_models:
                model_id = hashlib.md5(model_data["name"].encode()).hexdigest()

                model_info = ModelInfo(
                    id=model_id,
                    name=model_data["name"],
                    type=model_data["type"],
                    path=model_data["name"],  # For Hugging Face models, path is the model name
                    description=model_data["description"],
                    format="huggingface"
                )

                discovered_models.append(model_info)
                logger.info(f"Added Hugging Face model: {model_info.name} ({model_info.type})")

            return discovered_models

        except Exception as e:
            error = handle_exception(
                e,
                error_class=ModelError,
                reraise=False
            )
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
        if file_name.endswith(".gguf"):
            quantization = "unknown"

            # Try to detect quantization from filename
            if "q4_k_m" in file_name:
                quantization = "4-bit"
            elif "q5_k_m" in file_name:
                quantization = "5-bit"
            elif "q8_0" in file_name:
                quantization = "8-bit"

            return "llama", "gguf", quantization

        # Check for ONNX models
        elif file_name.endswith(".onnx") or (os.path.isdir(file_path) and any(f.endswith(".onnx") for f in os.listdir(file_path))):
            return "onnx", "onnx", "unknown"

        # Check for PyTorch models
        elif file_name.endswith(".pt") or file_name.endswith(".pth") or file_name.endswith(".bin"):
            return "pytorch", "pytorch", "unknown"

        # Check for TensorFlow models
        elif file_name.endswith(".pb") or (os.path.isdir(file_path) and any(f.endswith(".pb") for f in os.listdir(file_path))):
            return "tensorflow", "tensorflow", "unknown"

        # Check for Hugging Face models (directory with config.json)
        elif os.path.isdir(file_path) and os.path.exists(os.path.join(file_path, "config.json")):
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

    def load_model(self, model_id: str, **kwargs) -> Any:
        """
        Load a model.

        Args:
            model_id: ID of the model to load
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model instance

        Raises:
            ModelNotFoundError: If the model is not found
            ModelLoadError: If the model cannot be loaded
            ValidationError: If the model type is not supported
        """
        # Check if the model is already loaded
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]

        # Get model info
        model_info = self.get_model_info(model_id)
        if not model_info:
            raise ModelNotFoundError(
                message=f"Model with ID {model_id} not found",
                model_id=model_id
            )

        # Load the model based on its type
        model = None

        try:
            if model_info.type == "huggingface":
                model = self._load_huggingface_model(model_info, **kwargs)
            elif model_info.type == "llama":
                model = self._load_llama_model(model_info, **kwargs)
            elif model_info.type == "embedding":
                model = self._load_embedding_model(model_info, **kwargs)
            elif model_info.type == "onnx":
                model = self._load_onnx_model(model_info, **kwargs)
            else:
                raise ValidationError(
                    message=f"Unsupported model type: {model_info.type}",
                    field="model_type",
                    validation_errors=[{
                        "field": "model_type",
                        "value": model_info.type,
                        "error": "Unsupported model type"
                    }]
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
                original_exception=e
            )
        except (ValidationError, ModelError) as e:
            # Re-raise custom errors
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"Error loading model {model_info.name}: {e}")
            raise ModelLoadError(
                message=f"Failed to load model {model_info.name}: {e}",
                model_id=model_id,
                details={"model_type": model_info.type, "model_path": model_info.path},
                original_exception=e
            )

    def _load_huggingface_model(self, model_info: ModelInfo, **kwargs) -> Any:
        """
        Load a Hugging Face model.

        Args:
            model_info: Information about the model
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model instance

        Raises:
            ModelLoadError: If the model cannot be loaded
            ImportError: If transformers is not available
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers not available. Please install it with: pip install transformers torch")

        logger.info(f"Loading Hugging Face model: {model_info.name}")

        # Determine device
        device = kwargs.get("device", self.config.default_device)
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Determine model type
        model_type = kwargs.get("model_type", "text-generation")

        try:
            # Create pipeline
            model = pipeline(
                model_type,
                model=model_info.path,
                device=device,
                **kwargs
            )

            logger.info(f"Successfully loaded model {model_info.name} on {device}")
            return model

        except Exception as e:
            logger.error(f"Error loading Hugging Face model {model_info.name}: {e}")
            raise ModelLoadError(
                message=f"Failed to load Hugging Face model {model_info.name}: {e}",
                model_id=model_info.id,
                details={
                    "model_type": model_type,
                    "device": device,
                    "path": model_info.path
                },
                original_exception=e
            )

    def _load_llama_model(self, model_info: ModelInfo, **kwargs) -> Any:
        """
        Load a Llama model.

        Args:
            model_info: Information about the model
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model instance

        Raises:
            ImportError: If llama-cpp-python is not available
            ValueError: If the model cannot be loaded
        """
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python not available. Please install it with: pip install llama-cpp-python")

        logger.info(f"Loading Llama model: {model_info.name}")

        # Get model parameters
        n_ctx = kwargs.get("n_ctx", 2048)
        n_threads = kwargs.get("n_threads", self.config.max_threads) or max(1, os.cpu_count() // 2)

        try:
            # Load the model
            model = Llama(
                model_path=model_info.path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                **kwargs
            )

            logger.info(f"Successfully loaded model {model_info.name}")
            return model

        except Exception as e:
            logger.error(f"Error loading Llama model {model_info.name}: {e}")
            raise ValueError(f"Failed to load Llama model {model_info.name}: {e}")

    def _load_embedding_model(self, model_info: ModelInfo, **kwargs) -> Any:
        """
        Load an embedding model.

        Args:
            model_info: Information about the model
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model instance

        Raises:
            ImportError: If sentence-transformers is not available
            ValueError: If the model cannot be loaded
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("Sentence Transformers not available. Please install it with: pip install sentence-transformers")

        logger.info(f"Loading embedding model: {model_info.name}")

        # Determine device
        device = kwargs.get("device", self.config.default_device)
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            # Load the model
            model = SentenceTransformer(model_info.path, device=device, **kwargs)

            logger.info(f"Successfully loaded model {model_info.name} on {device}")
            return model

        except Exception as e:
            logger.error(f"Error loading embedding model {model_info.name}: {e}")
            raise ValueError(f"Failed to load embedding model {model_info.name}: {e}")

    def _load_onnx_model(self, model_info: ModelInfo, **kwargs) -> Any:
        """
        Load an ONNX model.

        Args:
            model_info: Information about the model
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model instance

        Raises:
            ImportError: If onnxruntime is not available
            ValueError: If the model cannot be loaded
        """
        if not ONNX_AVAILABLE:
            raise ImportError("ONNX Runtime not available. Please install it with: pip install onnxruntime")

        logger.info(f"Loading ONNX model: {model_info.name}")

        try:
            # Create ONNX session
            session_options = ort.SessionOptions()

            # Set execution provider
            providers = kwargs.get("providers", None)
            if providers is None:
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if torch.cuda.is_available() else ["CPUExecutionProvider"]

            # Load the model
            session = ort.InferenceSession(model_info.path, sess_options=session_options, providers=providers)

            logger.info(f"Successfully loaded model {model_info.name}")
            return session

        except Exception as e:
            logger.error(f"Error loading ONNX model {model_info.name}: {e}")
            raise ValueError(f"Failed to load ONNX model {model_info.name}: {e}")

    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.

        Args:
            model_id: ID of the model to unload

        Returns:
            True if the model was unloaded, False otherwise
        """
        with self.model_lock:
            if model_id in self.loaded_models:
                # Remove the model from the loaded models dictionary
                del self.loaded_models[model_id]

                # Force garbage collection to free memory
                import gc
                gc.collect()

                if TORCH_AVAILABLE and torch.cuda.is_available():
                    torch.cuda.empty_cache()

                return True

            return False

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the system.

        Returns:
            Dictionary with system information
        """
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "memory_gb": None,
            "gpu_available": False,
            "gpu_info": []
        }

        # Get memory information
        try:
            import psutil
            memory = psutil.virtual_memory()
            system_info["memory_gb"] = round(memory.total / (1024 ** 3), 2)
        except ImportError:
            pass

        # Get GPU information
        if TORCH_AVAILABLE and torch.cuda.is_available():
            system_info["gpu_available"] = True
            system_info["gpu_count"] = torch.cuda.device_count()

            for i in range(torch.cuda.device_count()):
                gpu_info = {
                    "name": torch.cuda.get_device_name(i),
                    "memory_gb": round(torch.cuda.get_device_properties(i).total_memory / (1024 ** 3), 2)
                }
                system_info["gpu_info"].append(gpu_info)

        return system_info

    def get_dependencies_info(self) -> Dict[str, Any]:
        """
        Get information about installed dependencies.

        Returns:
            Dictionary with dependency information
        """
        dependencies = {
            "torch": {"installed": TORCH_AVAILABLE, "version": None},
            "transformers": {"installed": TRANSFORMERS_AVAILABLE, "version": None},
            "sentence_transformers": {"installed": SENTENCE_TRANSFORMERS_AVAILABLE, "version": None},
            "llama_cpp": {"installed": LLAMA_CPP_AVAILABLE, "version": None},
            "onnxruntime": {"installed": ONNX_AVAILABLE, "version": None}
        }

        # Get versions
        if TORCH_AVAILABLE:
            dependencies["torch"]["version"] = torch.__version__

        if TRANSFORMERS_AVAILABLE:
            dependencies["transformers"]["version"] = transformers.__version__

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            import sentence_transformers
            dependencies["sentence_transformers"]["version"] = sentence_transformers.__version__

        if LLAMA_CPP_AVAILABLE:
            import llama_cpp
            dependencies["llama_cpp"]["version"] = llama_cpp.__version__

        if ONNX_AVAILABLE:
            dependencies["onnxruntime"]["version"] = ort.__version__

        # Check for download dependencies
        try:
            import requests
            dependencies["requests"] = {"installed": True, "version": requests.__version__}
        except ImportError:
            dependencies["requests"] = {"installed": False, "version": None}

        try:
            import huggingface_hub
            dependencies["huggingface_hub"] = {"installed": True, "version": huggingface_hub.__version__}
        except ImportError:
            dependencies["huggingface_hub"] = {"installed": False, "version": None}

        try:
            import tqdm
            dependencies["tqdm"] = {"installed": True, "version": tqdm.__version__}
        except ImportError:
            dependencies["tqdm"] = {"installed": False, "version": None}

        return dependencies

    def register_downloaded_model(self, download_task: 'DownloadTask', model_type: str, description: str = "") -> Optional[ModelInfo]:
        """
        Register a model that was downloaded using the ModelDownloader.

        Args:
            download_task: Download task that completed successfully
            model_type: Type of the model
            description: Optional description of the model

        Returns:
            ModelInfo instance or None if registration failed
        """
        if download_task.progress.status != "completed":
            logger.error(f"Cannot register model from incomplete download task: {download_task.id}")
            return None

        # Generate a unique ID for the model
        model_id = hashlib.md5(f"{download_task.model_id}_{download_task.destination}".encode()).hexdigest()

        # Determine model format and quantization
        model_format = ""
        quantization = ""

        if model_type == "huggingface":
            model_format = "huggingface"
        elif model_type == "llama":
            model_format = "gguf"

            # Try to detect quantization from filename
            file_name = os.path.basename(download_task.destination).lower()
            if "q4_k_m" in file_name:
                quantization = "4-bit"
            elif "q5_k_m" in file_name:
                quantization = "5-bit"
            elif "q8_0" in file_name:
                quantization = "8-bit"

        # Create model info
        model_info = ModelInfo(
            id=model_id,
            name=os.path.basename(download_task.destination),
            type=model_type,
            path=download_task.destination,
            description=description,
            format=model_format,
            quantization=quantization
        )

        # Register the model
        self.register_model(model_info)

        return model_info

    def get_performance_monitor(self) -> Optional['PerformanceMonitor']:
        """
        Get the performance monitor.

        Returns:
            PerformanceMonitor instance or None if not set
        """
        return self.performance_monitor

    def set_performance_monitor(self, monitor: 'PerformanceMonitor') -> None:
        """
        Set the performance monitor.

        Args:
            monitor: PerformanceMonitor instance
        """
        self.performance_monitor = monitor

    def track_inference(
        self,
        model_id: str,
        input_tokens: int = 0,
        parameters: Dict[str, Any] = None
    ) -> Optional['InferenceTracker']:
        """
        Create an inference tracker for a model.

        Args:
            model_id: ID of the model
            input_tokens: Number of input tokens
            parameters: Additional parameters for the inference

        Returns:
            InferenceTracker instance or None if performance monitor is not set
        """
        if not self.performance_monitor:
            return None

        from .performance_monitor import InferenceTracker
        return InferenceTracker(
            monitor=self.performance_monitor,
            model_id=model_id,
            input_tokens=input_tokens,
            parameters=parameters
        )

    def generate_performance_report(self, model_id: str) -> Optional['ModelPerformanceReport']:
        """
        Generate a performance report for a model.

        Args:
            model_id: ID of the model

        Returns:
            ModelPerformanceReport instance or None if performance monitor is not set
        """
        if not self.performance_monitor:
            return None

        model_info = self.get_model_info(model_id)
        if not model_info:
            logger.error(f"Model with ID {model_id} not found")
            return None

        return self.performance_monitor.generate_performance_report(
            model_id=model_id,
            model_name=model_info.name
        )

    def get_model_performance_metrics(self, model_id: str) -> List['InferenceMetrics']:
        """
        Get performance metrics for a model.

        Args:
            model_id: ID of the model

        Returns:
            List of InferenceMetrics instances or empty list if performance monitor is not set
        """
        if not self.performance_monitor:
            return []

        return self.performance_monitor.get_model_metrics(model_id)
