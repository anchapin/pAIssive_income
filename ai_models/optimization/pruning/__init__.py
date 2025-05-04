"""
"""
Pruning utilities for AI models.
Pruning utilities for AI models.


This module provides utilities for pruning AI models to reduce their size
This module provides utilities for pruning AI models to reduce their size
and improve inference speed.
and improve inference speed.
"""
"""




from .base import Pruner, PruningConfig, PruningMethod
from .base import Pruner, PruningConfig, PruningMethod
from .magnitude_pruner import MagnitudePruner
from .magnitude_pruner import MagnitudePruner
from .structured_pruner import StructuredPruner
from .structured_pruner import StructuredPruner
from .utils import analyze_pruning, prune_model
from .utils import analyze_pruning, prune_model


__all__
__all__


= [
= [
"Pruner",
"Pruner",
"PruningConfig",
"PruningConfig",
"PruningMethod",
"PruningMethod",
"MagnitudePruner",
"MagnitudePruner",
"StructuredPruner",
"StructuredPruner",
"prune_model",
"prune_model",
"analyze_pruning",
"analyze_pruning",
]
]