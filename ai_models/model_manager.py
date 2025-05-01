"""Model management functionality."""

import json
import logging
import os
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type, Union, cast

try:
    import torch
except ImportError:
    warnings.warn("PyTorch not available. Some features will be disabled.")

try:
    import transformers
except ImportError:
    warnings.warn("Transformers not available. Some features will be disabled.")

try:
    import sentence_transformers
except ImportError:
    warnings.warn(
        "Sentence-transformers not available. Some features will be disabled."
    )

try:
    import llama_cpp
except ImportError:
    warnings.warn("llama-cpp not available. Some features will be disabled.")

try:
    import onnxruntime as ort
except ImportError:
    warnings.warn("ONNX Runtime not available. Some features will be disabled.")

from .adapters import (
    LMStudioAdapter,
    OllamaAdapter,
    OpenAICompatibleAdapter,
    TensorRTAdapter,
)
from .adapters.base_adapter import BaseModelAdapter
from .model_config import ModelConfig, ModelType
from .model_downloader import ModelDownloader
from .schemas import ModelInfoSchema


class ModelInfo:
    """Information about a model."""

    def __init__(
        self,
        id: str,
        name: str,
        model_type: str,
        framework: str,
        path: str,
        description: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, any]] = None,
    ):
        """Initialize model info.

        Args:
            id: Unique identifier for the model
            name: Name of the model
            model_type: Type of model (text, embedding, etc.)
            framework: Framework used by the model (pytorch, tensorflow, etc.)
            path: Path to the model files
            description: Description of the model
            version: Version of the model
            metadata: Additional metadata
        """
        self.id = id
        self.name = name
        self.model_type = model_type
        self.framework = framework
        self.path = path
        self.description = description
        self.version = version
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata = metadata or {}

    def to_schema(self) -> ModelInfoSchema:
        """Convert to schema object.

        Returns:
            Schema representation of this model info
        """
        return ModelInfoSchema(
            id=self.id,
            name=self.name,
            model_type=self.model_type,
            framework=self.framework,
            path=self.path,
            description=self.description,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata,
        )


class ModelManager:
    """Manages loading and caching of AI models."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize model manager.

        Args:
            cache_dir: Directory to cache models in
        """
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/models")
        os.makedirs(self.cache_dir, exist_ok=True)

        self.model_configs: Dict[str, ModelConfig] = {}
        self.loaded_models: Dict[str, BaseModelAdapter] = {}
        self.downloader = ModelDownloader(cache_dir=self.cache_dir)
        self.logger = logging.getLogger(__name__)

    def add_model_config(self, config: ModelConfig) -> None:
        """Add a model configuration.

        Args:
            config: Model configuration to add
        """
        self.model_configs[config.name] = config

    def load_model(
        self, model_name: str, model_type: Optional[ModelType] = None, **kwargs
    ) -> BaseModelAdapter:
        """Load a model by name.

        Args:
            model_name: Name of model to load
            model_type: Optional type override
            **kwargs: Additional args passed to model constructor

        Returns:
            Loaded model adapter

        Raises:
            ValueError: If model config not found
            RuntimeError: If model loading fails
        """
        if model_name not in self.model_configs:
            raise ValueError(f"No configuration found for model: {model_name}")

        if model_name in self.loaded_models:
            return self.loaded_models[model_name]

        config = self.model_configs[model_name]
        model_type = model_type or config.model_type

        try:
            if model_type == ModelType.LLAMA_CPP:
                adapter = self._load_llama_model(config, **kwargs)
            elif model_type == ModelType.TRANSFORMERS:
                adapter = self._load_transformers_model(config, **kwargs)
            elif model_type == ModelType.SENTENCE_TRANSFORMERS:
                adapter = self._load_sentence_transformers_model(config, **kwargs)
            elif model_type == ModelType.ONNX:
                adapter = self._load_onnx_model(config, **kwargs)
            elif model_type == ModelType.TENSORRT:
                adapter = self._load_tensorrt_model(config, **kwargs)
            elif model_type == ModelType.LMSTUDIO:
                adapter = self._load_lmstudio_model(config, **kwargs)
            elif model_type == ModelType.OLLAMA:
                adapter = self._load_ollama_model(config, **kwargs)
            elif model_type == ModelType.OPENAI_COMPATIBLE:
                adapter = self._load_openai_compatible_model(config, **kwargs)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            self.loaded_models[model_name] = adapter
            return adapter

        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}") from e

    def unload_model(self, model_name: str) -> None:
        """Unload a model by name.

        Args:
            model_name: Name of model to unload
        """
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]

    def _load_llama_model(self, config: ModelConfig, **kwargs) -> BaseModelAdapter:
        """Load a LLaMA model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            LLaMA model adapter
        """
        model_path = self.downloader.ensure_model_files(
            config.source, model_name=config.name, model_type=config.model_type
        )
        model = llama_cpp.Llama(
            model_path=str(model_path), **{**config.model_kwargs, **kwargs}
        )
        return LMStudioAdapter(model)

    def _load_transformers_model(
        self, config: ModelConfig, **kwargs
    ) -> BaseModelAdapter:
        """Load a Hugging Face Transformers model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            Transformers model adapter
        """
        model = transformers.AutoModelForCausalLM.from_pretrained(
            config.source, **{**config.model_kwargs, **kwargs}
        )
        tokenizer = transformers.AutoTokenizer.from_pretrained(config.source)
        return OpenAICompatibleAdapter(model, tokenizer)

    def _load_sentence_transformers_model(
        self, config: ModelConfig, **kwargs
    ) -> BaseModelAdapter:
        """Load a sentence-transformers model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            Sentence transformers model adapter
        """
        model = sentence_transformers.SentenceTransformer(
            config.source, **{**config.model_kwargs, **kwargs}
        )
        return OpenAICompatibleAdapter(model)

    def _load_onnx_model(self, config: ModelConfig, **kwargs) -> BaseModelAdapter:
        """Load an ONNX model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            ONNX model adapter
        """
        model_path = self.downloader.ensure_model_files(
            config.source, model_name=config.name, model_type=config.model_type
        )
        session = ort.InferenceSession(str(model_path))
        return OpenAICompatibleAdapter(session)

    def _load_tensorrt_model(self, config: ModelConfig, **kwargs) -> BaseModelAdapter:
        """Load a TensorRT model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            TensorRT model adapter
        """
        model_path = self.downloader.ensure_model_files(
            config.source, model_name=config.name, model_type=config.model_type
        )
        return TensorRTAdapter(model_path, **kwargs)

    def _load_lmstudio_model(self, config: ModelConfig, **kwargs) -> BaseModelAdapter:
        """Load an LM Studio model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            LM Studio model adapter
        """
        return LMStudioAdapter(
            model_path=config.source, **{**config.model_kwargs, **kwargs}
        )

    def _load_ollama_model(self, config: ModelConfig, **kwargs) -> BaseModelAdapter:
        """Load an Ollama model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            Ollama model adapter
        """
        return OllamaAdapter(
            model_name=config.name, **{**config.model_kwargs, **kwargs}
        )

    def _load_openai_compatible_model(
        self, config: ModelConfig, **kwargs
    ) -> BaseModelAdapter:
        """Load an OpenAI-compatible model.

        Args:
            config: Model configuration
            **kwargs: Additional args passed to model constructor

        Returns:
            OpenAI compatible model adapter
        """
        return OpenAICompatibleAdapter(
            base_url=config.source, **{**config.model_kwargs, **kwargs}
        )
