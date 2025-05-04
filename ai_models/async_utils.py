"""
"""
Asynchronous utilities for the AI Models module.
Asynchronous utilities for the AI Models module.


This module provides utility functions for asynchronous processing with AI models,
This module provides utility functions for asynchronous processing with AI models,
making it easier to perform batch inference, parallel processing, and handle asynchronous operations.
making it easier to perform batch inference, parallel processing, and handle asynchronous operations.
"""
"""


import asyncio
import asyncio
import functools
import functools
import logging
import logging
import time
import time
from dataclasses import dataclass
from dataclasses import dataclass
from typing import (Any, AsyncIterator, Awaitable, Callable, Dict, Generic,
from typing import (Any, AsyncIterator, Awaitable, Callable, Dict, Generic,
List, Optional, TypeVar)
List, Optional, TypeVar)


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


# Type variables for generic typing
# Type variables for generic typing
T = TypeVar("T")
T = TypeVar("T")
U = TypeVar("U")
U = TypeVar("U")




@dataclass
@dataclass
class AsyncResult(Generic[T]):
    class AsyncResult(Generic[T]):
    """
    """
    Container for the result of an asynchronous operation.
    Container for the result of an asynchronous operation.


    Attributes:
    Attributes:
    result: The result of the operation, if successful
    result: The result of the operation, if successful
    error: The error that occurred, if any
    error: The error that occurred, if any
    is_success: Whether the operation was successful
    is_success: Whether the operation was successful
    processing_time: Time taken to process the operation in seconds
    processing_time: Time taken to process the operation in seconds
    metadata: Additional metadata for the operation
    metadata: Additional metadata for the operation
    """
    """


    result: Optional[T] = None
    result: Optional[T] = None
    error: Optional[Exception] = None
    error: Optional[Exception] = None
    is_success: bool = True
    is_success: bool = True
    processing_time: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


    def __post_init__(self):
    def __post_init__(self):
    """Initialize default values after creation."""
    if self.error is not None:
    self.is_success = False
    if self.metadata is None:
    self.metadata = {}


    async def run_async_with_timeout(coro, timeout: float = 60.0) -> AsyncResult[T]:
    """
    """
    Run a coroutine with a timeout.
    Run a coroutine with a timeout.


    Args:
    Args:
    coro: The coroutine to run
    coro: The coroutine to run
    timeout: Timeout in seconds
    timeout: Timeout in seconds


    Returns:
    Returns:
    AsyncResult with the result or error
    AsyncResult with the result or error
    """
    """
    start_time = time.time()
    start_time = time.time()
    result = AsyncResult()
    result = AsyncResult()


    try:
    try:
    # Run the coroutine with a timeout
    # Run the coroutine with a timeout
    task_result = await asyncio.wait_for(coro, timeout=timeout)
    task_result = await asyncio.wait_for(coro, timeout=timeout)
    result.result = task_result
    result.result = task_result
    result.is_success = True
    result.is_success = True
except asyncio.TimeoutError:
except asyncio.TimeoutError:
    result.error = asyncio.TimeoutError(
    result.error = asyncio.TimeoutError(
    f"Operation timed out after {timeout} seconds"
    f"Operation timed out after {timeout} seconds"
    )
    )
    result.is_success = False
    result.is_success = False
except Exception as e:
except Exception as e:
    result.error = e
    result.error = e
    result.is_success = False
    result.is_success = False
