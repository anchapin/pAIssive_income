#!/usr/bin/env python3
"""
Setup uv Package Manager

This script ensures uv is properly installed and configured.
"""

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def install_uv() -> bool:
    """Install uv if not already installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info(f"uv is already installed (version: {result.stdout.strip()}).")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("uv command not found. Will attempt to install it.")

    logger.info("Installing uv...")
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "uv",
        ])
        # Verify installation
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info(
                f"Successfully installed uv (version: {result.stdout.strip()})."
            )
            return True
        else:
            logger.error("Failed to verify uv installation after pip install.")
            return False
    except subprocess.CalledProcessError:
        logger.exception("Failed to install uv with pip.")
        logger.info("Please try installing uv manually:")
        logger.info("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def create_uv_config() -> bool:
    """Create .uv.toml configuration file if it doesn't exist."""
    uv_config_path = Path(".uv.toml")
    if uv_config_path.exists():
        logger.info(f"{uv_config_path} already exists.")
        return True

    logger.info(f"Creating {uv_config_path}...")
    try:
        with open(uv_config_path, "w") as f:
            f.write("""[pip]
index-url = "https://pypi.org/simple"
extra-index-url = []
no-binary = []
only-binary = []

[venv]
python = "3.10"
""")
        logger.info(f"Created {uv_config_path}")
        return True
    except Exception as e:
        logger.exception(f"Error creating {uv_config_path}")
        return False


def main() -> int:
    """Main function."""
    logger.info("Setting up uv package manager...")

    if not install_uv():
        logger.error("Failed to install uv. Exiting.")
        return 1

    if not create_uv_config():
        logger.error("Failed to create uv configuration. Exiting.")
        return 1

    logger.info("uv setup completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
