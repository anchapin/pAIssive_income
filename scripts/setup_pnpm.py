#!/usr/bin/env python3
"""
Setup pnpm Package Manager

This script ensures pnpm is properly installed and configured.
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


def check_node_installed() -> bool:
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info(f"Node.js is installed (version: {result.stdout.strip()}).")
            return True
        else:
            logger.error("Node.js check returned non-zero exit code.")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.exception("Node.js is not installed. Please install Node.js first.")
        logger.info("Download from: https://nodejs.org/")
        return False


def install_pnpm() -> bool:
    """Install pnpm if not already installed."""
    try:
        result = subprocess.run(["pnpm", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info(
                f"pnpm is already installed (version: {result.stdout.strip()})."
            )
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("pnpm command not found. Will attempt to install it.")

    logger.info("Installing pnpm...")

    # Try using Corepack first (recommended)
    try:
        logger.info("Trying to enable Corepack...")
        subprocess.check_call(["corepack", "enable"])
        subprocess.check_call(["corepack", "prepare", "pnpm@latest", "--activate"])

        # Verify installation
        result = subprocess.run(["pnpm", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info(
                f"Successfully installed pnpm with Corepack (version: {result.stdout.strip()})."
            )
            return True
        else:
            logger.warning("Failed to verify pnpm installation after Corepack setup.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Corepack not available. Falling back to npm...")

    # Fallback to npm
    try:
        logger.info("Installing pnpm globally with npm...")
        subprocess.check_call(["npm", "install", "-g", "pnpm"])

        # Verify installation
        result = subprocess.run(["pnpm", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info(
                f"Successfully installed pnpm with npm (version: {result.stdout.strip()})."
            )
            return True
        else:
            logger.error("Failed to verify pnpm installation after npm install.")
            return False
    except subprocess.CalledProcessError:
        logger.exception("Failed to install pnpm with npm.")
        return False


def create_npmrc() -> bool:
    """Create .npmrc configuration file if it doesn't exist."""
    npmrc_path = Path(".npmrc")
    if npmrc_path.exists():
        logger.info(f"{npmrc_path} already exists.")
        return True

    logger.info(f"Creating {npmrc_path}...")
    try:
        with open(npmrc_path, "w") as f:
            f.write("""# Use pnpm as the package manager
engine-strict=true
resolution-mode=highest
auto-install-peers=true
""")
        logger.info(f"Created {npmrc_path}")
        return True
    except Exception as e:
        logger.exception(f"Error creating {npmrc_path}")
        return False


def main() -> int:
    """Main function."""
    logger.info("Setting up pnpm package manager...")

    if not check_node_installed():
        logger.error("Node.js is required for pnpm. Exiting.")
        return 1

    if not install_pnpm():
        logger.error("Failed to install pnpm. Exiting.")
        return 1

    if not create_npmrc():
        logger.error("Failed to create pnpm configuration. Exiting.")
        return 1

    logger.info("pnpm setup completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
