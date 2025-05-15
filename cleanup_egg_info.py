#!/usr/bin/env python
"""Script to clean up .egg-info directories before building packages."""

import glob
import logging
import shutil

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def cleanup_egg_info() -> None:
    """Find and remove all .egg-info directories in the project."""
    count = 0
    for egg_info in glob.glob("**/*.egg-info", recursive=True):
        logging.info(f"Removing: {egg_info}")
        try:
            shutil.rmtree(egg_info)
            count += 1
        except OSError as e:
            logging.exception(f"Error removing {egg_info}: {e}")

    if count > 0:
        logging.info(f"Removed {count} .egg-info directories.")
    else:
        logging.info("No .egg-info directories found.")


if __name__ == "__main__":
    cleanup_egg_info()
