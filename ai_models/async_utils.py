"""Utilities for async operations and batch processing."""

import asyncio
import functools
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Generic, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class AsyncResult(Generic[T]):
    """Container for async operation results."""

    result: Optional[T] = None
    error: Optional[Exception] = None
    is_complete: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


async def handle_task_exception(task: asyncio.Task) -> None:
    """Handle exceptions from a task and log them."""
    try:
        await task
    except Exception as e:
        logger.error("Task failed with error: {}".format(e))
        # Re-raise the exception to ensure it's not silently swallowed
        raise


async def run_with_timeout(coro: Awaitable[T], timeout: float) -> T:
    """Run a coroutine with a timeout.

    Args:
        coro: The coroutine to run
        timeout: Timeout in seconds

    Returns:
        The result of the coroutine

    Raises:
        asyncio.TimeoutError: If the operation times out
        Exception: Any other exception from the coroutine
    """
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        logger.warning("Operation timed out after {} seconds".format(timeout))
        raise
    except Exception as e:
        logger.error("Operation failed with error: {}".format(e))
        raise


class AsyncBuffer(Generic[T]):
    """A buffer for async operations that supports batching."""

    def __init__(
        self,
        maxsize: int = 1000,
        batch_size: int = 10,
        flush_interval: float = 1.0,
    ):
        """Initialize the buffer.

        Args:
            maxsize: Maximum size of the buffer
            batch_size: Size of batches to process
            flush_interval: How often to flush the buffer in seconds
        """
        self._buffer = deque(maxlen=maxsize)
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None

    async def put(self, item: T) -> None:
        """Add an item to the buffer.

        Args:
            item: Item to add to the buffer
        """
        async with self._lock:
            self._buffer.append(item)
            if len(self._buffer) >= self._batch_size:
                await self.flush()

    async def flush(self) -> None:
        """Flush the current contents of the buffer."""
        async with self._lock:
            items = list(self._buffer)
            self._buffer.clear()
            if items:
                try:
                    await self.process_batch(items)
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    raise

    async def process_batch(self, items: List[T]) -> None:
        """Process a batch of items. Override this method in subclasses.

        Args:
            items: List of items to process
        """
        raise NotImplementedError

    def start(self) -> None:
        """Start the automatic flushing task."""
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._auto_flush())

    def stop(self) -> None:
        """Stop the automatic flushing task."""
        if self._flush_task is not None:
            self._flush_task.cancel()
            self._flush_task = None

    async def _auto_flush(self) -> None:
        """Automatically flush the buffer at regular intervals."""
        while True:
            try:
                await asyncio.sleep(self._flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in auto flush: {}".format(e))


async def stream_processor(
    input_queue: asyncio.Queue[T],
    output_queue: asyncio.Queue[Any],
    process_func: Any,
    batch_size: int = 10,
    timeout: float = 1.0,
) -> None:
    """Process items from a queue in batches.

    Args:
        input_queue: Queue containing input items
        output_queue: Queue to put processed results into
        process_func: Function to process batches
        batch_size: Size of batches to process
        timeout: How long to wait for items before processing partial batch
    """
    batch = []
    last_process_time = asyncio.get_event_loop().time()

    while True:
        try:
            # Try to get an item from the queue
            try:
                item = await asyncio.wait_for(input_queue.get(), timeout)
                batch.append(item)
                input_queue.task_done()
            except asyncio.TimeoutError:
                # Process partial batch on timeout if we have items
                if batch:
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_process_time >= timeout:
                        await process_batch(batch, process_func, output_queue)
                        batch = []
                        last_process_time = current_time
                continue

            # Process batch if it's full
            if len(batch) >= batch_size:
                await process_batch(batch, process_func, output_queue)
                batch = []
                last_process_time = asyncio.get_event_loop().time()

        except asyncio.CancelledError:
            # Process any remaining items before exiting
            if batch:
                await process_batch(batch, process_func, output_queue)
            break
        except Exception as e:
            logger.error("Error in stream processor: {}".format(e))
            raise


async def process_batch(batch: List[T], process_func: Any, output_queue: asyncio.Queue) -> None:
    """Process a batch of items and put results in output queue.

    Args:
        batch: List of items to process
        process_func: Function to process items
        output_queue: Queue to put results into
    """
    try:
        results = await process_func(batch)
        for result in results:
            await output_queue.put(result)
    except Exception as e:
        logger.error("Error processing batch: {}".format(e))
        raise


async def run_in_thread(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run a blocking function in a thread pool.

    This function allows running blocking I/O operations without blocking
    the event loop, which is essential for maintaining responsiveness in
    async applications.

    Args:
        func: The blocking function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call

    Raises:
        Exception: Any exception raised by the function
    """
    loop = asyncio.get_event_loop()

    # Use functools.partial to create a callable with the args and kwargs
    pfunc = functools.partial(func, *args, **kwargs)

    # Run the function in the default thread pool
    try:
        return await loop.run_in_executor(None, pfunc)
    except Exception as e:
        logger.error("Error running function {} in thread: {}".format(func.__name__, e))
        raise


@dataclass
class AsyncResult(Generic[T]):
    """Result of an asynchronous operation."""

    success: bool
    result: Optional[T] = None
    error: Optional[Exception] = None

    @classmethod
    def success_result(cls, result: T) -> "AsyncResult[T]":
        """Create a successful result.

        Args:
            result: The result value

        Returns:
            AsyncResult with success=True and the result
        """
        return cls(success=True, result=result)

    @classmethod
    def error_result(cls, error: Exception) -> "AsyncResult[T]":
        """Create an error result.

        Args:
            error: The exception that occurred

        Returns:
            AsyncResult with success=False and the error
        """
        return cls(success=False, error=error)


class AsyncModelProcessor:
    """Processes model operations asynchronously."""

    def __init__(self, model_manager):
        """Initialize the async model processor.

        Args:
            model_manager: Model manager instance for loading models
        """
        self.model_manager = model_manager
        self.logger = logging.getLogger(__name__)

    async def generate_text_batch(
        self,
        model_id: str,
        prompts: List[str],
        model_version: Optional[str] = None,
        concurrency: int = 4,
        **kwargs,
    ) -> List[AsyncResult[str]]:
        """Generate text for multiple prompts asynchronously.

        Args:
            model_id: ID of the model to use
            prompts: List of prompts to process
            model_version: Optional version of the model
            concurrency: Maximum number of concurrent operations
            **kwargs: Additional parameters for text generation

        Returns:
            List of AsyncResult objects with generated texts
        """
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        # Create tasks for each prompt
        tasks = []
        for prompt in prompts:
            task = asyncio.create_task(
                self._generate_text_with_semaphore(
                    semaphore, model_id, prompt, model_version, **kwargs
                )
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        return results

    async def _generate_text_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        model_id: str,
        prompt: str,
        model_version: Optional[str] = None,
        **kwargs,
    ) -> AsyncResult[str]:
        """Generate text with semaphore for concurrency control.

        Args:
            semaphore: Semaphore for concurrency control
            model_id: ID of the model to use
            prompt: Prompt to process
            model_version: Optional version of the model
            **kwargs: Additional parameters for text generation

        Returns:
            AsyncResult with generated text or error
        """
        async with semaphore:
            try:
                # Load the model
                model = self.model_manager.load_model(model_id)

                # Generate text
                result = await run_in_thread(model.generate_text, prompt=prompt, **kwargs)

                return AsyncResult.success_result(result)
            except Exception as e:
                self.logger.error(f"Error generating text: {e}")
                return AsyncResult.error_result(e)

    async def generate_embeddings_batch(
        self,
        model_id: str,
        texts: List[str],
        model_version: Optional[str] = None,
        concurrency: int = 8,
        **kwargs,
    ) -> List[AsyncResult[List[float]]]:
        """Generate embeddings for multiple texts asynchronously.

        Args:
            model_id: ID of the model to use
            texts: List of texts to embed
            model_version: Optional version of the model
            concurrency: Maximum number of concurrent operations
            **kwargs: Additional parameters for embedding generation

        Returns:
            List of AsyncResult objects with embeddings
        """
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        # Create tasks for each text
        tasks = []
        for text in texts:
            task = asyncio.create_task(
                self._generate_embedding_with_semaphore(
                    semaphore, model_id, text, model_version, **kwargs
                )
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        return results

    async def _generate_embedding_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        model_id: str,
        text: str,
        model_version: Optional[str] = None,
        **kwargs,
    ) -> AsyncResult[List[float]]:
        """Generate embedding with semaphore for concurrency control.

        Args:
            semaphore: Semaphore for concurrency control
            model_id: ID of the model to use
            text: Text to embed
            model_version: Optional version of the model
            **kwargs: Additional parameters for embedding generation

        Returns:
            AsyncResult with embedding or error
        """
        async with semaphore:
            try:
                # Load the model
                model = self.model_manager.load_model(model_id)

                # Generate embedding
                result = await run_in_thread(model.generate_embedding, text=text, **kwargs)

                return AsyncResult.success_result(result)
            except Exception as e:
                self.logger.error(f"Error generating embedding: {e}")
                return AsyncResult.error_result(e)
