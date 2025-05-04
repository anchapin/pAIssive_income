"""
"""
Local AI Integration Templates for the pAIssive Income project.
Local AI Integration Templates for the pAIssive Income project.


This module provides templates for integrating local AI models into your applications.
This module provides templates for integrating local AI models into your applications.
It includes classes and functions for loading models, processing user input, caching responses,
It includes classes and functions for loading models, processing user input, caching responses,
and handling errors.
and handling errors.


Dependencies:
    Dependencies:
    - transformers
    - transformers
    - torch
    - torch
    - sentence-transformers
    - sentence-transformers
    - llama-cpp-python (optional, for llama models)
    - llama-cpp-python (optional, for llama models)
    - onnxruntime (optional, for ONNX models)
    - onnxruntime (optional, for ONNX models)
    """
    """


    try:
    try:
    import torch  # noqa: F401
    import torch  # noqa: F401
    import transformers
    import transformers


    from sentence_transformers import SentenceTransformer
    from sentence_transformers import SentenceTransformer
    from transformers import (  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error
    from transformers import (  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error
    AutoModelForCausalLM, AutoTokenizer, pipeline)
    AutoModelForCausalLM, AutoTokenizer, pipeline)


    SENTENCE_TRANSFORMERS_AVAILABLE
    SENTENCE_TRANSFORMERS_AVAILABLE
    from llama_cpp import Llama
    from llama_cpp import Llama


    LLAMA_CPP_AVAILABLE
    LLAMA_CPP_AVAILABLE
    import onnxruntime
    import onnxruntime


    # Set up logging
    # Set up logging
    logging.basicConfig(
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    )
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)


    # Try to import optional dependencies
    # Try to import optional dependencies
    try:
    try:
    # noqa: F401
    # noqa: F401
    # noqa: F401
    # noqa: F401
    # noqa: F401
    # noqa: F401


    TRANSFORMERS_AVAILABLE = True
    TRANSFORMERS_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Transformers or PyTorch not available. Some functionality will be limited."
    "Transformers or PyTorch not available. Some functionality will be limited."
    )
    )
    TRANSFORMERS_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "Sentence Transformers not available. Embedding functionality will be limited."
    "Sentence Transformers not available. Embedding functionality will be limited."
    )
    )
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SENTENCE_TRANSFORMERS_AVAILABLE = False


    try:
    try:
    = True
    = True
except ImportError:
except ImportError:
    logger.warning(
    logger.warning(
    "llama-cpp-python not available. Llama model support will be limited."
    "llama-cpp-python not available. Llama model support will be limited."
    )
    )
    LLAMA_CPP_AVAILABLE = False
    LLAMA_CPP_AVAILABLE = False


    try:
    try:
    as ort  # noqa: F401
    as ort  # noqa: F401


    ONNX_AVAILABLE = True
    ONNX_AVAILABLE = True
