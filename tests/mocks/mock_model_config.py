"""
Mock ModelConfig class for testing.
"""

from typing import Any, Dict, List, Optional


class MockModelConfig:
    """Mock ModelConfig class that accepts model and temperature parameters."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        models_dir: Optional[str] = None,
        cache_dir: Optional[str] = None,
        model_sources: Optional[List[str]] = None,
        auto_discover: bool = True,
        max_threads: Optional[int] = None,
        **kwargs,
    ) -> None:
        """Initialize mock model configuration.

        Args:
            model: Model name or identifier
            temperature: Temperature for sampling
            max_tokens: Maximum tokens to generate
            models_dir: Directory containing model files
            cache_dir: Directory for caching model data
            model_sources: List of model sources
            auto_discover: Whether to auto - discover models on init
            max_threads: Maximum number of threads for model loading
            **kwargs: Additional parameters
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.models_dir = models_dir or "./models"
        self.cache_dir = cache_dir or "./cache"
        self.model_sources = model_sources or ["local"]
        self.auto_discover = auto_discover
        self._max_threads = max_threads
        self.kwargs = kwargs

    @property
    def max_threads(self) -> Optional[int]:
        """Get maximum number of threads."""
        return self._max_threads

    @property
    def cache_enabled(self) -> bool:
        """Get whether caching is enabled."""
        return True

    @property
    def cache_ttl(self) -> int:
        """Get cache time - to - live in seconds."""
        return 86400  # 24 hours default

    @property
    def max_cache_size(self) -> int:
        """Get maximum cache size in bytes."""
        return 1000  # Default value

    @property
    def default_device(self) -> str:
        """Get default device for model inference."""
        return "auto"

    @property
    def default_text_model(self) -> Optional[str]:
        """Get default text generation model ID."""
        return "gpt2"

    @property
    def default_embedding_model(self) -> Optional[str]:
        """Get default text embedding model ID."""
        return "all - MiniLM - L6 - v2"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "models_dir": self.models_dir,
            "cache_dir": self.cache_dir,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "max_cache_size": self.max_cache_size,
            "default_device": self.default_device,
            "max_threads": self.max_threads,
            "auto_discover": self.auto_discover,
            "model_sources": self.model_sources,
            "default_text_model": self.default_text_model,
            "default_embedding_model": self.default_embedding_model,
            **self.kwargs,
        }

    @classmethod
    def get_default(cls) -> "MockModelConfig":
        """Get default configuration."""
        return cls()
