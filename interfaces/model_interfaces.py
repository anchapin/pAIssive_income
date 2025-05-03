"""
Interfaces for the AI Models module.

This module provides interfaces for the AI models components to enable dependency injection
and improve testability and maintainability.
"""


from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IModelConfig

(ABC):
    """Interface for model configuration."""

@property
    @abstractmethod
    def models_dir(self) -> str:
        """Get the models directory."""
        pass

@property
    @abstractmethod
    def cache_dir(self) -> str:
        """Get the cache directory."""
        pass

@property
    @abstractmethod
    def auto_discover(self) -> bool:
        """Get whether to auto-discover models."""
        pass

@property
    @abstractmethod
    def max_threads(self) -> int:
        """Get the maximum number of threads to use."""
        pass

@classmethod
    @abstractmethod
    def get_default(cls) -> "IModelConfig":
        """Get the default configuration."""
        pass


class IModelInfo(ABC):
    """Interface for model information."""

@property
    @abstractmethod
    def id(self) -> str:
        """Get the model ID."""
        pass

@property
    @abstractmethod
    def name(self) -> str:
        """Get the model name."""
        pass

@property
    @abstractmethod
    def description(self) -> str:
        """Get the model description."""
        pass

@property
    @abstractmethod
    def type(self) -> str:
        """Get the model type."""
        pass

@property
    @abstractmethod
    def path(self) -> str:
        """Get the model path."""
        pass

@property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Get the model metadata."""
        pass


class IModelManager(ABC):
    """Interface for model manager."""

@property
    @abstractmethod
    def config(self) -> IModelConfig:
        """Get the model configuration."""
        pass

@abstractmethod
    def get_model_info(self, model_id: str) -> IModelInfo:
        """
        Get information about a model.

Args:
            model_id: ID of the model

Returns:
            Model information
        """
        pass

@abstractmethod
    def list_models(self) -> List[IModelInfo]:
        """
        List all available models.

Returns:
            List of model information
        """
        pass

@abstractmethod
    def load_model(self, model_id: str, **kwargs) -> Any:
        """
        Load a model.

Args:
            model_id: ID of the model to load
            **kwargs: Additional arguments to pass to the model loader

Returns:
            Loaded model
        """
        pass

@abstractmethod
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model.

Args:
            model_id: ID of the model to unload

Returns:
            True if successful, False otherwise
        """
        pass

@abstractmethod
    def discover_models(self) -> List[IModelInfo]:
        """
        Discover models in the models directory.

Returns:
            List of discovered model information
        """
        pass


class IModelAdapter(ABC):
    """Interface for model adapters."""

@property
    @abstractmethod
    def name(self) -> str:
        """Get the adapter name."""
        pass

@property
    @abstractmethod
    def description(self) -> str:
        """Get the adapter description."""
        pass

@abstractmethod
    def is_available(self) -> bool:
        """
        Check if the adapter is available.

Returns:
            True if available, False otherwise
        """
        pass

@abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to the adapter.

Args:
            **kwargs: Connection parameters

Returns:
            True if successful, False otherwise
        """
        pass

@abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the adapter.

Returns:
            True if successful, False otherwise
        """
        pass

@abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from the adapter.

Returns:
            List of model dictionaries
        """
        pass


class ICacheManager(ABC):
    """Interface for cache manager."""

@abstractmethod
    def get(self, key: str) -> Any:
        """
        Get a value from the cache.

Args:
            key: Cache key

Returns:
            Cached value, or None if not found
        """
        pass

@abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

Returns:
            True if successful, False otherwise
        """
        pass

@abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

Args:
            key: Cache key

Returns:
            True if successful, False otherwise
        """
        pass

@abstractmethod
    def clear(self) -> bool:
        """
        Clear the cache.

Returns:
            True if successful, False otherwise
        """
        pass


class IPerformanceMonitor(ABC):
    """Interface for performance monitor."""

@abstractmethod
    def start_tracking(self, model_id: str, operation: str) -> str:
        """
        Start tracking performance for a model operation.

Args:
            model_id: ID of the model
            operation: Operation being performed

Returns:
            Tracking ID
        """
        pass

@abstractmethod
    def end_tracking(
        self, tracking_id: str, result_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        End tracking performance for a model operation.

Args:
            tracking_id: Tracking ID
            result_size: Size of the result in bytes

Returns:
            Performance metrics
        """
        pass

@abstractmethod
    def get_metrics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics.

Args:
            model_id: Optional model ID to filter metrics

Returns:
            Performance metrics
        """
        pass