setup_content = """Setup and installation for the pAIssive-income package.

Provides configuration for package dependencies, metadata, and build settings.
"""

from setuptools import setup, find_packages

setup(
    name="paissive-income",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "requests>=2.26.0",
        "pytest>=6.2.5",
        "pytest-asyncio>=0.16.0",
        "aiohttp>=3.8.0",
        "sqlalchemy>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "black",
            "isort",
            "mypy",
            "ruff",
        ],
    },
    python_requires=">=3.9",
)
