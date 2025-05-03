"""
Cache control utilities for managing caching settings across the project.

This module provides centralized control over caching settings for different parts
of the application, allowing for consistent cache management from a single location.
"""

import logging
from enum import Enum
from typing import Any, Dict, Set, Union

from .cache_service import default_cache

logger = logging.getLogger(__name__)


class CachingPolicy(Enum):
    """Enum defining different caching policies."""

    DISABLED = "disabled"  # No caching
    MINIMAL = "minimal"  # Only cache critical operations
    BALANCED = "balanced"  # Balance between performance and freshness
    AGGRESSIVE = "aggressive"  # Cache everything possible


class CacheCategory(Enum):
    """Enum defining different categories of cached data."""

    AI_MODELS = "ai_models"
    NICHE_ANALYSIS = "niche_analysis"
    MONETIZATION = "monetization"
    MARKETING = "marketing"
    USER_PREFERENCES = "user_preferences"
    SYSTEM = "system"


class CacheControls:
    """
    Central management for caching settings across the application.

    This class provides methods to control caching behavior across
    different parts of the application, allowing for consistent
    cache management from a single location.
    """

    def __init__(self):
        """Initialize with default caching settings."""
        # Default TTLs (in seconds) by category
        self.default_ttls = {
            CacheCategory.AI_MODELS: 3600,  # 1 hour
            CacheCategory.NICHE_ANALYSIS: 86400,  # 24 hours
            CacheCategory.MONETIZATION: 86400,  # 24 hours
            CacheCategory.MARKETING: 21600,  # 6 hours
            CacheCategory.USER_PREFERENCES: 604800,  # 7 days
            CacheCategory.SYSTEM: 300,  # 5 minutes
        }

        # Current caching policy
        self.current_policy = CachingPolicy.BALANCED

        # Namespaces that are disabled (won't be cached)
        self.disabled_namespaces: Set[str] = set()

        # Map of namespaces to their categories
        self.namespace_categories: Dict[str, CacheCategory] = {
            # AI Models
            "ai_embeddings": CacheCategory.AI_MODELS,
            "ai_completions": CacheCategory.AI_MODELS,
            "ai_model_metadata": CacheCategory.AI_MODELS,
            # Niche Analysis
            "niche_scores": CacheCategory.NICHE_ANALYSIS,
            "opportunity_scores": CacheCategory.NICHE_ANALYSIS,
            "market_data": CacheCategory.NICHE_ANALYSIS,
            # Monetization
            "pricing_rules": CacheCategory.MONETIZATION,
            "cost_calculations": CacheCategory.MONETIZATION,
            "usage_cost_calculations": CacheCategory.MONETIZATION,
            "cost_estimates": CacheCategory.MONETIZATION,
            # Marketing
            "BlogPostGenerator_cache": CacheCategory.MARKETING,
            "SocialMediaPostGenerator_cache": CacheCategory.MARKETING,
            "EmailNewsletterGenerator_cache": CacheCategory.MARKETING,
            # System
            "system_settings": CacheCategory.SYSTEM,
        }

        # Apply the default policy
        self.apply_policy(self.current_policy)

    def set_ttl(self, category: Union[CacheCategory, str], ttl_seconds: int) -> None:
        """
        Set the TTL for a specific category of cached data.

        Args:
            category: The category to set TTL for
            ttl_seconds: Time - to - live in seconds
        """
        if isinstance(category, str):
            try:
                category = CacheCategory(category)
            except ValueError:
                logger.warning(f"Unknown cache category: {category}")
                return

        self.default_ttls[category] = ttl_seconds
        logger.info(f"Set TTL for category {category.value} to {ttl_seconds} seconds")

    def apply_policy(self, policy: Union[CachingPolicy, str]) -> None:
        """
        Apply a caching policy across all cached data.

        Args:
            policy: The caching policy to apply
        """
        if isinstance(policy, str):
            try:
                policy = CachingPolicy(policy)
            except ValueError:
                logger.warning(f"Unknown caching policy: {policy}")
                return

        self.current_policy = policy
        logger.info(f"Applying caching policy: {policy.value}")

        # Clear the disabled namespaces set before reconfiguring
        self.disabled_namespaces.clear()

        # Apply policy - specific settings
        if policy == CachingPolicy.DISABLED:
            # Disable all caching
            for namespace in self.namespace_categories.keys():
                self.disabled_namespaces.add(namespace)

        elif policy == CachingPolicy.MINIMAL:
            # Only cache critical operations
            critical_categories = {
                CacheCategory.AI_MODELS,
                CacheCategory.NICHE_ANALYSIS,
            }

            for namespace, category in self.namespace_categories.items():
                if category not in critical_categories:
                    self.disabled_namespaces.add(namespace)

        elif policy == CachingPolicy.BALANCED:
            # Default behavior - no namespaces disabled
            pass

        elif policy == CachingPolicy.AGGRESSIVE:
            # Increase TTLs for aggressive caching
            for category in self.default_ttls.keys():
                self.default_ttls[category] *= 2

    def get_ttl(self, namespace: str) -> int:
        """
        Get the TTL for a specific namespace.

        Args:
            namespace: Cache namespace

        Returns:
            TTL in seconds, or 0 if caching is disabled for this namespace
        """
        if namespace in self.disabled_namespaces:
            return 0

        category = self.namespace_categories.get(namespace, CacheCategory.SYSTEM)
        return self.default_ttls[category]

    def is_caching_enabled(self, namespace: str) -> bool:
        """
        Check if caching is enabled for a specific namespace.

        Args:
            namespace: Cache namespace

        Returns:
            True if caching is enabled, False otherwise
        """
        return namespace not in self.disabled_namespaces

    def disable_namespace(self, namespace: str) -> None:
        """
        Disable caching for a specific namespace.

        Args:
            namespace: Cache namespace to disable
        """
        self.disabled_namespaces.add(namespace)
        logger.info(f"Disabled caching for namespace: {namespace}")

    def enable_namespace(self, namespace: str) -> None:
        """
        Enable caching for a specific namespace.

        Args:
            namespace: Cache namespace to enable
        """
        if namespace in self.disabled_namespaces:
            self.disabled_namespaces.remove(namespace)
            logger.info(f"Enabled caching for namespace: {namespace}")

    def clear_all_caches(self) -> None:
        """Clear all caches across the application."""
        default_cache.clear_all()
        logger.info("Cleared all caches")

    def clear_category(self, category: Union[CacheCategory, str]) -> None:
        """
        Clear all caches for a specific category.

        Args:
            category: Category to clear caches for
        """
        if isinstance(category, str):
            try:
                category = CacheCategory(category)
            except ValueError:
                logger.warning(f"Unknown cache category: {category}")
                return

        namespaces = [ns for ns, 
            cat in self.namespace_categories.items() if cat == category]
        for namespace in namespaces:
            default_cache.clear(namespace=namespace)

        logger.info(f"Cleared caches for category: {category.value}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the caching system.

        Returns:
            Dictionary containing cache status information
        """
        return {
            "policy": self.current_policy.value,
            "ttls": {cat.value: ttl for cat, ttl in self.default_ttls.items()},
            "disabled_namespaces": list(self.disabled_namespaces),
            "namespace_categories": {
                ns: cat.value for ns, cat in self.namespace_categories.items()
            },
            "stats": default_cache.get_stats(),
        }


# Create a global instance for use throughout the application
cache_controls = CacheControls()


def register_namespace(namespace: str, category: Union[CacheCategory, str]) -> None:
    """
    Register a new namespace with its associated category.

    Args:
        namespace: Cache namespace to register
        category: Category to associate with the namespace
    """
    if isinstance(category, str):
        try:
            category = CacheCategory(category)
        except ValueError:
            logger.warning(f"Unknown cache category: {category}")
            return

    cache_controls.namespace_categories[namespace] = category
    logger.info(f"Registered namespace '{namespace}' under category '{category.value}'")


def get_ttl_for_namespace(namespace: str) -> int:
    """
    Get the current TTL for a namespace.

    Args:
        namespace: Cache namespace

    Returns:
        TTL in seconds
    """
    return cache_controls.get_ttl(namespace)
