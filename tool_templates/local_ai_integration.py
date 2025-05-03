"""
Local AI Integration Templates for the pAIssive Income project.

This module provides templates for integrating local AI models into your applications.
It includes classes and functions for loading models, processing user input, caching responses,
and handling errors.

Dependencies:
- transformers
- torch
- sentence-transformers
- llama-cpp-python (optional, for llama models)
- onnxruntime (optional, for ONNX models)
"""

try:
    import torch  # noqa: F401
    import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    from sentence_transformers import SentenceTransformer

SENTENCE_TRANSFORMERS_AVAILABLE 
    from llama_cpp import Llama

LLAMA_CPP_AVAILABLE 
    import onnxruntime

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
# noqa: F401
  # noqa: F401
# noqa: F401

TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning(
        "Transformers or PyTorch not available. Some functionality will be limited."
    )
    TRANSFORMERS_AVAILABLE = False

try:
= True
except ImportError:
    logger.warning(
        "Sentence Transformers not available. Embedding functionality will be limited."
    )
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
= True
except ImportError:
    logger.warning(
        "llama-cpp-python not available. Llama model support will be limited."
    )
    LLAMA_CPP_AVAILABLE = False

try:
as ort  # noqa: F401

ONNX_AVAILABLE = True
except ImportError:
    logger.warning("ONNX Runtime not available. ONNX model support will be limited.")
    ONNX_AVAILABLE = False


class ModelCache:
    """
    Cache for AI model responses to improve performance and reduce resource usage.

This implementation provides a two-tiered caching system:
    1. In-memory cache for fast access to frequently used items
    2. Persistent file-based cache for longer-term storage

The cache uses a deterministic hashing algorithm to generate unique keys based on:
    - Model name
    - Input text
    - Model parameters

This ensures identical requests get the same cached response, reducing
    computational load and improving response times. The system also handles:
    - Thread safety with locks for concurrent access
    - TTL (time-to-live) expiration for cache items
    - LRU (least recently used) eviction policy for memory cache
    - Automatic cleanup of invalid or expired cache entries
    """

def __init__(
        self, cache_dir: str = ".cache", max_size: int = 1000, ttl: int = 86400
    ):
        """
        Initialize the model cache.

Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of items to keep in memory cache
            ttl: Time-to-live for cache items in seconds (default: 24 hours)
        """
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl = ttl
        # The memory cache is a dictionary: {cache_key: {response, timestamp, metadata}}
        self.memory_cache = {}
        # Use a thread lock to ensure thread safety for cache operations
        self.cache_lock = threading.Lock()

# Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Initialized model cache in {cache_dir}")

def _get_cache_key(
        self, model_name: str, input_text: str, params: Dict[str, Any]
    ) -> str:
        """
        Generate a cache key from the model name, input text, and parameters.

This method creates a deterministic hash that uniquely identifies a specific
        model inference request based on all its inputs. The algorithm:
        1. Converts parameters to a consistent string representation
        2. Concatenates model name, input text, and parameters
        3. Creates an MD5 hash of this string for a compact, fixed-length key

Using a cryptographic hash function ensures:
        - Uniformity: Even small changes in input produce different keys
        - Determinism: Same inputs always produce the same key
        - Fixed length: Keys have consistent length regardless of input size

Args:
            model_name: Name of the model
            input_text: Input text to the model
            params: Model parameters

Returns:
            Cache key string
        """
        # Create a string representation of the parameters
        # Sort the keys to ensure consistent ordering regardless of dict creation order
        params_str = json.dumps(params, sort_keys=True)

# Create a hash of the input and parameters
        # Using MD5 for speed and sufficient collision resistance for caching
        key = hashlib.md5(
            f"{model_name}:{input_text}:{params_str}".encode()
        ).hexdigest()

            return key

def _get_cache_file_path(self, key: str) -> str:
        """
        Get the file path for a cache item.

Args:
            key: Cache key

Returns:
            File path for the cache item
        """
                    return os.path.join(self.cache_dir, f"{key}.json")

