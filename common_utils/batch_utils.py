"""
"""
Batch processing utilities for optimizing operations that can be processed in groups.
Batch processing utilities for optimizing operations that can be processed in groups.


This module provides utilities for batch processing operations, such as:
    This module provides utilities for batch processing operations, such as:
    - Chunking large datasets into batches
    - Chunking large datasets into batches
    - Processing batches in parallel or sequentially
    - Processing batches in parallel or sequentially
    - Aggregating batch results
    - Aggregating batch results
    - Tracking batch processing progress
    - Tracking batch processing progress
    """
    """




    import logging
    import logging
    import math
    import math
    import time
    import time
    import uuid
    import uuid
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from dataclasses import dataclass
    from dataclasses import dataclass
    from datetime import datetime
    from datetime import datetime


    (
    (
    Any,
    Any,
    Callable,
    Callable,
    Dict,
    Dict,
    Generic,
    Generic,
    Iterator,
    Iterator,
    List,
    List,
    TypeVar,
    TypeVar,
    Union,
    Union,
    )
    )


    # Type variables for generic functions
    # Type variables for generic functions
    T = TypeVar("T")  # Input item type
    T = TypeVar("T")  # Input item type
    R = TypeVar("R")  # Result item type
    R = TypeVar("R")  # Result item type


    # Set up logging
    # Set up logging
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    @dataclass
    @dataclass
    class BatchProcessingStats:
    class BatchProcessingStats:
    """Statistics for a batch processing operation."""

    batch_id: str
    total_items: int
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    start_time: datetime = None
    end_time: datetime = None
    processing_time_ms: float = 0.0

    @property
    def is_complete(self) -> bool:
    """Check if batch processing is complete."""
    return self.processed_items >= self.total_items

    @property
    def success_rate(self) -> float:
    """Calculate the success rate as a percentage."""
    if self.processed_items == 0:
    return 0.0
    return (self.successful_items / self.processed_items) * 100

    @property
    def items_per_second(self) -> float:
    """Calculate the processing rate in items per second."""
    if not self.processing_time_ms or self.processing_time_ms == 0:
    return 0.0
    return self.processed_items / (self.processing_time_ms / 1000)

    def to_dict(self) -> Dict[str, Any]:
    """Convert stats to a dictionary."""
    return {
    "batch_id": self.batch_id,
    "total_items": self.total_items,
    "processed_items": self.processed_items,
    "successful_items": self.successful_items,
    "failed_items": self.failed_items,
    "start_time": self.start_time.isoformat() if self.start_time else None,
    "end_time": self.end_time.isoformat() if self.end_time else None,
    "processing_time_ms": self.processing_time_ms,
    "is_complete": self.is_complete,
    "success_rate": self.success_rate,
    "items_per_second": self.items_per_second,
    }


    @dataclass
    class BatchResult(Generic[T, R]):

    batch_id: str
    results: List[R]
    errors: Dict[int, Exception]
    stats: BatchProcessingStats

    def get_successful_results(self) -> List[R]:
    """Get only the successful results."""
    return self.results

    def get_error_items(self) -> Dict[int, Exception]:
    """Get the items that resulted in errors."""
    return self.errors


    def chunk_list(items: List[T], batch_size: int) -> List[List[T]]:
    """
    """
    Split a list into chunks of the specified size.
    Split a list into chunks of the specified size.


    Args:
    Args:
    items: The list to split
    items: The list to split
    batch_size: The maximum size of each chunk
    batch_size: The maximum size of each chunk


    Returns:
    Returns:
    A list of lists, where each inner list is a chunk of the original list
    A list of lists, where each inner list is a chunk of the original list
    """
    """
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]




    def process_batch(
    def process_batch(
    items: List[T],
    items: List[T],
    processor_func: Callable[[T], R],
    processor_func: Callable[[T], R],
    max_workers: int = None,
    max_workers: int = None,
    batch_id: str = None,
    batch_id: str = None,
    timeout: float = None,
    timeout: float = None,
    ) -> BatchResult[T, R]:
    ) -> BatchResult[T, R]:
    """
    """
    Process a batch of items using a processor function.
    Process a batch of items using a processor function.


    Args:
    Args:
    items: List of items to process
    items: List of items to process
    processor_func: Function to process each item
    processor_func: Function to process each item
    max_workers: Maximum number of workers for parallel processing (if None, uses CPU count)
    max_workers: Maximum number of workers for parallel processing (if None, uses CPU count)
    batch_id: Optional ID for the batch (if None, generates a UUID)
    batch_id: Optional ID for the batch (if None, generates a UUID)
    timeout: Optional timeout in seconds for each item's processing
    timeout: Optional timeout in seconds for each item's processing


    Returns:
    Returns:
    BatchResult containing results, errors, and statistics
    BatchResult containing results, errors, and statistics
    """
    """
    if not batch_id:
    if not batch_id:
    batch_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())


    stats = BatchProcessingStats(
    stats = BatchProcessingStats(
    batch_id=batch_id, total_items=len(items), start_time=datetime.now()
    batch_id=batch_id, total_items=len(items), start_time=datetime.now()
    )
    )


    results = [None] * len(items)  # Pre-allocate results list
    results = [None] * len(items)  # Pre-allocate results list
    errors = {}  # Dictionary to track errors by index
    errors = {}  # Dictionary to track errors by index


    start_time = time.time()
    start_time = time.time()


    # Process items in parallel using ThreadPoolExecutor
    # Process items in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # Submit all tasks
    # Submit all tasks
    future_to_index = {
    future_to_index = {
    executor.submit(processor_func, item): i for i, item in enumerate(items)
    executor.submit(processor_func, item): i for i, item in enumerate(items)
    }
    }


    # Process results as they complete
    # Process results as they complete
    for future in as_completed(future_to_index):
    for future in as_completed(future_to_index):
    index = future_to_index[future]
    index = future_to_index[future]
    try:
    try:
    result = future.result(timeout=timeout)
    result = future.result(timeout=timeout)
    results[index] = result
    results[index] = result
    stats.successful_items += 1
    stats.successful_items += 1
