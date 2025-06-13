"""
CI Environment Detection Module

This module provides functions to detect and handle different environments:
- Operating Systems: Windows, macOS, Linux, WSL
- CI environments: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines,
  TeamCity, Bitbucket, AppVeyor, Drone, Buddy, Buildkite, AWS CodeBuild, Vercel, Netlify,
  Heroku, Semaphore, Codefresh, Woodpecker, Harness, Render, Railway, Fly.io, etc.
- Container environments: Docker, Docker Compose, Kubernetes, Docker Swarm
- Cloud environments: AWS, Azure, GCP
- Serverless environments: Lambda, Azure Functions, Cloud Functions

It's designed to be used across the application to ensure consistent
environment detection and handling with proper fallbacks.
"""

from .detect_ci_environment import (
    create_ci_directories,
    detect_ci_environment,
    safe_file_exists,
    safe_read_file,
)

__all__ = [
    "detect_ci_environment",
    "safe_file_exists",
    "safe_read_file",
    "create_ci_directories",
]