finally:
finally:
    result.processing_time = time.time() - start_time
    result.processing_time = time.time() - start_time


    return result
    return result




    async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """
    """
    Run a blocking function in a thread pool.
    Run a blocking function in a thread pool.


    Args:
    Args:
    func: The function to run
    func: The function to run
    *args: Positional arguments for the function
    *args: Positional arguments for the function
    **kwargs: Keyword arguments for the function
    **kwargs: Keyword arguments for the function


    Returns:
    Returns:
    The result of the function
    The result of the function
    """
    """
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))




    async def gather_with_concurrency(n: int, *tasks) -> List[Any]:
    async def gather_with_concurrency(n: int, *tasks) -> List[Any]:
    """
    """
    Run tasks with a limit on concurrency.
    Run tasks with a limit on concurrency.


    Args:
    Args:
    n: Maximum number of tasks to run concurrently
    n: Maximum number of tasks to run concurrently
    *tasks: The tasks to run
    *tasks: The tasks to run


    Returns:
    Returns:
    List of results from the tasks
    List of results from the tasks
    """
    """
    semaphore = asyncio.Semaphore(n)
    semaphore = asyncio.Semaphore(n)


    async def _run_task_with_semaphore(task):
    async def _run_task_with_semaphore(task):
    async with semaphore:
    async with semaphore:
    return await task
    return await task


    return await asyncio.gather(*(_run_task_with_semaphore(task) for task in tasks))
    return await asyncio.gather(*(_run_task_with_semaphore(task) for task in tasks))




    async def batch_process_async(
    async def batch_process_async(
    items: List[T], process_func: Callable[[T], Awaitable[U]], batch_size: int = 5
    items: List[T], process_func: Callable[[T], Awaitable[U]], batch_size: int = 5
    ) -> List[AsyncResult[U]]:
    ) -> List[AsyncResult[U]]:
    """
    """
    Process a list of items in batches, with error handling for each item.
    Process a list of items in batches, with error handling for each item.


    Args:
    Args:
    items: List of items to process
    items: List of items to process
    process_func: Async function to process each item
    process_func: Async function to process each item
    batch_size: Number of items to process concurrently
    batch_size: Number of items to process concurrently


    Returns:
    Returns:
    List of AsyncResult objects with results or errors
    List of AsyncResult objects with results or errors
    """
    """
    results = []
    results = []


    for i in range(0, len(items), batch_size):
    for i in range(0, len(items), batch_size):
    batch = items[i : i + batch_size]
    batch = items[i : i + batch_size]
    batch_tasks = []
    batch_tasks = []


    for item in batch:
    for item in batch:


    async def process_item(item=item):
    async def process_item(item=item):
    start_time = time.time()
    start_time = time.time()
    result = AsyncResult()
    result = AsyncResult()


    try:
    try:
    result.result = await process_func(item)
    result.result = await process_func(item)
    result.is_success = True
    result.is_success = True
except Exception as e:
except Exception as e:
    result.error = e
    result.error = e
    result.is_success = False
    result.is_success = False
    logger.error(f"Error processing item: {e}")
    logger.error(f"Error processing item: {e}")
finally:
finally:
    result.processing_time = time.time() - start_time
    result.processing_time = time.time() - start_time


    return result
    return result


    batch_tasks.append(process_item())
    batch_tasks.append(process_item())


    # Process the batch
    # Process the batch
    batch_results = await asyncio.gather(*batch_tasks)
    batch_results = await asyncio.gather(*batch_tasks)
    results.extend(batch_results)
    results.extend(batch_results)


    return results
    return results




    async def stream_processor(
    async def stream_processor(
    input_stream: AsyncIterator[T],
    input_stream: AsyncIterator[T],
    process_func: Callable[[T], Awaitable[U]],
    process_func: Callable[[T], Awaitable[U]],
    buffer_size: int = 10,
    buffer_size: int = 10,
    ) -> AsyncIterator[U]:
    ) -> AsyncIterator[U]:
    """
    """
    Process items from an input stream and yield results as they become available.
    Process items from an input stream and yield results as they become available.


    Args:
    Args:
    input_stream: Async iterator producing input items
    input_stream: Async iterator producing input items
    process_func: Async function to process each item
    process_func: Async function to process each item
    buffer_size: Number of items to buffer for processing
    buffer_size: Number of items to buffer for processing


    Yields:
    Yields:
    Processed results as they become available
    Processed results as they become available
    """
    """
    pending = set()
    pending = set()


    async def process_item(item):
    async def process_item(item):
    return await process_func(item)
    return await process_func(item)


    # Process items from the input stream
    # Process items from the input stream
    try:
    try:
    # Fill the initial buffer
    # Fill the initial buffer
    for _ in range(buffer_size):
    for _ in range(buffer_size):
    try:
    try:
    item = await asyncio.anext(input_stream)
    item = await asyncio.anext(input_stream)
    task = asyncio.create_task(process_item(item))
    task = asyncio.create_task(process_item(item))
    pending.add(task)
    pending.add(task)
    task.add_done_callback(pending.discard)
    task.add_done_callback(pending.discard)
