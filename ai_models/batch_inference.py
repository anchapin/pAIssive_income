"""
Batch processing for AI model inference.

This module provides facilities for batch processing AI model inference operations,
including text generation, embeddings, classification, and image processing.
"""


import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from common_utils.batch_utils import BatchProcessingStats

from .async_utils import AsyncModelProcessor, AsyncResult
from .model_manager import ModelManager
from .performance_monitor import PerformanceMonitor



# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar("T")  # Input type
R = TypeVar("R")  # Result type


@dataclass
class BatchInferenceRequest(Generic[T]):
    """A request to process a batch of inputs through a model."""

    model_id: str
    inputs: List[T]
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_version: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "num_inputs": len(self.inputs),
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class BatchInferenceResult(Generic[T, R]):
    """Results of a batch inference operation."""

    request: BatchInferenceRequest[T]
    results: List[R]
    errors: Dict[int, Exception]
    stats: BatchProcessingStats
    completed_at: datetime = field(default_factory=datetime.now)

    def get_successful_results(self) -> List[R]:
        """Get only the successful results."""
        return self.results

    def get_failed_inputs(self) -> List[Tuple[int, T, Exception]]:
        """Get inputs that resulted in errors along with their exceptions."""
        return [
            (idx, self.request.inputs[idx], error) for idx, error in self.errors.items()
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.request.batch_id,
            "model_id": self.request.model_id,
            "model_version": self.request.model_version,
            "num_inputs": len(self.request.inputs),
            "num_successful": len(self.results) - len(self.errors),
            "num_failed": len(self.errors),
            "processing_time_ms": self.stats.processing_time_ms,
            "items_per_second": self.stats.items_per_second,
            "created_at": self.request.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


class BatchInferenceProcessor:
    """
    Processes inference requests in batches for improved efficiency.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        performance_monitor: Optional[PerformanceMonitor] = None,
        default_batch_size: int = 16,
        default_concurrency: int = 4,
    ):
        """
        Initialize the batch inference processor.

        Args:
            model_manager: Model manager instance for loading models
            performance_monitor: Optional performance monitor for tracking metrics
            default_batch_size: Default batch size for batch operations
            default_concurrency: Default concurrency for processing within batches
        """
        self.model_manager = model_manager
        self.performance_monitor = performance_monitor
        self.default_batch_size = default_batch_size
        self.default_concurrency = default_concurrency
        self.async_processor = AsyncModelProcessor(model_manager)
        self.batch_history = {}

    def generate_text_batch(
        self,
        model_id: str,
        prompts: List[str],
        model_version: Optional[str] = None,
        batch_size: Optional[int] = None,
        concurrency: Optional[int] = None,
        **kwargs
    ) -> BatchInferenceResult[str, str]:
        """
        Generate text for a batch of prompts.

        Args:
            model_id: ID of the model to use
            prompts: List of prompts to process
            model_version: Optional version of the model
            batch_size: Size of each batch (defaults to default_batch_size)
            concurrency: Concurrency level within each batch (defaults to default_concurrency)
            **kwargs: Additional parameters for text generation

        Returns:
            Batch inference result with generated texts
        """
        # Create the batch request
        batch_id = str(uuid.uuid4())
        request = BatchInferenceRequest(
            batch_id=batch_id,
            model_id=model_id,
            inputs=prompts,
            model_version=model_version,
            parameters=kwargs,
        )

        # Prepare stats
        stats = BatchProcessingStats(
            batch_id=batch_id, total_items=len(prompts), start_time=datetime.now()
        )

        effective_concurrency = concurrency or self.default_concurrency

        # Process the batch asynchronously
        results = []
        errors = {}

        # Get the event loop or create one if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        start_time = time.time()

        # Run the async processing
        async_results: List[AsyncResult[str]] = loop.run_until_complete(
            self.async_processor.generate_text_batch(
                model_id=model_id,
                prompts=prompts,
                model_version=model_version,
                concurrency=effective_concurrency,
                **kwargs
            )
        )

        # Process results
        for i, result in enumerate(async_results):
            if result.success:
                results.append(result.result)
                stats.successful_items += 1
            else:
                results.append(None)  # Add None placeholder for failed results
                errors[i] = result.error
                stats.failed_items += 1

            stats.processed_items += 1

        # Update stats
        stats.end_time = datetime.now()
        stats.processing_time_ms = (time.time() - start_time) * 1000

        # Create the batch result
        batch_result = BatchInferenceResult(
            request=request, results=results, errors=errors, stats=stats
        )

        # Store in history
        self.batch_history[batch_id] = batch_result

        return batch_result

    def generate_embeddings_batch(
        self,
        model_id: str,
        texts: List[str],
        model_version: Optional[str] = None,
        batch_size: Optional[int] = None,
        concurrency: Optional[int] = None,
        **kwargs
    ) -> BatchInferenceResult[str, List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            model_id: ID of the model to use
            texts: List of texts to embed
            model_version: Optional version of the model
            batch_size: Size of each batch (defaults to default_batch_size)
            concurrency: Concurrency level within each batch (defaults to default_concurrency)
            **kwargs: Additional parameters for embedding generation

        Returns:
            Batch inference result with embeddings
        """
        # Create the batch request
        batch_id = str(uuid.uuid4())
        request = BatchInferenceRequest(
            batch_id=batch_id,
            model_id=model_id,
            inputs=texts,
            model_version=model_version,
            parameters=kwargs,
        )

        # Prepare stats
        stats = BatchProcessingStats(
            batch_id=batch_id, total_items=len(texts), start_time=datetime.now()
        )

        effective_concurrency = concurrency or self.default_concurrency

        # Process the batch asynchronously
        results = []
        errors = {}

        # Get the event loop or create one if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        start_time = time.time()

        # Run the async processing
        async_results: List[AsyncResult[List[float]]] = loop.run_until_complete(
            self.async_processor.generate_embeddings_batch(
                model_id=model_id,
                texts=texts,
                model_version=model_version,
                concurrency=effective_concurrency,
                **kwargs
            )
        )

        # Process results
        for i, result in enumerate(async_results):
            if result.success:
                results.append(result.result)
                stats.successful_items += 1
            else:
                results.append(None)  # Add None placeholder for failed results
                errors[i] = result.error
                stats.failed_items += 1

            stats.processed_items += 1

        # Update stats
        stats.end_time = datetime.now()
        stats.processing_time_ms = (time.time() - start_time) * 1000

        # Create the batch result
        batch_result = BatchInferenceResult(
            request=request, results=results, errors=errors, stats=stats
        )

        # Store in history
        self.batch_history[batch_id] = batch_result

        return batch_result

    def get_batch_result(self, batch_id: str) -> Optional[BatchInferenceResult]:
        """
        Get a batch result by its ID.

        Args:
            batch_id: ID of the batch to retrieve

        Returns:
            BatchInferenceResult if found, None otherwise
        """
        return self.batch_history.get(batch_id)

    def get_recent_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get information about recent batches.

        Args:
            limit: Maximum number of batches to return

        Returns:
            List of batch summary dictionaries
        """
        # Sort by created time (most recent first)
        sorted_batches = sorted(
            self.batch_history.values(),
            key=lambda r: r.request.created_at,
            reverse=True,
        )

        # Return limited number of batch summaries
        return [batch.to_dict() for batch in sorted_batches[:limit]]


# Convenience functions for batch processing
def generate_text_batch(
    model_manager: ModelManager,
    model_id: str,
    prompts: List[str],
    model_version: Optional[str] = None,
    batch_size: int = 16,
    concurrency: int = 4,
    **kwargs
) -> BatchInferenceResult[str, str]:
    """
    Generate text for multiple prompts in batch mode.

    Args:
        model_manager: Model manager instance
        model_id: ID of the model to use
        prompts: List of prompts to process
        model_version: Optional version of the model
        batch_size: Size of each batch
        concurrency: Concurrency level within each batch
        **kwargs: Additional parameters for text generation

    Returns:
        BatchInferenceResult with generated texts
    """
    processor = BatchInferenceProcessor(model_manager, default_batch_size=batch_size)
    return processor.generate_text_batch(
        model_id=model_id,
        prompts=prompts,
        model_version=model_version,
        concurrency=concurrency,
        **kwargs
    )


def generate_embeddings_batch(
    model_manager: ModelManager,
    model_id: str,
    texts: List[str],
    model_version: Optional[str] = None,
    batch_size: int = 32,
    concurrency: int = 8,
    **kwargs
) -> BatchInferenceResult[str, List[float]]:
    """
    Generate embeddings for multiple texts in batch mode.

    Args:
        model_manager: Model manager instance
        model_id: ID of the model to use
        texts: List of texts to embed
        model_version: Optional version of the model
        batch_size: Size of each batch
        concurrency: Concurrency level within each batch
        **kwargs: Additional parameters for embedding generation

    Returns:
        BatchInferenceResult with embeddings
    """
    processor = BatchInferenceProcessor(model_manager, default_batch_size=batch_size)
    return processor.generate_embeddings_batch(
        model_id=model_id,
        texts=texts,
        model_version=model_version,
        concurrency=concurrency,
        **kwargs
    )