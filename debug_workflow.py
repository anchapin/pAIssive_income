#!/usr/bin/env python3
"""
Workflow debug script to help identify common issues.
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check the current environment."""
    logger.info("=== Environment Check ===")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Check CI environment
    is_ci = os.environ.get("CI") == "true"
    is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    logger.info(f"CI environment: {is_ci}")
    logger.info(f"GitHub Actions: {is_github_actions}")

def check_dependencies():
    """Check for required dependencies."""
    logger.info("=== Dependency Check ===")
    
    required_packages = [
        "pytest", "ruff", "pyrefly", "safety", "bandit"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is available")
        except ImportError:
            logger.warning(f"✗ {package} is not available")

def check_files():
    """Check for required files."""
    logger.info("=== File Check ===")
    
    required_files = [
        "requirements.txt",
        "pytest.ini",
        "pyproject.toml",
        "run_tests.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            logger.info(f"✓ {file_path} exists")
        else:
            logger.warning(f"✗ {file_path} is missing")

def main():
    """Main debug function."""
    logger.info("Starting workflow debug check...")
    check_environment()
    check_dependencies()
    check_files()
    logger.info("Debug check complete")

if __name__ == "__main__":
    main()
