"""
Perplexity metric for benchmarking AI models.

This module provides a metric for measuring the perplexity of language models.
"""

try:
    import torch
except ImportError:
    pass


import math
from typing import Callable, Dict, List

from .base_metric import BaseMetric


    import torch
    import numpy

# Try to import optional dependencies
try:


    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class PerplexityMetric(BaseMetric):
    """
    Metric for measuring perplexity.
    """

    def __init__(self, **kwargs):
        """
        Initialize the perplexity metric.

        Args:
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="perplexity", unit="", **kwargs)
        self.total_loss = 0
        self.total_tokens = 0

    def measure(self, func: Callable, texts: List[str], *args, **kwargs) -> float:
        """
        Measure the perplexity of a model on a dataset.

        Args:
            func: Function that returns (loss, num_tokens) for a text
            texts: List of texts
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Perplexity
        """
        total_loss = 0
        total_tokens = 0

        for text in texts:
            # Get loss and number of tokens
            loss, num_tokens = func(text, *args, **kwargs)

            total_loss += loss * num_tokens
            total_tokens += num_tokens

        # Calculate perplexity
        if TORCH_AVAILABLE and isinstance(total_loss, torch.Tensor):
            perplexity = (
                torch.exp(total_loss / total_tokens).item()
                if total_tokens > 0
                else float("in")
            )
        elif NUMPY_AVAILABLE and isinstance(total_loss, np.ndarray):
            perplexity = (
                float(np.exp(total_loss / total_tokens))
                if total_tokens > 0
                else float("in")
            )
        else:
            perplexity = (
                math.exp(total_loss / total_tokens)
                if total_tokens > 0
                else float("in")
            )

        # Update counters
        self.total_loss += total_loss
        self.total_tokens += total_tokens

        # Add value
        self.add_value(perplexity)

                return perplexity

    def measure_single(self, loss: float, num_tokens: int) -> float:
        """
        Measure the perplexity for a single text.

        Args:
            loss: Loss value
            num_tokens: Number of tokens

        Returns:
            Perplexity
        """
        # Calculate perplexity
        if TORCH_AVAILABLE and isinstance(loss, torch.Tensor):
            perplexity = torch.exp(loss).item()
        elif NUMPY_AVAILABLE and isinstance(loss, np.ndarray):
            perplexity = float(np.exp(loss))
        else:
            perplexity = math.exp(loss)

        # Update counters
        self.total_loss += loss * num_tokens
        self.total_tokens += num_tokens

        # Add value
        self.add_value(perplexity)

                return perplexity

    def get_overall_perplexity(self) -> float:
        """
        Get the overall perplexity across all measurements.

        Returns:
            Overall perplexity
        """
        if self.total_tokens == 0:
                    return float("in")

        if TORCH_AVAILABLE and isinstance(self.total_loss, torch.Tensor):
                    return torch.exp(self.total_loss / self.total_tokens).item()
        elif NUMPY_AVAILABLE and isinstance(self.total_loss, np.ndarray):
                    return float(np.exp(self.total_loss / self.total_tokens))
        else:
                    return math.exp(self.total_loss / self.total_tokens)

    def reset(self) -> None:
        """
        Reset the metric.
        """
        super().reset()
        self.total_loss = 0
        self.total_tokens = 0

    def get_stats(self) -> Dict[str, float]:
        """
        Get statistics about the perplexity values.

        Returns:
            Dictionary with statistics
        """
        stats = super().get_stats()

        # Add overall perplexity
        stats["overall"] = self.get_overall_perplexity()

                return stats