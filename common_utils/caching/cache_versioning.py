"""
Cache versioning module for the pAIssive Income project.

This module provides automatic cache key versioning to handle cache invalidation
when code or data models change, ensuring stale cached results aren't returned.
"""

import hashlib
import inspect
import logging
import os
import sys
import time
from typing import Any, Dict, Optional, Callable, Set, Tuple, Type

# Set up logging
logger = logging.getLogger(__name__)


class CacheVersionManager:
    """
    Manages versioning for cache keys to ensure proper cache invalidation.

    This class provides tools to automatically version cache keys based on:
    1. Code versions (using function/class source code hashes)
    2. Data model versions
    3. Manual version controls
    """

    def __init__(self):
        """Initialize the cache version manager."""
        # Dictionary mapping namespaces to their current versions
        self._namespace_versions: Dict[str, str] = {}

        # Dictionary mapping class/function objects to their version hashes
        self._code_versions: Dict[str, str] = {}

        # Base version hash for the application
        self._app_version_hash = self._generate_app_version_hash()

        # Set of namespaces that should be automatically versioned
        self._auto_versioned_namespaces: Set[str] = set()

        logger.info(
            f"Cache version manager initialized with app version hash: {self._app_version_hash[:8]}"
        )

    def register_namespace(
        self, namespace: str, version: Optional[str] = None, auto_version: bool = True
    ) -> str:
        """
        Register a cache namespace with version control.

        Args:
            namespace: Cache namespace to register
            version: Explicit version string (optional)
            auto_version: Whether to automatically version this namespace

        Returns:
            The version string for this namespace
        """
        # Use provided version or generate one
        if version is None:
            version = f"{self._app_version_hash}-{int(time.time())}"

        # Store the version
        self._namespace_versions[namespace] = version

        # Register for auto-versioning if requested
        if auto_version:
            self._auto_versioned_namespaces.add(namespace)

        logger.debug(
            f"Registered cache namespace '{namespace}' with version: {version[:8]}..."
        )

        return version

    def get_namespace_version(self, namespace: str) -> str:
        """
        Get the current version for a cache namespace.

        Args:
            namespace: Cache namespace to get version for

        Returns:
            Version string for the namespace
        """
        # Return existing version or register a new one
        if namespace not in self._namespace_versions:
            return self.register_namespace(namespace)

        return self._namespace_versions[namespace]

    def update_namespace_version(
        self, namespace: str, version: Optional[str] = None
    ) -> str:
        """
        Update the version for a cache namespace.

        Args:
            namespace: Cache namespace to update
            version: New version string (optional, generates one if not provided)

        Returns:
            Updated version string
        """
        if version is None:
            version = f"{self._app_version_hash}-{int(time.time())}"

        # Store the new version
        self._namespace_versions[namespace] = version

        logger.info(
            f"Updated cache namespace '{namespace}' to version: {version[:8]}..."
        )

        return version

    def version_cache_key(self, key: str, namespace: str) -> str:
        """
        Add version information to a cache key.

        Args:
            key: Original cache key
            namespace: Cache namespace

        Returns:
            Versioned cache key
        """
        version = self.get_namespace_version(namespace)
        return f"v:{version}:{key}"

    def get_function_version_hash(self, func: Callable) -> str:
        """
        Generate a version hash for a function based on its source code.

        Args:
            func: Function to generate version hash for

        Returns:
            Version hash string
        """
        # Use cached version if available
        func_id = f"{func.__module__}.{func.__qualname__}"
        if func_id in self._code_versions:
            return self._code_versions[func_id]

        # Get source code and hash it
        try:
            source = inspect.getsource(func)
            version_hash = hashlib.md5(source.encode()).hexdigest()

            # Cache the result
            self._code_versions[func_id] = version_hash

            return version_hash
        except (IOError, TypeError) as e:
            logger.warning(f"Could not get source for function {func_id}: {e}")
            # Fall back to function name and module as version
            return hashlib.md5(func_id.encode()).hexdigest()

    def get_class_version_hash(self, cls: Type) -> str:
        """
        Generate a version hash for a class based on its source code.

        Args:
            cls: Class to generate version hash for

        Returns:
            Version hash string
        """
        # Use cached version if available
        cls_id = f"{cls.__module__}.{cls.__qualname__}"
        if cls_id in self._code_versions:
            return self._code_versions[cls_id]

        # Get source code and hash it
        try:
            source = inspect.getsource(cls)
            version_hash = hashlib.md5(source.encode()).hexdigest()

            # Cache the result
            self._code_versions[cls_id] = version_hash

            return version_hash
        except (IOError, TypeError) as e:
            logger.warning(f"Could not get source for class {cls_id}: {e}")
            # Fall back to class name and module as version
            return hashlib.md5(cls_id.encode()).hexdigest()

    def get_data_model_version_hash(self, model_class: Type) -> str:
        """
        Generate a version hash for a data model class.

        This is designed to detect changes in data models that would affect
        cached results, particularly useful for ORM models or schema classes.

        Args:
            model_class: Data model class to version

        Returns:
            Version hash string
        """
        # Start with the class source code
        cls_hash = self.get_class_version_hash(model_class)

        # Include attribute types and names in the hash
        attrs = {}
        for name, attr in inspect.getmembers(model_class):
            # Skip private attributes and methods
            if name.startswith("_") or callable(attr):
                continue

            # Add attribute name and type to dict
            attrs[name] = str(type(attr))

        # Hash the combined information
        combined = f"{cls_hash}:{str(attrs)}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _generate_app_version_hash(self) -> str:
        """
        Generate a version hash for the entire application.

        This creates a base version that changes whenever the application
        code is modified, ensuring cache invalidation on code updates.

        Returns:
            Application version hash string
        """
        # Start with app directory and Python version
        app_info = f"{os.path.dirname(sys.modules['__main__'].__file__)}:{sys.version}"

        # Add main module file path and timestamp
        try:
            main_module = sys.modules["__main__"]
            main_path = getattr(main_module, "__file__", "")
            if main_path and os.path.exists(main_path):
                app_info += f":{main_path}:{os.path.getmtime(main_path)}"
        except (AttributeError, OSError):
            pass

        # Hash the combined information
        return hashlib.md5(app_info.encode()).hexdigest()


