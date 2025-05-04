"""
"""
Interfaces for the AI Models module.
Interfaces for the AI Models module.


This module provides interfaces for the AI models components to enable dependency injection
This module provides interfaces for the AI models components to enable dependency injection
and improve testability and maintainability.
and improve testability and maintainability.
"""
"""




from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional




class IModelConfig:
    class IModelConfig:


    pass  # Added missing block
    pass  # Added missing block
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

    @property
    @abstractmethod
    def config(self) -> IModelConfig:
    """Get the model configuration."""
    pass

    @abstractmethod
    def get_model_info(self, model_id: str) -> IModelInfo:
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
    Model information
    Model information
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def list_models(self) -> List[IModelInfo]:
    def list_models(self) -> List[IModelInfo]:
    """
    """
    List all available models.
    List all available models.


    Returns:
    Returns:
    List of model information
    List of model information
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def load_model(self, model_id: str, **kwargs) -> Any:
    def load_model(self, model_id: str, **kwargs) -> Any:
    """
    """
    Load a model.
    Load a model.


    Args:
    Args:
    model_id: ID of the model to load
    model_id: ID of the model to load
    **kwargs: Additional arguments to pass to the model loader
    **kwargs: Additional arguments to pass to the model loader


    Returns:
    Returns:
    Loaded model
    Loaded model
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def unload_model(self, model_id: str) -> bool:
    def unload_model(self, model_id: str) -> bool:
    """
    """
    Unload a model.
    Unload a model.


    Args:
    Args:
    model_id: ID of the model to unload
    model_id: ID of the model to unload


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def discover_models(self) -> List[IModelInfo]:
    def discover_models(self) -> List[IModelInfo]:
    """
    """
    Discover models in the models directory.
    Discover models in the models directory.


    Returns:
    Returns:
    List of discovered model information
    List of discovered model information
    """
    """
    pass
    pass




    class IModelAdapter(ABC):
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
    """
    Check if the adapter is available.
    Check if the adapter is available.


    Returns:
    Returns:
    True if available, False otherwise
    True if available, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def connect(self, **kwargs) -> bool:
    def connect(self, **kwargs) -> bool:
    """
    """
    Connect to the adapter.
    Connect to the adapter.


    Args:
    Args:
    **kwargs: Connection parameters
    **kwargs: Connection parameters


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def disconnect(self) -> bool:
    def disconnect(self) -> bool:
    """
    """
    Disconnect from the adapter.
    Disconnect from the adapter.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
    def get_models(self) -> List[Dict[str, Any]]:
    """
    """
    Get available models from the adapter.
    Get available models from the adapter.


    Returns:
    Returns:
    List of model dictionaries
    List of model dictionaries
    """
    """
    pass
    pass




    class ICacheManager(ABC):
    class ICacheManager(ABC):
    """Interface for cache manager."""

    @abstractmethod
    def get(self, key: str) -> Any:
    """
    """
    Get a value from the cache.
    Get a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Cached value, or None if not found
    Cached value, or None if not found
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    """
    Set a value in the cache.
    Set a value in the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key
    value: Value to cache
    value: Value to cache
    ttl: Time to live in seconds
    ttl: Time to live in seconds


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def delete(self, key: str) -> bool:
    def delete(self, key: str) -> bool:
    """
    """
    Delete a value from the cache.
    Delete a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def clear(self) -> bool:
    def clear(self) -> bool:
    """
    """
    Clear the cache.
    Clear the cache.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    pass
    pass




    class IPerformanceMonitor(ABC):
    class IPerformanceMonitor(ABC):
    """Interface for performance monitor."""

    @abstractmethod
    def start_tracking(self, model_id: str, operation: str) -> str:
    """
    """
    Start tracking performance for a model operation.
    Start tracking performance for a model operation.


    Args:
    Args:
    model_id: ID of the model
    model_id: ID of the model
    operation: Operation being performed
    operation: Operation being performed


    Returns:
    Returns:
    Tracking ID
    Tracking ID
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def end_tracking(
    def end_tracking(
    self, tracking_id: str, result_size: Optional[int] = None
    self, tracking_id: str, result_size: Optional[int] = None
    ) -> Dict[str, Any]:
    ) -> Dict[str, Any]:
    """
    """
    End tracking performance for a model operation.
    End tracking performance for a model operation.


    Args:
    Args:
    tracking_id: Tracking ID
    tracking_id: Tracking ID
    result_size: Size of the result in bytes
    result_size: Size of the result in bytes


    Returns:
    Returns:
    Performance metrics
    Performance metrics
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def get_metrics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
    def get_metrics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
    """
    """
    Get performance metrics.
    Get performance metrics.


    Args:
    Args:
    model_id: Optional model ID to filter metrics
    model_id: Optional model ID to filter metrics


    Returns:
    Returns:
    Performance metrics
    Performance metrics
    """
    """
    pass
    pass