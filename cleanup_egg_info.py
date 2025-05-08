#!/usr/bin/env python
"""Script to clean up .egg-info directories before building packages."""

import glob
import shutil


def cleanup_egg_info():
    """Find and remove all .egg-info directories in the project."""
    count = 0
    for egg_info in glob.glob("**/*.egg-info", recursive=True):
        print(f"Removing: {egg_info}")
        shutil.rmtree(egg_info)
        count += 1

    if count > 0:
        print(f"Removed {count} .egg-info directories.")
    else:
        print("No .egg-info directories found.")


if __name__ == "__main__":
    cleanup_egg_info()