except StopAsyncIteration:
except StopAsyncIteration:
    break
    break


    # Process the rest of the stream
    # Process the rest of the stream
    while pending:
    while pending:
    # Get the first completed task
    # Get the first completed task
    done, pending = await asyncio.wait(
    done, pending = await asyncio.wait(
    pending, return_when=asyncio.FIRST_COMPLETED
    pending, return_when=asyncio.FIRST_COMPLETED
    )
    )


    # Yield the results
    # Yield the results
    for task in done:
    for task in done:
    yield task.result()
    yield task.result()


    # Refill the buffer
    # Refill the buffer
    try:
    try:
    for _ in range(buffer_size - len(pending)):
    for _ in range(buffer_size - len(pending)):
    item = await asyncio.anext(input_stream)
    item = await asyncio.anext(input_stream)
    task = asyncio.create_task(process_item(item))
    task = asyncio.create_task(process_item(item))
    pending.add(task)
    pending.add(task)
    task.add_done_callback(pending.discard)
    task.add_done_callback(pending.discard)
except StopAsyncIteration:
except StopAsyncIteration:
    pass
    pass
except Exception as e:
except Exception as e:
    logger.error(f"Error in stream processor: {e}")
    logger.error(f"Error in stream processor: {e}")
    raise
    raise




    class AsyncModelProcessor:
    class AsyncModelProcessor:
    """
    """
    Helper class for processing data through AI models asynchronously.
    Helper class for processing data through AI models asynchronously.
    """
    """


    def __init__(self, model_manager):
    def __init__(self, model_manager):
    """
    """
    Initialize the async model processor.
    Initialize the async model processor.


    Args:
    Args:
    model_manager: The model manager instance to use for loading models
    model_manager: The model manager instance to use for loading models
    """
    """
    self.model_manager = model_manager
    self.model_manager = model_manager
    self.loaded_models = {}
    self.loaded_models = {}
    self.semaphore = asyncio.Semaphore(10)  # Default concurrency limit
    self.semaphore = asyncio.Semaphore(10)  # Default concurrency limit


    async def ensure_model_loaded(
    async def ensure_model_loaded(
    self, model_id: str, version: str = None, **kwargs
    self, model_id: str, version: str = None, **kwargs
    ) -> Any:
    ) -> Any:
    """
    """
    Ensure a model is loaded before using it.
    Ensure a model is loaded before using it.


    Args:
    Args:
    model_id: ID of the model to load
    model_id: ID of the model to load
    version: Optional version of the model
    version: Optional version of the model
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    The loaded model
    The loaded model
    """
    """
    key = f"{model_id}_{version}" if version else model_id
    key = f"{model_id}_{version}" if version else model_id


    if key not in self.loaded_models:
    if key not in self.loaded_models:
    self.loaded_models[key] = await self.model_manager.load_model_async(
    self.loaded_models[key] = await self.model_manager.load_model_async(
    model_id, version, **kwargs
    model_id, version, **kwargs
    )
    )


    return self.loaded_models[key]
    return self.loaded_models[key]


    async def process_batch(
    async def process_batch(
    self,
    self,
    model_id: str,
    model_id: str,
    items: List[Dict[str, Any]],
    items: List[Dict[str, Any]],
    process_func: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
    process_func: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
    model_version: str = None,
    model_version: str = None,
    concurrency: int = 5,
    concurrency: int = 5,
    **kwargs,
    **kwargs,
    ) -> List[AsyncResult[Any]]:
    ) -> List[AsyncResult[Any]]:
    """
    """
    Process a batch of items using a model.
    Process a batch of items using a model.


    Args:
    Args:
    model_id: ID of the model to use
    model_id: ID of the model to use
    items: List of items to process
    items: List of items to process
    process_func: Function to process each item with the model
    process_func: Function to process each item with the model
    model_version: Optional version of the model
    model_version: Optional version of the model
    concurrency: Number of items to process concurrently
    concurrency: Number of items to process concurrently
    **kwargs: Additional parameters for model loading
    **kwargs: Additional parameters for model loading


    Returns:
    Returns:
    List of AsyncResult objects with results or errors
    List of AsyncResult objects with results or errors
    """
    """
    # Ensure the model is loaded
    # Ensure the model is loaded
    model = await self.ensure_model_loaded(model_id, model_version, **kwargs)
    model = await self.ensure_model_loaded(model_id, model_version, **kwargs)


    # Process the items
    # Process the items
    async def process_item(item):
    async def process_item(item):
    return await process_func(model, item)
    return await process_func(model, item)


    return await batch_process_async(items, process_item, concurrency)
    return await batch_process_async(items, process_item, concurrency)


    async def generate_text_batch(
    async def generate_text_batch(
    self,
    self,
    model_id: str,
    model_id: str,
    prompts: List[str],
    prompts: List[str],
    model_version: str = None,
    model_version: str = None,
    concurrency: int = 5,
    concurrency: int = 5,
    **kwargs,
    **kwargs,
    ) -> List[AsyncResult[str]]:
    ) -> List[AsyncResult[str]]:
    """
    """
    Generate text for multiple prompts in parallel.
    Generate text for multiple prompts in parallel.


    Args:
    Args:
    model_id: ID of the model to use
    model_id: ID of the model to use
    prompts: List of prompts to process
    prompts: List of prompts to process
    model_version: Optional version of the model
    model_version: Optional version of the model
    concurrency: Number of prompts to process concurrently
    concurrency: Number of prompts to process concurrently
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    List of AsyncResult objects with generated text or errors
    List of AsyncResult objects with generated text or errors
    """
    """
    # Get the model info to determine adapter type
    # Get the model info to determine adapter type
    model_info = self.model_manager.get_model_info(model_id)
    model_info = self.model_manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ValueError(f"Model with ID {model_id} not found")
    raise ValueError(f"Model with ID {model_id} not found")


    adapter = None
    adapter = None


    # If the model has an adapter assigned, use it
    # If the model has an adapter assigned, use it
    if hasattr(self.model_manager, "get_adapter_for_model"):
    if hasattr(self.model_manager, "get_adapter_for_model"):
    adapter = self.model_manager.get_adapter_for_model(model_id)
    adapter = self.model_manager.get_adapter_for_model(model_id)


    # If adapter is available, use it directly
    # If adapter is available, use it directly
    if adapter and hasattr(adapter, "generate_text_async"):
    if adapter and hasattr(adapter, "generate_text_async"):
    # Create a wrapper for the process_func
    # Create a wrapper for the process_func
    async def process_func(prompt):
    async def process_func(prompt):
    return await adapter.generate_text_async(model_id, prompt, **kwargs)
    return await adapter.generate_text_async(model_id, prompt, **kwargs)


    return await batch_process_async(prompts, process_func, concurrency)
    return await batch_process_async(prompts, process_func, concurrency)


    # Otherwise, use the model directly (this assumes the model has a generate method)
    # Otherwise, use the model directly (this assumes the model has a generate method)
    else:
    else:
    # Ensure the model is loaded
    # Ensure the model is loaded
    model = await self.ensure_model_loaded(model_id, model_version, **kwargs)
    model = await self.ensure_model_loaded(model_id, model_version, **kwargs)


    # Use run_in_thread for models that don't have async methods
    # Use run_in_thread for models that don't have async methods
    async def process_func(prompt):
    async def process_func(prompt):
    if hasattr(model, "generate_text_async"):
    if hasattr(model, "generate_text_async"):
    return await model.generate_text_async(prompt, **kwargs)
    return await model.generate_text_async(prompt, **kwargs)
    elif hasattr(model, "generate_text"):
    elif hasattr(model, "generate_text"):
    return await run_in_thread(model.generate_text, prompt, **kwargs)
    return await run_in_thread(model.generate_text, prompt, **kwargs)
    else:
    else:
    raise NotImplementedError(
    raise NotImplementedError(
    f"Model {model_id} does not support text generation"
    f"Model {model_id} does not support text generation"
    )
    )


    return await batch_process_async(prompts, process_func, concurrency)
    return await batch_process_async(prompts, process_func, concurrency)


    async def generate_embeddings_batch(
    async def generate_embeddings_batch(
    self,
    self,
    model_id: str,
    model_id: str,
    texts: List[str],
    texts: List[str],
    model_version: str = None,
    model_version: str = None,
    concurrency: int = 10,
    concurrency: int = 10,
    **kwargs,
    **kwargs,
    ) -> List[AsyncResult[List[float]]]:
    ) -> List[AsyncResult[List[float]]]:
    """
    """
    Generate embeddings for multiple texts in parallel.
    Generate embeddings for multiple texts in parallel.


    Args:
    Args:
    model_id: ID of the model to use
    model_id: ID of the model to use
    texts: List of texts to process
    texts: List of texts to process
    model_version: Optional version of the model
    model_version: Optional version of the model
    concurrency: Number of texts to process concurrently
    concurrency: Number of texts to process concurrently
    **kwargs: Additional parameters for embedding generation
    **kwargs: Additional parameters for embedding generation


    Returns:
    Returns:
    List of AsyncResult objects with embeddings or errors
    List of AsyncResult objects with embeddings or errors
    """
    """
    # Get the model info to determine adapter type
    # Get the model info to determine adapter type
    model_info = self.model_manager.get_model_info(model_id)
    model_info = self.model_manager.get_model_info(model_id)
    if not model_info:
    if not model_info:
    raise ValueError(f"Model with ID {model_id} not found")
    raise ValueError(f"Model with ID {model_id} not found")


    adapter = None
    adapter = None


    # If the model has an adapter assigned, use it
    # If the model has an adapter assigned, use it
    if hasattr(self.model_manager, "get_adapter_for_model"):
    if hasattr(self.model_manager, "get_adapter_for_model"):
    adapter = self.model_manager.get_adapter_for_model(model_id)
    adapter = self.model_manager.get_adapter_for_model(model_id)


    # If adapter is available, use it directly
    # If adapter is available, use it directly
    if adapter and hasattr(adapter, "create_embedding_async"):
    if adapter and hasattr(adapter, "create_embedding_async"):
    # Create a wrapper for the process_func
    # Create a wrapper for the process_func
    async def process_func(text):
    async def process_func(text):
    return await adapter.create_embedding_async(model_id, text, **kwargs)
    return await adapter.create_embedding_async(model_id, text, **kwargs)


    return await batch_process_async(texts, process_func, concurrency)
    return await batch_process_async(texts, process_func, concurrency)


    # Otherwise, use the model directly
    # Otherwise, use the model directly
    else:
    else:
    # Ensure the model is loaded
    # Ensure the model is loaded
    model = await self.ensure_model_loaded(model_id, model_version, **kwargs)
    model = await self.ensure_model_loaded(model_id, model_version, **kwargs)


    # Use run_in_thread for models that don't have async methods
    # Use run_in_thread for models that don't have async methods
    async def process_func(text):
    async def process_func(text):
    if hasattr(model, "create_embedding_async"):
    if hasattr(model, "create_embedding_async"):
    return await model.create_embedding_async(text, **kwargs)
    return await model.create_embedding_async(text, **kwargs)
    elif hasattr(model, "create_embedding"):
    elif hasattr(model, "create_embedding"):
    return await run_in_thread(model.create_embedding, text, **kwargs)
    return await run_in_thread(model.create_embedding, text, **kwargs)
    else:
    else:
    raise NotImplementedError(
    raise NotImplementedError(
    f"Model {model_id} does not support embedding generation"
    f"Model {model_id} does not support embedding generation"
    )
    )


    return await batch_process_async(texts, process_func, concurrency)
    return await batch_process_async(texts, process_func, concurrency)




    # Utility function to convert a synchronous function to asynchronous
    # Utility function to convert a synchronous function to asynchronous
    def to_async(func):
    def to_async(func):
    """
    """
    Convert a synchronous function to asynchronous.
    Convert a synchronous function to asynchronous.


    Args:
    Args:
    func: The synchronous function to convert
    func: The synchronous function to convert


    Returns:
    Returns:
    Asynchronous version of the function
    Asynchronous version of the function
    """
    """


    @functools.wraps(func)
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
    async def wrapper(*args, **kwargs):
    return await run_in_thread(func, *args, **kwargs)
    return await run_in_thread(func, *args, **kwargs)


    return wrapper
    return wrapper