def get(
        self, model_name: str, input_text: str, params: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Get a cached response if available.

This method implements the cache lookup strategy:
        1. Generate a unique cache key for the request
        2. First check memory cache (fast, but volatile)
        3. If not in memory, check file cache (slower, but persistent)
        4. In both cases, verify the cache item hasn't expired (TTL)
        5. For file cache hits, load into memory cache for faster future access
        6. Apply LRU eviction if memory cache exceeds max size

The multi-tiered approach balances speed (memory) with persistence (file),
        while the TTL mechanism ensures cached data doesn't become stale.

Args:
            model_name: Name of the model
            input_text: Input text to the model
            params: Model parameters

Returns:
            Cached response or None if not found/expired
        """
        key = self._get_cache_key(model_name, input_text, params)

# Check memory cache first (fast access)
        with self.cache_lock:
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                # Check if the item is still valid (not expired)
                if time.time() - cache_item["timestamp"] < self.ttl:
                    logger.debug(f"Cache hit (memory): {key}")
                                return cache_item["response"]
                else:
                    # Remove expired item from memory cache
                    del self.memory_cache[key]

# If not in memory cache or expired, check file cache
        cache_file = self._get_cache_file_path(key)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache_item = json.load(f)

# Check if the item is still valid (not expired)
                if time.time() - cache_item["timestamp"] < self.ttl:
                    # Add to memory cache for faster future access
                    with self.cache_lock:
                        self.memory_cache[key] = cache_item

# Implement LRU eviction if memory cache exceeds max size
                        if len(self.memory_cache) > self.max_size:
                            # Find and remove the oldest item (lowest timestamp)
                            oldest_key = min(
                                self.memory_cache.keys(),
                                key=lambda k: self.memory_cache[k]["timestamp"],
                            )
                            del self.memory_cache[oldest_key]

logger.debug(f"Cache hit (file): {key}")
                                return cache_item["response"]
                else:
                    # Remove expired cache file
                    os.remove(cache_file)
            except (json.JSONDecodeError, KeyError) as e:
                # Handle corrupted cache files
                logger.warning(f"Error reading cache file {cache_file}: {e}")
                # Remove corrupted cache file
                os.remove(cache_file)

# Cache miss if execution reaches here
        logger.debug(f"Cache miss: {key}")
                    return None

def set(
        self, model_name: str, input_text: str, params: Dict[str, Any], response: Any
    ) -> None:
        """
        Cache a model response.

This method implements the cache storage strategy:
        1. Generate a unique cache key for the request
        2. Create a cache item with response data and metadata
        3. Store in memory cache with thread safety
        4. Implement LRU eviction if memory cache exceeds max size
        5. Persist to file cache for longer-term storage

The dual storage approach ensures fast access for frequently used items
        while maintaining persistence across application restarts.

Args:
            model_name: Name of the model
            input_text: Input text to the model
            params: Model parameters
            response: Model response to cache
        """
        key = self._get_cache_key(model_name, input_text, params)
        timestamp = time.time()

# Create cache item with response and metadata
        cache_item = {
            "model_name": model_name,
            "input_text": input_text,
            "params": params,
            "response": response,
            "timestamp": timestamp,
        }

# Add to memory cache with thread safety
        with self.cache_lock:
            self.memory_cache[key] = cache_item

# Apply LRU eviction if memory cache exceeds max size
            if len(self.memory_cache) > self.max_size:
                # Find and remove the oldest item (lowest timestamp)
                oldest_key = min(
                    self.memory_cache.keys(),
                    key=lambda k: self.memory_cache[k]["timestamp"],
                )
                del self.memory_cache[oldest_key]

# Persist to file cache
        cache_file = self._get_cache_file_path(key)
        try:
            with open(cache_file, "w") as f:
                json.dump(cache_item, f)
            logger.debug(f"Cached response: {key}")
        except Exception as e:
            logger.warning(f"Error writing cache file {cache_file}: {e}")

def clear(self, older_than: Optional[int] = None) -> int:
        """
        Clear the cache.

This method provides cache maintenance with two modes:
        1. Complete clear: Remove all cache items (memory and file)
        2. Age-based clear: Remove only items older than a specified time

The age-based option is particularly useful for:
        - Periodic cleanup of stale data
        - Clearing only old data while preserving recent items
        - Managing cache size without complete invalidation

Thread safety is maintained through locks for memory cache operations.

Args:
            older_than: Clear items older than this many seconds
                       If None, clear all items

Returns:
            Number of items cleared
        """
        count = 0

# Clear memory cache with thread safety
        with self.cache_lock:
            if older_than is not None:
                # Age-based clear for memory cache
                current_time = time.time()
                keys_to_remove = [
                    key
                    for key, item in self.memory_cache.items()
                    if current_time - item["timestamp"] > older_than
                ]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                count += len(keys_to_remove)
            else:
                # Complete clear for memory cache
                count += len(self.memory_cache)
                self.memory_cache.clear()

# Clear file cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    if older_than is not None:
                        # Age-based clear for file cache
                        # Use file modification time as a proxy for cache item timestamp
                        file_time = os.path.getmtime(file_path)
                        if time.time() - file_time > older_than:
                            os.remove(file_path)
                            count += 1
                    else:
                        # Complete clear for file cache
                        os.remove(file_path)
                        count += 1
                except OSError as e:
                    logger.warning(f"Error removing cache file {file_path}: {e}")

logger.info(f"Cleared {count} items from cache")
                    return count


class BaseLocalAIModel(ABC):
    """
    Abstract base class for local AI models.
    """

def __init__(self, model_name: str, cache_enabled: bool = True):
        """
        Initialize the base local AI model.

Args:
            model_name: Name of the model
            cache_enabled: Whether to enable response caching
        """
        self.model_name = model_name
        self.cache_enabled = cache_enabled
        self.cache = ModelCache() if cache_enabled else None
        self.model = None
        self.initialized = False
        logger.info(f"Initializing {self.__class__.__name__} with model {model_name}")

@abstractmethod
    def load_model(self) -> None:
        """
        Load the AI model.
        """
        pass

@abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on a prompt.

Args:
            prompt: Input prompt
            **kwargs: Additional parameters for text generation

Returns:
            Generated text
        """
        pass

def _get_cached_response(
        self, prompt: str, params: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get a cached response if available.

Args:
            prompt: Input prompt
            params: Generation parameters

Returns:
            Cached response or None if not found
        """
        if self.cache_enabled and self.cache is not None:
                        return self.cache.get(self.model_name, prompt, params)
                    return None

def _cache_response(
        self, prompt: str, params: Dict[str, Any], response: str
    ) -> None:
        """
        Cache a model response.

Args:
            prompt: Input prompt
            params: Generation parameters
            response: Model response to cache
        """
        if self.cache_enabled and self.cache is not None:
            self.cache.set(self.model_name, prompt, params, response)


class HuggingFaceModel(BaseLocalAIModel):
    """
    Local AI model using Hugging Face Transformers.
    """

def __init__(
        self,
        model_name: str,
        model_type: str = "text-generation",
        device: str = "auto",
        cache_enabled: bool = True,
        **model_kwargs,
    ):
        """
        Initialize a Hugging Face model.

Args:
            model_name: Name or path of the model
            model_type: Type of model (text-generation, text2text-generation, etc.)
            device: Device to run the model on (auto, cpu, cuda, etc.)
            cache_enabled: Whether to enable response caching
            **model_kwargs: Additional parameters for model initialization
        """
        super().__init__(model_name, cache_enabled)

if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers or PyTorch not available. Please install them with: pip install transformers torch"
            )

self.model_type = model_type
        self.device = device
        self.model_kwargs = model_kwargs
        self.tokenizer = None
        self.pipeline = None

def load_model(self) -> None:
        """
        Load the Hugging Face model.
        """
        logger.info(f"Loading Hugging Face model: {self.model_name}")

try:
            # Determine device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"

# Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

# Create pipeline
            self.pipeline = pipeline(
                self.model_type,
                model=self.model_name,
                tokenizer=self.tokenizer,
                device=self.device,
                **self.model_kwargs,
            )

self.initialized = True
            logger.info(f"Successfully loaded model {self.model_name} on {self.device}")

except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise

def generate_text(
        self,
        prompt: str,
        max_length: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        num_return_sequences: int = 1,
        **kwargs,
    ) -> str:
        """
        Generate text using the Hugging Face model.

Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            num_return_sequences: Number of sequences to generate
            **kwargs: Additional parameters for text generation

Returns:
            Generated text
        """
        if not self.initialized:
            self.load_model()

# Prepare parameters
        params = {
            "max_length": max_length,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_return_sequences": num_return_sequences,
            **kwargs,
        }

# Check cache
        cached_response = self._get_cached_response(prompt, params)
        if cached_response is not None:
                        return cached_response

try:
            # Generate text
            outputs = self.pipeline(prompt, **params)

# Process output based on pipeline type
            if self.model_type == "text-generation":
                if num_return_sequences == 1:
                    response = outputs[0]["generated_text"]
                else:
                    response = [output["generated_text"] for output in outputs]
            else:
                response = outputs

# Cache response
            self._cache_response(prompt, params, response)

            return response

except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise


class LlamaModel(BaseLocalAIModel):
    """
    Local AI model using llama.cpp.
    """

def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: Optional[int] = None,
        cache_enabled: bool = True,
        **model_kwargs,
    ):
        """
        Initialize a Llama model.

Args:
            model_path: Path to the model file
            n_ctx: Context size
            n_threads: Number of threads to use
            cache_enabled: Whether to enable response caching
            **model_kwargs: Additional parameters for model initialization
        """
        super().__init__(os.path.basename(model_path), cache_enabled)

if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python not available. Please install it with: pip install llama-cpp-python"
            )

self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads or max(1, os.cpu_count() // 2)
        self.model_kwargs = model_kwargs

def load_model(self) -> None:
        """
        Load the Llama model.
        """
        logger.info(f"Loading Llama model: {self.model_path}")

try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                **self.model_kwargs,
            )

self.initialized = True
            logger.info(f"Successfully loaded model {self.model_path}")

except Exception as e:
            logger.error(f"Error loading model {self.model_path}: {e}")
            raise

def generate_text(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """
        Generate text using the Llama model.

Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            stop: List of strings to stop generation when encountered
            **kwargs: Additional parameters for text generation

Returns:
            Generated text
        """
        if not self.initialized:
            self.load_model()

# Prepare parameters
        params = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stop": stop,
            **kwargs,
        }

# Check cache
        cached_response = self._get_cached_response(prompt, params)
        if cached_response is not None:
                        return cached_response

try:
            # Generate text
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop=stop,
                **kwargs,
            )

response = output["choices"][0]["text"]

# Cache response
            self._cache_response(prompt, params, response)

            return response

except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise


class EmbeddingModel(BaseLocalAIModel):
    """
    Local AI model for generating embeddings.
    """

def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "auto",
        cache_enabled: bool = True,
        **model_kwargs,
    ):
        """
        Initialize an embedding model.

Args:
            model_name: Name or path of the model
            device: Device to run the model on (auto, cpu, cuda, etc.)
            cache_enabled: Whether to enable response caching
            **model_kwargs: Additional parameters for model initialization
        """
        super().__init__(model_name, cache_enabled)

if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Sentence Transformers not available. Please install it with: pip install sentence-transformers"
            )

self.device = device
        self.model_kwargs = model_kwargs

def load_model(self) -> None:
        """
        Load the embedding model.
        """
        logger.info(f"Loading embedding model: {self.model_name}")

try:
            # Determine device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model
            self.model = SentenceTransformer(
                self.model_name, device=self.device, **self.model_kwargs
            )

self.initialized = True
            logger.info(f"Successfully loaded model {self.model_name} on {self.device}")

except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise

def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Not applicable for embedding models.
        """
        raise NotImplementedError(
            "Embedding models do not support text generation. Use encode() instead."
        )

def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        **kwargs,
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text.

Args:
            texts: Input text or list of texts
            batch_size: Batch size for encoding
            normalize_embeddings: Whether to normalize embeddings
            **kwargs: Additional parameters for encoding

Returns:
            Text embeddings
        """
        if not self.initialized:
            self.load_model()

# Prepare parameters
        params = {
            "batch_size": batch_size,
            "normalize_embeddings": normalize_embeddings,
            **kwargs,
        }

# For caching, we need a string key
        if isinstance(texts, list):
            cache_key = json.dumps(texts)
        else:
            cache_key = texts

# Check cache
        cached_response = self._get_cached_response(cache_key, params)
        if cached_response is not None:
                        return cached_response

try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize_embeddings,
                **kwargs,
            )

# Convert to list for JSON serialization
            if isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.tolist()
            elif isinstance(embeddings, list) and isinstance(
                embeddings[0], torch.Tensor
            ):
                embeddings = [emb.tolist() for emb in embeddings]
            elif (
                isinstance(embeddings, list)
                and isinstance(embeddings[0], list)
                and isinstance(embeddings[0][0], torch.Tensor)
            ):
                embeddings = [[e.tolist() for e in emb] for emb in embeddings]

# Cache response
            self._cache_response(cache_key, params, embeddings)

            return embeddings

except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

def compute_similarity(self, text1: str, text2: str, **kwargs) -> float:
        """
        Compute similarity between two texts.

Args:
            text1: First text
            text2: Second text
            **kwargs: Additional parameters for encoding

Returns:
            Similarity score between 0 and 1
        """
        if not self.initialized:
            self.load_model()

try:
            # Generate embeddings
            embedding1 = self.encode(text1, **kwargs)
            embedding2 = self.encode(text2, **kwargs)

# Compute cosine similarity
            if isinstance(embedding1[0], list):
                embedding1 = embedding1[0]
            if isinstance(embedding2[0], list):
                embedding2 = embedding2[0]

# Convert to torch tensors
            tensor1 = torch.tensor(embedding1)
            tensor2 = torch.tensor(embedding2)

# Compute cosine similarity
            similarity = torch.nn.functional.cosine_similarity(
                tensor1.unsqueeze(0), tensor2.unsqueeze(0)
            ).item()

            return similarity

except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise


class LocalAIModel:
    """
    Factory class for creating local AI models.
    """

@staticmethod
    def create(model_type: str, model_path: str, **kwargs) -> BaseLocalAIModel:
        """
        Create a local AI model.

Args:
            model_type: Type of model (huggingface, llama, embedding)
            model_path: Path or name of the model
            **kwargs: Additional parameters for model initialization

Returns:
            Local AI model instance
        """
        if model_type.lower() == "huggingface":
                        return HuggingFaceModel(model_path, **kwargs)
        elif model_type.lower() == "llama":
                        return LlamaModel(model_path, **kwargs)
        elif model_type.lower() == "embedding":
                        return EmbeddingModel(model_path, **kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")


# Example usage
if __name__ == "__main__":
    # Example 1: Hugging Face model
    if TRANSFORMERS_AVAILABLE:
        try:
            hf_model = LocalAIModel.create(
                model_type="huggingface",
                model_path="gpt2",  # Small model for testing
                model_type_hf="text-generation",
                cache_enabled=True,
            )

response = hf_model.generate_text(
                prompt="AI tools can help with", max_length=100, temperature=0.7
            )

print("Hugging Face Model Response:")
            print(response)
            print()
        except Exception as e:
            print(f"Error with Hugging Face model: {e}")

# Example 2: Embedding model
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            embedding_model = LocalAIModel.create(
                model_type="embedding",
                model_path="all-MiniLM-L6-v2",
                cache_enabled=True,
            )

text1 = "AI tools can automate repetitive tasks."
            text2 = "Artificial intelligence software can handle routine jobs."

similarity = embedding_model.compute_similarity(text1, text2)

print("Embedding Model Similarity:")
            print(f"Text 1: {text1}")
            print(f"Text 2: {text2}")
            print(f"Similarity: {similarity:.4f}")
            print()
        except Exception as e:
            print(f"Error with Embedding model: {e}")

# Example 3: Llama model (requires model file)
    if LLAMA_CPP_AVAILABLE:
        try:
            # This requires a downloaded model file
            model_path = "path/to/llama/model.bin"
            if os.path.exists(model_path):
                llama_model = LocalAIModel.create(
                    model_type="llama", model_path=model_path, cache_enabled=True
                )

response = llama_model.generate_text(
                    prompt="AI tools can help with", max_tokens=100, temperature=0.7
                )

print("Llama Model Response:")
                print(response)
                print()
        except Exception as e:
            print(f"Error with Llama model: {e}")