"""setup - Module for setup."""

from setuptools import find_packages, setup

setup(
    name="paissive_income",  # Main package name
    version="0.1.0",
    description="pAIssive income main package",
    packages=find_packages(exclude=["api.middleware*", "services.service_discovery*"]),
    python_requires=">=3.9",
    # Exclude the subdirectories with their own setup.py files
    package_data={
        "": ["*.py", "*.json", "*.yml"],
    },
)
