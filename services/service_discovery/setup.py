"""setup - Module for services/service_discovery.setup."""

# Standard library imports

# Third-party imports
from setuptools import find_packages
from setuptools import setup

# Local imports

setup(
    # Unique name to prevent egg-info conflicts
    name="paissive_income_service_discovery",
    version="0.1.0",
    description="Service discovery components for pAIssive income project",
    packages=find_packages(),
    python_requires=">=3.9",
)
