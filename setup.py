"""setup - Module for setup."""

# Standard library imports

# Third-party imports
from setuptools import find_packages, setup

# Local imports

setup(
    name="paissive_income",  # Main package name
    version="0.1.0",
    description="pAIssive income main package",
    packages=find_packages(exclude=["api.middleware*", "services.service_discovery*"]),
    python_requires=">=3.10",
    # Exclude the subdirectories with their own setup.py files
    package_data={
        "": ["*.py", "*.json", "*.yml"],
    },
    extras_require={
        "agents": ["crewai>=0.28.0"],
        "memory": ["mem0ai>=0.1.100", "qdrant-client>=1.9.1", "openai>=1.33.0", "pytz>=2024.1"],
        "dev": ["pytest>=8.0.0", "pytest-cov>=4.1.0", "pytest-mock>=3.10.0"],
    },
)
