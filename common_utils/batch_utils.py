"""
Batch processing utilities for optimizing operations that can be processed in groups.

This module provides utilities for batch processing operations, such as:
- Chunking large datasets into batches
- Processing batches in parallel or sequentially
- Aggregating batch results
- Tracking batch processing progress
"""


import logging
import math
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import 

(
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    TypeVar,
    Union,
)

# Type variables for generic functions
T = TypeVar("T")  # Input item type
R = TypeVar("R")  # Result item type

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
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
    """Results from a batch processing operation."""

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
    Split a list into chunks of the specified size.

    Args:
        items: The list to split
        batch_size: The maximum size of each chunk

    Returns:
        A list of lists, where each inner list is a chunk of the original list
    """
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


def process_batch(
    items: List[T],
    processor_func: Callable[[T], R],
    max_workers: int = None,
    batch_id: str = None,
    timeout: float = None,
) -> BatchResult[T, R]:
    """
    Process a batch of items using a processor function.

    Args:
        items: List of items to process
        processor_func: Function to process each item
        max_workers: Maximum number of workers for parallel processing (if None, uses CPU count)
        batch_id: Optional ID for the batch (if None, generates a UUID)
        timeout: Optional timeout in seconds for each item's processing

    Returns:
        BatchResult containing results, errors, and statistics
    """
    if not batch_id:
        batch_id = str(uuid.uuid4())

    stats = BatchProcessingStats(
        batch_id=batch_id, total_items=len(items), start_time=datetime.now()
    )

    results = [None] * len(items)  # Pre-allocate results list
    errors = {}  # Dictionary to track errors by index

    start_time = time.time()

    # Process items in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(processor_func, item): i for i, item in enumerate(items)
        }

        # Process results as they complete
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result(timeout=timeout)
                results[index] = result
                stats.successful_items += 1
            except Exception as exc:
                errors[index] = exc
                stats.failed_items += 1
                logger.warning(f"Item {index} in batch {batch_id} failed: {exc}")

            stats.processed_items += 1

    # Update stats
    stats.end_time = datetime.now()
    stats.processing_time_ms = (time.time() - start_time) * 1000

    return BatchResult(batch_id=batch_id, results=results, errors=errors, stats=stats)


def process_batches(
    items: List[T],
    processor_func: Callable[[T], R],
    batch_size: int,
    max_workers: int = None,
    batch_id_prefix: str = None,
    timeout: float = None,
) -> List[BatchResult[T, R]]:
    """
    Process a large list of items in batches.

    Args:
        items: List of items to process
        processor_func: Function to process each item
        batch_size: Maximum size of each batch
        max_workers: Maximum number of workers for parallel processing within each batch
        batch_id_prefix: Optional prefix for batch IDs
        timeout: Optional timeout in seconds for each item's processing

    Returns:
        List of BatchResults, one for each batch
    """
    # Split items into batches
    batches = chunk_list(items, batch_size)
    batch_results = []

    for i, batch in enumerate(batches):
        batch_id = f"{batch_id_prefix}-{i}" if batch_id_prefix else f"batch-{i}"

        # Process each batch
        result = process_batch(
            items=batch,
            processor_func=processor_func,
            max_workers=max_workers,
            batch_id=batch_id,
            timeout=timeout,
        )

        batch_results.append(result)

    return batch_results


def aggregate_batch_results(
    batch_results: List[BatchResult[T, R]],
) -> BatchResult[T, R]:
    """
    Aggregate multiple batch results into a single result.

    Args:
        batch_results: List of batch results to aggregate

    Returns:
        A single BatchResult combining all input results
    """
    if not batch_results:
        return None

    # Create a new aggregate batch ID
    aggregate_batch_id = f"aggregate-{uuid.uuid4()}"

    # Initialize stats for the aggregate batch
    total_items = sum(result.stats.total_items for result in batch_results)
    aggregate_stats = BatchProcessingStats(
        batch_id=aggregate_batch_id,
        total_items=total_items,
        processed_items=sum(result.stats.processed_items for result in batch_results),
        successful_items=sum(result.stats.successful_items for result in batch_results),
        failed_items=sum(result.stats.failed_items for result in batch_results),
    )

    # Set start time to the earliest start time of any batch
    start_times = [
        result.stats.start_time for result in batch_results if result.stats.start_time
    ]
    if start_times:
        aggregate_stats.start_time = min(start_times)

    # Set end time to the latest end time of any batch
    end_times = [
        result.stats.end_time for result in batch_results if result.stats.end_time
    ]
    if end_times:
        aggregate_stats.end_time = max(end_times)

    # Calculate total processing time
    if aggregate_stats.start_time and aggregate_stats.end_time:
        time_diff = (
            aggregate_stats.end_time - aggregate_stats.start_time
        ).total_seconds()
        aggregate_stats.processing_time_ms = time_diff * 1000

    # Aggregate results and errors
    all_results = []
    all_errors = {}

    offset = 0
    for result in batch_results:
        all_results.extend(result.results)

        # Adjust error indices to match the combined list
        for idx, error in result.errors.items():
            all_errors[offset + idx] = error

        offset += len(result.stats.total_items)

    return BatchResult(
        batch_id=aggregate_batch_id,
        results=all_results,
        errors=all_errors,
        stats=aggregate_stats,
    )


class BatchProcessor(Generic[T, R]):
    """
    A class to handle batch processing operations.
    """

    def __init__(
        self,
        processor_func: Callable[[T], R],
        batch_size: int = 100,
        max_workers: int = None,
        timeout: float = None,
    ):
        """
        Initialize the batch processor.

        Args:
            processor_func: Function to process each item
            batch_size: Default size of each batch
            max_workers: Maximum number of workers for parallel processing
            timeout: Timeout in seconds for each item's processing
        """
        self.processor_func = processor_func
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.timeout = timeout
        self.batch_results = []

    def process(self, items: List[T], batch_size: int = None) -> BatchResult[T, R]:
        """
        Process items in batches and return the aggregated result.

        Args:
            items: List of items to process
            batch_size: Override the default batch size

        Returns:
            Aggregated BatchResult
        """
        effective_batch_size = batch_size or self.batch_size

        # Generate a batch ID prefix
        batch_id_prefix = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Process in batches
        batch_results = process_batches(
            items=items,
            processor_func=self.processor_func,
            batch_size=effective_batch_size,
            max_workers=self.max_workers,
            batch_id_prefix=batch_id_prefix,
            timeout=self.timeout,
        )

        # Store results
        self.batch_results.extend(batch_results)

        # Return aggregated results
        return aggregate_batch_results(batch_results)

    def get_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all processed batches.

        Returns:
            List of batch statistics dictionaries
        """
        return [result.stats.to_dict() for result in self.batch_results]