except ImportError:
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False
    ONNX_AVAILABLE = False




    class ModelCache:
    class ModelCache:
    """
    """
    Cache for AI model responses to improve performance and reduce resource usage.
    Cache for AI model responses to improve performance and reduce resource usage.


    This implementation provides a two-tiered caching system:
    This implementation provides a two-tiered caching system:
    1. In-memory cache for fast access to frequently used items
    1. In-memory cache for fast access to frequently used items
    2. Persistent file-based cache for longer-term storage
    2. Persistent file-based cache for longer-term storage


    The cache uses a deterministic hashing algorithm to generate unique keys based on:
    The cache uses a deterministic hashing algorithm to generate unique keys based on:
    - Model name
    - Model name
    - Input text
    - Input text
    - Model parameters
    - Model parameters


    This ensures identical requests get the same cached response, reducing
    This ensures identical requests get the same cached response, reducing
    computational load and improving response times. The system also handles:
    computational load and improving response times. The system also handles:
    - Thread safety with locks for concurrent access
    - Thread safety with locks for concurrent access
    - TTL (time-to-live) expiration for cache items
    - TTL (time-to-live) expiration for cache items
    - LRU (least recently used) eviction policy for memory cache
    - LRU (least recently used) eviction policy for memory cache
    - Automatic cleanup of invalid or expired cache entries
    - Automatic cleanup of invalid or expired cache entries
    """
    """


    def __init__(
    def __init__(
    self, cache_dir: str = ".cache", max_size: int = 1000, ttl: int = 86400
    self, cache_dir: str = ".cache", max_size: int = 1000, ttl: int = 86400
    ):
    ):
    """
    """
    Initialize the model cache.
    Initialize the model cache.


    Args:
    Args:
    cache_dir: Directory to store cache files
    cache_dir: Directory to store cache files
    max_size: Maximum number of items to keep in memory cache
    max_size: Maximum number of items to keep in memory cache
    ttl: Time-to-live for cache items in seconds (default: 24 hours)
    ttl: Time-to-live for cache items in seconds (default: 24 hours)
    """
    """
    self.cache_dir = cache_dir
    self.cache_dir = cache_dir
    self.max_size = max_size
    self.max_size = max_size
    self.ttl = ttl
    self.ttl = ttl
    # The memory cache is a dictionary: {cache_key: {response, timestamp, metadata}}
    # The memory cache is a dictionary: {cache_key: {response, timestamp, metadata}}
    self.memory_cache = {}
    self.memory_cache = {}
    # Use a thread lock to ensure thread safety for cache operations
    # Use a thread lock to ensure thread safety for cache operations
    self.cache_lock = threading.Lock()
    self.cache_lock = threading.Lock()


    # Create cache directory if it doesn't exist
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    logger.info(f"Initialized model cache in {cache_dir}")
    logger.info(f"Initialized model cache in {cache_dir}")


    def _get_cache_key(
    def _get_cache_key(
    self, model_name: str, input_text: str, params: Dict[str, Any]
    self, model_name: str, input_text: str, params: Dict[str, Any]
    ) -> str:
    ) -> str:
    """
    """
    Generate a cache key from the model name, input text, and parameters.
    Generate a cache key from the model name, input text, and parameters.


    This method creates a deterministic hash that uniquely identifies a specific
    This method creates a deterministic hash that uniquely identifies a specific
    model inference request based on all its inputs. The algorithm:
    model inference request based on all its inputs. The algorithm:
    1. Converts parameters to a consistent string representation
    1. Converts parameters to a consistent string representation
    2. Concatenates model name, input text, and parameters
    2. Concatenates model name, input text, and parameters
    3. Creates an MD5 hash of this string for a compact, fixed-length key
    3. Creates an MD5 hash of this string for a compact, fixed-length key


    Using a cryptographic hash function ensures:
    Using a cryptographic hash function ensures:
    - Uniformity: Even small changes in input produce different keys
    - Uniformity: Even small changes in input produce different keys
    - Determinism: Same inputs always produce the same key
    - Determinism: Same inputs always produce the same key
    - Fixed length: Keys have consistent length regardless of input size
    - Fixed length: Keys have consistent length regardless of input size


    Args:
    Args:
    model_name: Name of the model
    model_name: Name of the model
    input_text: Input text to the model
    input_text: Input text to the model
    params: Model parameters
    params: Model parameters


    Returns:
    Returns:
    Cache key string
    Cache key string
    """
    """
    # Create a string representation of the parameters
    # Create a string representation of the parameters
    # Sort the keys to ensure consistent ordering regardless of dict creation order
    # Sort the keys to ensure consistent ordering regardless of dict creation order
    params_str = json.dumps(params, sort_keys=True)
    params_str = json.dumps(params, sort_keys=True)


    # Create a hash of the input and parameters
    # Create a hash of the input and parameters
    # Using MD5 for speed and sufficient collision resistance for caching
    # Using MD5 for speed and sufficient collision resistance for caching
    key = hashlib.md5(
    key = hashlib.md5(
    f"{model_name}:{input_text}:{params_str}".encode()
    f"{model_name}:{input_text}:{params_str}".encode()
    ).hexdigest()
    ).hexdigest()


    return key
    return key


    def _get_cache_file_path(self, key: str) -> str:
    def _get_cache_file_path(self, key: str) -> str:
    """
    """
    Get the file path for a cache item.
    Get the file path for a cache item.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    File path for the cache item
    File path for the cache item
    """
    """
    return os.path.join(self.cache_dir, f"{key}.json")
    return os.path.join(self.cache_dir, f"{key}.json")


    def get(
    def get(
    self, model_name: str, input_text: str, params: Dict[str, Any]
    self, model_name: str, input_text: str, params: Dict[str, Any]
    ) -> Optional[Any]:
    ) -> Optional[Any]:
    """
    """
    Get a cached response if available.
    Get a cached response if available.


    This method implements the cache lookup strategy:
    This method implements the cache lookup strategy:
    1. Generate a unique cache key for the request
    1. Generate a unique cache key for the request
    2. First check memory cache (fast, but volatile)
    2. First check memory cache (fast, but volatile)
    3. If not in memory, check file cache (slower, but persistent)
    3. If not in memory, check file cache (slower, but persistent)
    4. In both cases, verify the cache item hasn't expired (TTL)
    4. In both cases, verify the cache item hasn't expired (TTL)
    5. For file cache hits, load into memory cache for faster future access
    5. For file cache hits, load into memory cache for faster future access
    6. Apply LRU eviction if memory cache exceeds max size
    6. Apply LRU eviction if memory cache exceeds max size


    The multi-tiered approach balances speed (memory) with persistence (file),
    The multi-tiered approach balances speed (memory) with persistence (file),
    while the TTL mechanism ensures cached data doesn't become stale.
    while the TTL mechanism ensures cached data doesn't become stale.


    Args:
    Args:
    model_name: Name of the model
    model_name: Name of the model
    input_text: Input text to the model
    input_text: Input text to the model
    params: Model parameters
    params: Model parameters


    Returns:
    Returns:
    Cached response or None if not found/expired
    Cached response or None if not found/expired
    """
    """
    key = self._get_cache_key(model_name, input_text, params)
    key = self._get_cache_key(model_name, input_text, params)


    # Check memory cache first (fast access)
    # Check memory cache first (fast access)
    with self.cache_lock:
    with self.cache_lock:
    if key in self.memory_cache:
    if key in self.memory_cache:
    cache_item = self.memory_cache[key]
    cache_item = self.memory_cache[key]
    # Check if the item is still valid (not expired)
    # Check if the item is still valid (not expired)
    if time.time() - cache_item["timestamp"] < self.ttl:
    if time.time() - cache_item["timestamp"] < self.ttl:
    logger.debug(f"Cache hit (memory): {key}")
    logger.debug(f"Cache hit (memory): {key}")
    return cache_item["response"]
    return cache_item["response"]
    else:
    else:
    # Remove expired item from memory cache
    # Remove expired item from memory cache
    del self.memory_cache[key]
    del self.memory_cache[key]


    # If not in memory cache or expired, check file cache
    # If not in memory cache or expired, check file cache
    cache_file = self._get_cache_file_path(key)
    cache_file = self._get_cache_file_path(key)
    if os.path.exists(cache_file):
    if os.path.exists(cache_file):
    try:
    try:
    with open(cache_file, "r") as f:
    with open(cache_file, "r") as f:
    cache_item = json.load(f)
    cache_item = json.load(f)


    # Check if the item is still valid (not expired)
    # Check if the item is still valid (not expired)
    if time.time() - cache_item["timestamp"] < self.ttl:
    if time.time() - cache_item["timestamp"] < self.ttl:
    # Add to memory cache for faster future access
    # Add to memory cache for faster future access
    with self.cache_lock:
    with self.cache_lock:
    self.memory_cache[key] = cache_item
    self.memory_cache[key] = cache_item


    # Implement LRU eviction if memory cache exceeds max size
    # Implement LRU eviction if memory cache exceeds max size
    if len(self.memory_cache) > self.max_size:
    if len(self.memory_cache) > self.max_size:
    # Find and remove the oldest item (lowest timestamp)
    # Find and remove the oldest item (lowest timestamp)
    oldest_key = min(
    oldest_key = min(
    self.memory_cache.keys(),
    self.memory_cache.keys(),
    key=lambda k: self.memory_cache[k]["timestamp"],
    key=lambda k: self.memory_cache[k]["timestamp"],
    )
    )
    del self.memory_cache[oldest_key]
    del self.memory_cache[oldest_key]


    logger.debug(f"Cache hit (file): {key}")
    logger.debug(f"Cache hit (file): {key}")
    return cache_item["response"]
    return cache_item["response"]
    else:
    else:
    # Remove expired cache file
    # Remove expired cache file
    os.remove(cache_file)
    os.remove(cache_file)