# Create a default instance for use throughout the application
version_manager = CacheVersionManager()


def generate_versioned_key(
    func: Callable,
    args: Tuple,
    kwargs: Dict[str, Any],
    namespace: str,
    include_func_version: bool = True,
    base_key: Optional[str] = None,
) -> str:
    """
    Generate a versioned cache key for a function call.

    This combines the base key generation with version information to ensure
    proper cache invalidation when code changes.

    Args:
        func: Function being called
        args: Function positional arguments
        kwargs: Function keyword arguments
        namespace: Cache namespace
        include_func_version: Whether to include function source code in version
        base_key: Optional base key to use instead of generating one

    Returns:
        Versioned cache key
    """
    from .cache_service import _generate_cache_key

    # Start with base key - either provided or generated
    if base_key is None:
        base_key = _generate_cache_key(func, args, kwargs)

    # Add function version to namespace if requested
    if include_func_version:
        func_version = version_manager.get_function_version_hash(func)
        versioned_namespace = f"{namespace}.{func_version[:8]}"
    else:
        versioned_namespace = namespace

    # Version the key
    return version_manager.version_cache_key(base_key, versioned_namespace)


def clear_namespace_on_code_change(namespace: str, func_or_class: Any = None) -> None:
    """
    Register a namespace to be cleared when specific code changes.

    This ties a cache namespace to a specific function, method or class,
    ensuring the cache is invalidated when that code changes.

    Args:
        namespace: Cache namespace to monitor
        func_or_class: Function or class to monitor for changes
    """
    if func_or_class is None:
        # Try to determine the caller
        frame = inspect.currentframe().f_back
        try:
            func_or_class = frame.f_locals.get("self", None).__class__
        except (AttributeError, KeyError):
            logger.warning(
                f"Could not automatically determine caller for namespace {namespace}"
            )
            return

    # Generate new version based on function/class source
    if inspect.isfunction(func_or_class) or inspect.ismethod(func_or_class):
        new_version = version_manager.get_function_version_hash(func_or_class)
    elif inspect.isclass(func_or_class):
        new_version = version_manager.get_class_version_hash(func_or_class)
    else:
        logger.warning(
            f"Unsupported object type for code change monitoring: {type(func_or_class)}"
        )
        return

    # Update the namespace version
    version_manager.update_namespace_version(namespace, f"code-{new_version}")
