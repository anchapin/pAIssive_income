#!/usr/bin/env python
"""Script to clean up .egg-info directories before building packages."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Set up a dedicated logger for this module
logger = logging.getLogger(__name__)


def cleanup_egg_info() -> None:
    """Find and remove all .egg-info directories in the project."""
    count = 0
    for egg_info in Path().glob("**/*.egg-info"):
        logger.info("Removing: %s", egg_info)
        shutil.rmtree(egg_info)
        count += 1

    if count > 0:
        logger.info("Removed %d .egg-info directories.", count)
    else:
        logger.info("No .egg-info directories found.")


if __name__ == "__main__":
    cleanup_egg_info()