except Exception as exc:
except Exception as exc:
    errors[index] = exc
    errors[index] = exc
    stats.failed_items += 1
    stats.failed_items += 1
    logger.warning(f"Item {index} in batch {batch_id} failed: {exc}")
    logger.warning(f"Item {index} in batch {batch_id} failed: {exc}")


    stats.processed_items += 1
    stats.processed_items += 1


    # Update stats
    # Update stats
    stats.end_time = datetime.now()
    stats.end_time = datetime.now()
    stats.processing_time_ms = (time.time() - start_time) * 1000
    stats.processing_time_ms = (time.time() - start_time) * 1000


    return BatchResult(batch_id=batch_id, results=results, errors=errors, stats=stats)
    return BatchResult(batch_id=batch_id, results=results, errors=errors, stats=stats)




    def process_batches(
    def process_batches(
    items: List[T],
    items: List[T],
    processor_func: Callable[[T], R],
    processor_func: Callable[[T], R],
    batch_size: int,
    batch_size: int,
    max_workers: int = None,
    max_workers: int = None,
    batch_id_prefix: str = None,
    batch_id_prefix: str = None,
    timeout: float = None,
    timeout: float = None,
    ) -> List[BatchResult[T, R]]:
    ) -> List[BatchResult[T, R]]:
    """
    """
    Process a large list of items in batches.
    Process a large list of items in batches.


    Args:
    Args:
    items: List of items to process
    items: List of items to process
    processor_func: Function to process each item
    processor_func: Function to process each item
    batch_size: Maximum size of each batch
    batch_size: Maximum size of each batch
    max_workers: Maximum number of workers for parallel processing within each batch
    max_workers: Maximum number of workers for parallel processing within each batch
    batch_id_prefix: Optional prefix for batch IDs
    batch_id_prefix: Optional prefix for batch IDs
    timeout: Optional timeout in seconds for each item's processing
    timeout: Optional timeout in seconds for each item's processing


    Returns:
    Returns:
    List of BatchResults, one for each batch
    List of BatchResults, one for each batch
    """
    """
    # Split items into batches
    # Split items into batches
    batches = chunk_list(items, batch_size)
    batches = chunk_list(items, batch_size)
    batch_results = []
    batch_results = []


    for i, batch in enumerate(batches):
    for i, batch in enumerate(batches):
    batch_id = f"{batch_id_prefix}-{i}" if batch_id_prefix else f"batch-{i}"
    batch_id = f"{batch_id_prefix}-{i}" if batch_id_prefix else f"batch-{i}"


    # Process each batch
    # Process each batch
    result = process_batch(
    result = process_batch(
    items=batch,
    items=batch,
    processor_func=processor_func,
    processor_func=processor_func,
    max_workers=max_workers,
    max_workers=max_workers,
    batch_id=batch_id,
    batch_id=batch_id,
    timeout=timeout,
    timeout=timeout,
    )
    )


    batch_results.append(result)
    batch_results.append(result)


    return batch_results
    return batch_results




    def aggregate_batch_results(
    def aggregate_batch_results(
    batch_results: List[BatchResult[T, R]],
    batch_results: List[BatchResult[T, R]],
    ) -> BatchResult[T, R]:
    ) -> BatchResult[T, R]:
    """
    """
    Aggregate multiple batch results into a single result.
    Aggregate multiple batch results into a single result.


    Args:
    Args:
    batch_results: List of batch results to aggregate
    batch_results: List of batch results to aggregate


    Returns:
    Returns:
    A single BatchResult combining all input results
    A single BatchResult combining all input results
    """
    """
    if not batch_results:
    if not batch_results:
    return None
    return None


    # Create a new aggregate batch ID
    # Create a new aggregate batch ID
    aggregate_batch_id = f"aggregate-{uuid.uuid4()}"
    aggregate_batch_id = f"aggregate-{uuid.uuid4()}"


    # Initialize stats for the aggregate batch
    # Initialize stats for the aggregate batch
    total_items = sum(result.stats.total_items for result in batch_results)
    total_items = sum(result.stats.total_items for result in batch_results)
    aggregate_stats = BatchProcessingStats(
    aggregate_stats = BatchProcessingStats(
    batch_id=aggregate_batch_id,
    batch_id=aggregate_batch_id,
    total_items=total_items,
    total_items=total_items,
    processed_items=sum(result.stats.processed_items for result in batch_results),
    processed_items=sum(result.stats.processed_items for result in batch_results),
    successful_items=sum(result.stats.successful_items for result in batch_results),
    successful_items=sum(result.stats.successful_items for result in batch_results),
    failed_items=sum(result.stats.failed_items for result in batch_results),
    failed_items=sum(result.stats.failed_items for result in batch_results),
    )
    )


    # Set start time to the earliest start time of any batch
    # Set start time to the earliest start time of any batch
    start_times = [
    start_times = [
    result.stats.start_time for result in batch_results if result.stats.start_time
    result.stats.start_time for result in batch_results if result.stats.start_time
    ]
    ]
    if start_times:
    if start_times:
    aggregate_stats.start_time = min(start_times)
    aggregate_stats.start_time = min(start_times)


    # Set end time to the latest end time of any batch
    # Set end time to the latest end time of any batch
    end_times = [
    end_times = [
    result.stats.end_time for result in batch_results if result.stats.end_time
    result.stats.end_time for result in batch_results if result.stats.end_time
    ]
    ]
    if end_times:
    if end_times:
    aggregate_stats.end_time = max(end_times)
    aggregate_stats.end_time = max(end_times)


    # Calculate total processing time
    # Calculate total processing time
    if aggregate_stats.start_time and aggregate_stats.end_time:
    if aggregate_stats.start_time and aggregate_stats.end_time:
    time_diff = (
    time_diff = (
    aggregate_stats.end_time - aggregate_stats.start_time
    aggregate_stats.end_time - aggregate_stats.start_time
    ).total_seconds()
    ).total_seconds()
    aggregate_stats.processing_time_ms = time_diff * 1000
    aggregate_stats.processing_time_ms = time_diff * 1000


    # Aggregate results and errors
    # Aggregate results and errors
    all_results = []
    all_results = []
    all_errors = {}
    all_errors = {}


    offset = 0
    offset = 0
    for result in batch_results:
    for result in batch_results:
    all_results.extend(result.results)
    all_results.extend(result.results)


    # Adjust error indices to match the combined list
    # Adjust error indices to match the combined list
    for idx, error in result.errors.items():
    for idx, error in result.errors.items():
    all_errors[offset + idx] = error
    all_errors[offset + idx] = error


    offset += len(result.stats.total_items)
    offset += len(result.stats.total_items)


    return BatchResult(
    return BatchResult(
    batch_id=aggregate_batch_id,
    batch_id=aggregate_batch_id,
    results=all_results,
    results=all_results,
    errors=all_errors,
    errors=all_errors,
    stats=aggregate_stats,
    stats=aggregate_stats,
    )
    )




    class BatchProcessor(Generic[T, R]):
    class BatchProcessor(Generic[T, R]):
    """
    """
    A class to handle batch processing operations.
    A class to handle batch processing operations.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    processor_func: Callable[[T], R],
    processor_func: Callable[[T], R],
    batch_size: int = 100,
    batch_size: int = 100,
    max_workers: int = None,
    max_workers: int = None,
    timeout: float = None,
    timeout: float = None,
    ):
    ):
    """
    """
    Initialize the batch processor.
    Initialize the batch processor.


    Args:
    Args:
    processor_func: Function to process each item
    processor_func: Function to process each item
    batch_size: Default size of each batch
    batch_size: Default size of each batch
    max_workers: Maximum number of workers for parallel processing
    max_workers: Maximum number of workers for parallel processing
    timeout: Timeout in seconds for each item's processing
    timeout: Timeout in seconds for each item's processing
    """
    """
    self.processor_func = processor_func
    self.processor_func = processor_func
    self.batch_size = batch_size
    self.batch_size = batch_size
    self.max_workers = max_workers
    self.max_workers = max_workers
    self.timeout = timeout
    self.timeout = timeout
    self.batch_results = []
    self.batch_results = []


    def process(self, items: List[T], batch_size: int = None) -> BatchResult[T, R]:
    def process(self, items: List[T], batch_size: int = None) -> BatchResult[T, R]:
    """
    """
    Process items in batches and return the aggregated result.
    Process items in batches and return the aggregated result.


    Args:
    Args:
    items: List of items to process
    items: List of items to process
    batch_size: Override the default batch size
    batch_size: Override the default batch size


    Returns:
    Returns:
    Aggregated BatchResult
    Aggregated BatchResult
    """
    """
    effective_batch_size = batch_size or self.batch_size
    effective_batch_size = batch_size or self.batch_size


    # Generate a batch ID prefix
    # Generate a batch ID prefix
    batch_id_prefix = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    batch_id_prefix = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


    # Process in batches
    # Process in batches
    batch_results = process_batches(
    batch_results = process_batches(
    items=items,
    items=items,
    processor_func=self.processor_func,
    processor_func=self.processor_func,
    batch_size=effective_batch_size,
    batch_size=effective_batch_size,
    max_workers=self.max_workers,
    max_workers=self.max_workers,
    batch_id_prefix=batch_id_prefix,
    batch_id_prefix=batch_id_prefix,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )


    # Store results
    # Store results
    self.batch_results.extend(batch_results)
    self.batch_results.extend(batch_results)


    # Return aggregated results
    # Return aggregated results
    return aggregate_batch_results(batch_results)
    return aggregate_batch_results(batch_results)


    def get_stats(self) -> List[Dict[str, Any]]:
    def get_stats(self) -> List[Dict[str, Any]]:
    """
    """
    Get statistics for all processed batches.
    Get statistics for all processed batches.


    Returns:
    Returns:
    List of batch statistics dictionaries
    List of batch statistics dictionaries
    """
    """
    return [result.stats.to_dict() for result in self.batch_results]
    return [result.stats.to_dict() for result in self.batch_results]




    class StreamingBatchProcessor(Generic[T, R]):
    class StreamingBatchProcessor(Generic[T, R]):
    """
    """
    A processor that handles streaming batch processing with incremental results.
    A processor that handles streaming batch processing with incremental results.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    processor_func: Callable[[T], R],
    processor_func: Callable[[T], R],
    batch_size: int = 100,
    batch_size: int = 100,
    max_workers: int = None,
    max_workers: int = None,
    timeout: float = None,
    timeout: float = None,
    ):
    ):
    """
    """
    Initialize the streaming batch processor.
    Initialize the streaming batch processor.


    Args:
    Args:
    processor_func: Function to process each item
    processor_func: Function to process each item
    batch_size: Size of each batch
    batch_size: Size of each batch
    max_workers: Maximum number of workers for parallel processing
    max_workers: Maximum number of workers for parallel processing
    timeout: Timeout in seconds for each item's processing
    timeout: Timeout in seconds for each item's processing
    """
    """
    self.processor_func = processor_func
    self.processor_func = processor_func
    self.batch_size = batch_size
    self.batch_size = batch_size
    self.max_workers = max_workers
    self.max_workers = max_workers
    self.timeout = timeout
    self.timeout = timeout


    def process_stream(
    def process_stream(
    self, items_iterator: Iterator[T]
    self, items_iterator: Iterator[T]
    ) -> Iterator[Union[R, Exception]]:
    ) -> Iterator[Union[R, Exception]]:
    """
    """
    Process items from an iterator and yield results as they become available.
    Process items from an iterator and yield results as they become available.


    Args:
    Args:
    items_iterator: Iterator providing items to process
    items_iterator: Iterator providing items to process


    Yields:
    Yields:
    Results or exceptions as they are processed
    Results or exceptions as they are processed
    """
    """
    # Buffer to collect items for batch processing
    # Buffer to collect items for batch processing
    item_buffer = []
    item_buffer = []


    # Process items in batches from the iterator
    # Process items in batches from the iterator
    for item in items_iterator:
    for item in items_iterator:
    item_buffer.append(item)
    item_buffer.append(item)


    # When we reach batch size, process the batch
    # When we reach batch size, process the batch
    if len(item_buffer) >= self.batch_size:
    if len(item_buffer) >= self.batch_size:
    batch_result = process_batch(
    batch_result = process_batch(
    items=item_buffer,
    items=item_buffer,
    processor_func=self.processor_func,
    processor_func=self.processor_func,
    max_workers=self.max_workers,
    max_workers=self.max_workers,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )


    # Yield results in order
    # Yield results in order
    for i in range(len(item_buffer)):
    for i in range(len(item_buffer)):
    if i in batch_result.errors:
    if i in batch_result.errors:
    yield batch_result.errors[i]
    yield batch_result.errors[i]
    else:
    else:
    yield batch_result.results[i]
    yield batch_result.results[i]


    # Clear the buffer for the next batch
    # Clear the buffer for the next batch
    item_buffer = []
    item_buffer = []


    # Process any remaining items
    # Process any remaining items
    if item_buffer:
    if item_buffer:
    batch_result = process_batch(
    batch_result = process_batch(
    items=item_buffer,
    items=item_buffer,
    processor_func=self.processor_func,
    processor_func=self.processor_func,
    max_workers=self.max_workers,
    max_workers=self.max_workers,
    timeout=self.timeout,
    timeout=self.timeout,
    )
    )


    # Yield remaining results
    # Yield remaining results
    for i in range(len(item_buffer)):
    for i in range(len(item_buffer)):
    if i in batch_result.errors:
    if i in batch_result.errors:
    yield batch_result.errors[i]
    yield batch_result.errors[i]
    else:
    else:
    yield batch_result.results[i]
    yield batch_result.results[i]




    def estimate_optimal_batch_size(
    def estimate_optimal_batch_size(
    sample_items: List[T],
    sample_items: List[T],
    processor_func: Callable[[T], R],
    processor_func: Callable[[T], R],
    min_batch_size: int = 10,
    min_batch_size: int = 10,
    max_batch_size: int = 1000,
    max_batch_size: int = 1000,
    target_batch_time_ms: float = 500,
    target_batch_time_ms: float = 500,
    test_sizes: List[int] = None,
    test_sizes: List[int] = None,
    ) -> int:
    ) -> int:
    """
    """
    Estimate the optimal batch size based on processing time.
    Estimate the optimal batch size based on processing time.


    Args:
    Args:
    sample_items: Sample items to test with
    sample_items: Sample items to test with
    processor_func: Function to process each item
    processor_func: Function to process each item
    min_batch_size: Minimum batch size to consider
    min_batch_size: Minimum batch size to consider
    max_batch_size: Maximum batch size to consider
    max_batch_size: Maximum batch size to consider
    target_batch_time_ms: Target processing time for each batch in milliseconds
    target_batch_time_ms: Target processing time for each batch in milliseconds
    test_sizes: List of batch sizes to test (defaults to [min_batch_size, min*2, min*4])
    test_sizes: List of batch sizes to test (defaults to [min_batch_size, min*2, min*4])


    Returns:
    Returns:
    Recommended batch size
    Recommended batch size
    """
    """
    if len(sample_items) == 0:
    if len(sample_items) == 0:
    return min_batch_size
    return min_batch_size


    # Use default test sizes if not provided
    # Use default test sizes if not provided
    if test_sizes is None:
    if test_sizes is None:
    test_sizes = [min_batch_size, min_batch_size * 2, min_batch_size * 4]
    test_sizes = [min_batch_size, min_batch_size * 2, min_batch_size * 4]


    # Ensure we have enough sample items
    # Ensure we have enough sample items
    max_test_size = max(test_sizes)
    max_test_size = max(test_sizes)
    if len(sample_items) < max_test_size:
    if len(sample_items) < max_test_size:
    # If we don't have enough samples, duplicate the existing ones
    # If we don't have enough samples, duplicate the existing ones
    multiplier = math.ceil(max_test_size / len(sample_items))
    multiplier = math.ceil(max_test_size / len(sample_items))
    sample_items = (sample_items * multiplier)[:max_test_size]
    sample_items = (sample_items * multiplier)[:max_test_size]


    # Measure processing time for different batch sizes
    # Measure processing time for different batch sizes
    timing_results = []
    timing_results = []


    for size in test_sizes:
    for size in test_sizes:
    # Use a subset of the sample items
    # Use a subset of the sample items
    test_items = sample_items[:size]
    test_items = sample_items[:size]


    # Time the processing
    # Time the processing
    start_time = time.time()
    start_time = time.time()
    process_batch(test_items, processor_func)
    process_batch(test_items, processor_func)
    elapsed_ms = (time.time() - start_time) * 1000
    elapsed_ms = (time.time() - start_time) * 1000


    # Calculate time per item
    # Calculate time per item
    time_per_item = elapsed_ms / size
    time_per_item = elapsed_ms / size
    timing_results.append((size, elapsed_ms, time_per_item))
    timing_results.append((size, elapsed_ms, time_per_item))


    # Calculate the average time per item across all tests
    # Calculate the average time per item across all tests
    avg_time_per_item = sum(r[2] for r in timing_results) / len(timing_results)
    avg_time_per_item = sum(r[2] for r in timing_results) / len(timing_results)


    # Calculate the recommended batch size based on target time
    # Calculate the recommended batch size based on target time
    recommended_size = int(target_batch_time_ms / avg_time_per_item)
    recommended_size = int(target_batch_time_ms / avg_time_per_item)


    # Bound within min and max sizes
    # Bound within min and max sizes
    recommended_size = max(min_batch_size, min(recommended_size, max_batch_size))
    recommended_size = max(min_batch_size, min(recommended_size, max_batch_size))


    return recommended_size
    return recommended_size