class StreamingBatchProcessor(Generic[T, R]):
    """
    A processor that handles streaming batch processing with incremental results.
    """

    def __init__(
        self,
        processor_func: Callable[[T], R],
        batch_size: int = 100,
        max_workers: int = None,
        timeout: float = None,
    ):
        """
        Initialize the streaming batch processor.

        Args:
            processor_func: Function to process each item
            batch_size: Size of each batch
            max_workers: Maximum number of workers for parallel processing
            timeout: Timeout in seconds for each item's processing
        """
        self.processor_func = processor_func
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.timeout = timeout

    def process_stream(
        self, items_iterator: Iterator[T]
    ) -> Iterator[Union[R, Exception]]:
        """
        Process items from an iterator and yield results as they become available.

        Args:
            items_iterator: Iterator providing items to process

        Yields:
            Results or exceptions as they are processed
        """
        # Buffer to collect items for batch processing
        item_buffer = []

        # Process items in batches from the iterator
        for item in items_iterator:
            item_buffer.append(item)

            # When we reach batch size, process the batch
            if len(item_buffer) >= self.batch_size:
                batch_result = process_batch(
                    items=item_buffer,
                    processor_func=self.processor_func,
                    max_workers=self.max_workers,
                    timeout=self.timeout,
                )

                # Yield results in order
                for i in range(len(item_buffer)):
                    if i in batch_result.errors:
                        yield batch_result.errors[i]
                    else:
                        yield batch_result.results[i]

                # Clear the buffer for the next batch
                item_buffer = []

        # Process any remaining items
        if item_buffer:
            batch_result = process_batch(
                items=item_buffer,
                processor_func=self.processor_func,
                max_workers=self.max_workers,
                timeout=self.timeout,
            )

            # Yield remaining results
            for i in range(len(item_buffer)):
                if i in batch_result.errors:
                    yield batch_result.errors[i]
                else:
                    yield batch_result.results[i]


def estimate_optimal_batch_size(
    sample_items: List[T],
    processor_func: Callable[[T], R],
    min_batch_size: int = 10,
    max_batch_size: int = 1000,
    target_batch_time_ms: float = 500,
    test_sizes: List[int] = None,
) -> int:
    """
    Estimate the optimal batch size based on processing time.

    Args:
        sample_items: Sample items to test with
        processor_func: Function to process each item
        min_batch_size: Minimum batch size to consider
        max_batch_size: Maximum batch size to consider
        target_batch_time_ms: Target processing time for each batch in milliseconds
        test_sizes: List of batch sizes to test (defaults to [min_batch_size, min*2, min*4])

    Returns:
        Recommended batch size
    """
    if len(sample_items) == 0:
        return min_batch_size

    # Use default test sizes if not provided
    if test_sizes is None:
        test_sizes = [min_batch_size, min_batch_size * 2, min_batch_size * 4]

    # Ensure we have enough sample items
    max_test_size = max(test_sizes)
    if len(sample_items) < max_test_size:
        # If we don't have enough samples, duplicate the existing ones
        multiplier = math.ceil(max_test_size / len(sample_items))
        sample_items = (sample_items * multiplier)[:max_test_size]

    # Measure processing time for different batch sizes
    timing_results = []

    for size in test_sizes:
        # Use a subset of the sample items
        test_items = sample_items[:size]

        # Time the processing
        start_time = time.time()
        process_batch(test_items, processor_func)
        elapsed_ms = (time.time() - start_time) * 1000

        # Calculate time per item
        time_per_item = elapsed_ms / size
        timing_results.append((size, elapsed_ms, time_per_item))

    # Calculate the average time per item across all tests
    avg_time_per_item = sum(r[2] for r in timing_results) / len(timing_results)

    # Calculate the recommended batch size based on target time
    recommended_size = int(target_batch_time_ms / avg_time_per_item)

    # Bound within min and max sizes
    recommended_size = max(min_batch_size, min(recommended_size, max_batch_size))

    return recommended_size