except (json.JSONDecodeError, KeyError) as e:
except (json.JSONDecodeError, KeyError) as e:
    # Handle corrupted cache files
    # Handle corrupted cache files
    logger.warning(f"Error reading cache file {cache_file}: {e}")
    logger.warning(f"Error reading cache file {cache_file}: {e}")
    # Remove corrupted cache file
    # Remove corrupted cache file
    os.remove(cache_file)
    os.remove(cache_file)


    # Cache miss if execution reaches here
    # Cache miss if execution reaches here
    logger.debug(f"Cache miss: {key}")
    logger.debug(f"Cache miss: {key}")
    return None
    return None


    def set(
    def set(
    self, model_name: str, input_text: str, params: Dict[str, Any], response: Any
    self, model_name: str, input_text: str, params: Dict[str, Any], response: Any
    ) -> None:
    ) -> None:
    """
    """
    Cache a model response.
    Cache a model response.


    This method implements the cache storage strategy:
    This method implements the cache storage strategy:
    1. Generate a unique cache key for the request
    1. Generate a unique cache key for the request
    2. Create a cache item with response data and metadata
    2. Create a cache item with response data and metadata
    3. Store in memory cache with thread safety
    3. Store in memory cache with thread safety
    4. Implement LRU eviction if memory cache exceeds max size
    4. Implement LRU eviction if memory cache exceeds max size
    5. Persist to file cache for longer-term storage
    5. Persist to file cache for longer-term storage


    The dual storage approach ensures fast access for frequently used items
    The dual storage approach ensures fast access for frequently used items
    while maintaining persistence across application restarts.
    while maintaining persistence across application restarts.


    Args:
    Args:
    model_name: Name of the model
    model_name: Name of the model
    input_text: Input text to the model
    input_text: Input text to the model
    params: Model parameters
    params: Model parameters
    response: Model response to cache
    response: Model response to cache
    """
    """
    key = self._get_cache_key(model_name, input_text, params)
    key = self._get_cache_key(model_name, input_text, params)
    timestamp = time.time()
    timestamp = time.time()


    # Create cache item with response and metadata
    # Create cache item with response and metadata
    cache_item = {
    cache_item = {
    "model_name": model_name,
    "model_name": model_name,
    "input_text": input_text,
    "input_text": input_text,
    "params": params,
    "params": params,
    "response": response,
    "response": response,
    "timestamp": timestamp,
    "timestamp": timestamp,
    }
    }


    # Add to memory cache with thread safety
    # Add to memory cache with thread safety
    with self.cache_lock:
    with self.cache_lock:
    self.memory_cache[key] = cache_item
    self.memory_cache[key] = cache_item


    # Apply LRU eviction if memory cache exceeds max size
    # Apply LRU eviction if memory cache exceeds max size
    if len(self.memory_cache) > self.max_size:
    if len(self.memory_cache) > self.max_size:
    # Find and remove the oldest item (lowest timestamp)
    # Find and remove the oldest item (lowest timestamp)
    oldest_key = min(
    oldest_key = min(
    self.memory_cache.keys(),
    self.memory_cache.keys(),
    key=lambda k: self.memory_cache[k]["timestamp"],
    key=lambda k: self.memory_cache[k]["timestamp"],
    )
    )
    del self.memory_cache[oldest_key]
    del self.memory_cache[oldest_key]


    # Persist to file cache
    # Persist to file cache
    cache_file = self._get_cache_file_path(key)
    cache_file = self._get_cache_file_path(key)
    try:
    try:
    with open(cache_file, "w") as f:
    with open(cache_file, "w") as f:
    json.dump(cache_item, f)
    json.dump(cache_item, f)
    logger.debug(f"Cached response: {key}")
    logger.debug(f"Cached response: {key}")
