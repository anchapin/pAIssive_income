"""
ARTIST experiments package.

This package contains experiments related to the ARTIST framework.
"""

# Conditional imports to handle missing dependencies gracefully
__all__ = []

try:
    from artist_experiments.math_problem_solving import (
        run_experiment as run_math_experiment,
    )
    __all__.append("run_math_experiment")
except ImportError:
    # sympy not available, skip math experiments
    pass

try:
    from artist_experiments.multi_api_orchestration import (
        run_experiment as run_api_experiment,
    )
    __all__.append("run_api_experiment")
except ImportError:
    # API orchestration dependencies not available
    pass
