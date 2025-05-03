"""
Asynchronous utilities for the AI Models module.

This module provides utility functions for asynchronous processing with AI models,
making it easier to perform batch inference, parallel processing, and handle asynchronous operations.
"""


import asyncio
import functools
import logging
import time
from dataclasses import dataclass
from typing import 

(
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Type variables for generic typing
T = TypeVar("T")
U = TypeVar("U")


@dataclass
class AsyncResult(Generic[T]):
    """
    Container for the result of an asynchronous operation.

    Attributes:
        result: The result of the operation, if successful
        error: The error that occurred, if any
        is_success: Whether the operation was successful
        processing_time: Time taken to process the operation in seconds
        metadata: Additional metadata for the operation
    """

    result: Optional[T] = None
    error: Optional[Exception] = None
    is_success: bool = True
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values after creation."""
        if self.error is not None:
            self.is_success = False
        if self.metadata is None:
            self.metadata = {}


async def run_async_with_timeout(coro, timeout: float = 60.0) -> AsyncResult[T]:
    """
    Run a coroutine with a timeout.

    Args:
        coro: The coroutine to run
        timeout: Timeout in seconds

    Returns:
        AsyncResult with the result or error
    """
    start_time = time.time()
    result = AsyncResult()

    try:
        # Run the coroutine with a timeout
        task_result = await asyncio.wait_for(coro, timeout=timeout)
        result.result = task_result
        result.is_success = True
    except asyncio.TimeoutError:
        result.error = asyncio.TimeoutError(
            f"Operation timed out after {timeout} seconds"
        )
        result.is_success = False
    except Exception as e:
        result.error = e
        result.is_success = False
    finally:
        result.processing_time = time.time() - start_time

    return result


async def run_in_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a blocking function in a thread pool.

    Args:
        func: The function to run
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The result of the function
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def gather_with_concurrency(n: int, *tasks) -> List[Any]:
    """
    Run tasks with a limit on concurrency.

    Args:
        n: Maximum number of tasks to run concurrently
        *tasks: The tasks to run

    Returns:
        List of results from the tasks
    """
    semaphore = asyncio.Semaphore(n)

    async def _run_task_with_semaphore(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(_run_task_with_semaphore(task) for task in tasks))


async def batch_process_async(
    items: List[T], process_func: Callable[[T], Awaitable[U]], batch_size: int = 5
) -> List[AsyncResult[U]]:
    """
    Process a list of items in batches, with error handling for each item.

    Args:
        items: List of items to process
        process_func: Async function to process each item
        batch_size: Number of items to process concurrently

    Returns:
        List of AsyncResult objects with results or errors
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_tasks = []

        for item in batch:

            async def process_item(item=item):
                start_time = time.time()
                result = AsyncResult()

                try:
                    result.result = await process_func(item)
                    result.is_success = True
                except Exception as e:
                    result.error = e
                    result.is_success = False
                    logger.error(f"Error processing item: {e}")
                finally:
                    result.processing_time = time.time() - start_time

                return result

            batch_tasks.append(process_item())

        # Process the batch
        batch_results = await asyncio.gather(*batch_tasks)
        results.extend(batch_results)

    return results


async def stream_processor(
    input_stream: AsyncIterator[T],
    process_func: Callable[[T], Awaitable[U]],
    buffer_size: int = 10,
) -> AsyncIterator[U]:
    """
    Process items from an input stream and yield results as they become available.

    Args:
        input_stream: Async iterator producing input items
        process_func: Async function to process each item
        buffer_size: Number of items to buffer for processing

    Yields:
        Processed results as they become available
    """
    pending = set()

    async def process_item(item):
        return await process_func(item)

    # Process items from the input stream
    try:
        # Fill the initial buffer
        for _ in range(buffer_size):
            try:
                item = await asyncio.anext(input_stream)
                task = asyncio.create_task(process_item(item))
                pending.add(task)
                task.add_done_callback(pending.discard)
            except StopAsyncIteration:
                break

        # Process the rest of the stream
        while pending:
            # Get the first completed task
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            # Yield the results
            for task in done:
                yield task.result()

            # Refill the buffer
            try:
                for _ in range(buffer_size - len(pending)):
                    item = await asyncio.anext(input_stream)
                    task = asyncio.create_task(process_item(item))
                    pending.add(task)
                    task.add_done_callback(pending.discard)
            except StopAsyncIteration:
                pass
    except Exception as e:
        logger.error(f"Error in stream processor: {e}")
        raise


class AsyncModelProcessor:
    """
    Helper class for processing data through AI models asynchronously.
    """

    def __init__(self, model_manager):
        """
        Initialize the async model processor.

        Args:
            model_manager: The model manager instance to use for loading models
        """
        self.model_manager = model_manager
        self.loaded_models = {}
        self.semaphore = asyncio.Semaphore(10)  # Default concurrency limit

    async def ensure_model_loaded(
        self, model_id: str, version: str = None, **kwargs
    ) -> Any:
        """
        Ensure a model is loaded before using it.

        Args:
            model_id: ID of the model to load
            version: Optional version of the model
            **kwargs: Additional parameters for model loading

        Returns:
            The loaded model
        """
        key = f"{model_id}_{version}" if version else model_id

        if key not in self.loaded_models:
            self.loaded_models[key] = await self.model_manager.load_model_async(
                model_id, version, **kwargs
            )

        return self.loaded_models[key]

    async def process_batch(
        self,
        model_id: str,
        items: List[Dict[str, Any]],
        process_func: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        model_version: str = None,
        concurrency: int = 5,
        **kwargs,
    ) -> List[AsyncResult[Any]]:
        """
        Process a batch of items using a model.

        Args:
            model_id: ID of the model to use
            items: List of items to process
            process_func: Function to process each item with the model
            model_version: Optional version of the model
            concurrency: Number of items to process concurrently
            **kwargs: Additional parameters for model loading

        Returns:
            List of AsyncResult objects with results or errors
        """
        # Ensure the model is loaded
        model = await self.ensure_model_loaded(model_id, model_version, **kwargs)

        # Process the items
        async def process_item(item):
            return await process_func(model, item)

        return await batch_process_async(items, process_item, concurrency)

    async def generate_text_batch(
        self,
        model_id: str,
        prompts: List[str],
        model_version: str = None,
        concurrency: int = 5,
        **kwargs,
    ) -> List[AsyncResult[str]]:
        """
        Generate text for multiple prompts in parallel.

        Args:
            model_id: ID of the model to use
            prompts: List of prompts to process
            model_version: Optional version of the model
            concurrency: Number of prompts to process concurrently
            **kwargs: Additional parameters for text generation

        Returns:
            List of AsyncResult objects with generated text or errors
        """
        # Get the model info to determine adapter type
        model_info = self.model_manager.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model with ID {model_id} not found")

        adapter = None

        # If the model has an adapter assigned, use it
        if hasattr(self.model_manager, "get_adapter_for_model"):
            adapter = self.model_manager.get_adapter_for_model(model_id)

        # If adapter is available, use it directly
        if adapter and hasattr(adapter, "generate_text_async"):
            # Create a wrapper for the process_func
            async def process_func(prompt):
                return await adapter.generate_text_async(model_id, prompt, **kwargs)

            return await batch_process_async(prompts, process_func, concurrency)

        # Otherwise, use the model directly (this assumes the model has a generate method)
        else:
            # Ensure the model is loaded
            model = await self.ensure_model_loaded(model_id, model_version, **kwargs)

            # Use run_in_thread for models that don't have async methods
            async def process_func(prompt):
                if hasattr(model, "generate_text_async"):
                    return await model.generate_text_async(prompt, **kwargs)
                elif hasattr(model, "generate_text"):
                    return await run_in_thread(model.generate_text, prompt, **kwargs)
                else:
                    raise NotImplementedError(
                        f"Model {model_id} does not support text generation"
                    )

            return await batch_process_async(prompts, process_func, concurrency)

    async def generate_embeddings_batch(
        self,
        model_id: str,
        texts: List[str],
        model_version: str = None,
        concurrency: int = 10,
        **kwargs,
    ) -> List[AsyncResult[List[float]]]:
        """
        Generate embeddings for multiple texts in parallel.

        Args:
            model_id: ID of the model to use
            texts: List of texts to process
            model_version: Optional version of the model
            concurrency: Number of texts to process concurrently
            **kwargs: Additional parameters for embedding generation

        Returns:
            List of AsyncResult objects with embeddings or errors
        """
        # Get the model info to determine adapter type
        model_info = self.model_manager.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model with ID {model_id} not found")

        adapter = None

        # If the model has an adapter assigned, use it
        if hasattr(self.model_manager, "get_adapter_for_model"):
            adapter = self.model_manager.get_adapter_for_model(model_id)

        # If adapter is available, use it directly
        if adapter and hasattr(adapter, "create_embedding_async"):
            # Create a wrapper for the process_func
            async def process_func(text):
                return await adapter.create_embedding_async(model_id, text, **kwargs)

            return await batch_process_async(texts, process_func, concurrency)

        # Otherwise, use the model directly
        else:
            # Ensure the model is loaded
            model = await self.ensure_model_loaded(model_id, model_version, **kwargs)

            # Use run_in_thread for models that don't have async methods
            async def process_func(text):
                if hasattr(model, "create_embedding_async"):
                    return await model.create_embedding_async(text, **kwargs)
                elif hasattr(model, "create_embedding"):
                    return await run_in_thread(model.create_embedding, text, **kwargs)
                else:
                    raise NotImplementedError(
                        f"Model {model_id} does not support embedding generation"
                    )

            return await batch_process_async(texts, process_func, concurrency)


# Utility function to convert a synchronous function to asynchronous
def to_async(func):
    """
    Convert a synchronous function to asynchronous.

    Args:
        func: The synchronous function to convert

    Returns:
        Asynchronous version of the function
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_in_thread(func, *args, **kwargs)

    return wrapper