except Exception as e:
except Exception as e:
    logger.warning(f"Error writing cache file {cache_file}: {e}")
    logger.warning(f"Error writing cache file {cache_file}: {e}")


    def clear(self, older_than: Optional[int] = None) -> int:
    def clear(self, older_than: Optional[int] = None) -> int:
    """
    """
    Clear the cache.
    Clear the cache.


    This method provides cache maintenance with two modes:
    This method provides cache maintenance with two modes:
    1. Complete clear: Remove all cache items (memory and file)
    1. Complete clear: Remove all cache items (memory and file)
    2. Age-based clear: Remove only items older than a specified time
    2. Age-based clear: Remove only items older than a specified time


    The age-based option is particularly useful for:
    The age-based option is particularly useful for:
    - Periodic cleanup of stale data
    - Periodic cleanup of stale data
    - Clearing only old data while preserving recent items
    - Clearing only old data while preserving recent items
    - Managing cache size without complete invalidation
    - Managing cache size without complete invalidation


    Thread safety is maintained through locks for memory cache operations.
    Thread safety is maintained through locks for memory cache operations.


    Args:
    Args:
    older_than: Clear items older than this many seconds
    older_than: Clear items older than this many seconds
    If None, clear all items
    If None, clear all items


    Returns:
    Returns:
    Number of items cleared
    Number of items cleared
    """
    """
    count = 0
    count = 0


    # Clear memory cache with thread safety
    # Clear memory cache with thread safety
    with self.cache_lock:
    with self.cache_lock:
    if older_than is not None:
    if older_than is not None:
    # Age-based clear for memory cache
    # Age-based clear for memory cache
    current_time = time.time()
    current_time = time.time()
    keys_to_remove = [
    keys_to_remove = [
    key
    key
    for key, item in self.memory_cache.items()
    for key, item in self.memory_cache.items()
    if current_time - item["timestamp"] > older_than
    if current_time - item["timestamp"] > older_than
    ]
    ]
    for key in keys_to_remove:
    for key in keys_to_remove:
    del self.memory_cache[key]
    del self.memory_cache[key]
    count += len(keys_to_remove)
    count += len(keys_to_remove)
    else:
    else:
    # Complete clear for memory cache
    # Complete clear for memory cache
    count += len(self.memory_cache)
    count += len(self.memory_cache)
    self.memory_cache.clear()
    self.memory_cache.clear()


    # Clear file cache
    # Clear file cache
    for filename in os.listdir(self.cache_dir):
    for filename in os.listdir(self.cache_dir):
    if filename.endswith(".json"):
    if filename.endswith(".json"):
    file_path = os.path.join(self.cache_dir, filename)
    file_path = os.path.join(self.cache_dir, filename)
    try:
    try:
    if older_than is not None:
    if older_than is not None:
    # Age-based clear for file cache
    # Age-based clear for file cache
    # Use file modification time as a proxy for cache item timestamp
    # Use file modification time as a proxy for cache item timestamp
    file_time = os.path.getmtime(file_path)
    file_time = os.path.getmtime(file_path)
    if time.time() - file_time > older_than:
    if time.time() - file_time > older_than:
    os.remove(file_path)
    os.remove(file_path)
    count += 1
    count += 1
    else:
    else:
    # Complete clear for file cache
    # Complete clear for file cache
    os.remove(file_path)
    os.remove(file_path)
    count += 1
    count += 1
except OSError as e:
except OSError as e:
    logger.warning(f"Error removing cache file {file_path}: {e}")
    logger.warning(f"Error removing cache file {file_path}: {e}")


    logger.info(f"Cleared {count} items from cache")
    logger.info(f"Cleared {count} items from cache")
    return count
    return count




    class BaseLocalAIModel(ABC):
    class BaseLocalAIModel(ABC):
    """
    """
    Abstract base class for local AI models.
    Abstract base class for local AI models.
    """
    """


    def __init__(self, model_name: str, cache_enabled: bool = True):
    def __init__(self, model_name: str, cache_enabled: bool = True):
    """
    """
    Initialize the base local AI model.
    Initialize the base local AI model.


    Args:
    Args:
    model_name: Name of the model
    model_name: Name of the model
    cache_enabled: Whether to enable response caching
    cache_enabled: Whether to enable response caching
    """
    """
    self.model_name = model_name
    self.model_name = model_name
    self.cache_enabled = cache_enabled
    self.cache_enabled = cache_enabled
    self.cache = ModelCache() if cache_enabled else None
    self.cache = ModelCache() if cache_enabled else None
    self.model = None
    self.model = None
    self.initialized = False
    self.initialized = False
    logger.info(f"Initializing {self.__class__.__name__} with model {model_name}")
    logger.info(f"Initializing {self.__class__.__name__} with model {model_name}")


    @abstractmethod
    @abstractmethod
    def load_model(self) -> None:
    def load_model(self) -> None:
    """
    """
    Load the AI model.
    Load the AI model.
    """
    """
    pass
    pass


    @abstractmethod
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
    def generate_text(self, prompt: str, **kwargs) -> str:
    """
    """
    Generate text based on a prompt.
    Generate text based on a prompt.


    Args:
    Args:
    prompt: Input prompt
    prompt: Input prompt
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    pass
    pass


    def _get_cached_response(
    def _get_cached_response(
    self, prompt: str, params: Dict[str, Any]
    self, prompt: str, params: Dict[str, Any]
    ) -> Optional[str]:
    ) -> Optional[str]:
    """
    """
    Get a cached response if available.
    Get a cached response if available.


    Args:
    Args:
    prompt: Input prompt
    prompt: Input prompt
    params: Generation parameters
    params: Generation parameters


    Returns:
    Returns:
    Cached response or None if not found
    Cached response or None if not found
    """
    """
    if self.cache_enabled and self.cache is not None:
    if self.cache_enabled and self.cache is not None:
    return self.cache.get(self.model_name, prompt, params)
    return self.cache.get(self.model_name, prompt, params)
    return None
    return None


    def _cache_response(
    def _cache_response(
    self, prompt: str, params: Dict[str, Any], response: str
    self, prompt: str, params: Dict[str, Any], response: str
    ) -> None:
    ) -> None:
    """
    """
    Cache a model response.
    Cache a model response.


    Args:
    Args:
    prompt: Input prompt
    prompt: Input prompt
    params: Generation parameters
    params: Generation parameters
    response: Model response to cache
    response: Model response to cache
    """
    """
    if self.cache_enabled and self.cache is not None:
    if self.cache_enabled and self.cache is not None:
    self.cache.set(self.model_name, prompt, params, response)
    self.cache.set(self.model_name, prompt, params, response)




    class HuggingFaceModel(BaseLocalAIModel):
    class HuggingFaceModel(BaseLocalAIModel):
    """
    """
    Local AI model using Hugging Face Transformers.
    Local AI model using Hugging Face Transformers.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_name: str,
    model_name: str,
    model_type: str = "text-generation",
    model_type: str = "text-generation",
    device: str = "auto",
    device: str = "auto",
    cache_enabled: bool = True,
    cache_enabled: bool = True,
    **model_kwargs,
    **model_kwargs,
    ):
    ):
    """
    """
    Initialize a Hugging Face model.
    Initialize a Hugging Face model.


    Args:
    Args:
    model_name: Name or path of the model
    model_name: Name or path of the model
    model_type: Type of model (text-generation, text2text-generation, etc.)
    model_type: Type of model (text-generation, text2text-generation, etc.)
    device: Device to run the model on (auto, cpu, cuda, etc.)
    device: Device to run the model on (auto, cpu, cuda, etc.)
    cache_enabled: Whether to enable response caching
    cache_enabled: Whether to enable response caching
    **model_kwargs: Additional parameters for model initialization
    **model_kwargs: Additional parameters for model initialization
    """
    """
    super().__init__(model_name, cache_enabled)
    super().__init__(model_name, cache_enabled)


    if not TRANSFORMERS_AVAILABLE:
    if not TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Transformers or PyTorch not available. Please install them with: pip install transformers torch"
    "Transformers or PyTorch not available. Please install them with: pip install transformers torch"
    )
    )


    self.model_type = model_type
    self.model_type = model_type
    self.device = device
    self.device = device
    self.model_kwargs = model_kwargs
    self.model_kwargs = model_kwargs
    self.tokenizer = None
    self.tokenizer = None
    self.pipeline = None
    self.pipeline = None


    def load_model(self) -> None:
    def load_model(self) -> None:
    """
    """
    Load the Hugging Face model.
    Load the Hugging Face model.
    """
    """
    logger.info(f"Loading Hugging Face model: {self.model_name}")
    logger.info(f"Loading Hugging Face model: {self.model_name}")


    try:
    try:
    # Determine device
    # Determine device
    if self.device == "auto":
    if self.device == "auto":
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    self.device = "cuda" if torch.cuda.is_available() else "cpu"


    # Load tokenizer
    # Load tokenizer
    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)


    # Create pipeline
    # Create pipeline
    self.pipeline = pipeline(
    self.pipeline = pipeline(
    self.model_type,
    self.model_type,
    model=self.model_name,
    model=self.model_name,
    tokenizer=self.tokenizer,
    tokenizer=self.tokenizer,
    device=self.device,
    device=self.device,
    **self.model_kwargs,
    **self.model_kwargs,
    )
    )


    self.initialized = True
    self.initialized = True
    logger.info(f"Successfully loaded model {self.model_name} on {self.device}")
    logger.info(f"Successfully loaded model {self.model_name} on {self.device}")


