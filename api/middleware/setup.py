"""setup - Module for api/middleware.setup."""

# Standard library imports

# Third-party imports
from setuptools import find_packages, setup

# Local imports

setup(
    name="paissive_income_middleware",  # Unique name to prevent egg-info conflicts
    version="0.1.0",
    description="Middleware components for pAIssive income project",
    packages=find_packages(),
    python_requires=">=3.9",
)
