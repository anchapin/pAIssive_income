"""
Setup script for the AI Models package.
"""

import os

from setuptools import find_packages, setup

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get the version from the version file
with open(os.path.join("ai_models", "version.py"), encoding="utf-8") as f:
    version = f.read().strip().split("=")[1].strip(" \"'")

# Get the requirements from the requirements file
with open(os.path.join("ai_models", "requirements.txt"), encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="ai-models",
    version=version,
    description="A framework for managing, optimizing, and serving AI models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Chapin",
    author_email="a.n.chapin@gmail.com",
    url="https://github.com/anchapin/pAIssive_income",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-models=ai_models.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