except Exception as e:
except Exception as e:
    logger.error(f"Error loading model {self.model_name}: {e}")
    logger.error(f"Error loading model {self.model_name}: {e}")
    raise
    raise


    def generate_text(
    def generate_text(
    self,
    self,
    prompt: str,
    prompt: str,
    max_length: int = 1000,
    max_length: int = 1000,
    temperature: float = 0.7,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_p: float = 0.9,
    top_k: int = 50,
    top_k: int = 50,
    num_return_sequences: int = 1,
    num_return_sequences: int = 1,
    **kwargs,
    **kwargs,
    ) -> str:
    ) -> str:
    """
    """
    Generate text using the Hugging Face model.
    Generate text using the Hugging Face model.


    Args:
    Args:
    prompt: Input prompt
    prompt: Input prompt
    max_length: Maximum length of generated text
    max_length: Maximum length of generated text
    temperature: Temperature for sampling
    temperature: Temperature for sampling
    top_p: Top-p sampling parameter
    top_p: Top-p sampling parameter
    top_k: Top-k sampling parameter
    top_k: Top-k sampling parameter
    num_return_sequences: Number of sequences to generate
    num_return_sequences: Number of sequences to generate
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    if not self.initialized:
    if not self.initialized:
    self.load_model()
    self.load_model()


    # Prepare parameters
    # Prepare parameters
    params = {
    params = {
    "max_length": max_length,
    "max_length": max_length,
    "temperature": temperature,
    "temperature": temperature,
    "top_p": top_p,
    "top_p": top_p,
    "top_k": top_k,
    "top_k": top_k,
    "num_return_sequences": num_return_sequences,
    "num_return_sequences": num_return_sequences,
    **kwargs,
    **kwargs,
    }
    }


    # Check cache
    # Check cache
    cached_response = self._get_cached_response(prompt, params)
    cached_response = self._get_cached_response(prompt, params)
    if cached_response is not None:
    if cached_response is not None:
    return cached_response
    return cached_response


    try:
    try:
    # Generate text
    # Generate text
    outputs = self.pipeline(prompt, **params)
    outputs = self.pipeline(prompt, **params)


    # Process output based on pipeline type
    # Process output based on pipeline type
    if self.model_type == "text-generation":
    if self.model_type == "text-generation":
    if num_return_sequences == 1:
    if num_return_sequences == 1:
    response = outputs[0]["generated_text"]
    response = outputs[0]["generated_text"]
    else:
    else:
    response = [output["generated_text"] for output in outputs]
    response = [output["generated_text"] for output in outputs]
    else:
    else:
    response = outputs
    response = outputs


    # Cache response
    # Cache response
    self._cache_response(prompt, params, response)
    self._cache_response(prompt, params, response)


    return response
    return response


