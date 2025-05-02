"""
Setup script for the pAIssive Income Python SDK.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paissive_income_sdk",
    version="0.1.0",
    author="pAIssive Income Team",
    author_email="support@paissiveincome.example.com",
    description="Python SDK for the pAIssive Income API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paissive-income/paissive-income-sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)
