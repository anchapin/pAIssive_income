"""
Perplexity metric for benchmarking language models.

This module provides a metric for measuring the perplexity of language models.
"""

import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .base_metric import BaseMetric

# Try to import optional dependencies
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class PerplexityMetric(BaseMetric):
    """
    Metric for measuring perplexity of language models.
    """

    def __init__(self, **kwargs):
        """
        Initialize the perplexity metric.

        Args:
            **kwargs: Additional parameters for the metric
        """
        super().__init__(name="perplexity", unit="", **kwargs)
        self.total_loss = 0.0
        self.total_tokens = 0

    def measure(
        self, 
        model: Any, 
        tokenizer: Any, 
        text: Union[str, List[str]], 
        device: str = "cpu",
        **kwargs
    ) -> float:
        """
        Measure the perplexity of a model on text.

        Args:
            model: Language model
            tokenizer: Tokenizer for the model
            text: Input text or list of texts
            device: Device to run the model on
            **kwargs: Additional parameters for the model

        Returns:
            Perplexity score
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for perplexity calculation")

        # Convert single text to list
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        # Calculate perplexity for each text
        total_loss = 0.0
        total_tokens = 0

        for input_text in texts:
            loss, tokens = self._calculate_loss(model, tokenizer, input_text, device, **kwargs)
            total_loss += loss
            total_tokens += tokens

        # Calculate perplexity
        perplexity = math.exp(total_loss / total_tokens) if total_tokens > 0 else float('inf')

        # Update counters
        self.total_loss += total_loss
        self.total_tokens += total_tokens

        # Add value
        self.add_value(perplexity)

        return perplexity