except Exception as e:
except Exception as e:
    logger.error(f"Error generating text: {e}")
    logger.error(f"Error generating text: {e}")
    raise
    raise




    class LlamaModel(BaseLocalAIModel):
    class LlamaModel(BaseLocalAIModel):
    """
    """
    Local AI model using llama.cpp.
    Local AI model using llama.cpp.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_path: str,
    model_path: str,
    n_ctx: int = 2048,
    n_ctx: int = 2048,
    n_threads: Optional[int] = None,
    n_threads: Optional[int] = None,
    cache_enabled: bool = True,
    cache_enabled: bool = True,
    **model_kwargs,
    **model_kwargs,
    ):
    ):
    """
    """
    Initialize a Llama model.
    Initialize a Llama model.


    Args:
    Args:
    model_path: Path to the model file
    model_path: Path to the model file
    n_ctx: Context size
    n_ctx: Context size
    n_threads: Number of threads to use
    n_threads: Number of threads to use
    cache_enabled: Whether to enable response caching
    cache_enabled: Whether to enable response caching
    **model_kwargs: Additional parameters for model initialization
    **model_kwargs: Additional parameters for model initialization
    """
    """
    super().__init__(os.path.basename(model_path), cache_enabled)
    super().__init__(os.path.basename(model_path), cache_enabled)


    if not LLAMA_CPP_AVAILABLE:
    if not LLAMA_CPP_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "llama-cpp-python not available. Please install it with: pip install llama-cpp-python"
    "llama-cpp-python not available. Please install it with: pip install llama-cpp-python"
    )
    )


    self.model_path = model_path
    self.model_path = model_path
    self.n_ctx = n_ctx
    self.n_ctx = n_ctx
    self.n_threads = n_threads or max(1, os.cpu_count() // 2)
    self.n_threads = n_threads or max(1, os.cpu_count() // 2)
    self.model_kwargs = model_kwargs
    self.model_kwargs = model_kwargs


    def load_model(self) -> None:
    def load_model(self) -> None:
    """
    """
    Load the Llama model.
    Load the Llama model.
    """
    """
    logger.info(f"Loading Llama model: {self.model_path}")
    logger.info(f"Loading Llama model: {self.model_path}")


    try:
    try:
    self.model = Llama(
    self.model = Llama(
    model_path=self.model_path,
    model_path=self.model_path,
    n_ctx=self.n_ctx,
    n_ctx=self.n_ctx,
    n_threads=self.n_threads,
    n_threads=self.n_threads,
    **self.model_kwargs,
    **self.model_kwargs,
    )
    )


    self.initialized = True
    self.initialized = True
    logger.info(f"Successfully loaded model {self.model_path}")
    logger.info(f"Successfully loaded model {self.model_path}")


except Exception as e:
except Exception as e:
    logger.error(f"Error loading model {self.model_path}: {e}")
    logger.error(f"Error loading model {self.model_path}: {e}")
    raise
    raise


    def generate_text(
    def generate_text(
    self,
    self,
    prompt: str,
    prompt: str,
    max_tokens: int = 512,
    max_tokens: int = 512,
    temperature: float = 0.7,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_p: float = 0.9,
    top_k: int = 40,
    top_k: int = 40,
    stop: Optional[List[str]] = None,
    stop: Optional[List[str]] = None,
    **kwargs,
    **kwargs,
    ) -> str:
    ) -> str:
    """
    """
    Generate text using the Llama model.
    Generate text using the Llama model.


    Args:
    Args:
    prompt: Input prompt
    prompt: Input prompt
    max_tokens: Maximum number of tokens to generate
    max_tokens: Maximum number of tokens to generate
    temperature: Temperature for sampling
    temperature: Temperature for sampling
    top_p: Top-p sampling parameter
    top_p: Top-p sampling parameter
    top_k: Top-k sampling parameter
    top_k: Top-k sampling parameter
    stop: List of strings to stop generation when encountered
    stop: List of strings to stop generation when encountered
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    Generated text
    Generated text
    """
    """
    if not self.initialized:
    if not self.initialized:
    self.load_model()
    self.load_model()


    # Prepare parameters
    # Prepare parameters
    params = {
    params = {
    "max_tokens": max_tokens,
    "max_tokens": max_tokens,
    "temperature": temperature,
    "temperature": temperature,
    "top_p": top_p,
    "top_p": top_p,
    "top_k": top_k,
    "top_k": top_k,
    "stop": stop,
    "stop": stop,
    **kwargs,
    **kwargs,
    }
    }


    # Check cache
    # Check cache
    cached_response = self._get_cached_response(prompt, params)
    cached_response = self._get_cached_response(prompt, params)
    if cached_response is not None:
    if cached_response is not None:
    return cached_response
    return cached_response


    try:
    try:
    # Generate text
    # Generate text
    output = self.model(
    output = self.model(
    prompt,
    prompt,
    max_tokens=max_tokens,
    max_tokens=max_tokens,
    temperature=temperature,
    temperature=temperature,
    top_p=top_p,
    top_p=top_p,
    top_k=top_k,
    top_k=top_k,
    stop=stop,
    stop=stop,
    **kwargs,
    **kwargs,
    )
    )


    response = output["choices"][0]["text"]
    response = output["choices"][0]["text"]


    # Cache response
    # Cache response
    self._cache_response(prompt, params, response)
    self._cache_response(prompt, params, response)


    return response
    return response


except Exception as e:
except Exception as e:
    logger.error(f"Error generating text: {e}")
    logger.error(f"Error generating text: {e}")
    raise
    raise




    class EmbeddingModel(BaseLocalAIModel):
    class EmbeddingModel(BaseLocalAIModel):
    """
    """
    Local AI model for generating embeddings.
    Local AI model for generating embeddings.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    model_name: str = "all-MiniLM-L6-v2",
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "auto",
    device: str = "auto",
    cache_enabled: bool = True,
    cache_enabled: bool = True,
    **model_kwargs,
    **model_kwargs,
    ):
    ):
    """
    """
    Initialize an embedding model.
    Initialize an embedding model.


    Args:
    Args:
    model_name: Name or path of the model
    model_name: Name or path of the model
    device: Device to run the model on (auto, cpu, cuda, etc.)
    device: Device to run the model on (auto, cpu, cuda, etc.)
    cache_enabled: Whether to enable response caching
    cache_enabled: Whether to enable response caching
    **model_kwargs: Additional parameters for model initialization
    **model_kwargs: Additional parameters for model initialization
    """
    """
    super().__init__(model_name, cache_enabled)
    super().__init__(model_name, cache_enabled)


    if not SENTENCE_TRANSFORMERS_AVAILABLE:
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "Sentence Transformers not available. Please install it with: pip install sentence-transformers"
    "Sentence Transformers not available. Please install it with: pip install sentence-transformers"
    )
    )


    self.device = device
    self.device = device
    self.model_kwargs = model_kwargs
    self.model_kwargs = model_kwargs


    def load_model(self) -> None:
    def load_model(self) -> None:
    """
    """
    Load the embedding model.
    Load the embedding model.
    """
    """
    logger.info(f"Loading embedding model: {self.model_name}")
    logger.info(f"Loading embedding model: {self.model_name}")


    try:
    try:
    # Determine device
    # Determine device
    if self.device == "auto":
    if self.device == "auto":
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    self.device = "cuda" if torch.cuda.is_available() else "cpu"


    # Load model
    # Load model
    self.model = SentenceTransformer(
    self.model = SentenceTransformer(
    self.model_name, device=self.device, **self.model_kwargs
    self.model_name, device=self.device, **self.model_kwargs
    )
    )


    self.initialized = True
    self.initialized = True
    logger.info(f"Successfully loaded model {self.model_name} on {self.device}")
    logger.info(f"Successfully loaded model {self.model_name} on {self.device}")


