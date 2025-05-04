"""
"""
Batch inference module for the AI Models module.
Batch inference module for the AI Models module.


This module provides functionality for running batch inference with AI models,
This module provides functionality for running batch inference with AI models,
allowing for efficient processing of large datasets.
allowing for efficient processing of large datasets.
"""
"""


import asyncio
import asyncio
import logging
import logging
import time
import time
import uuid
import uuid
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from enum import Enum
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from typing import Any, Dict, Generic, List, Optional, TypeVar


from .async_utils import AsyncModelProcessor, AsyncResult
from .async_utils import AsyncModelProcessor, AsyncResult


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




class BatchStatus(Enum):
    class BatchStatus(Enum):
    """Status of a batch inference job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


    @dataclass
    class BatchInferenceRequest(Generic[T]):

    model_id: str
    inputs: List[T]
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_version: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


    @dataclass
    class BatchInferenceResult(Generic[T, U]):

    batch_id: str
    status: BatchStatus
    results: List[AsyncResult[U]]
    inputs: List[T]
    model_id: str
    model_version: Optional[str]
    start_time: float
    end_time: Optional[float] = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def processing_time(self) -> float:
    """Get the total processing time for the batch."""
    if self.end_time is None:
    return time.time() - self.start_time
    return self.end_time - self.start_time

    @property
    def success_count(self) -> int:
    """Get the number of successful results."""
    return sum(1 for result in self.results if result.is_success)

    @property
    def failure_count(self) -> int:
    """Get the number of failed results."""
    return sum(1 for result in self.results if not result.is_success)

    @property
    def success_rate(self) -> float:
    """Get the success rate as a percentage."""
    if not self.results:
    return 0.0
    return self.success_count / len(self.results) * 100.0


    class BatchInferenceManager:
    """
    """
    Manager for batch inference jobs.
    Manager for batch inference jobs.


    This class provides functionality for running batch inference with AI models,
    This class provides functionality for running batch inference with AI models,
    allowing for efficient processing of large datasets. It supports both synchronous
    allowing for efficient processing of large datasets. It supports both synchronous
    and asynchronous processing, with configurable batch sizes and concurrency limits.
    and asynchronous processing, with configurable batch sizes and concurrency limits.
    """
    """


    def __init__(self, model_manager):
    def __init__(self, model_manager):
    """
    """
    Initialize the batch inference manager.
    Initialize the batch inference manager.


    Args:
    Args:
    model_manager: The model manager instance to use for loading models
    model_manager: The model manager instance to use for loading models
    """
    """
    self.model_manager = model_manager
    self.model_manager = model_manager
    self.async_processor = AsyncModelProcessor(model_manager)
    self.async_processor = AsyncModelProcessor(model_manager)
    self.batch_results = {}
    self.batch_results = {}
    self.active_batches = {}
    self.active_batches = {}
    self.default_batch_size = 10
    self.default_batch_size = 10
    self.default_concurrency = 5
    self.default_concurrency = 5


    async def process_batch_async(
    async def process_batch_async(
    self,
    self,
    request: BatchInferenceRequest[T],
    request: BatchInferenceRequest[T],
    process_func,
    process_func,
    batch_size: int = None,
    batch_size: int = None,
    concurrency: int = None,
    concurrency: int = None,
    ) -> BatchInferenceResult[T, U]:
    ) -> BatchInferenceResult[T, U]:
    """
    """
    Process a batch of inputs asynchronously.
    Process a batch of inputs asynchronously.


    Args:
    Args:
    request: The batch inference request
    request: The batch inference request
    process_func: Function to process each input with the model
    process_func: Function to process each input with the model
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    concurrency: Number of items to process concurrently (defaults to self.default_concurrency)
    concurrency: Number of items to process concurrently (defaults to self.default_concurrency)


    Returns:
    Returns:
    BatchInferenceResult with the results of the batch processing
    BatchInferenceResult with the results of the batch processing
    """
    """
    batch_size = batch_size or self.default_batch_size
    batch_size = batch_size or self.default_batch_size
    concurrency = concurrency or self.default_concurrency
    concurrency = concurrency or self.default_concurrency


    # Create a batch result object
    # Create a batch result object
    batch_result = BatchInferenceResult(
    batch_result = BatchInferenceResult(
    batch_id=request.batch_id,
    batch_id=request.batch_id,
    status=BatchStatus.RUNNING,
    status=BatchStatus.RUNNING,
    results=[],
    results=[],
    inputs=request.inputs,
    inputs=request.inputs,
    model_id=request.model_id,
    model_id=request.model_id,
    model_version=request.model_version,
    model_version=request.model_version,
    start_time=time.time(),
    start_time=time.time(),
    )
    )


    # Store the batch result
    # Store the batch result
    self.batch_results[request.batch_id] = batch_result
    self.batch_results[request.batch_id] = batch_result
    self.active_batches[request.batch_id] = asyncio.current_task()
    self.active_batches[request.batch_id] = asyncio.current_task()


    try:
    try:
    # Process the batch
    # Process the batch
    results = await self.async_processor.process_batch(
    results = await self.async_processor.process_batch(
    model_id=request.model_id,
    model_id=request.model_id,
    items=request.inputs,
    items=request.inputs,
    process_func=process_func,
    process_func=process_func,
    model_version=request.model_version,
    model_version=request.model_version,
    concurrency=concurrency,
    concurrency=concurrency,
    **request.parameters,
    **request.parameters,
    )
    )


    # Update the batch result
    # Update the batch result
    batch_result.results = results
    batch_result.results = results
    batch_result.status = BatchStatus.COMPLETED
    batch_result.status = BatchStatus.COMPLETED
    batch_result.end_time = time.time()
    batch_result.end_time = time.time()


    # Log the results
    # Log the results
    logger.info(
    logger.info(
    f"Batch {request.batch_id} completed: "
    f"Batch {request.batch_id} completed: "
    f"{batch_result.success_count}/{len(request.inputs)} successful "
    f"{batch_result.success_count}/{len(request.inputs)} successful "
    f"({batch_result.success_rate:.1f}% success rate) "
    f"({batch_result.success_rate:.1f}% success rate) "
    f"in {batch_result.processing_time:.2f}s"
    f"in {batch_result.processing_time:.2f}s"
    )
    )


    return batch_result
    return batch_result


except Exception as e:
except Exception as e:
    # Update the batch result with the error
    # Update the batch result with the error
    batch_result.status = BatchStatus.FAILED
    batch_result.status = BatchStatus.FAILED
    batch_result.error = e
    batch_result.error = e
    batch_result.end_time = time.time()
    batch_result.end_time = time.time()


    # Log the error
    # Log the error
    logger.error(f"Batch {request.batch_id} failed: {str(e)}")
    logger.error(f"Batch {request.batch_id} failed: {str(e)}")
    raise
    raise


finally:
finally:
    # Remove the batch from active batches
    # Remove the batch from active batches
    if request.batch_id in self.active_batches:
    if request.batch_id in self.active_batches:
    del self.active_batches[request.batch_id]
    del self.active_batches[request.batch_id]


    def process_batch(
    def process_batch(
    self,
    self,
    request: BatchInferenceRequest[T],
    request: BatchInferenceRequest[T],
    process_func,
    process_func,
    batch_size: int = None,
    batch_size: int = None,
    concurrency: int = None,
    concurrency: int = None,
    ) -> BatchInferenceResult[T, U]:
    ) -> BatchInferenceResult[T, U]:
    """
    """
    Process a batch of inputs synchronously.
    Process a batch of inputs synchronously.


    Args:
    Args:
    request: The batch inference request
    request: The batch inference request
    process_func: Function to process each input with the model
    process_func: Function to process each input with the model
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    concurrency: Number of items to process concurrently (defaults to self.default_concurrency)
    concurrency: Number of items to process concurrently (defaults to self.default_concurrency)


    Returns:
    Returns:
    BatchInferenceResult with the results of the batch processing
    BatchInferenceResult with the results of the batch processing
    """
    """
    # Create an event loop if one doesn't exist
    # Create an event loop if one doesn't exist
    try:
    try:
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
except RuntimeError:
except RuntimeError:
    loop = asyncio.new_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.set_event_loop(loop)


    # Run the async function in the event loop
    # Run the async function in the event loop
    return loop.run_until_complete(
    return loop.run_until_complete(
    self.process_batch_async(request, process_func, batch_size, concurrency)
    self.process_batch_async(request, process_func, batch_size, concurrency)
    )
    )


    async def generate_text_batch_async(
    async def generate_text_batch_async(
    self,
    self,
    model_id: str,
    model_id: str,
    prompts: List[str],
    prompts: List[str],
    batch_id: str = None,
    batch_id: str = None,
    model_version: str = None,
    model_version: str = None,
    batch_size: int = None,
    batch_size: int = None,
    concurrency: int = None,
    concurrency: int = None,
    **kwargs,
    **kwargs,
    ) -> BatchInferenceResult[str, str]:
    ) -> BatchInferenceResult[str, str]:
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
    batch_id: Optional ID for the batch (generated if not provided)
    batch_id: Optional ID for the batch (generated if not provided)
    model_version: Optional version of the model
    model_version: Optional version of the model
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    concurrency: Number of prompts to process concurrently (defaults to self.default_concurrency)
    concurrency: Number of prompts to process concurrently (defaults to self.default_concurrency)
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    BatchInferenceResult with the generated text or errors
    BatchInferenceResult with the generated text or errors
    """
    """
    # Create a batch inference request
    # Create a batch inference request
    request = BatchInferenceRequest(
    request = BatchInferenceRequest(
    model_id=model_id,
    model_id=model_id,
    inputs=prompts,
    inputs=prompts,
    batch_id=batch_id or str(uuid.uuid4()),
    batch_id=batch_id or str(uuid.uuid4()),
    model_version=model_version,
    model_version=model_version,
    parameters=kwargs,
    parameters=kwargs,
    )
    )


    # Process the batch
    # Process the batch
    return await self.async_processor.generate_text_batch(
    return await self.async_processor.generate_text_batch(
    model_id=model_id,
    model_id=model_id,
    prompts=prompts,
    prompts=prompts,
    model_version=model_version,
    model_version=model_version,
    concurrency=concurrency or self.default_concurrency,
    concurrency=concurrency or self.default_concurrency,
    **kwargs,
    **kwargs,
    )
    )


    def generate_text_batch(
    def generate_text_batch(
    self,
    self,
    model_id: str,
    model_id: str,
    prompts: List[str],
    prompts: List[str],
    batch_id: str = None,
    batch_id: str = None,
    model_version: str = None,
    model_version: str = None,
    batch_size: int = None,
    batch_size: int = None,
    concurrency: int = None,
    concurrency: int = None,
    **kwargs,
    **kwargs,
    ) -> BatchInferenceResult[str, str]:
    ) -> BatchInferenceResult[str, str]:
    """
    """
    Generate text for multiple prompts in parallel (synchronous version).
    Generate text for multiple prompts in parallel (synchronous version).


    Args:
    Args:
    model_id: ID of the model to use
    model_id: ID of the model to use
    prompts: List of prompts to process
    prompts: List of prompts to process
    batch_id: Optional ID for the batch (generated if not provided)
    batch_id: Optional ID for the batch (generated if not provided)
    model_version: Optional version of the model
    model_version: Optional version of the model
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    concurrency: Number of prompts to process concurrently (defaults to self.default_concurrency)
    concurrency: Number of prompts to process concurrently (defaults to self.default_concurrency)
    **kwargs: Additional parameters for text generation
    **kwargs: Additional parameters for text generation


    Returns:
    Returns:
    BatchInferenceResult with the generated text or errors
    BatchInferenceResult with the generated text or errors
    """
    """
    # Create an event loop if one doesn't exist
    # Create an event loop if one doesn't exist
    try:
    try:
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
except RuntimeError:
except RuntimeError:
    loop = asyncio.new_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.set_event_loop(loop)


    # Run the async function in the event loop
    # Run the async function in the event loop
    return loop.run_until_complete(
    return loop.run_until_complete(
    self.generate_text_batch_async(
    self.generate_text_batch_async(
    model_id,
    model_id,
    prompts,
    prompts,
    batch_id,
    batch_id,
    model_version,
    model_version,
    batch_size,
    batch_size,
    concurrency,
    concurrency,
    **kwargs,
    **kwargs,
    )
    )
    )
    )


    async def generate_embeddings_batch_async(
    async def generate_embeddings_batch_async(
    self,
    self,
    model_id: str,
    model_id: str,
    texts: List[str],
    texts: List[str],
    batch_id: str = None,
    batch_id: str = None,
    model_version: str = None,
    model_version: str = None,
    batch_size: int = None,
    batch_size: int = None,
    concurrency: int = None,
    concurrency: int = None,
    **kwargs,
    **kwargs,
    ) -> BatchInferenceResult[str, List[float]]:
    ) -> BatchInferenceResult[str, List[float]]:
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
    batch_id: Optional ID for the batch (generated if not provided)
    batch_id: Optional ID for the batch (generated if not provided)
    model_version: Optional version of the model
    model_version: Optional version of the model
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    concurrency: Number of texts to process concurrently (defaults to self.default_concurrency)
    concurrency: Number of texts to process concurrently (defaults to self.default_concurrency)
    **kwargs: Additional parameters for embedding generation
    **kwargs: Additional parameters for embedding generation


    Returns:
    Returns:
    BatchInferenceResult with the embeddings or errors
    BatchInferenceResult with the embeddings or errors
    """
    """
    # Create a batch inference request
    # Create a batch inference request
    request = BatchInferenceRequest(
    request = BatchInferenceRequest(
    model_id=model_id,
    model_id=model_id,
    inputs=texts,
    inputs=texts,
    batch_id=batch_id or str(uuid.uuid4()),
    batch_id=batch_id or str(uuid.uuid4()),
    model_version=model_version,
    model_version=model_version,
    parameters=kwargs,
    parameters=kwargs,
    )
    )


    # Process the batch
    # Process the batch
    return await self.async_processor.generate_embeddings_batch(
    return await self.async_processor.generate_embeddings_batch(
    model_id=model_id,
    model_id=model_id,
    texts=texts,
    texts=texts,
    model_version=model_version,
    model_version=model_version,
    concurrency=concurrency or self.default_concurrency,
    concurrency=concurrency or self.default_concurrency,
    **kwargs,
    **kwargs,
    )
    )


    def generate_embeddings_batch(
    def generate_embeddings_batch(
    self,
    self,
    model_id: str,
    model_id: str,
    texts: List[str],
    texts: List[str],
    batch_id: str = None,
    batch_id: str = None,
    model_version: str = None,
    model_version: str = None,
    batch_size: int = None,
    batch_size: int = None,
    concurrency: int = None,
    concurrency: int = None,
    **kwargs,
    **kwargs,
    ) -> BatchInferenceResult[str, List[float]]:
    ) -> BatchInferenceResult[str, List[float]]:
    """
    """
    Generate embeddings for multiple texts in parallel (synchronous version).
    Generate embeddings for multiple texts in parallel (synchronous version).


    Args:
    Args:
    model_id: ID of the model to use
    model_id: ID of the model to use
    texts: List of texts to process
    texts: List of texts to process
    batch_id: Optional ID for the batch (generated if not provided)
    batch_id: Optional ID for the batch (generated if not provided)
    model_version: Optional version of the model
    model_version: Optional version of the model
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    batch_size: Size of each sub-batch (defaults to self.default_batch_size)
    concurrency: Number of texts to process concurrently (defaults to self.default_concurrency)
    concurrency: Number of texts to process concurrently (defaults to self.default_concurrency)
    **kwargs: Additional parameters for embedding generation
    **kwargs: Additional parameters for embedding generation


    Returns:
    Returns:
    BatchInferenceResult with the embeddings or errors
    BatchInferenceResult with the embeddings or errors
    """
    """
    # Create an event loop if one doesn't exist
    # Create an event loop if one doesn't exist
    try:
    try:
    loop = asyncio.get_event_loop()
    loop = asyncio.get_event_loop()
except RuntimeError:
except RuntimeError:
    loop = asyncio.new_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.set_event_loop(loop)


    # Run the async function in the event loop
    # Run the async function in the event loop
    return loop.run_until_complete(
    return loop.run_until_complete(
    self.generate_embeddings_batch_async(
    self.generate_embeddings_batch_async(
    model_id,
    model_id,
    texts,
    texts,
    batch_id,
    batch_id,
    model_version,
    model_version,
    batch_size,
    batch_size,
    concurrency,
    concurrency,
    **kwargs,
    **kwargs,
    )
    )
    )
    )


    def get_batch_result(self, batch_id: str) -> Optional[BatchInferenceResult]:
    def get_batch_result(self, batch_id: str) -> Optional[BatchInferenceResult]:
    """
    """
    Get the result of a batch inference job.
    Get the result of a batch inference job.


    Args:
    Args:
    batch_id: ID of the batch
    batch_id: ID of the batch


    Returns:
    Returns:
    BatchInferenceResult or None if the batch ID is not found
    BatchInferenceResult or None if the batch ID is not found
    """
    """
    return self.batch_results.get(batch_id)
    return self.batch_results.get(batch_id)


    def cancel_batch(self, batch_id: str) -> bool:
    def cancel_batch(self, batch_id: str) -> bool:
    """
    """
    Cancel a running batch inference job.
    Cancel a running batch inference job.


    Args:
    Args:
    batch_id: ID of the batch to cancel
    batch_id: ID of the batch to cancel


    Returns:
    Returns:
    True if the batch was cancelled, False otherwise
    True if the batch was cancelled, False otherwise
    """
    """
    if batch_id in self.active_batches:
    if batch_id in self.active_batches:
    task = self.active_batches[batch_id]
    task = self.active_batches[batch_id]
    task.cancel()
    task.cancel()


    # Update the batch result
    # Update the batch result
    if batch_id in self.batch_results:
    if batch_id in self.batch_results:
    self.batch_results[batch_id].status = BatchStatus.CANCELLED
    self.batch_results[batch_id].status = BatchStatus.CANCELLED
    self.batch_results[batch_id].end_time = time.time()
    self.batch_results[batch_id].end_time = time.time()


    # Remove the batch from active batches
    # Remove the batch from active batches
    del self.active_batches[batch_id]
    del self.active_batches[batch_id]


    logger.info(f"Batch {batch_id} cancelled")
    logger.info(f"Batch {batch_id} cancelled")
    return True
    return True


    return False
    return False


    def get_active_batches(self) -> List[str]:
    def get_active_batches(self) -> List[str]:
    """
    """
    Get the IDs of all active batch inference jobs.
    Get the IDs of all active batch inference jobs.


    Returns:
    Returns:
    List of batch IDs
    List of batch IDs
    """
    """
    return list(self.active_batches.keys())
    return list(self.active_batches.keys())


    def get_batch_results(self) -> Dict[str, BatchInferenceResult]:
    def get_batch_results(self) -> Dict[str, BatchInferenceResult]:
    """
    """
    Get all batch inference results.
    Get all batch inference results.


    Returns:
    Returns:
    Dictionary of batch IDs to BatchInferenceResult objects
    Dictionary of batch IDs to BatchInferenceResult objects
    """
    """
    return self.batch_results
    return self.batch_results


    def clear_batch_results(self, batch_id: Optional[str] = None) -> None:
    def clear_batch_results(self, batch_id: Optional[str] = None) -> None:
    """
    """
    Clear batch inference results.
    Clear batch inference results.


    Args:
    Args:
    batch_id: Optional ID of the batch to clear. If None, all results are cleared.
    batch_id: Optional ID of the batch to clear. If None, all results are cleared.
    """
    """
    if batch_id:
    if batch_id:
    if batch_id in self.batch_results:
    if batch_id in self.batch_results:
    del self.batch_results[batch_id]
    del self.batch_results[batch_id]
    else:
    else:
    self.batch_results.clear()
    self.batch_results.clear()




    # Example usage
    # Example usage
    if __name__ == "__main__":
    if __name__ == "__main__":
    from .model_manager import ModelManager
    from .model_manager import ModelManager


    # Create a model manager
    # Create a model manager
    manager = ModelManager()
    manager = ModelManager()


    # Create a batch inference manager
    # Create a batch inference manager
    batch_manager = BatchInferenceManager(manager)
    batch_manager = BatchInferenceManager(manager)


    # Generate text for multiple prompts
    # Generate text for multiple prompts
    prompts = [
    prompts = [
    "Write a short story about a robot.",
    "Write a short story about a robot.",
    "Explain quantum computing in simple terms.",
    "Explain quantum computing in simple terms.",
    "What are the benefits of exercise?",
    "What are the benefits of exercise?",
    ]
    ]


    try:
    try:
    # Get available models
    # Get available models
    models = manager.get_all_models()
    models = manager.get_all_models()
    if models:
    if models:
    model_id = models[0].id
    model_id = models[0].id
    print(f"Using model: {model_id}")
    print(f"Using model: {model_id}")


    # Generate text for multiple prompts
    # Generate text for multiple prompts
    result = batch_manager.generate_text_batch(
    result = batch_manager.generate_text_batch(
    model_id=model_id,
    model_id=model_id,
    prompts=prompts,
    prompts=prompts,
    temperature=0.7,
    temperature=0.7,
    max_tokens=100,
    max_tokens=100,
    )
    )


    # Print the results
    # Print the results
    print(f"Batch ID: {result.batch_id}")
    print(f"Batch ID: {result.batch_id}")
    print(f"Status: {result.status}")
    print(f"Status: {result.status}")
    print(f"Success rate: {result.success_rate:.1f}%")
    print(f"Success rate: {result.success_rate:.1f}%")
    print(f"Processing time: {result.processing_time:.2f}s")
    print(f"Processing time: {result.processing_time:.2f}s")


    for i, (prompt, result) in enumerate(zip(prompts, result.results)):
    for i, (prompt, result) in enumerate(zip(prompts, result.results)):
    print(f"\nPrompt {i+1}: {prompt}")
    print(f"\nPrompt {i+1}: {prompt}")
    if result.is_success:
    if result.is_success:
    print(f"Response: {result.result}")
    print(f"Response: {result.result}")
    else:
    else:
    print(f"Error: {result.error}")
    print(f"Error: {result.error}")
    else:
    else:
    print("No models available.")
    print("No models available.")
except Exception as e:
except Exception as e:
    print(f"Error: {e}")
    print(f"Error: {e}")

