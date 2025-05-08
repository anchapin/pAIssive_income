"""conftest - Module for tests.conftest.

Ensures that pytest does not collect or execute any files or directories ignored by .gitignore.
"""

import subprocess
import os
import pytest

def is_git_tracked(path):
    """Return True if the file is tracked by git (not ignored), False otherwise."""
    try:
        # Use git ls-files to check if the file is tracked (not ignored)
        # --error-unmatch causes non-tracked files to raise an error
        subprocess.check_output(
            ["git", "ls-files", "--error-unmatch", os.path.relpath(path)], stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def pytest_collect_file(parent, path):
    """Hook called by pytest for every file considered for collection.

    Skips files that are not tracked by git (i.e., are git-ignored).
    """
    # Only apply check to files (not directories)
    if path.isfile():
        abspath = str(path)
        if not is_git_tracked(abspath):
            # Skip collection of ignored/untracked files
            return None
    # Let pytest handle normal collection
    # Returning None means normal behavior if not ignored