except Exception as e:
except Exception as e:
    logger.error(f"Error loading model {self.model_name}: {e}")
    logger.error(f"Error loading model {self.model_name}: {e}")
    raise
    raise


    def generate_text(self, prompt: str, **kwargs) -> str:
    def generate_text(self, prompt: str, **kwargs) -> str:
    """
    """
    Not applicable for embedding models.
    Not applicable for embedding models.
    """
    """
    raise NotImplementedError(
    raise NotImplementedError(
    "Embedding models do not support text generation. Use encode() instead."
    "Embedding models do not support text generation. Use encode() instead."
    )
    )


    def encode(
    def encode(
    self,
    self,
    texts: Union[str, List[str]],
    texts: Union[str, List[str]],
    batch_size: int = 32,
    batch_size: int = 32,
    normalize_embeddings: bool = True,
    normalize_embeddings: bool = True,
    **kwargs,
    **kwargs,
    ) -> Union[List[float], List[List[float]]]:
    ) -> Union[List[float], List[List[float]]]:
    """
    """
    Generate embeddings for text.
    Generate embeddings for text.


    Args:
    Args:
    texts: Input text or list of texts
    texts: Input text or list of texts
    batch_size: Batch size for encoding
    batch_size: Batch size for encoding
    normalize_embeddings: Whether to normalize embeddings
    normalize_embeddings: Whether to normalize embeddings
    **kwargs: Additional parameters for encoding
    **kwargs: Additional parameters for encoding


    Returns:
    Returns:
    Text embeddings
    Text embeddings
    """
    """
    if not self.initialized:
    if not self.initialized:
    self.load_model()
    self.load_model()


    # Prepare parameters
    # Prepare parameters
    params = {
    params = {
    "batch_size": batch_size,
    "batch_size": batch_size,
    "normalize_embeddings": normalize_embeddings,
    "normalize_embeddings": normalize_embeddings,
    **kwargs,
    **kwargs,
    }
    }


    # For caching, we need a string key
    # For caching, we need a string key
    if isinstance(texts, list):
    if isinstance(texts, list):
    cache_key = json.dumps(texts)
    cache_key = json.dumps(texts)
    else:
    else:
    cache_key = texts
    cache_key = texts


    # Check cache
    # Check cache
    cached_response = self._get_cached_response(cache_key, params)
    cached_response = self._get_cached_response(cache_key, params)
    if cached_response is not None:
    if cached_response is not None:
    return cached_response
    return cached_response


    try:
    try:
    # Generate embeddings
    # Generate embeddings
    embeddings = self.model.encode(
    embeddings = self.model.encode(
    texts,
    texts,
    batch_size=batch_size,
    batch_size=batch_size,
    normalize_embeddings=normalize_embeddings,
    normalize_embeddings=normalize_embeddings,
    **kwargs,
    **kwargs,
    )
    )


    # Convert to list for JSON serialization
    # Convert to list for JSON serialization
    if isinstance(embeddings, torch.Tensor):
    if isinstance(embeddings, torch.Tensor):
    embeddings = embeddings.tolist()
    embeddings = embeddings.tolist()
    elif isinstance(embeddings, list) and isinstance(
    elif isinstance(embeddings, list) and isinstance(
    embeddings[0], torch.Tensor
    embeddings[0], torch.Tensor
    ):
    ):
    embeddings = [emb.tolist() for emb in embeddings]
    embeddings = [emb.tolist() for emb in embeddings]
    elif (
    elif (
    isinstance(embeddings, list)
    isinstance(embeddings, list)
    and isinstance(embeddings[0], list)
    and isinstance(embeddings[0], list)
    and isinstance(embeddings[0][0], torch.Tensor)
    and isinstance(embeddings[0][0], torch.Tensor)
    ):
    ):
    embeddings = [[e.tolist() for e in emb] for emb in embeddings]
    embeddings = [[e.tolist() for e in emb] for emb in embeddings]


    # Cache response
    # Cache response
    self._cache_response(cache_key, params, embeddings)
    self._cache_response(cache_key, params, embeddings)


    return embeddings
    return embeddings


except Exception as e:
except Exception as e:
    logger.error(f"Error generating embeddings: {e}")
    logger.error(f"Error generating embeddings: {e}")
    raise
    raise


    def compute_similarity(self, text1: str, text2: str, **kwargs) -> float:
    def compute_similarity(self, text1: str, text2: str, **kwargs) -> float:
    """
    """
    Compute similarity between two texts.
    Compute similarity between two texts.


    Args:
    Args:
    text1: First text
    text1: First text
    text2: Second text
    text2: Second text
    **kwargs: Additional parameters for encoding
    **kwargs: Additional parameters for encoding


    Returns:
    Returns:
    Similarity score between 0 and 1
    Similarity score between 0 and 1
    """
    """
    if not self.initialized:
    if not self.initialized:
    self.load_model()
    self.load_model()


    try:
    try:
    # Generate embeddings
    # Generate embeddings
    embedding1 = self.encode(text1, **kwargs)
    embedding1 = self.encode(text1, **kwargs)
    embedding2 = self.encode(text2, **kwargs)
    embedding2 = self.encode(text2, **kwargs)


    # Compute cosine similarity
    # Compute cosine similarity
    if isinstance(embedding1[0], list):
    if isinstance(embedding1[0], list):
    embedding1 = embedding1[0]
    embedding1 = embedding1[0]
    if isinstance(embedding2[0], list):
    if isinstance(embedding2[0], list):
    embedding2 = embedding2[0]
    embedding2 = embedding2[0]


    # Convert to torch tensors
    # Convert to torch tensors
    tensor1 = torch.tensor(embedding1)
    tensor1 = torch.tensor(embedding1)
    tensor2 = torch.tensor(embedding2)
    tensor2 = torch.tensor(embedding2)


    # Compute cosine similarity
    # Compute cosine similarity
    similarity = torch.nn.functional.cosine_similarity(
    similarity = torch.nn.functional.cosine_similarity(
    tensor1.unsqueeze(0), tensor2.unsqueeze(0)
    tensor1.unsqueeze(0), tensor2.unsqueeze(0)
    ).item()
    ).item()


    return similarity
    return similarity


