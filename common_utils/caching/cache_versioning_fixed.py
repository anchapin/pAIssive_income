"""
Cache versioning utilities.

This module provides tools for versioning cached data based on code changes,
ensuring that cached results are invalidated when the underlying code changes.
"""

import hashlib
import inspect
import logging
import os
import sys
from typing import Any, Callable, Dict, Optional, Set, Tuple, Type

logger = logging.getLogger(__name__)


class CacheVersionManager:
    """
    Manages versioning for cached data.

    This class tracks code versions and namespace versions to ensure proper
    cache invalidation when code or data dependencies change.
    """

    def __init__(self):
        """Initialize the version manager."""
        # Dictionary to store code versions by function/class ID
        self._code_versions = {}

        # Dictionary to store namespace versions
        self._namespace_versions = {}

        # Set to track namespaces that should be cleared on app restart
        self._clear_on_restart = set()

        # Generate application version hash
        self._app_version = self._generate_app_version_hash()

    def version_cache_key(self, key: str, namespace: str) -> str:
        """
        Add version information to a cache key.

        This ensures the key changes when code or namespace dependencies change.

        Args:
            key: Original cache key
            namespace: Cache namespace

        Returns:
            Versioned cache key
        """
        # Get namespace version (or create if it doesn't exist)
        if namespace not in self._namespace_versions:
            self._namespace_versions[namespace] = "v1"

        namespace_version = self._namespace_versions[namespace]

        # Combine app version, namespace version, and original key
        versioned_key = f"{self._app_version[:8]}.{namespace}.{namespace_version}.{key}"
        return versioned_key

    def update_namespace_version(self, namespace: str, reason: str = "manual") -> None:
        """
        Update the version for a namespace.

        This invalidates all cached items in the namespace.

        Args:
            namespace: Cache namespace to update
            reason: Reason for the update (for logging)
        """
        # Get current version or set to v0 if it doesn't exist
        current = self._namespace_versions.get(namespace, "v0")

        # Increment version number
        if current.startswith("v") and current[1:].isdigit():
            version_num = int(current[1:])
            new_version = f"v{version_num + 1}"
        else:
            new_version = "v1"

        # Update version
        self._namespace_versions[namespace] = new_version
        logger.info(
            f"Updated cache namespace {namespace} from {current} to {new_version} ({reason})"
        )

    def clear_namespace_on_restart(self, namespace: str) -> None:
        """
        Mark a namespace to be cleared when the application restarts.

        Args:
            namespace: Cache namespace to clear on restart
        """
        self._clear_on_restart.add(namespace)
        logger.debug(f"Namespace {namespace} will be cleared on next application restart")

    def get_namespaces_to_clear(self) -> Set[str]:
        """
        Get the set of namespaces that should be cleared on restart.

        Returns:
            Set of namespace names
        """
        return self._clear_on_restart.copy()

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
            # Using SHA-256 for better security
            # Note: This is not used for cryptographic security purposes
            version_hash = hashlib.sha256(source.encode()).hexdigest()

            # Cache the result
            self._code_versions[func_id] = version_hash

            return version_hash
        except (IOError, TypeError) as e:
            logger.warning(f"Could not get source for function {func_id}: {e}")
            # Fall back to function name and module as version
            # Using SHA-256 for better security
            return hashlib.sha256(func_id.encode()).hexdigest()

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
            # Using SHA-256 for better security
            # Note: This is not used for cryptographic security purposes
            version_hash = hashlib.sha256(source.encode()).hexdigest()

            # Cache the result
            self._code_versions[cls_id] = version_hash

            return version_hash
        except (IOError, TypeError) as e:
            logger.warning(f"Could not get source for class {cls_id}: {e}")
            # Fall back to class name and module as version
            # Using SHA-256 for better security
            return hashlib.sha256(cls_id.encode()).hexdigest()

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
        # Using SHA-256 for better security
        # Note: This is not used for cryptographic security purposes
        return hashlib.sha256(combined.encode()).hexdigest()

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
        # Using SHA-256 for better security
        # Note: This is not used for cryptographic security purposes
        return hashlib.sha256(app_info.encode()).hexdigest()


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
            logger.warning(f"Could not automatically determine caller for namespace {namespace}")
            return

    # Generate new version based on function/class source
    if inspect.isfunction(func_or_class) or inspect.ismethod(func_or_class):
        new_version = version_manager.get_function_version_hash(func_or_class)
    elif inspect.isclass(func_or_class):
        new_version = version_manager.get_class_version_hash(func_or_class)
    else:
        logger.warning(f"Unsupported object type for code change monitoring: {type(func_or_class)}")
        return

    # Update the namespace version
    version_manager.update_namespace_version(namespace, f"code-{new_version}")
