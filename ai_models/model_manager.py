"""Model manager module for handling AI model loading and configuration."""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from interfaces.model_interfaces import IModelConfig, IModelManager

from .adapters import (
    AdapterFactory,
    BaseModelAdapter,
    LMStudioAdapter,
)
from .model_config import ModelConfig
from .model_downloader import ModelDownloader

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a model."""

    id: str
    name: str
    provider: str
    model_type: str
    path: str
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ModelManager(IModelManager):
    """Manages AI model loading, caching, and inference."""

    def __init__(self, config: IModelConfig):
        self.config = config
        self._models_dir = config.models_dir
        self._cache_dir = config.cache_dir
        self._model_downloader = ModelDownloader(self._models_dir, config)
        self.loaded_models: Dict[str, BaseModelAdapter] = {}
        self._discover_models()

    def _discover_models(self) -> None:
        if not self.config.auto_discover:
            return

        if not os.path.exists(self._models_dir):
            os.makedirs(self._models_dir)

        # Auto-discover models in models directory
        for model_dir in os.listdir(self._models_dir):
            model_path = os.path.join(self._models_dir, model_dir)
            if os.path.isdir(model_path):
                try:
                    self._model_downloader.register_local_model(model_dir, model_path)
                except Exception as e:
                    logger.warning(f"Failed to register local model {model_dir}: {e}")

    def load_model(self, model_id: str) -> BaseModelAdapter:
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]

        # Check if model needs to be downloaded
        if not self._model_downloader.is_model_available(model_id):
            self._model_downloader.download_model(model_id)

        model_info = self._model_downloader.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found")

        # Create appropriate adapter
        if "lmstudio" in model_info.provider.lower():
            adapter = LMStudioAdapter(model_info)
        elif "openai" in model_info.provider.lower():
            adapter = AdapterFactory.create("openai", model_info)
        elif "ollama" in model_info.provider.lower():
            adapter = AdapterFactory.create("ollama", model_info)
        else:
            adapter = AdapterFactory.create_default(model_info)

        self.loaded_models[model_id] = adapter
        return adapter

    def unload_model(self, model_id: str) -> bool:
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            return True
        return False

    def get_model_info(self, model_id: str) -> Optional[Any]:
        return self._model_downloader.get_model_info(model_id)