except Exception as e:
except Exception as e:
    logger.error(f"Error computing similarity: {e}")
    logger.error(f"Error computing similarity: {e}")
    raise
    raise




    class LocalAIModel:
    class LocalAIModel:
    """
    """
    Factory class for creating local AI models.
    Factory class for creating local AI models.
    """
    """


    @staticmethod
    @staticmethod
    def create(model_type: str, model_path: str, **kwargs) -> BaseLocalAIModel:
    def create(model_type: str, model_path: str, **kwargs) -> BaseLocalAIModel:
    """
    """
    Create a local AI model.
    Create a local AI model.


    Args:
    Args:
    model_type: Type of model (huggingface, llama, embedding)
    model_type: Type of model (huggingface, llama, embedding)
    model_path: Path or name of the model
    model_path: Path or name of the model
    **kwargs: Additional parameters for model initialization
    **kwargs: Additional parameters for model initialization


    Returns:
    Returns:
    Local AI model instance
    Local AI model instance
    """
    """
    if model_type.lower() == "huggingface":
    if model_type.lower() == "huggingface":
    return HuggingFaceModel(model_path, **kwargs)
    return HuggingFaceModel(model_path, **kwargs)
    elif model_type.lower() == "llama":
    elif model_type.lower() == "llama":
    return LlamaModel(model_path, **kwargs)
    return LlamaModel(model_path, **kwargs)
    elif model_type.lower() == "embedding":
    elif model_type.lower() == "embedding":
    return EmbeddingModel(model_path, **kwargs)
    return EmbeddingModel(model_path, **kwargs)
    else:
    else:
    raise ValueError(f"Unknown model type: {model_type}")
    raise ValueError(f"Unknown model type: {model_type}")




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    # Example 1: Hugging Face model
    # Example 1: Hugging Face model
    if TRANSFORMERS_AVAILABLE:
    if TRANSFORMERS_AVAILABLE:
    try:
    try:
    hf_model = LocalAIModel.create(
    hf_model = LocalAIModel.create(
    model_type="huggingface",
    model_type="huggingface",
    model_path="gpt2",  # Small model for testing
    model_path="gpt2",  # Small model for testing
    model_type_hf="text-generation",
    model_type_hf="text-generation",
    cache_enabled=True,
    cache_enabled=True,
    )
    )


    response = hf_model.generate_text(
    response = hf_model.generate_text(
    prompt="AI tools can help with", max_length=100, temperature=0.7
    prompt="AI tools can help with", max_length=100, temperature=0.7
    )
    )


    print("Hugging Face Model Response:")
    print("Hugging Face Model Response:")
    print(response)
    print(response)
    print()
    print()
except Exception as e:
except Exception as e:
    print(f"Error with Hugging Face model: {e}")
    print(f"Error with Hugging Face model: {e}")


    # Example 2: Embedding model
    # Example 2: Embedding model
    if SENTENCE_TRANSFORMERS_AVAILABLE:
    if SENTENCE_TRANSFORMERS_AVAILABLE:
    try:
    try:
    embedding_model = LocalAIModel.create(
    embedding_model = LocalAIModel.create(
    model_type="embedding",
    model_type="embedding",
    model_path="all-MiniLM-L6-v2",
    model_path="all-MiniLM-L6-v2",
    cache_enabled=True,
    cache_enabled=True,
    )
    )


    text1 = "AI tools can automate repetitive tasks."
    text1 = "AI tools can automate repetitive tasks."
    text2 = "Artificial intelligence software can handle routine jobs."
    text2 = "Artificial intelligence software can handle routine jobs."


    similarity = embedding_model.compute_similarity(text1, text2)
    similarity = embedding_model.compute_similarity(text1, text2)


    print("Embedding Model Similarity:")
    print("Embedding Model Similarity:")
    print(f"Text 1: {text1}")
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Text 2: {text2}")
    print(f"Similarity: {similarity:.4f}")
    print(f"Similarity: {similarity:.4f}")
    print()
    print()
except Exception as e:
except Exception as e:
    print(f"Error with Embedding model: {e}")
    print(f"Error with Embedding model: {e}")


    # Example 3: Llama model (requires model file)
    # Example 3: Llama model (requires model file)
    if LLAMA_CPP_AVAILABLE:
    if LLAMA_CPP_AVAILABLE:
    try:
    try:
    # This requires a downloaded model file
    # This requires a downloaded model file
    model_path = "path/to/llama/model.bin"
    model_path = "path/to/llama/model.bin"
    if os.path.exists(model_path):
    if os.path.exists(model_path):
    llama_model = LocalAIModel.create(
    llama_model = LocalAIModel.create(
    model_type="llama", model_path=model_path, cache_enabled=True
    model_type="llama", model_path=model_path, cache_enabled=True
    )
    )


    response = llama_model.generate_text(
    response = llama_model.generate_text(
    prompt="AI tools can help with", max_tokens=100, temperature=0.7
    prompt="AI tools can help with", max_tokens=100, temperature=0.7
    )
    )


    print("Llama Model Response:")
    print("Llama Model Response:")
    print(response)
    print(response)
    print()
    print()
except Exception as e:
except Exception as e:
    print(f"Error with Llama model: {e}")
    print(f"Error with Llama model: {e}")