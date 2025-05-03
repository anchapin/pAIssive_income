"""Model manager module for handling AI model loading and configuration."""

import asyncio
import logging
import os
import re
import stat
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Union

from errors import ModelError, ModelLoadError, SecurityError
from interfaces.model_interfaces import IModelConfig, IModelManager

from .adapters import (
    AdapterFactory,
    BaseModelAdapter,
    LMStudioAdapter,
)
from .model_base_types import ModelInfo
from .model_config import ModelConfig
from .model_downloader import ModelDownloader

# Set up logging with secure defaults
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "logs", "model_manager.log"),
            mode="a",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ModelManager(IModelManager):
    """Manages AI model loading, caching, and inference with security features."""

    def __init__(self, config: IModelConfig):
        """Initialize the model manager with secure defaults."""
        self._config = config
        self._models_dir = config.models_dir
        self._cache_dir = config.cache_dir
        self._model_downloader = ModelDownloader(self._models_dir, config)
        self.loaded_models: Dict[str, BaseModelAdapter] = {}

        # Lock for thread safety
        self._model_lock = threading.RLock()

        # Create necessary directories with secure permissions
        try:
            self._create_secure_directory(self._models_dir)
            self._create_secure_directory(self._cache_dir)
            self._create_secure_directory(os.path.join(os.path.dirname(__file__), "logs"))
        except OSError as e:
            raise SecurityError(f"Failed to create secure directories: {e}")

        self._discover_models()

    def _create_secure_directory(self, path: str) -> None:
        """Create directory with secure permissions."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(path, mode=0o750, exist_ok=True)

            # Set secure permissions
            os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)  # 0o750

            # Verify permissions
            st = os.stat(path)
            if st.st_mode & 0o777 != 0o750:
                raise SecurityError(f"Failed to set secure permissions on {path}")

        except Exception as e:
            raise SecurityError(f"Error setting up secure directory {path}: {e}")

    @property
    def config(self) -> IModelConfig:
        """Get the model configuration."""
        return self._config

    def discover_models(self) -> List[ModelInfo]:
        """
        Discover available models securely.

        Returns:
            List of discovered model information

        Raises:
            SecurityError: If directory permissions are incorrect
        """
        discovered_models = []

        try:
            # Verify models directory exists with correct permissions
            if not os.path.exists(self._models_dir):
                self._create_secure_directory(self._models_dir)
            else:
                st = os.stat(self._models_dir)
                if st.st_mode & 0o777 != 0o750:
                    raise SecurityError(
                        f"Insecure permissions on models directory: {self._models_dir}"
                    )

            # Auto-discover models in models directory
            for model_dir in os.listdir(self._models_dir):
                model_path = os.path.join(self._models_dir, model_dir)
                if os.path.isdir(model_path):
                    try:
                        # Validate model directory name
                        if not self._is_safe_directory_name(model_dir):
                            logger.warning(f"Skipping directory with unsafe name: {model_dir}")
                            continue

                        # Validate model directory permissions
                        st = os.stat(model_path)
                        if st.st_mode & 0o777 != 0o750:
                            logger.warning(f"Insecure permissions on model directory: {model_path}")
                            continue

                        # Verify read access
                        if not os.access(model_path, os.R_OK):
                            logger.warning(
                                f"Insufficient permissions to read model directory: {model_path}"
                            )
                            continue

                        model_info = self._model_downloader.register_local_model(
                            model_dir, model_path
                        )
                        if model_info:
                            discovered_models.append(model_info)
                    except Exception as e:
                        logger.warning(f"Failed to register local model {model_dir}: {e}")

        except Exception as e:
            logger.error(f"Error discovering models: {e}")
            raise ModelError(f"Model discovery failed: {e}")

        return discovered_models

    def _is_safe_directory_name(self, name: str) -> bool:
        """Check if directory name contains only safe characters."""
        return bool(re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.]+$", name))

    def _discover_models(self) -> None:
        """Internal method to discover models if auto-discover is enabled."""
        if not self.config.auto_discover:
            return

        self.discover_models()

    def load_model(self, model_id: str, version: str = None, **kwargs) -> BaseModelAdapter:
        """
        Load a model (synchronous version) with security checks.

        Args:
            model_id: ID of the model to load
            version: Optional version of the model to load
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model adapter

        Raises:
            ModelLoadError: If model cannot be loaded
            SecurityError: If security checks fail
        """
        # Validate model ID
        if not self._is_safe_model_id(model_id):
            raise SecurityError(f"Invalid model ID format: {model_id}")

        with self._model_lock:
            try:
                # Check if model is already loaded
                if model_id in self.loaded_models:
                    return self.loaded_models[model_id]

                # Check if model needs to be downloaded
                if not self._model_downloader.is_model_available(model_id):
                    try:
                        self._model_downloader.download_model(model_id)
                    except Exception as e:
                        raise ModelLoadError(f"Failed to download model {model_id}: {e}")

                model_info = self._model_downloader.get_model_info(model_id)
                if not model_info:
                    raise ModelLoadError(f"Model {model_id} not found")

                # Create appropriate adapter with proper error handling
                adapter = self._create_model_adapter(model_info)
                self.loaded_models[model_id] = adapter
                return adapter

            except SecurityError:
                raise
            except Exception as e:
                logger.error(f"Failed to load model {model_id}: {e}")
                raise ModelLoadError(f"Failed to load model {model_id}: {e}")

    def _is_safe_model_id(self, model_id: str) -> bool:
        """Check if model ID contains only safe characters."""
        return bool(re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.]+$", model_id))

    async def load_model_async(
        self, model_id: str, version: str = None, **kwargs
    ) -> BaseModelAdapter:
        """
        Load a model asynchronously with security checks.

        Args:
            model_id: ID of the model to load
            version: Optional version of the model to load
            **kwargs: Additional parameters for model loading

        Returns:
            Loaded model adapter

        Raises:
            ModelLoadError: If model cannot be loaded
            SecurityError: If security checks fail
        """
        # Run synchronous load_model in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                None, lambda: self.load_model(model_id, version, **kwargs)
            )
        except Exception as e:
            logger.error(f"Failed to load model {model_id} asynchronously: {e}")
            raise

    def _create_model_adapter(self, model_info: ModelInfo) -> BaseModelAdapter:
        """
        Create an appropriate model adapter based on model info with security checks.

        Args:
            model_info: Information about the model

        Returns:
            Model adapter instance

        Raises:
            ModelLoadError: If adapter creation fails
            SecurityError: If security checks fail
        """
        try:
            # Validate model provider
            if not self._is_safe_provider(model_info.provider):
                raise SecurityError(f"Invalid model provider: {model_info.provider}")

            # Create appropriate adapter
            if "lmstudio" in model_info.provider.lower():
                return LMStudioAdapter(model_info)
            elif "openai" in model_info.provider.lower():
                return AdapterFactory.create("openai", model_info)
            elif "ollama" in model_info.provider.lower():
                return AdapterFactory.create("ollama", model_info)
            else:
                return AdapterFactory.create_default(model_info)

        except SecurityError:
            raise
        except Exception as e:
            logger.error(f"Failed to create adapter for model {model_info.id}: {e}")
            raise ModelLoadError(f"Failed to create adapter for model {model_info.id}: {e}")

    def _is_safe_provider(self, provider: str) -> bool:
        """Check if provider name is safe."""
        allowed_providers = {"lmstudio", "openai", "ollama", "huggingface", "local"}
        return provider.lower() in allowed_providers

    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory securely.

        Args:
            model_id: ID of the model to unload

        Returns:
            True if model was unloaded, False if it wasn't loaded
        """
        if not self._is_safe_model_id(model_id):
            raise SecurityError(f"Invalid model ID format: {model_id}")

        with self._model_lock:
            if model_id in self.loaded_models:
                try:
                    # Clean up adapter resources
                    adapter = self.loaded_models[model_id]
                    if hasattr(adapter, "cleanup"):
                        adapter.cleanup()
                    del self.loaded_models[model_id]
                    return True
                except Exception as e:
                    logger.error(f"Error unloading model {model_id}: {e}")
            return False

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get information about a model securely.

        Args:
            model_id: ID of the model

        Returns:
            ModelInfo instance or None if not found

        Raises:
            SecurityError: If model ID format is invalid
        """
        if not self._is_safe_model_id(model_id):
            raise SecurityError(f"Invalid model ID format: {model_id}")

        try:
            return self._model_downloader.get_model_info(model_id)
        except Exception as e:
            logger.error(f"Error getting model info for {model_id}: {e}")
            return None

    def list_models(self) -> List[ModelInfo]:
        """
        List all available models securely.

        Returns:
            List of model information

        Raises:
            ModelError: If listing models fails
        """
        try:
            return self._model_downloader.list_models()
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise ModelError(f"Failed to list models: {e}")

    def validate_model_security(self, model_info: ModelInfo) -> None:
        """
        Validate model security requirements.

        Args:
            model_info: Model information to validate

        Raises:
            SecurityError: If security requirements are not met
        """
        try:
            # Check model path exists and has correct permissions
            model_path = model_info.path
            if not os.path.exists(model_path):
                raise SecurityError(f"Model path does not exist: {model_path}")

            st = os.stat(model_path)
            if st.st_mode & 0o777 != 0o750:
                raise SecurityError(f"Insecure permissions on model path: {model_path}")

            # Validate model ID format
            if not self._is_safe_model_id(model_info.id):
                raise SecurityError(f"Invalid model ID format: {model_info.id}")

            # Validate model provider
            if not self._is_safe_provider(model_info.provider):
                raise SecurityError(f"Invalid model provider: {model_info.provider}")

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Model security validation failed: {e}")
