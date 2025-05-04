"""
"""
Cache versioning module for the pAIssive Income project.
Cache versioning module for the pAIssive Income project.


This module provides automatic cache key versioning to handle cache invalidation
This module provides automatic cache key versioning to handle cache invalidation
when code or data models change, ensuring stale cached results aren't returned.
when code or data models change, ensuring stale cached results aren't returned.
"""
"""




import hashlib
import hashlib
import inspect
import inspect
import logging
import logging
import os
import os
import sys
import sys
import time
import time
from typing import Any, Callable, Dict, Optional, Set, Tuple, Type
from typing import Any, Callable, Dict, Optional, Set, Tuple, Type


from .cache_service import _generate_cache_key
from .cache_service import _generate_cache_key


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class CacheVersionManager:
    class CacheVersionManager:
    """
    """
    Manages versioning for cache keys to ensure proper cache invalidation.
    Manages versioning for cache keys to ensure proper cache invalidation.


    This class provides tools to automatically version cache keys based on:
    This class provides tools to automatically version cache keys based on:
    1. Code versions (using function/class source code hashes)
    1. Code versions (using function/class source code hashes)
    2. Data model versions
    2. Data model versions
    3. Manual version controls
    3. Manual version controls
    """
    """


    def __init__(self):
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
    """
    Register a cache namespace with version control.
    Register a cache namespace with version control.


    Args:
    Args:
    namespace: Cache namespace to register
    namespace: Cache namespace to register
    version: Explicit version string (optional)
    version: Explicit version string (optional)
    auto_version: Whether to automatically version this namespace
    auto_version: Whether to automatically version this namespace


    Returns:
    Returns:
    The version string for this namespace
    The version string for this namespace
    """
    """
    # Use provided version or generate one
    # Use provided version or generate one
    if version is None:
    if version is None:
    version = f"{self._app_version_hash}-{int(time.time())}"
    version = f"{self._app_version_hash}-{int(time.time())}"


    # Store the version
    # Store the version
    self._namespace_versions[namespace] = version
    self._namespace_versions[namespace] = version


    # Register for auto-versioning if requested
    # Register for auto-versioning if requested
    if auto_version:
    if auto_version:
    self._auto_versioned_namespaces.add(namespace)
    self._auto_versioned_namespaces.add(namespace)


    logger.debug(
    logger.debug(
    f"Registered cache namespace '{namespace}' with version: {version[:8]}..."
    f"Registered cache namespace '{namespace}' with version: {version[:8]}..."
    )
    )


    return version
    return version


    def get_namespace_version(self, namespace: str) -> str:
    def get_namespace_version(self, namespace: str) -> str:
    """
    """
    Get the current version for a cache namespace.
    Get the current version for a cache namespace.


    Args:
    Args:
    namespace: Cache namespace to get version for
    namespace: Cache namespace to get version for


    Returns:
    Returns:
    Version string for the namespace
    Version string for the namespace
    """
    """
    # Return existing version or register a new one
    # Return existing version or register a new one
    if namespace not in self._namespace_versions:
    if namespace not in self._namespace_versions:
    return self.register_namespace(namespace)
    return self.register_namespace(namespace)


    return self._namespace_versions[namespace]
    return self._namespace_versions[namespace]


    def update_namespace_version(
    def update_namespace_version(
    self, namespace: str, version: Optional[str] = None
    self, namespace: str, version: Optional[str] = None
    ) -> str:
    ) -> str:
    """
    """
    Update the version for a cache namespace.
    Update the version for a cache namespace.


    Args:
    Args:
    namespace: Cache namespace to update
    namespace: Cache namespace to update
    version: New version string (optional, generates one if not provided)
    version: New version string (optional, generates one if not provided)


    Returns:
    Returns:
    Updated version string
    Updated version string
    """
    """
    if version is None:
    if version is None:
    version = f"{self._app_version_hash}-{int(time.time())}"
    version = f"{self._app_version_hash}-{int(time.time())}"


    # Store the new version
    # Store the new version
    self._namespace_versions[namespace] = version
    self._namespace_versions[namespace] = version


    logger.info(
    logger.info(
    f"Updated cache namespace '{namespace}' to version: {version[:8]}..."
    f"Updated cache namespace '{namespace}' to version: {version[:8]}..."
    )
    )


    return version
    return version


    def version_cache_key(self, key: str, namespace: str) -> str:
    def version_cache_key(self, key: str, namespace: str) -> str:
    """
    """
    Add version information to a cache key.
    Add version information to a cache key.


    Args:
    Args:
    key: Original cache key
    key: Original cache key
    namespace: Cache namespace
    namespace: Cache namespace


    Returns:
    Returns:
    Versioned cache key
    Versioned cache key
    """
    """
    version = self.get_namespace_version(namespace)
    version = self.get_namespace_version(namespace)
    return f"v:{version}:{key}"
    return f"v:{version}:{key}"


    def get_function_version_hash(self, func: Callable) -> str:
    def get_function_version_hash(self, func: Callable) -> str:
    """
    """
    Generate a version hash for a function based on its source code.
    Generate a version hash for a function based on its source code.


    Args:
    Args:
    func: Function to generate version hash for
    func: Function to generate version hash for


    Returns:
    Returns:
    Version hash string
    Version hash string
    """
    """
    # Use cached version if available
    # Use cached version if available
    func_id = f"{func.__module__}.{func.__qualname__}"
    func_id = f"{func.__module__}.{func.__qualname__}"
    if func_id in self._code_versions:
    if func_id in self._code_versions:
    return self._code_versions[func_id]
    return self._code_versions[func_id]


    # Get source code and hash it
    # Get source code and hash it
    try:
    try:
    source = inspect.getsource(func)
    source = inspect.getsource(func)
    version_hash = hashlib.md5(source.encode()).hexdigest()
    version_hash = hashlib.md5(source.encode()).hexdigest()


    # Cache the result
    # Cache the result
    self._code_versions[func_id] = version_hash
    self._code_versions[func_id] = version_hash


    return version_hash
    return version_hash
except (IOError, TypeError) as e:
except (IOError, TypeError) as e:
    logger.warning(f"Could not get source for function {func_id}: {e}")
    logger.warning(f"Could not get source for function {func_id}: {e}")
    # Fall back to function name and module as version
    # Fall back to function name and module as version
    return hashlib.md5(func_id.encode()).hexdigest()
    return hashlib.md5(func_id.encode()).hexdigest()


    def get_class_version_hash(self, cls: Type) -> str:
    def get_class_version_hash(self, cls: Type) -> str:
    """
    """
    Generate a version hash for a class based on its source code.
    Generate a version hash for a class based on its source code.


    Args:
    Args:
    cls: Class to generate version hash for
    cls: Class to generate version hash for


    Returns:
    Returns:
    Version hash string
    Version hash string
    """
    """
    # Use cached version if available
    # Use cached version if available
    cls_id = f"{cls.__module__}.{cls.__qualname__}"
    cls_id = f"{cls.__module__}.{cls.__qualname__}"
    if cls_id in self._code_versions:
    if cls_id in self._code_versions:
    return self._code_versions[cls_id]
    return self._code_versions[cls_id]


    # Get source code and hash it
    # Get source code and hash it
    try:
    try:
    source = inspect.getsource(cls)
    source = inspect.getsource(cls)
    version_hash = hashlib.md5(source.encode()).hexdigest()
    version_hash = hashlib.md5(source.encode()).hexdigest()


    # Cache the result
    # Cache the result
    self._code_versions[cls_id] = version_hash
    self._code_versions[cls_id] = version_hash


    return version_hash
    return version_hash
except (IOError, TypeError) as e:
except (IOError, TypeError) as e:
    logger.warning(f"Could not get source for class {cls_id}: {e}")
    logger.warning(f"Could not get source for class {cls_id}: {e}")
    # Fall back to class name and module as version
    # Fall back to class name and module as version
    return hashlib.md5(cls_id.encode()).hexdigest()
    return hashlib.md5(cls_id.encode()).hexdigest()


    def get_data_model_version_hash(self, model_class: Type) -> str:
    def get_data_model_version_hash(self, model_class: Type) -> str:
    """
    """
    Generate a version hash for a data model class.
    Generate a version hash for a data model class.


    This is designed to detect changes in data models that would affect
    This is designed to detect changes in data models that would affect
    cached results, particularly useful for ORM models or schema classes.
    cached results, particularly useful for ORM models or schema classes.


    Args:
    Args:
    model_class: Data model class to version
    model_class: Data model class to version


    Returns:
    Returns:
    Version hash string
    Version hash string
    """
    """
    # Start with the class source code
    # Start with the class source code
    cls_hash = self.get_class_version_hash(model_class)
    cls_hash = self.get_class_version_hash(model_class)


    # Include attribute types and names in the hash
    # Include attribute types and names in the hash
    attrs = {}
    attrs = {}
    for name, attr in inspect.getmembers(model_class):
    for name, attr in inspect.getmembers(model_class):
    # Skip private attributes and methods
    # Skip private attributes and methods
    if name.startswith("_") or callable(attr):
    if name.startswith("_") or callable(attr):
    continue
    continue


    # Add attribute name and type to dict
    # Add attribute name and type to dict
    attrs[name] = str(type(attr))
    attrs[name] = str(type(attr))


    # Hash the combined information
    # Hash the combined information
    combined = f"{cls_hash}:{str(attrs)}"
    combined = f"{cls_hash}:{str(attrs)}"
    return hashlib.md5(combined.encode()).hexdigest()
    return hashlib.md5(combined.encode()).hexdigest()


    def _generate_app_version_hash(self) -> str:
    def _generate_app_version_hash(self) -> str:
    """
    """
    Generate a version hash for the entire application.
    Generate a version hash for the entire application.


    This creates a base version that changes whenever the application
    This creates a base version that changes whenever the application
    code is modified, ensuring cache invalidation on code updates.
    code is modified, ensuring cache invalidation on code updates.


    Returns:
    Returns:
    Application version hash string
    Application version hash string
    """
    """
    # Start with app directory and Python version
    # Start with app directory and Python version
    app_info = f"{os.path.dirname(sys.modules['__main__'].__file__)}:{sys.version}"
    app_info = f"{os.path.dirname(sys.modules['__main__'].__file__)}:{sys.version}"


    # Add main module file path and timestamp
    # Add main module file path and timestamp
    try:
    try:
    main_module = sys.modules["__main__"]
    main_module = sys.modules["__main__"]
    main_path = getattr(main_module, "__file__", "")
    main_path = getattr(main_module, "__file__", "")
    if main_path and os.path.exists(main_path):
    if main_path and os.path.exists(main_path):
    app_info += f":{main_path}:{os.path.getmtime(main_path)}"
    app_info += f":{main_path}:{os.path.getmtime(main_path)}"
except (AttributeError, OSError):
except (AttributeError, OSError):
    pass
    pass


    # Hash the combined information
    # Hash the combined information
    return hashlib.md5(app_info.encode()).hexdigest()
    return hashlib.md5(app_info.encode()).hexdigest()




    # Create a default instance for use throughout the application
    # Create a default instance for use throughout the application
    version_manager = CacheVersionManager()
    version_manager = CacheVersionManager()




    def generate_versioned_key(
    def generate_versioned_key(
    func: Callable,
    func: Callable,
    args: Tuple,
    args: Tuple,
    kwargs: Dict[str, Any],
    kwargs: Dict[str, Any],
    namespace: str,
    namespace: str,
    include_func_version: bool = True,
    include_func_version: bool = True,
    base_key: Optional[str] = None,
    base_key: Optional[str] = None,
    ) -> str:
    ) -> str:
    """
    """
    Generate a versioned cache key for a function call.
    Generate a versioned cache key for a function call.


    This combines the base key generation with version information to ensure
    This combines the base key generation with version information to ensure
    proper cache invalidation when code changes.
    proper cache invalidation when code changes.


    Args:
    Args:
    func: Function being called
    func: Function being called
    args: Function positional arguments
    args: Function positional arguments
    kwargs: Function keyword arguments
    kwargs: Function keyword arguments
    namespace: Cache namespace
    namespace: Cache namespace
    include_func_version: Whether to include function source code in version
    include_func_version: Whether to include function source code in version
    base_key: Optional base key to use instead of generating one
    base_key: Optional base key to use instead of generating one


    Returns:
    Returns:
    Versioned cache key
    Versioned cache key
    """
    """
    # Start with base key - either provided or generated
    # Start with base key - either provided or generated
    if base_key is None:
    if base_key is None:
    base_key = _generate_cache_key(func, args, kwargs)
    base_key = _generate_cache_key(func, args, kwargs)


    # Add function version to namespace if requested
    # Add function version to namespace if requested
    if include_func_version:
    if include_func_version:
    func_version = version_manager.get_function_version_hash(func)
    func_version = version_manager.get_function_version_hash(func)
    versioned_namespace = f"{namespace}.{func_version[:8]}"
    versioned_namespace = f"{namespace}.{func_version[:8]}"
    else:
    else:
    versioned_namespace = namespace
    versioned_namespace = namespace


    # Version the key
    # Version the key
    return version_manager.version_cache_key(base_key, versioned_namespace)
    return version_manager.version_cache_key(base_key, versioned_namespace)




    def clear_namespace_on_code_change(namespace: str, func_or_class: Any = None) -> None:
    def clear_namespace_on_code_change(namespace: str, func_or_class: Any = None) -> None:
    """
    """
    Register a namespace to be cleared when specific code changes.
    Register a namespace to be cleared when specific code changes.


    This ties a cache namespace to a specific function, method or class,
    This ties a cache namespace to a specific function, method or class,
    ensuring the cache is invalidated when that code changes.
    ensuring the cache is invalidated when that code changes.


    Args:
    Args:
    namespace: Cache namespace to monitor
    namespace: Cache namespace to monitor
    func_or_class: Function or class to monitor for changes
    func_or_class: Function or class to monitor for changes
    """
    """
    if func_or_class is None:
    if func_or_class is None:
    # Try to determine the caller
    # Try to determine the caller
    frame = inspect.currentframe().f_back
    frame = inspect.currentframe().f_back
    try:
    try:
    func_or_class = frame.f_locals.get("sel", None).__class__
    func_or_class = frame.f_locals.get("sel", None).__class__
except (AttributeError, KeyError):
except (AttributeError, KeyError):
    logger.warning(
    logger.warning(
    f"Could not automatically determine caller for namespace {namespace}"
    f"Could not automatically determine caller for namespace {namespace}"
    )
    )
    return # Generate new version based on function/class source
    return # Generate new version based on function/class source
    if inspect.isfunction(func_or_class) or inspect.ismethod(func_or_class):
    if inspect.isfunction(func_or_class) or inspect.ismethod(func_or_class):
    new_version = version_manager.get_function_version_hash(func_or_class)
    new_version = version_manager.get_function_version_hash(func_or_class)
    elif inspect.isclass(func_or_class):
    elif inspect.isclass(func_or_class):
    new_version = version_manager.get_class_version_hash(func_or_class)
    new_version = version_manager.get_class_version_hash(func_or_class)
    else:
    else:
    logger.warning(
    logger.warning(
    f"Unsupported object type for code change monitoring: {type(func_or_class)}"
    f"Unsupported object type for code change monitoring: {type(func_or_class)}"
    )
    )
    return # Update the namespace version
    return # Update the namespace version
    version_manager.update_namespace_version(namespace, f"code-{new_version}")
    version_manager.update_namespace_version(namespace, f"code-{new_version}")