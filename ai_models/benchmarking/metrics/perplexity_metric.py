"""
"""
Perplexity metric for benchmarking language models.
Perplexity metric for benchmarking language models.


This module provides a metric for measuring the perplexity of language models.
This module provides a metric for measuring the perplexity of language models.
"""
"""


import math
import math
from typing import Any, List, Union
from typing import Any, List, Union


from .base_metric import BaseMetric
from .base_metric import BaseMetric


# Try to import optional dependencies
# Try to import optional dependencies
try:
    try:
    import torch
    import torch


    TORCH_AVAILABLE = True
    TORCH_AVAILABLE = True
except ImportError:
except ImportError:
    TORCH_AVAILABLE = False
    TORCH_AVAILABLE = False


    try:
    try:
    import numpy as np
    import numpy as np


    NUMPY_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
except ImportError:
    NUMPY_AVAILABLE = False
    NUMPY_AVAILABLE = False




    class PerplexityMetric(BaseMetric):
    class PerplexityMetric(BaseMetric):
    """
    """
    Metric for measuring perplexity of language models.
    Metric for measuring perplexity of language models.
    """
    """


    def __init__(self, **kwargs):
    def __init__(self, **kwargs):
    """
    """
    Initialize the perplexity metric.
    Initialize the perplexity metric.


    Args:
    Args:
    **kwargs: Additional parameters for the metric
    **kwargs: Additional parameters for the metric
    """
    """
    super().__init__(name="perplexity", unit="", **kwargs)
    super().__init__(name="perplexity", unit="", **kwargs)
    self.total_loss = 0.0
    self.total_loss = 0.0
    self.total_tokens = 0
    self.total_tokens = 0


    def measure(
    def measure(
    self,
    self,
    model: Any,
    model: Any,
    tokenizer: Any,
    tokenizer: Any,
    text: Union[str, List[str]],
    text: Union[str, List[str]],
    device: str = "cpu",
    device: str = "cpu",
    **kwargs
    **kwargs
    ) -> float:
    ) -> float:
    """
    """
    Measure the perplexity of a model on text.
    Measure the perplexity of a model on text.


    Args:
    Args:
    model: Language model
    model: Language model
    tokenizer: Tokenizer for the model
    tokenizer: Tokenizer for the model
    text: Input text or list of texts
    text: Input text or list of texts
    device: Device to run the model on
    device: Device to run the model on
    **kwargs: Additional parameters for the model
    **kwargs: Additional parameters for the model


    Returns:
    Returns:
    Perplexity score
    Perplexity score
    """
    """
    if not TORCH_AVAILABLE:
    if not TORCH_AVAILABLE:
    raise ImportError("PyTorch is required for perplexity calculation")
    raise ImportError("PyTorch is required for perplexity calculation")


    # Convert single text to list
    # Convert single text to list
    if isinstance(text, str):
    if isinstance(text, str):
    texts = [text]
    texts = [text]
    else:
    else:
    texts = text
    texts = text


    # Calculate perplexity for each text
    # Calculate perplexity for each text
    total_loss = 0.0
    total_loss = 0.0
    total_tokens = 0
    total_tokens = 0


    for input_text in texts:
    for input_text in texts:
    loss, tokens = self._calculate_loss(
    loss, tokens = self._calculate_loss(
    model, tokenizer, input_text, device, **kwargs
    model, tokenizer, input_text, device, **kwargs
    )
    )
    total_loss += loss
    total_loss += loss
    total_tokens += tokens
    total_tokens += tokens


    # Calculate perplexity
    # Calculate perplexity
    perplexity = (
    perplexity = (
    math.exp(total_loss / total_tokens) if total_tokens > 0 else float("inf")
    math.exp(total_loss / total_tokens) if total_tokens > 0 else float("inf")
    )
    )


    # Update counters
    # Update counters
    self.total_loss += total_loss
    self.total_loss += total_loss
    self.total_tokens += total_tokens
    self.total_tokens += total_tokens


    # Add value
    # Add value
    self.add_value(perplexity)
    self.add_value(perplexity)


    return perplexity
    return perplexity

